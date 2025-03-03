import discord
from discord.ext import commands
from discord import app_commands

ALLOWED_ROLE_ID = 1218583488710840432 

class ReloadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reload", description="Reload a specific cog (provide the cog's filename without .py)")
    @app_commands.checks.has_role(ALLOWED_ROLE_ID)
    async def reload(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"✅ Reloaded cog: `{cog}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to reload cog `{cog}`: {e}", ephemeral=True)

    @commands.command(name="reload")
    async def reload_prefix(self, ctx: commands.Context, cog: str):
        if ALLOWED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            return await ctx.send("❌ You don't have permission to use this command!")
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Reloaded cog: `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload cog `{cog}`: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ReloadCog(bot))
