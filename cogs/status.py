# cogs/status.py
import discord
from discord.ext import commands
from discord import app_commands, Activity, ActivityType, Status

ROLE_ID_STATUS = [1218583488710840432]  

class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="setstatus", description="Set the bot's status and activity.")
    async def setstatus(self, ctx: commands.Context, status: str, activity_type: str, *, message: str):
        if not any(role.id in ROLE_ID_STATUS for role in ctx.author.roles):
            await ctx.send("❌ You don't have permission to use this command!", delete_after=5)
            return

        status_dict = {
            "online": Status.online,
            "idle": Status.idle,
            "dnd": Status.dnd,
            "invisible": Status.invisible
        }
        activity_dict = {
            "playing": ActivityType.playing,
            "watching": ActivityType.watching,
            "listening": ActivityType.listening,
            "competing": ActivityType.competing
        }

        if status.lower() not in status_dict:
            await ctx.send("❌ Invalid status! Choose from: online, idle, dnd, invisible", delete_after=5)
            return

        if activity_type.lower() not in activity_dict:
            await ctx.send("❌ Invalid activity type! Choose from: playing, watching, listening, competing", delete_after=5)
            return

        await self.bot.change_presence(
            status=status_dict[status.lower()],
            activity=discord.Activity(type=activity_dict[activity_type.lower()], name=message)
        )
        await ctx.send(f"✅ Bot status updated to **{status.capitalize()}** and **{activity_type.capitalize()} {message}**")

async def setup(bot: commands.Bot):
    await bot.add_cog(StatusCog(bot))
