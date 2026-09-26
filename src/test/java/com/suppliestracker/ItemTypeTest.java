package com.suppliestracker;

import static org.junit.Assert.assertEquals;
import net.runelite.api.gameval.ItemID;
import org.junit.Test;

public class ItemTypeTest
{
	private static ItemType categorize(int id, String name)
	{
		return ItemType.categorize(new SuppliesTrackerItem(id, name, 1, 0));
	}

	@Test
	public void fullDosePotionsArePotions()
	{
		assertEquals(ItemType.POTION, categorize(ItemID._4DOSEPRAYERRESTORE, "Prayer potion(4)"));
		assertEquals(ItemType.POTION, categorize(ItemID.BRUTAL_2DOSEPRAYERRESTORE, "Prayer mix(2)"));
	}

	@Test
	public void bonesAndAshesArePrayer()
	{
		assertEquals(ItemType.PRAYER, categorize(ItemID.DRAGON_BONES, "Dragon bones"));
		assertEquals(ItemType.PRAYER, categorize(ItemID.INFERNAL_ASHES, "Infernal ashes"));
	}

	@Test
	public void projectilesAreAmmo()
	{
		assertEquals(ItemType.AMMO, categorize(ItemID.RUNE_ARROW, "Rune arrow"));
		assertEquals(ItemType.AMMO, categorize(ItemID.MCANNONBALL, "Cannonball"));
		assertEquals(ItemType.AMMO, categorize(ItemID.RUNE_DART, "Rune dart"));
	}

	@Test
	public void runesAreRunes()
	{
		assertEquals(ItemType.RUNE, categorize(ItemID.FIRERUNE, "Fire rune"));
		assertEquals(ItemType.RUNE, categorize(ItemID.WRATHRUNE, "Wrath rune"));
	}

	@Test
	public void teleportsCoinsAndJewellery()
	{
		assertEquals(ItemType.TELEPORT, categorize(ItemID.POH_TABLET_VARROCKTELEPORT, "Varrock teleport"));
		assertEquals(ItemType.COINS, categorize(ItemID.COINS, "Coins"));
		assertEquals(ItemType.JEWELLERY, categorize(ItemID.RING_OF_DUELING_8, "Ring of dueling(8)"));
	}

	@Test
	public void farmingSupplies()
	{
		assertEquals(ItemType.FARMING, categorize(ItemID.RANARR_SEED, "Ranarr seed"));
		assertEquals(ItemType.FARMING, categorize(ItemID.BUCKET_ULTRACOMPOST, "Ultracompost"));
	}

	@Test
	public void chargedWeaponsAndTomePagesAreCharges()
	{
		assertEquals(ItemType.CHARGES, categorize(ItemID.SCYTHE_OF_VITUR, "Scythe of vitur"));
		assertEquals(ItemType.CHARGES, categorize(ItemID.SOAKED_PAGE, "Soaked page"));
	}

	@Test
	public void baitIsBait()
	{
		assertEquals(ItemType.BAIT, categorize(ItemID.FEATHER, "Feather"));
	}

	@Test
	public void anythingElseFallsBackToFood()
	{
		assertEquals(ItemType.FOOD, categorize(ItemID.SHARK, "Shark"));
	}
}
