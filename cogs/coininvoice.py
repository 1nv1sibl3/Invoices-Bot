# cogs/coininvoice.py

import json
import os
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands

COINS_INVOICE = "coin_invoices.json"
INVOICES_ROLE = 1337080845718126673 
LOG_CHANNEL_ID = 1336384115959791728 

if not os.path.exists(COINS_INVOICE):
    with open(COINS_INVOICE, "w") as f:
        json.dump([], f)

class CoinInvoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="coininvoice", description="Create a coin invoice for a player.")
    @app_commands.describe(
        player="The player receiving the coins",
        ingame_name="The player's in-game name",
        coin_amount="Amount of coins",
        discount="Discount percentage (0-100)"
    )
    async def coininvoice(self, interaction: discord.Interaction, player: discord.Member, ingame_name: str, coin_amount: int, discount: float):
        # Check if the user invoking the command has the required role
        if INVOICES_ROLE not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            return

        if discount < 0 or discount > 100:
            await interaction.response.send_message("❌ Discount must be between 0% and 100%!", ephemeral=True)
            return

        nr_amount = coin_amount / 10
        discounted_nr = nr_amount * ((100 - discount) / 100)
        date_of_purchase = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        invoice_entry = {
            "UserID": player.id,
            "Username": player.name,
            "InGameName": ingame_name,
            "Coins": coin_amount,
            "INR_Equivalent": nr_amount,
            "Discount": discount,
            "Final_INR_Amount": discounted_nr,
            "DateOfPurchase": date_of_purchase,
            "StaffHandler": interaction.user.id
        }

        with open(COINS_INVOICE, "r") as f:
            invoices = json.load(f)
        invoices.append(invoice_entry)
        with open(COINS_INVOICE, "w") as f:
            json.dump(invoices, f, indent=4)

        embed = discord.Embed(title="📝 Coin Invoice", color=discord.Color.gold())
        embed.add_field(name="👤 Player", value=f"{player.mention} ({player.name})", inline=True)
        embed.add_field(name="🎮 In-Game Name", value=f"`{ingame_name}`", inline=True)
        embed.add_field(name="💰 Coins", value=f"`{coin_amount}`", inline=False)
        embed.add_field(name="💵 INR Equivalent (before discount)", value=f"`{nr_amount}`", inline=True)
        embed.add_field(name="🎟 Discount Applied", value=f"`{discount}%`", inline=True)
        embed.add_field(name="💲 Final INR Amount", value=f"`{discounted_nr}`", inline=False)
        embed.add_field(name="📅 Date of Purchase", value=f"`{date_of_purchase}`", inline=False)
        embed.add_field(name="🛠 Staff Handler", value=interaction.user.mention, inline=True)
        embed.set_footer(text="⚠ Status: Payment Done")

        await interaction.response.send_message("✅ **Invoice generated successfully!**", ephemeral=False)

        try:
            await player.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(f"⚠ {player.mention} has DMs closed. Unable to send invoice.", ephemeral=True)
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CoinInvoiceCog(bot))
