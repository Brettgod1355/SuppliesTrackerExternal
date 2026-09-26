package com.suppliestracker;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import net.runelite.api.gameval.ItemID;
import org.junit.Test;

public class LookupTest
{
	@Test
	public void blowpipeDartForNameIgnoresCase()
	{
		assertEquals(BlowpipeDart.DRAGON, BlowpipeDart.forName("Dragon"));
		assertEquals(BlowpipeDart.AMETHYST, BlowpipeDart.forName("AMETHYST"));
	}

	@Test
	public void blowpipeDartForNameDefaultsToMithril()
	{
		assertEquals(BlowpipeDart.MITHRIL, BlowpipeDart.forName("not a dart"));
	}

	@Test
	public void blowpipeDartForProjId()
	{
		assertEquals(BlowpipeDart.RUNE, BlowpipeDart.forProjID(231));
		assertNull(BlowpipeDart.forProjID(-1));
	}

	@Test
	public void runeLookupByIndex()
	{
		assertEquals(Runes.AIR, Runes.getRune(1));
		assertEquals(Runes.AETHER, Runes.getRune(23));
		assertNull(Runes.getRune(0));
	}

	@Test
	public void everyRuneIsTrackedAsARune()
	{
		for (Runes rune : Runes.values())
		{
			assertTrue(rune.name(), SuppliesTrackerPlugin.runeIds.contains(rune.getItemId()));
		}
	}

	@Test
	public void tomePages()
	{
		assertTrue(ElementalTomes.isPage(ItemID.WINT_BURNT_PAGE));
		assertTrue(ElementalTomes.isPage(ItemID.SOILED_PAGE));
		assertTrue(ElementalTomes.isPage(ItemID.SOAKED_PAGE));
		assertTrue(ElementalTomes.isPage(ItemID.WINT_SEARING_PAGE));
		assertFalse(ElementalTomes.isPage(ItemID.TOME_OF_FIRE));
	}

	@Test
	public void bait()
	{
		assertTrue(Bait.isBait(ItemID.FEATHER));
		assertTrue(Bait.isBait(ItemID.DIABOLIC_WORMS));
		assertFalse(Bait.isBait(ItemID.SHARK));
	}
}
