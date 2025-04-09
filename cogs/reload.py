# cogs/reload.py

import discord
from discord.ext import commands
from discord import app_commands
from utils.permissions import user_has_permission

ALLOWED_ROLE_ID = 1357669593124045005 

class ReloadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- RELOAD COMMANDS ---

    # Slash command version
    @app_commands.command(name="reload", description="Reload a specific cog (provide the cog's filename without .py)")
    @app_commands.checks.has_role(ALLOWED_ROLE_ID)
    async def reload(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                title="Cog Reloaded",
                description=f"`{cog}` cog reloaded successfully.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to reload cog `{cog}`: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # Prefix command version
    @commands.command(name="reload")
    async def reload_prefix(self, ctx: commands.Context, cog: str):
        if ALLOWED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            return await ctx.send("❌ You don't have permission to use this command!")
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                title="Cog Reloaded",
                description=f"`{cog}` cog reloaded successfully.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to reload cog `{cog}`: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # --- LOAD COMMANDS ---

    # Slash command version
    @app_commands.command(name="load", description="Load a specific cog (provide the cog's filename without .py)")
    @app_commands.checks.has_role(ALLOWED_ROLE_ID)
    async def load(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            embed = discord.Embed(
                title="Cog Loaded",
                description=f"`{cog}` cog loaded successfully.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to load cog `{cog}`: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # Prefix command version
    @commands.command(name="load")
    async def load_prefix(self, ctx: commands.Context, cog: str):
        if ALLOWED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            return await ctx.send("❌ You don't have permission to use this command!")
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            embed = discord.Embed(
                title="Cog Loaded",
                description=f"`{cog}` cog loaded successfully.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to load cog `{cog}`: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # --- UNLOAD COMMANDS ---

    # Slash command version
    @app_commands.command(name="unload", description="Unload a specific cog (provide the cog's filename without .py)")
    @app_commands.checks.has_role(ALLOWED_ROLE_ID)
    async def unload(self, interaction: discord.Interaction, cog: str):
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                title="Cog Unloaded",
                description=f"`{cog}` cog unloaded successfully.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to unload cog `{cog}`: {e}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # Prefix command version
    @commands.command(name="unload")
    async def unload_prefix(self, ctx: commands.Context, cog: str):
        if ALLOWED_ROLE_ID not in [role.id for role in ctx.author.roles]:
            return await ctx.send("❌ You don't have permission to use this command!")
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                title="Cog Unloaded",
                description=f"`{cog}` cog unloaded successfully.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to unload cog `{cog}`: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReloadCog(bot))
