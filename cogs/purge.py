import discord
from discord.ext import commands
from typing import Optional


class PurgeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def safe_send(self, ctx: commands.Context, content=None, embed=None, ephemeral=False, delete_after: Optional[int] = 5):
        try:
            if ctx.interaction:
                if not ctx.interaction.response.is_done():
                    await ctx.interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
                else:
                    await ctx.followup.send(content=content, embed=embed, ephemeral=ephemeral)
            else:
                await ctx.send(content=content, embed=embed, delete_after=delete_after)
        except Exception as e:
            print(f"Error sending message: {e}")

    @commands.hybrid_group(name="purge", with_app_command=True, description="Purge messages with various filters.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await self.safe_send(ctx, content="❌ You must specify a valid subcommand. Try `/purge all 10`. ")

    @purge.command(name="all")
    async def purge_all(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search)
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages.")

    @purge.command(name="member")
    async def purge_member(self, ctx: commands.Context, search: Optional[int] = 50, member: discord.Member = None):
        if not member:
            await self.safe_send(ctx, content="❌ Please mention a member to purge messages from.")
            return
        deleted = await ctx.channel.purge(limit=search, check=lambda m: m.author == member)
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages from {member.mention}.")

    @purge.command(name="bot")
    async def purge_bot(self, ctx: commands.Context, search: Optional[int] = 50, prefix: str = None):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: m.author.bot and (prefix is None or m.content.startswith(prefix)))
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} bot messages{f' with prefix `{prefix}`' if prefix else ''}.")

    @purge.command(name="contains")
    async def purge_contains(self, ctx: commands.Context, search: Optional[int] = 50, *, substring: str):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: substring.lower() in m.content.lower())
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages containing `{substring}`.")

    @purge.command(name="embeds")
    async def purge_embeds(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: len(m.embeds) > 0)
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages with embeds.")

    @purge.command(name="emoji")
    async def purge_emoji(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: any(e in m.content for e in discord.utils.get(ctx.guild.emojis, animated=True)))
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages with emojis.")

    @purge.command(name="files")
    async def purge_files(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: len(m.attachments) > 0)
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages with attachments.")

    @purge.command(name="images")
    async def purge_images(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: len(m.attachments) > 0 or any(e.image for e in m.embeds))
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages with images or embeds.")

    @purge.command(name="links")
    async def purge_links(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: "http" in m.content or "discord.gg" in m.content)
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages with links.")

    @purge.command(name="pings")
    async def purge_pings(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: m.mentions or m.role_mentions)
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} messages with mentions or pings.")

    @purge.command(name="humans")
    async def purge_humans(self, ctx: commands.Context, search: Optional[int] = 50):
        deleted = await ctx.channel.purge(limit=search, check=lambda m: not m.author.bot)
        await self.safe_send(ctx, content=f"✅ Deleted {len(deleted)} human messages.")

    @purge.command(name="reactions")
    async def purge_reactions(self, ctx: commands.Context, search: Optional[int] = 50):
        async for message in ctx.channel.history(limit=search):
            try:
                await message.clear_reactions()
            except discord.Forbidden:
                continue
        await self.safe_send(ctx, content="✅ Reactions cleared from messages.")


async def setup(bot: commands.Bot):
    await bot.add_cog(PurgeCog(bot))