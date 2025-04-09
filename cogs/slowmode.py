import discord
from discord.ext import commands
from typing import Optional
import re


def parse_time(timestr: str) -> Optional[int]:
    match = re.fullmatch(r"(\d+)([smhd])", timestr.lower().strip())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    elif unit == "d":
        return value * 86400
    return None


class SlowmodeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="slowmode", aliases=["sm"], description="Set slowmode delay for the current channel.")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, duration: Optional[str] = None):
        if duration is None:
            current_delay = ctx.channel.slowmode_delay
            await ctx.send(f"⏱️ Slowmode is currently set to **{current_delay} seconds** in this channel.")
            return

        seconds = parse_time(duration)
        if seconds is None or seconds < 0 or seconds > 21600:
            await ctx.send("❌ Please provide a valid time (e.g., 10s, 5m, 1h) up to 6 hours.")
            return

        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            if seconds == 0:
                await ctx.send("✅ Slowmode has been disabled.")
            else:
                await ctx.send(f"✅ Slowmode has been set to **{duration}** ({seconds} seconds).")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to change the slowmode settings.")


async def setup(bot: commands.Bot):
    await bot.add_cog(SlowmodeCog(bot))