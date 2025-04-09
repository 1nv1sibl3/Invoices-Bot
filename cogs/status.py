# cogs/status.py
import discord
from discord.ext import commands
from discord import app_commands, Activity, ActivityType, Status
from utils.permissions import user_has_permission


class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="setstatus", description="Set the bot's status and activity.")
    async def setstatus(self, ctx: commands.Context, status: str, activity_type: str, *, message: str):
        if not user_has_permission("status", ctx.author):
            embed = discord.Embed(
                title="🚫 No Permission",
                description="You don't have permission to use the command.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True if ctx.interaction else False)

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
