# cogs/admin.py

import discord
from discord.ext import commands
from utils.permissions import add_perms, remove_perms, get_perms

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="setperms", description="Manage command permissions.")
    @commands.has_permissions(manage_guild=True)
    async def setperms(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: `add`, `remove`, or `show`.")

    @setperms.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx: commands.Context, cog: str,
                  roles: commands.Greedy[discord.Role] = commands.Greedy(converter=discord.Role),
                  users: commands.Greedy[discord.Member] = commands.Greedy(converter=discord.Member)):

        if not roles and not users:
            return await ctx.send("❌ Please mention at least one role or user to add.",
                                  ephemeral=not isinstance(ctx, commands.Context))

        if f"cogs.{cog}" not in self.bot.extensions:
            return await ctx.send(f"❌ The cog `{cog}` is not currently loaded.", ephemeral=not isinstance(ctx, commands.Context))

        add_perms(cog, roles, users)
        await ctx.send(f"✅ Added to `{cog}`:\n- **Roles:** {len(roles)}\n- **Users:** {len(users)}",
                       ephemeral=not isinstance(ctx, commands.Context))

    @setperms.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx: commands.Context, cog: str,
                     roles: commands.Greedy[discord.Role] = commands.Greedy(converter=discord.Role),
                     users: commands.Greedy[discord.Member] = commands.Greedy(converter=discord.Member)):

        if not roles and not users:
            return await ctx.send("❌ Please mention at least one role or user to remove.",
                                  ephemeral=not isinstance(ctx, commands.Context))

        if f"cogs.{cog}" not in self.bot.extensions:
            return await ctx.send(f"❌ The cog `{cog}` is not currently loaded.", ephemeral=not isinstance(ctx, commands.Context))

        remove_perms(cog, roles, users)
        await ctx.send(f"🗑️ Removed from `{cog}`:\n- **Roles:** {len(roles)}\n- **Users:** {len(users)}",
                       ephemeral=not isinstance(ctx, commands.Context))

    @setperms.command(name="show")
    @commands.has_permissions(manage_guild=True)
    async def show(self, ctx: commands.Context, cog: str):
        if f"cogs.{cog}" not in self.bot.extensions:
            return await ctx.send(f"❌ The cog `{cog}` is not currently loaded.", ephemeral=not isinstance(ctx, commands.Context))
        data = get_perms(cog)
        guild = ctx.guild
        roles = [guild.get_role(rid) for rid in data["roles"]]
        users = [guild.get_member(uid) for uid in data["users"]]

        embed = discord.Embed(title=f"🔐 Permissions for `{cog}`", color=discord.Color.blurple())
        embed.add_field(name="Roles", value="\n".join(r.mention for r in roles if r) or "None", inline=False)
        embed.add_field(name="Users", value="\n".join(u.mention for u in users if u) or "None", inline=False)
        await ctx.send(embed=embed, ephemeral=not isinstance(ctx, commands.Context))

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
