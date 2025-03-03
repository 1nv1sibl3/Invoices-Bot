# cogs/whichvc.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

ROLE_ID_WV = [
    1218583488710840432, 1302868010855436360, 1310020946106777723,
    1218583488710840432, 1331514281963032597, 1310020946106777723,
    1310023482825904249, 1310081206209089617, 1331515996678127616,
    1333029340266496031, 1337413387839078477, 1343193291046387733,
    1335610876757147809, 1335610369003098132, 1335610778148929697,
    1335610280964521994, 1243136413289943041
]

class WhichVcCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="whichvc", aliases=["wv"], description="Check which voice channel a user is in")
    async def whichvc(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        if not any(role.id in ROLE_ID_WV for role in ctx.author.roles):
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
