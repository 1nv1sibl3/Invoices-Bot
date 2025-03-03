# cogs/reminder.py

import json
import os
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord import app_commands

LOGS_FILE = 'logs.json'
INVOICES_FILE = 'invoices.json'
LOG_CHANNEL_ID = 1336384115959791728 
ALLOWED_ROLE_ID = 1337080845718126673    

def load_invoices():
    try:
        with open(INVOICES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_invoices(data):
    with open(INVOICES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_logs():
    try:
        with open(LOGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_logs(data):
    with open(LOGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class ReminderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reminder", description="Manually send a payment reminder to a user")
    @app_commands.describe(
        buyer="The buyer who needs a reminder",
        ingame_name="Buyer’s in-game name",
        staff="Staff member handling the payment (mention them)",
        service="Service name",
        amount="Amount in Rs.",
        expiration="Expiration time (e.g., 1d, 2h, 30m)"
    )
    @app_commands.checks.has_role(ALLOWED_ROLE_ID)
    async def reminder(self, interaction: discord.Interaction, buyer: discord.Member, ingame_name: str, staff: discord.Member, service: str, amount: int, expiration: str):
        # Derive buyer_id from the buyer member
        buyer_id = str(buyer.id)
        logs = load_logs()
        invoices = load_invoices()

        time_units = {"d": "days", "h": "hours", "m": "minutes"}
        try:
            num = int(expiration[:-1])
            unit = expiration[-1]
            if unit not in time_units:
                raise ValueError
            delta = timedelta(**{time_units[unit]: num})
            expiration_timestamp = int((datetime.now() + delta).timestamp())
        except (ValueError, TypeError):
            await interaction.response.send_message("❌ Invalid expiration format. Use `1d`, `2h`, `30m` etc.", ephemeral=True)
            return

        if buyer_id in invoices:
            del invoices[buyer_id]
            save_invoices(invoices)

        embed = discord.Embed(
            title="⏳ Manual Payment Reminder",
            description="This is a reminder for your pending payment. Please complete the payment before the due date to avoid any delays or penalties.",
            color=discord.Color.red()
        )
        embed.add_field(name="👤 Buyer", value=buyer.mention, inline=False)
        embed.add_field(name="🆔 Buyer ID", value=buyer_id, inline=False)
        embed.add_field(name="🎮 Buyer In-Game Name", value=ingame_name, inline=False)
        embed.add_field(name="🛠 Staff Handler", value=staff.mention, inline=False)
        embed.add_field(name="🛒 Service", value=service, inline=False)
        embed.add_field(name="💰 Amount", value=f"Rs. {amount}", inline=False)
        embed.add_field(name="⌛ Payment Date", value=f"<t:{expiration_timestamp}:D>", inline=False)
        embed.add_field(name="⚠ Status", value="**Pending Payment**", inline=False)
        embed.add_field(
            name="📌 Payment Instructions",
            value="Please make the payment via UPI and send proof in Modmail.\nIf you forgot the UPI ID, contact Modmail.",
            inline=False
        )

        try:
            await buyer.send(embed=embed)
            await interaction.response.send_message(f"✅ Reminder sent to {buyer.mention} via DM!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"⚠️ Could not DM {buyer.mention}. They might have DMs disabled!", ephemeral=True)

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        log_embed = discord.Embed(
            description=f"📢 Manual reminder sent to {buyer.mention}, handled by {interaction.user.mention}.",
            color=discord.Color.green()
        )
        await log_channel.send(embed=log_embed)

        logs[buyer_id] = {
            "status": "Manual Reminder Sent",
            "buyer": buyer.mention,
            "ingame_name": ingame_name,
            "staff": staff.mention,
            "service": service,
            "amount": amount,
            "expiration": expiration
        }
        save_logs(logs)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReminderCog(bot))
