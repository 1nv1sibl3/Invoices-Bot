# cogs/invoice.py

import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta
import os
from configs import INVOICE_CHANNEL_ID  

INVOICES_FILE = "invoices.json"

product_prices = {
    "celestia": 199,
    "eldrin": 149,
    "phantom": 99,
    "titan": 49
}

LOG_CHANNEL_ID = INVOICE_CHANNEL_ID  

def load_invoices():
    try:
        with open(INVOICES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_invoices(data):
    with open(INVOICES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class InvoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="invoice", description="Generate an invoice for a user")
    @app_commands.describe(
        buyer="The buyer (user mention)",
        in_game_name="The buyer's in-game name",
        service="The service/rank to purchase",
        duration="The duration (e.g., 28d, 2h, 30m)",
        reminder_time="Time before invoice expires to send a reminder (e.g., 1d, 12h, 30m)",
        attachment="Proof of payment (mandatory)"
    )
    @app_commands.choices(service=[
        app_commands.Choice(name="Celestia", value="celestia"),
        app_commands.Choice(name="Eldrin", value="eldrin"),
        app_commands.Choice(name="Phantom", value="phantom"),
        app_commands.Choice(name="Titan", value="titan")
    ])
    @app_commands.checks.has_role(1337080845718126673)
    async def invoice(self, interaction: discord.Interaction, buyer: discord.Member, in_game_name: str, service: app_commands.Choice[str], duration: str, reminder_time: str, attachment: discord.Attachment):
        service_value = service.value
        amount = product_prices[service_value]

        try:
            if duration.endswith('d'):
                duration_days = int(duration[:-1])
            elif duration.endswith('h'):
                duration_days = int(duration[:-1]) / 24
            elif duration.endswith('m'):
                duration_days = int(duration[:-1]) / 1440
            else:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ Invalid duration format! Use 'd' for days, 'h' for hours, or 'm' for minutes.", ephemeral=True)
            return

        expiration_time = datetime.utcnow() + timedelta(days=duration_days)

        try:
            if reminder_time.endswith('d'):
                reminder_offset = int(reminder_time[:-1])
            elif reminder_time.endswith('h'):
                reminder_offset = int(reminder_time[:-1]) / 24
            elif reminder_time.endswith('m'):
                reminder_offset = int(reminder_time[:-1]) / 1440
            else:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ Invalid reminder time format! Use 'd' for days, 'h' for hours, or 'm' for minutes.", ephemeral=True)
            return

        reminder_time_final = expiration_time - timedelta(days=reminder_offset)
        expiration_timestamp = f"<t:{int(expiration_time.timestamp())}:R>"
        reminder_timestamp = f"<t:{int(reminder_time_final.timestamp())}:R>"
        invoice_gen_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        embed = discord.Embed(
            title="📜 Payment Invoice",
            description="Thank you for your purchase! Contact support for any issues.",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 Buyer", value=buyer.mention, inline=False)
        embed.add_field(name="🆔 Buyer ID", value=str(buyer.id), inline=True)
        embed.add_field(name="🎮 Buyer In-Game Name", value=in_game_name, inline=False)
        embed.add_field(name="🛠️ Staff Handler", value=interaction.user.mention, inline=False)
        embed.add_field(name="🛒 Service", value=service_value.capitalize(), inline=False)
        embed.add_field(name="💰 Amount", value=f"Rs. {amount}", inline=True)
        embed.add_field(name="📅 Date & Time", value=invoice_gen_time, inline=False)
        embed.add_field(name="⏳ Duration", value=f"{duration_days} Day(s) ({expiration_timestamp})", inline=False)
        embed.add_field(name="🔔 Auto Reminder", value=f"Reminder will be sent {reminder_timestamp}", inline=False)
        embed.add_field(name="📄 Proof", value=f"[Attachment]({attachment.url})", inline=False)
        embed.set_footer(text="Thank you for your purchase! Contact support for any issues.")

        invoices = load_invoices()
        new_invoice = {
            "UserID": buyer.id,
            "service": service_value.capitalize(),
            "amount": amount,
            "expiration": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
            "reminder": reminder_time_final.strftime("%Y-%m-%d %H:%M:%S"),
            "ingame_name": in_game_name,
            "staff": str(interaction.user.id),
            "proof": attachment.url,
            "invoice_generated": invoice_gen_time
        }
        invoices.append(new_invoice)
        save_invoices(invoices)

        invoice_channel = self.bot.get_channel(INVOICE_CHANNEL_ID)
        await invoice_channel.send(embed=embed)

        try:
            await interaction.response.defer(ephemeral=True)
            await buyer.send(embed=embed)
            await interaction.followup.send(f"✅ Invoice sent to {buyer.mention} via DM!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(f"⚠️ Could not DM {buyer.mention}. They might have DMs disabled!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(InvoiceCog(bot))
