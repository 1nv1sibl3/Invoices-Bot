# cogs/message.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.permissions import user_has_permission

class MessageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="msg", aliases=["message"])
    async def msg(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None, *, message: str):
        
        if not user_has_permission("message", ctx.author):
            return await ctx.send("❌ You don't have permission to use this command!", delete_after=5)
        
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        target_channel = channel or ctx.channel
        await target_channel.send(message)

    @app_commands.command(name="message", description="Send a message to a channel (optional)")
    @app_commands.describe(
        message="The message to send",
        channel="Target channel (optional)"
    )
    async def slash_message(self, interaction: discord.Interaction, message: str, channel: Optional[discord.TextChannel] = None):
        if not user_has_permission("message", interaction.user.id):
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        await target_channel.send(message)
        await interaction.response.send_message("✅ Message sent!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageCog(bot))
