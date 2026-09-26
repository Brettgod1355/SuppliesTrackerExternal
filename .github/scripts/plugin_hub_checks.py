#!/usr/bin/env python3
"""
Local copy of the checks the RuneLite Plugin Hub packager runs on submitted plugins
(https://github.com/runelite/plugin-hub-tooling, package/.../Plugin.java), so problems show up
here instead of when the plugin is submitted.

Usage: plugin_hub_checks.py [path/to/built.jar]
Exits non-zero if any check fails. Warnings don't fail the build.
"""
import os
import re
import struct
import subprocess
import sys
import zipfile

MIB = 1024 * 1024
MAX_JAR_MIB = 10
MAX_SRC_MIB = 10
MAX_ICON_KIB = 256
MAX_ICON_SIZE = (48, 72)
JAVA_11_MAJOR = 55

PROPERTIES_FILE = "runelite-plugin.properties"
REQUIRED_PROPERTIES = {
	# key: template value the Plugin Hub rejects
	"displayName": "Example",
	"author": "Nobody",
	"description": "An example greeter plugin",
}
ALLOWED_PROPERTIES = {"displayName", "author", "description", "tags", "plugins", "build", "support"}
BUILD_TYPES = {"standard", "gradle"}
# files the Plugin Hub counts towards the source size limit
CORE_SOURCE = re.compile(r"^(\.github/|docs/|)readme(\..*)?$|^license|^src/main/|runelite-plugin.properties|\.gradle", re.IGNORECASE)

# Approximates package/src/main/resources/.../disallowed-apis.txt at the source level
DISALLOWED_APIS = [
	(re.compile(r"\bclient\s*\.\s*getVar\s*\("), "client.getVar is disallowed, use client.getVarbitValue / getVarpValue"),
	(re.compile(r"\.update\s*\(\s*\w*[Mm]essageNode"), "ChatMessageManager.update is a no-op and disallowed"),
	(re.compile(r"new\s+OkHttpClient\s*(\.Builder\s*)?\("), "don't create an OkHttpClient, @Inject the client's OkHttpClient"),
	(re.compile(r"new\s+Gson(Builder)?\s*\("), "don't create a Gson, @Inject the client's Gson (use .newBuilder() to customise it)"),
	(re.compile(r"\bWidgetInfo\b"), "WidgetInfo is disallowed, use ComponentID / InterfaceID"),
	(re.compile(r"\bWidgetID\b"), "WidgetID is disallowed, use ComponentID / InterfaceID"),
	(re.compile(r"getItemStats\s*\([^,()]+,[^()]+\)"), "use the getItemStats(int itemId) overload"),
	(re.compile(r"\bAccountClient\b|\bAccountSession\b"), "account APIs are disallowed"),
]

errors = 0
in_actions = os.environ.get("GITHUB_ACTIONS") == "true"


def error(message, file=None, line=None):
	global errors
	errors += 1
	report("error", message, file, line)


def warning(message, file=None, line=None):
	report("warning", message, file, line)


def report(level, message, file, line):
	if in_actions:
		location = ""
		if file:
			location = f" file={file}" + (f",line={line}" if line else "")
		print(f"::{level}{location}::{message}")
	else:
		where = f"{file}:{line}: " if file and line else f"{file}: " if file else ""
		print(f"{level.upper()}: {where}{message}")


def read_properties(path):
	props = {}
	with open(path, encoding="utf-8") as f:
		for number, raw in enumerate(f, 1):
			line = raw.strip()
			if not line or line[0] in "#!":
				continue
			key, _, value = re.split(r"\s*([=:])\s*", line, maxsplit=1) if re.search(r"[=:]", line) else (line, "", "")
			props[key] = (value.strip(), number)
	return props


def check_properties():
	if not os.path.exists(PROPERTIES_FILE):
		error(f"{PROPERTIES_FILE} is missing")
		return []

	props = read_properties(PROPERTIES_FILE)
	for key, template in REQUIRED_PROPERTIES.items():
		value = props.get(key, ("", None))[0]
		if not value or value == template:
			error(f'"{key}" must be set', PROPERTIES_FILE)

	build, line = props.get("build", ("", None))
	if not build:
		error('"build" must be set (build=standard is recommended)', PROPERTIES_FILE)
	elif build not in BUILD_TYPES:
		error(f'build must be one of {sorted(BUILD_TYPES)}, not "{build}"', PROPERTIES_FILE, line)

	for key, (_, line) in props.items():
		if key not in ALLOWED_PROPERTIES:
			error(f'unknown key "{key}" in {PROPERTIES_FILE}', PROPERTIES_FILE, line)

	plugins, line = props.get("plugins", ("", None))
	classes = [c.strip() for c in re.split(r"[,:;]", plugins) if c.strip()]
	if not classes:
		error('"plugins" must list at least one plugin class', PROPERTIES_FILE, line)
	return classes


