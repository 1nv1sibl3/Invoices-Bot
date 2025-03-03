# cogs/autoreminder.py

import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, timedelta
import os

INVOICES_FILE = "test_invoices.json"  
LOGS_FILE = "test_logs.json"          
LOG_CHANNEL_ID = 1336384115959791728    

def load_invoices():
    try:
        with open(INVOICES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_invoices(data):
    with open(INVOICES_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_logs():
    try:
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_logs(data):
    with open(LOGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class AutoReminderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.auto_reminder_loop.start()

    def cog_unload(self):
        self.auto_reminder_loop.cancel()

    @tasks.loop(minutes=1)
    async def auto_reminder_loop(self):
        now = datetime.utcnow()
        invoices = load_invoices()  
        logs = load_logs()          
        updated = False
        remaining_invoices = []

        for invoice in invoices:
            try:
                reminder_str = invoice.get("reminder")
                reminder_time = datetime.strptime(reminder_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                remaining_invoices.append(invoice)
                continue

            if now >= reminder_time:
                try:
                    user = await self.bot.fetch_user(int(invoice.get("UserID")))
                except Exception:
                    remaining_invoices.append(invoice)
                    continue

                embed = discord.Embed(
                    title="⏳ Payment Reminder",
                    description="This is a reminder for your pending payment. Please complete the payment as soon as possible.",
                    color=discord.Color.red()
                )
                embed.add_field(name="👤 Buyer", value=user.mention, inline=False)
                embed.add_field(name="🆔 Buyer ID", value=str(invoice.get("UserID")), inline=False)
                embed.add_field(name="🎮 Buyer In-Game Name", value=invoice.get("ingame_name", "N/A"), inline=False)
                embed.add_field(name="🛠 Staff Handler", value=f"<@{invoice.get('staff', 'N/A')}>", inline=False)
                embed.add_field(name="🛒 Service", value=invoice.get("service", "N/A"), inline=False)
                embed.add_field(name="💰 Amount", value=f"Rs. {invoice.get('amount', 'N/A')}", inline=False)
                embed.add_field(name="⌛ Payment Date", value=f"<t:{int(reminder_time.timestamp())}:D>", inline=False)
                embed.add_field(name="⚠ Status", value="**Pending Payment**", inline=False)
                embed.add_field(
                    name="📌 Payment Instructions",
                    value="Please make the payment via UPI and send proof to Modmail.\nIf you forgot the UPI ID, contact Modmail.",
                    inline=False
                )

                try:
                    await user.send(embed=embed)
                except discord.Forbidden:
                    pass

                logs.append(invoice)
                updated = True
            else:
                remaining_invoices.append(invoice)

        if updated:
            save_invoices(remaining_invoices)
            save_logs(logs)
            log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
            embed = discord.Embed(title="📢 Auto reminder was sent and logged", color=discord.Color.green())
            await log_channel.send(embed=embed)

    @auto_reminder_loop.before_loop
    async def before_auto_reminder(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoReminderCog(bot))
