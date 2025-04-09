# cogs/whichvc.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.permissions import user_has_permission


class WhichVcCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="whichvc", aliases=["wv"], description="Check which voice channel a user is in")
    async def whichvc(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        if not user_has_permission("whichvc", ctx.author):
            await ctx.send("❌ You don't have permission to use this command!", delete_after=5)
            return

        user = user or ctx.author

        if user.voice and user.voice.channel:
            await ctx.send(
                f"🎧 **{user.display_name}** is currently in **{user.voice.channel.name}** - <#{user.voice.channel.id}>"
            )
        else:
            await ctx.send(f"🚫 **{user.display_name}** is not in any voice channel!")

async def setup(bot: commands.Bot):
    await bot.add_cog(WhichVcCog(bot))
