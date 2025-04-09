# cogs/utilities.py

import discord
from discord.ext import commands
from utils.dump_formatter import apply_format, get_filtered_members, sort_members, parse_dump_flags
from utils.permissions import user_has_permission
import io

class Dump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dump", description="Dump members in a formatted list.")
    async def dump(self, ctx: commands.Context, *, args: str = ""):

        if not (user_has_permission("dump", ctx.author) or ctx.author.guild_permissions.manage_roles):
            if isinstance(ctx, commands.Context):
                return await ctx.send("❌ You don't have permission to use this command.")
            else:
                return await ctx.send("❌ You don't have permission to use this command.", ephemeral=True)

        if not args:
            usage = (
                "Usage: `!dump -r @Role1 @Role2 -e -f %n (%i)`\n"
                "Flags: `-r`, `--order`, `--desc`, `--limit`, `-f`, `--dateformat`, `-e`, `--separator`, `--no-roles`"
            )
            return await ctx.send(usage)

        config = parse_dump_flags(ctx.guild, args)
        if config is None:
            return await ctx.send("❌ Invalid flag usage.")

        members = ctx.guild.members
        filtered = get_filtered_members(
            members,
            has_roles=config["has_roles"],
            no_roles=config["no_roles"]
        )
        sorted_members = sort_members(filtered, key=config["order"], desc=config["desc"])
        limited = sorted_members[:config["limit"]] if config["limit"] else sorted_members

        lines = []
        for idx, m in enumerate(limited, start=1):
            line = apply_format(m, config["format"], config["dateformat"])
            if config["enumerate"]:
                line = f"{idx}. {line}"
            lines.append(line)

        if not lines:
            return await ctx.send("⚠️ No matching members found.")

        result = config["separator"].join(lines)

        if len(result) > 1900:
            return await ctx.send(file=discord.File(fp=io.StringIO(result), filename="dump.txt"))
        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(Dump(bot))