def check_plugin_classes(classes):
	for name in classes:
		path = os.path.join("src", "main", "java", *name.split(".")) + ".java"
		if not os.path.exists(path):
			error(f'plugin class "{name}" not found at {path}', PROPERTIES_FILE)
			continue
		with open(path, encoding="utf-8") as f:
			source = f.read()
		if not re.search(r"\bextends\s+Plugin\b", source) or "@PluginDescriptor" not in source:
			error(f'"{name}" must extend Plugin and have a @PluginDescriptor', path)


def check_license():
	if not os.path.exists("LICENSE"):
		error("Missing LICENSE file (the Plugin Hub recommends BSD 2-Clause)")


def check_icon():
	if not os.path.exists("icon.png"):
		return
	size = os.path.getsize("icon.png")
	if size > MAX_ICON_KIB * 1024:
		error(f"icon.png is {size // 1024}KiB, which is above the limit of {MAX_ICON_KIB}KiB", "icon.png")
	with open("icon.png", "rb") as f:
		header = f.read(24)
	if header[:8] != b"\x89PNG\r\n\x1a\n":
		error("icon.png is not a valid PNG", "icon.png")
		return
	width, height = struct.unpack(">II", header[16:24])
	if width > MAX_ICON_SIZE[0] or height > MAX_ICON_SIZE[1]:
		error(f"icon.png is {width}x{height}, it should be at most {MAX_ICON_SIZE[0]}x{MAX_ICON_SIZE[1]} px", "icon.png")


def check_source_size():
	files = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
	total = sum(os.path.getsize(f) for f in files if CORE_SOURCE.search(f) and os.path.isfile(f))
	if total > MAX_SRC_MIB * MIB:
		error(f"source is {total / MIB:.1f}MiB, which is above the limit of {MAX_SRC_MIB}MiB")


def check_disallowed_apis():
	for root, _, names in os.walk(os.path.join("src", "main", "java")):
		for name in names:
			if not name.endswith(".java"):
				continue
			path = os.path.join(root, name).replace(os.sep, "/")
			with open(path, encoding="utf-8") as f:
				for number, line in enumerate(f, 1):
					code = line.split("//", 1)[0]
					for pattern, message in DISALLOWED_APIS:
						if pattern.search(code):
							error(message, path, number)


def check_jar(jar):
	size = os.path.getsize(jar)
	if size > MAX_JAR_MIB * MIB:
		error(f"jar is {size / MIB:.1f}MiB, which is above the limit of {MAX_JAR_MIB}MiB", jar)
	elif size > MAX_JAR_MIB * MIB * 8 // 10:
		warning(f"jar is {size / MIB:.1f}MiB, which is nearing the limit of {MAX_JAR_MIB}MiB", jar)

	with zipfile.ZipFile(jar) as zf:
		multi_release = "Multi-Release: true" in zf.read("META-INF/MANIFEST.MF").decode("utf-8", "ignore") \
			if "META-INF/MANIFEST.MF" in zf.namelist() else False
		for entry in zf.namelist():
			if not entry.endswith(".class"):
				continue
			if entry.startswith("net/runelite/"):
				error("use of the net.runelite package namespace is not allowed", entry)
			if multi_release or entry.endswith("module-info.class"):
				continue
			major = struct.unpack(">H", zf.read(entry)[6:8])[0]
			if major > JAVA_11_MAJOR:
				error(f"plugins must be Java 11 compatible (class file version {major})", entry)


def main():
	classes = check_properties()
	check_plugin_classes(classes)
	check_license()
	check_icon()
	check_source_size()
	check_disallowed_apis()
	for jar in sys.argv[1:]:
		check_jar(jar)

	if errors:
		print(f"\nPlugin Hub checks failed with {errors} error(s)")
		sys.exit(1)
	print("Plugin Hub checks passed")


if __name__ == "__main__":
	main()
