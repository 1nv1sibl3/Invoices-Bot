# cogs/move.py

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union
from utils.permissions import user_has_permission

class MoveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="move", description="Move a player to another user's voice channel or to a specified voice channel.")
    @app_commands.describe(
        player="The player to be moved",
        target_user="The user whose voice channel the player should be moved to (optional)",
        target_channel="The voice channel to move the player to (optional)"
    )
    async def move_slash(self, interaction: discord.Interaction, player: discord.Member, 
                         target_user: Optional[discord.Member] = None, 
                         target_channel: Optional[discord.VoiceChannel] = None):
        if not user_has_permission("afk", ctx.author):
            await interaction.response.send_message(f"❌ {player.display_name} is not in a voice channel!", ephemeral=False)

        destination = None
        if target_user:
            if not target_user.voice or not target_user.voice.channel:
                await interaction.response.send_message(f"❌ {target_user.display_name} is not in a voice channel!", ephemeral=False)
                return
            destination = target_user.voice.channel
        elif target_channel:
            destination = target_channel
        else:
            await interaction.response.send_message("❌ You must specify either a target user in a voice channel or a voice channel!", ephemeral=False)
            return

        try:
            await player.move_to(destination)
            await interaction.response.send_message(f"✅ Moved {player.display_name} to **{destination.name}**!", ephemeral=False)
        except discord.Forbidden:
            await interaction.response.send_message(f"⚠️ I don't have permission to move {player.display_name}!", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error moving player: `{e}`", ephemeral=False)

    @commands.command(name="move", aliases=["mv"])
    async def move_prefix(self, ctx: commands.Context, player: discord.Member, 
                          target: Optional[Union[discord.Member, discord.VoiceChannel]] = None):

        if not user_has_permission("move", ctx.author):
            return await ctx.send("❌ You don't have permission to use this command!")
        
        if not player.voice or not player.voice.channel:
            return await ctx.send(f"❌ {player.display_name} is not in a voice channel!")

        if target is None:
            return await ctx.send("❌ You must specify either a target user in a voice channel or a voice channel!")
        
        destination = None
        if isinstance(target, discord.Member):
            if not target.voice or not target.voice.channel:
                return await ctx.send(f"❌ {target.display_name} is not in a voice channel!")
            destination = target.voice.channel
        elif isinstance(target, discord.VoiceChannel):
            destination = target
        else:
            return await ctx.send("❌ Invalid target specified!")
        
        try:
            await player.move_to(destination)
            await ctx.send(f"✅ Moved {player.display_name} to **{destination.name}**!")
        except discord.Forbidden:
            await ctx.send(f"⚠️ I don't have permission to move {player.display_name}!")
        except Exception as e:
            await ctx.send(f"⚠️ Error moving player: `{e}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(MoveCog(bot))
