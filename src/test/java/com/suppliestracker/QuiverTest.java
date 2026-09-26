package com.suppliestracker;

import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import net.runelite.api.Client;
import net.runelite.api.gameval.ItemID;
import net.runelite.api.gameval.VarPlayerID;
import org.junit.Before;
import org.junit.Test;

public class QuiverTest
{
	private SuppliesTrackerPlugin plugin;
	private Client client;
	private Quiver quiver;

	@Before
	public void setUp()
	{
		plugin = mock(SuppliesTrackerPlugin.class);
		client = mock(Client.class);
		plugin.client = client;
		quiver = new Quiver(plugin);
	}

	private void setQuiver(int ammoId, int count)
	{
		when(client.getVarpValue(VarPlayerID.DIZANAS_QUIVER_TEMP_AMMO)).thenReturn(ammoId);
		when(client.getVarpValue(VarPlayerID.DIZANAS_QUIVER_TEMP_AMMO_AMOUNT)).thenReturn(count);
		quiver.updateVarp(VarPlayerID.DIZANAS_QUIVER_TEMP_AMMO_AMOUNT);
	}

	@Test
	public void firingOneArrowTracksOne()
	{
		setQuiver(ItemID.RUNE_ARROW, 100);
		setQuiver(ItemID.RUNE_ARROW, 99);
		verify(plugin).buildEntries(ItemID.RUNE_ARROW, 1);
	}

	@Test
	public void darkBowDoubleShotTracksTwo()
	{
		setQuiver(ItemID.DRAGON_ARROW, 50);
		setQuiver(ItemID.DRAGON_ARROW, 48);
		verify(plugin).buildEntries(ItemID.DRAGON_ARROW, 2);
	}

	@Test
	public void largeDropIsNotTracked()
	{
		setQuiver(ItemID.RUNE_ARROW, 100);
		setQuiver(ItemID.RUNE_ARROW, 50);
		verify(plugin, never()).buildEntries(anyInt(), anyInt());
	}

	@Test
	public void lastArrowFiredTracksIt()
	{
		setQuiver(ItemID.RUNE_ARROW, 1);
		setQuiver(-1, 0);
		verify(plugin).buildEntries(ItemID.RUNE_ARROW, 1);
	}

	@Test
	public void emptyingAFullQuiverIsNotTracked()
	{
		setQuiver(ItemID.RUNE_ARROW, 100);
		setQuiver(-1, 0);
		verify(plugin, never()).buildEntries(anyInt(), anyInt());
	}

	@Test
	public void unrelatedVarpIsIgnored()
	{
		quiver.updateVarp(VarPlayerID.DIZANAS_QUIVER_TEMP_AMMO_AMOUNT + 12345);
		verifyNoInteractions(client);
	}
}
