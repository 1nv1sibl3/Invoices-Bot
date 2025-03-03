# cogs/afk.py

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import json
import os
from datetime import datetime

AFK_FILE = "afk.json"
AFK_ALLOWED_ROLE = [1302868010855436360, 1310021540053651536, 1218583488710840432,1331514281963032597,1310020946106777723,1310023482825904249,1310081206209089617,1331515996678127616,1333029340266496031,1337413387839078477,1343193291046387733]
IGNORED_CATEGORIES = [1228291469882691635, 1331496763114127452,1331496914092560495,1331638713431756962,1307045763385131139,1228291459665498152,1307044704260591646]  

def load_afk():
    try:
        with open(AFK_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_afk(data):
    with open(AFK_FILE, "w") as f:
        json.dump(data, f, indent=4)

class AFKManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.afk_users = load_afk()  # Format: { "user_id": {"reason": str, "time": ISO string, "original_nick": str } }

    @commands.hybrid_command(name="afk", description="Set your AFK status with an optional reason.")
    @app_commands.describe(reason="Reason for AFK (optional)")
    @commands.has_any_role()
    async def afk(self, ctx: commands.Context, *, reason: Optional[str] = None):
        reason = reason or "AFK"
        member = ctx.author
        original_nick = member.display_name
        if not original_nick.startswith("[AFK] "):
            new_nick = f"[AFK] {original_nick}"
        else:
            new_nick = original_nick
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
        await ctx.send(f"✅ {member.mention}, you are now AFK. Reason: `{reason}`")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.category_id in IGNORED_CATEGORIES:
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

        # Check if any mentioned users are AFK and notify
        for user in message.mentions:
            uid = str(user.id)
            if uid in self.afk_users:
                afk_info = self.afk_users[uid]
                reason = afk_info.get("reason", "No reason provided.")
                try:
                    afk_time = datetime.fromisoformat(afk_info.get("time"))
                except Exception:
                    afk_time = datetime.utcnow()
                elapsed = datetime.utcnow() - afk_time
                elapsed_seconds = int(elapsed.total_seconds())
                days = elapsed_seconds // 86400
                hours = (elapsed_seconds % 86400) // 3600
                minutes = (elapsed_seconds % 3600) // 60

                if days > 0:
                    time_str = f"{days}d {hours}h {minutes}m"
                elif hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"

                await message.channel.send(
                    f"{user.mention} is currently AFK: **{reason}** (AFK for {time_str})"
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(AFKManager(bot))
