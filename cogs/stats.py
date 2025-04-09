# cogs/stats.py

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import json
from typing import Optional
from utils.permissions import user_has_permission

# File paths
INVOICES_FILE = "./data/invoices.json"           
COINS_INVOICES_FILE = "./data/coin_invoices.json"  
LOGS_FILE = "./data/logs.json"                     

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
    @app_commands.describe(query="Enter a month (e.g. january), a year (e.g. 2025), or 'lifetime'")
    async def sale(self, ctx: commands.Context, query: str):

        if not user_has_permission("stats", ctx.author):
            embed = discord.Embed(
                title="🚫 No Permission",
                description="You don't have permission to use the command.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True if ctx.interaction else False)

        query_lower = query.lower().strip()
        service_invs = load_invoices()   # Active service invoices (with "invoice_generated")
        service_logs = load_logs()         # Logged service invoices (with "invoice_generated")
        coins_invs = load_coins_invoices() # Coin invoices (with "DateOfPurchase" and Final_INR_Amount)
        combined = []

        # Process active service invoices
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

        # Process logged service invoices
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
            month_names = {
                "january": 1, "february": 2, "march": 3, "april": 4,
                "may": 5, "june": 6, "july": 7, "august": 8,
                "september": 9, "october": 10, "november": 11, "december": 12
            }
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

        embed = discord.Embed(title=f"**{title}**", color=discord.Color.green())
        embed.add_field(name="📄 Total Invoices", value=f"`{total_invoices}`", inline=True)
        embed.add_field(name="🔧 Service Invoices", value=f"`{service_count}`", inline=True)
        embed.add_field(name="💵 Coins Invoices", value=f"`{coins_count}`", inline=True)
        embed.add_field(name="💸 Coins Profit", value=f"`Rs. {coins_profit}`", inline=False)
        embed.add_field(name="📈 Service Revenue", value=f"`Rs. {service_revenue}`", inline=False)
        embed.add_field(name="💰 Total Revenue", value=f"`Rs. {total_revenue}`", inline=False)
        embed.set_footer(text=f"Data as of <t:{int(datetime.utcnow().timestamp())}:F>")
        await ctx.send(embed=embed)


    @commands.hybrid_command(name="history", description="Retrieve purchase history for a user")
    @commands.has_role(1329709323273900095)
    @app_commands.describe(
        user="User to retrieve history for"
    )
    async def history(self, ctx: commands.Context, user: discord.Member):
        # Load invoice data from all sources
        service_invs = load_invoices()    
        service_logs = load_logs()            
        coins_invs = load_coins_invoices()    

        # Build full history for each category
        full_history = []
        active_history = []
        logged_history = []
        coins_history = []

        for inv in service_invs:
            if inv.get("UserID") == user.id:
                try:
                    dt = datetime.strptime(inv.get("invoice_generated", ""), "%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue
                entry = {
                    "service": inv.get("service"),
                    "amount": inv.get("amount"),
                    "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "Service Active",
                    "invoice_generated": inv.get("invoice_generated", "N/A")
                }
                full_history.append(entry)
                active_history.append(entry)

        for inv in service_logs:
            if inv.get("UserID") == user.id:
                try:
                    dt = datetime.strptime(inv.get("invoice_generated", ""), "%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue
                entry = {
                    "service": inv.get("service"),
                    "amount": inv.get("amount"),
                    "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "Service Logged",
                    "invoice_generated": inv.get("invoice_generated", "N/A")
                }
                full_history.append(entry)
                logged_history.append(entry)

        for inv in coins_invs:
            if inv.get("UserID") == user.id:
                try:
                    dt = datetime.strptime(inv.get("DateOfPurchase", ""), "%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue
                entry = {
                    "service": inv.get("service") if inv.get("service") and inv.get("service").lower() != "none" else "Coins",
                    "amount": inv.get("Final_INR_Amount"),
                    "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "Coins",
                    "invoice_generated": inv.get("DateOfPurchase", "N/A")
                }
                full_history.append(entry)
                coins_history.append(entry)

        if not full_history:
            await ctx.send(f"No purchase history found for {user.mention}.", ephemeral=True)
            return

        # Sort each list by date descending
        def sort_entries(entries):
            return sorted(entries, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        
        full_history = sort_entries(full_history)
        active_history = sort_entries(active_history)
        logged_history = sort_entries(logged_history)
        coins_history = sort_entries(coins_history)

        # Prepare data dictionary for the view
        history_data = {
            "all": full_history,
            "active": active_history,
            "logged": logged_history,
            "coins": coins_history
        }

        view = HistoryCategoryView(user, history_data, per_page=5)
        await ctx.send(embed=view.get_embed(), view=view)

    @commands.hybrid_command(name="services", description="List active service invoices with expiry details; optionally filter by service name")
    @commands.has_role(1329709323273900095)
    @app_commands.describe(query="Type 'active' for all, or a specific service name")
    async def services(self, ctx: commands.Context, query: str):
        query_lower = query.lower().strip()
        service_invs = load_invoices()

        if query_lower == "active":
            filtered = service_invs
            title = "📋 Active Service Invoices"
        else:
            filtered = [inv for inv in service_invs if inv.get("service", "").lower() == query_lower]
            title = f"📋 Active Invoices for {query_lower.capitalize()}"

        if not filtered:
            await ctx.send("❌ No active invoices found for that query.", ephemeral=True)
            return

        # Column definitions (adjust widths as needed)
        col_user_width = 15
        col_service_width = 10
        col_date_width = 18
        col_expire_width = 10

        # Header + separator
        header = (
            f"{'User':<{col_user_width}} | "
            f"{'Service':<{col_service_width}} | "
            f"{'Date':<{col_date_width}} | "
            f"{'Expires':<{col_expire_width}}"
        )
        separator = "-" * (col_user_width + col_service_width + col_date_width + col_expire_width + 9)  # +9 for separators/spaces

        lines = [header, separator]

        for inv in filtered:
            # 1) Resolve user name
            uid = str(inv.get("UserID", "N/A"))
            user_obj = ctx.guild.get_member(int(uid)) if uid.isdigit() else None
            if user_obj:
                # Truncate display name if needed
                user_name = user_obj.display_name
            else:
                user_name = uid
            if len(user_name) > col_user_width:
                user_name = user_name[: col_user_width - 2] + ".."  # e.g. "Mr_Jagdish.." if too long

            # 2) Service name
            service_name = inv.get("service", "N/A")
            if len(service_name) > col_service_width:
                service_name = service_name[: col_service_width - 2] + ".."

            # 3) Parse invoice_generated to date + expires in days
            raw_date = inv.get("invoice_generated", "")
            try:
                dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d %b %Y %I:%M %p")  # e.g. "06 Feb 2025 04:09 PM"
                if len(date_str) > col_date_width:
                    date_str = date_str[: col_date_width - 2] + ".."
                expiration_dt = dt + timedelta(days=28)
                days_remaining = (expiration_dt - datetime.utcnow()).days
                expires_str = f"{days_remaining}d" if days_remaining >= 0 else "Expired"
            except Exception:
                date_str = "N/A"
                expires_str = "N/A"

            # 4) Build line with fixed columns
            line = (
                f"{user_name:<{col_user_width}} | "
                f"{service_name:<{col_service_width}} | "
                f"{date_str:<{col_date_width}} | "
                f"{expires_str:<{col_expire_width}}"
            )
            lines.append(line)

        code_block = "```" + "\n".join(lines) + "```"
        embed = discord.Embed(title=title, description=code_block, color=discord.Color.purple())
        embed.set_footer(text="Data retrieved from active invoices")
        await ctx.send(embed=embed)



# Pagination view for /history
class HistoryCategoryView(discord.ui.View):
    def __init__(self, user: discord.Member, history_data: dict, per_page=5):
        super().__init__(timeout=120)
        self.user = user
        self.history_data = history_data  # Dict with keys: all, active, logged, coins
        self.per_page = per_page
        self.current_category = "all"
        self.entries = self.history_data[self.current_category]
        self.page = 0

    def get_embed(self):
        embed = discord.Embed(
            title=f"Purchase History for {self.user.display_name} ({self.current_category.capitalize()})",
            color=discord.Color.blue()
        )
        start = self.page * self.per_page
        end = start + self.per_page
        for entry in self.entries[start:end]:
            try:
                dt = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
                timestamp = int(dt.timestamp())
                date_formatted = f"<t:{timestamp}:F>"
            except Exception:
                date_formatted = entry["date"]
            embed.add_field(
                name=f"{entry['type']} - {entry['service']}",
                value=f"Amount: `Rs. {entry['amount']}`\nDate: {date_formatted}\nInvoice: `{entry.get('invoice_generated','N/A')}`",
                inline=False
            )
        total_pages = (len(self.entries) - 1) // self.per_page + 1 if self.entries else 1
        embed.set_footer(text=f"Page {self.page+1}/{total_pages}")
        if self.current_category == "coins" and self.page == 0:
            total_profit = sum(e["amount"] for e in self.entries)
            embed.add_field(name="Total Coins Profit", value=f"`Rs. {total_profit}`", inline=False)
        return embed

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="All", style=discord.ButtonStyle.primary)
    async def all_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = "all"
        self.entries = self.history_data["all"]
        self.page = 0
        await self.update_message(interaction)

    @discord.ui.button(label="Active", style=discord.ButtonStyle.primary)
    async def active_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = "active"
        self.entries = self.history_data["active"]
        self.page = 0
        await self.update_message(interaction)

    @discord.ui.button(label="Logged", style=discord.ButtonStyle.primary)
    async def logged_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = "logged"
        self.entries = self.history_data["logged"]
        self.page = 0
        await self.update_message(interaction)

    @discord.ui.button(label="Coins", style=discord.ButtonStyle.primary)
    async def coins_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = "coins"
        self.entries = self.history_data["coins"]
        self.page = 0
        await self.update_message(interaction)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.page + 1) * self.per_page < len(self.entries):
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))