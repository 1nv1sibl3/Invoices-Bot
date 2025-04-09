# cogs/afk.py

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List
import json
import os
from datetime import datetime
from utils.permissions import *

AFK_FILE = "./data/afk.json"
AFK_CONFIG_FILE = "./data/afk_config.json"

def load_afk():
    try:
        with open(AFK_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_afk(data):
    with open(AFK_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_config():
    try:
        with open(AFK_CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"ignored_channels": [], "ignored_categories": []}

def save_config(config):
    with open(AFK_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

class AFKManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.afk_users = load_afk()
        self.config = load_config()

    @commands.hybrid_command(name="afk", description="Set AFK for yourself or another user")
    @app_commands.describe(user="User to set AFK (optional)", reason="Reason for AFK (optional)")
    async def afk(self, ctx: commands.Context, user: Optional[discord.Member] = None, *, reason: Optional[str] = None):

        if not user_has_permission("afk", ctx.author):
            return

        member = user or ctx.author
        reason = reason or "AFK"

        original_nick = member.display_name
        new_nick = f"[AFK] {original_nick}" if not original_nick.startswith("[AFK] ") else original_nick

        try:
            await member.edit(nick=new_nick)
        except Exception:
            pass

        self.afk_users[str(member.id)] = {
            "reason": reason,
            "time": datetime.utcnow().isoformat(),
            "original_nick": original_nick
        }
        save_afk(self.afk_users)

        if ctx.author == member:
            await ctx.send(f"✅ {member.mention}, you are now AFK. Reason: `{reason}`")
        else:
            await ctx.send(f"✅ Set AFK for {member.mention}. Reason: `{reason}`")

    @commands.hybrid_group(name="afkconfig", description="Configure AFK ignored channels/categories")
    @commands.has_permissions(manage_guild=True)
    async def afk_config(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `add` or `remove` subcommand to modify AFK ignore settings.")

    @afk_config.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def afk_config_add(self, ctx, ignore_channels: commands.Greedy[discord.TextChannel] = None, ignore_categories: commands.Greedy[discord.CategoryChannel] = None):
        ignore_channels = ignore_channels or []
        ignore_categories = ignore_categories or []

        for channel in ignore_channels:
            if channel.id not in self.config["ignored_channels"]:
                self.config["ignored_channels"].append(channel.id)
        for category in ignore_categories:
            if category.id not in self.config["ignored_categories"]:
                self.config["ignored_categories"].append(category.id)

        save_config(self.config)
        await ctx.send("✅ AFK ignore configuration updated.")

    @afk_config.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def afk_config_remove(self, ctx, ignore_channels: commands.Greedy[discord.TextChannel] = None, ignore_categories: commands.Greedy[discord.CategoryChannel] = None):
        ignore_channels = ignore_channels or []
        ignore_categories = ignore_categories or []

        for channel in ignore_channels:
            if channel.id in self.config["ignored_channels"]:
                self.config["ignored_channels"].remove(channel.id)
        for category in ignore_categories:
            if category.id in self.config["ignored_categories"]:
                self.config["ignored_categories"].remove(category.id)

        save_config(self.config)
        await ctx.send("🗑️ AFK ignore configuration updated.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id in self.config["ignored_channels"] or message.channel.category_id in self.config["ignored_categories"]:
            return

        user_id = str(message.author.id)
        if user_id in self.afk_users:
            afk_data = self.afk_users[user_id]
            original_nick = afk_data.get("original_nick")
            try:
                if original_nick:
                    await message.author.edit(nick=original_nick)
            except Exception:
                pass
            del self.afk_users[user_id]
            save_afk(self.afk_users)
            try:
                await message.channel.send(f"Welcome back, {message.author.mention}! Your AFK status has been removed.")
            except Exception:
                pass

        for user in message.mentions:
            uid = str(user.id)
            if uid in self.afk_users:
                afk_info = self.afk_users[uid]
                reason = afk_info.get("reason", "No reason provided.")
                try:
                    afk_time = datetime.fromisoformat(afk_info.get("time"))
                except Exception:
                    afk_time = datetime.utcnow()
                timestamp = int(afk_time.timestamp())
                await message.channel.send(
                    f"{user.mention} is currently AFK: **{reason}** (since <t:{timestamp}:R>)"
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(AFKManager(bot))
