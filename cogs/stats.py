# cogs/stats.py

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import json
from typing import Optional

# File paths
INVOICES_FILE = "invoices.json"           
COINS_INVOICES_FILE = "coin_invoices.json"  
LOGS_FILE = "logs.json"                     

# Helper functions to load data
def load_invoices():
    try:
        with open(INVOICES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_coins_invoices():
    try:
        with open(COINS_INVOICES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_logs():
    try:
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

class StatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # /sale command (hybrid)
    @commands.hybrid_command(name="sale", description="Show sales stats by month, year, or lifetime")
    @commands.has_role(1329709323273900095)
    @app_commands.describe(query="Enter a month (e.g. january), a year (e.g. 2025), or 'lifetime'")
    async def sale(self, ctx: commands.Context, query: str):
        query_lower = query.lower().strip()
        service_invs = load_invoices()   
        service_logs = load_logs()       
        coins_invs = load_coins_invoices()
        combined = []

     
        for inv in service_invs:
            try:
                dt = datetime.strptime(inv.get("invoice_generated", ""), "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            combined.append({
                "UserID": inv.get("UserID"),
                "service": inv.get("service"),
                "amount": inv.get("amount"),
                "date": dt,
                "type": "Service Active"
            })
    
        for inv in service_logs:
            try:
                dt = datetime.strptime(inv.get("invoice_generated", ""), "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            combined.append({
                "UserID": inv.get("UserID"),
                "service": inv.get("service"),
                "amount": inv.get("amount"),
                "date": dt,
                "type": "Service Logged"
            })
        # Process coin invoices (using DateOfPurchase and Final_INR_Amount)
        for inv in coins_invs:
            try:
                dt = datetime.strptime(inv.get("DateOfPurchase", ""), "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            combined.append({
                "UserID": inv.get("UserID"),
                "service": inv.get("service"),
                "amount": inv.get("Final_INR_Amount"),
                "date": dt,
                "type": "Coins"
            })

        # Filtering based on query
        if query_lower == "lifetime":
            filtered = combined
            title = "Lifetime Sales Stats"
        elif query_lower.isdigit():
            year = int(query_lower)
            filtered = [inv for inv in combined if inv["date"].year == year]
            title = f"Sales Stats for {year}"
        else:
            month_names = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
                           "july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
            if query_lower not in month_names:
                await ctx.send("❌ Invalid query. Please enter a valid month name, year, or 'lifetime'.", ephemeral=True)
                return
            month = month_names[query_lower]
            filtered = [inv for inv in combined if inv["date"].month == month]
            title = f"Sales Stats for {query_lower.capitalize()}"

        total_revenue = sum(inv.get("amount", 0) for inv in filtered)
        total_invoices = len(filtered)
        service_count = sum(1 for inv in filtered if "Service" in inv["type"])
        coins_count = sum(1 for inv in filtered if inv["type"] == "Coins")
        coins_profit = sum(inv.get("amount", 0) for inv in filtered if inv["type"] == "Coins")
        service_revenue = total_revenue - coins_profit

        embed = discord.Embed(title=title, color=discord.Color.green())
        embed.add_field(name="Total Revenue", value=f"Rs. {total_revenue}", inline=False)
        embed.add_field(name="Total Invoices", value=str(total_invoices), inline=True)
        embed.add_field(name="Service Invoices", value=str(service_count), inline=True)
        embed.add_field(name="Coins Invoices", value=str(coins_count), inline=True)
        embed.add_field(name="Coins Profit", value=f"Rs. {coins_profit}", inline=False)
        embed.add_field(name="Service Revenue", value=f"Rs. {service_revenue}", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="history", description="Retrieve purchase history for a user")
    @commands.has_role(1329709323273900095)
    @app_commands.describe(user="User to retrieve history for", category="Enter 'all' for full history or 'coins' for coin purchases")
    async def history(self, ctx: commands.Context, user: discord.Member, category: Optional[str] = "all"):
        category = category.lower()
        service_invs = load_invoices()      # Active service invoices
        service_logs = load_logs()            # Logged service invoices
        coins_invs = load_coins_invoices()    # Coin invoices

        history = []
        if category == "coins":
            for inv in coins_invs:
                if inv.get("UserID") == user.id:
                    try:
                        dt = datetime.strptime(inv.get("DateOfPurchase", ""), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                    history.append({
                        "service": inv.get("service") or "Coins",
                        "amount": inv.get("Final_INR_Amount"),
                        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Coins"
                    })
        else:
            for inv in service_invs:
                if inv.get("UserID") == user.id:
                    try:
                        dt = datetime.strptime(inv.get("invoice_generated", ""), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                    history.append({
                        "service": inv.get("service"),
                        "amount": inv.get("amount"),
                        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Service Active"
                    })
            for inv in service_logs:
                if inv.get("UserID") == user.id:
                    try:
                        dt = datetime.strptime(inv.get("invoice_generated", ""), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                    history.append({
                        "service": inv.get("service"),
                        "amount": inv.get("amount"),
                        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Service Logged"
                    })
            for inv in coins_invs:
                if inv.get("UserID") == user.id:
                    try:
                        dt = datetime.strptime(inv.get("DateOfPurchase", ""), "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                    history.append({
                        "service": inv.get("service") if inv.get("service") and inv.get("service").lower() != "none" else "Coins",
                        "amount": inv.get("Final_INR_Amount"),
                        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Coins"
                    })

        if not history:
            await ctx.send(f"No purchase history found for {user.mention}.", ephemeral=True)
            return

        # Sort history by date descending
        history.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        per_page = 5
        total_profit = 0
        if category == "coins":
            total_profit = sum(entry["amount"] for entry in history if entry["type"] == "Coins")

        def build_embed(page: int):
            embed = discord.Embed(
                title=f"Purchase History for {user.display_name}",
                color=discord.Color.blue()
            )
            start = page * per_page
            end = start + per_page
            for entry in history[start:end]:
                # Parse the date and convert to Discord timestamp format
                try:
                    dt = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
                    timestamp = int(dt.timestamp())
                    date_formatted = f"<t:{timestamp}:F>"
                except Exception:
                    date_formatted = entry["date"]
                service_name = entry["service"] if entry["service"] and entry["service"].lower() != "none" else "Coins"
                embed.add_field(
                    name=f"{entry['type']} - {service_name}",
                    value=f"Amount: Rs. {entry['amount']}\nDate: {date_formatted}",
                    inline=False
                )
            total_pages = (len(history) - 1) // per_page + 1
            embed.set_footer(text=f"Page {page+1}/{total_pages}")
            if category == "coins" and page == 0:
                embed.add_field(name="Total Coins Profit", value=f"Rs. {total_profit}", inline=False)
            return embed

        if len(history) <= per_page:
            embed = build_embed(0)
            await ctx.send(embed=embed)
        else:
            view = HistoryView(history, per_page, total_profit if category == "coins" else None)
            await ctx.send(embed=view.get_embed(), view=view)

    @commands.hybrid_command(name="services", description="List active services; optionally filter by service name")
    @commands.has_role(1329709323273900095)
    @app_commands.describe(query="Type 'active' for all, or a specific service name")
    async def services(self, ctx: commands.Context, query: str):
        query_lower = query.lower().strip()
        service_invs = load_invoices()
        if query_lower == "active":
            filtered = service_invs
            title = "Active Service Invoices"
        else:
            filtered = [inv for inv in service_invs if inv.get("service", "").lower() == query_lower]
            title = f"Active Invoices for {query_lower.capitalize()}"
        if not filtered:
            await ctx.send("No active invoices found for that query.", ephemeral=True)
            return
        description_lines = []
        for inv in filtered:
            line = f"UserID: {inv.get('UserID')}, Service: {inv.get('service')}, Amount: Rs. {inv.get('amount')}, Date: {inv.get('invoice_generated','N/A')}"
            description_lines.append(line)
        description = "\n".join(description_lines)
        embed = discord.Embed(title=title, description=description, color=discord.Color.purple())
        await ctx.send(embed=embed)

# Pagination view for /history
class HistoryView(discord.ui.View):
    def __init__(self, entries, per_page=5, coins_profit: Optional[float] = None):
        super().__init__(timeout=60)
        self.entries = entries
        self.per_page = per_page
        self.current = 0
        self.coins_profit = coins_profit

    def get_embed(self):
        embed = discord.Embed(title="Purchase History", color=discord.Color.blue())
        start = self.current
        end = start + self.per_page
        for entry in self.entries[start:end]:
            try:
                dt = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
                timestamp = int(dt.timestamp())
                date_formatted = f"<t:{timestamp}:F>"
            except Exception:
                date_formatted = entry["date"]
            service_name = entry["service"] if entry["service"] and entry["service"].lower() != "none" else "Coins"
            embed.add_field(
                name=f"{entry['type']} - {service_name}",
                value=f"Amount: Rs. {entry['amount']}\nDate: {date_formatted}",
                inline=False
            )
        total_pages = (len(self.entries) - 1) // self.per_page + 1
        embed.set_footer(text=f"Page {self.current // self.per_page + 1}/{total_pages}")
        if self.coins_profit is not None and self.current == 0:
            embed.add_field(name="Total Coins Profit", value=f"Rs. {self.coins_profit}", inline=False)
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current - self.per_page >= 0:
            self.current -= self.per_page
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current + self.per_page < len(self.entries):
            self.current += self.per_page
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()

async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))