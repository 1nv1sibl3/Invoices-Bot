# cogs/rolemap.py
import discord
from discord.ext import commands
from discord import app_commands
import os
from utils.permissions import user_has_permission

class RoleMapCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="rolemap", description="Displays all roles in the server with their IDs.")
    @commands.has_permissions(manage_guild=True)
    async def rolemap(self, ctx: commands.Context):
        roles = ctx.guild.roles[::-1]  
        role_list = "\n".join([f"{role.name} → {role.id}" for role in roles if role.id != ctx.guild.id])
        
        if len(role_list) > 2000:
            with open("rolemap.txt", "w", encoding="utf-8") as file:
                file.write(role_list)
            await ctx.send("📂 **Role list is too long! Uploaded as a file:**", file=discord.File("rolemap.txt"))
            os.remove("rolemap.txt")  
        else:
            embed = discord.Embed(title="📜 Server Role Map", description=role_list, color=discord.Color.blue())
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)

    @rolemap.error
    async def rolemap_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need the `Manage Server` permission to use this command!", delete_after=5)

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleMapCog(bot))
