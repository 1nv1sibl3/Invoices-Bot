import discord
from discord.ext import commands, tasks
from typing import Optional
import re, json, os
from datetime import datetime, timedelta

LOCK_LOG_PATH = './data/lock_log.json'


def parse_time(timestr: str) -> Optional[int]:
    match = re.fullmatch(r"(\d+)([smhd])", timestr.lower().strip())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    elif unit == "d":
        return value * 86400
    return None


def load_locks():
    if not os.path.exists(LOCK_LOG_PATH):
        return {}
    with open(LOCK_LOG_PATH, 'r') as f:
        return json.load(f)


def save_locks(data):
    with open(LOCK_LOG_PATH, 'w') as f:
        json.dump(data, f, indent=4)


class LockdownCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.locks = load_locks()
        self.check_unlocks.start()

    def cog_unload(self):
        self.check_unlocks.cancel()

    @tasks.loop(seconds=30)
    async def check_unlocks(self):
        now = datetime.utcnow().timestamp()
        to_remove = []
        for gid, channels in self.locks.items():
            for cid, expire in channels.items():
                if expire and now > expire:
                    guild = self.bot.get_guild(int(gid))
                    if not guild:
                        continue
                    channel = guild.get_channel(int(cid))
                    if channel:
                        await channel.set_permissions(guild.default_role, send_messages=None)
                    to_remove.append((gid, cid))

        for gid, cid in to_remove:
            self.locks[gid].pop(cid, None)
            if not self.locks[gid]:
                self.locks.pop(gid)
        if to_remove:
            save_locks(self.locks)

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, target: Optional[str] = None, duration: Optional[str] = None):
        if target == "server":
            seconds = parse_time(duration) if duration else None
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                if seconds:
                    self._add_lock(ctx.guild.id, channel.id, seconds)
            await ctx.send(f"🔒 Locked all channels{' for ' + duration if duration else ' indefinitely'}.")
        else:
            channel = ctx.channel if not target else await commands.TextChannelConverter().convert(ctx, target)
            seconds = parse_time(duration) if duration else None
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            if seconds:
                self._add_lock(ctx.guild.id, channel.id, seconds)
            await ctx.send(f"🔒 Locked {channel.mention}{' for ' + duration if duration else ' indefinitely'}.")

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, target: Optional[str] = None):
        if target == "server":
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(ctx.guild.default_role, send_messages=None)
            self.locks.pop(str(ctx.guild.id), None)
            await ctx.send("🔓 Unlocked all channels.")
        else:
            channel = ctx.channel if not target else await commands.TextChannelConverter().convert(ctx, target)
            await channel.set_permissions(ctx.guild.default_role, send_messages=None)
            self.locks.get(str(ctx.guild.id), {}).pop(str(channel.id), None)
            await ctx.send(f"🔓 Unlocked {channel.mention}.")
            save_locks(self.locks)

    def _add_lock(self, guild_id, channel_id, seconds):
        gid, cid = str(guild_id), str(channel_id)
        expire_time = datetime.utcnow().timestamp() + seconds
        if gid not in self.locks:
            self.locks[gid] = {}
        self.locks[gid][cid] = expire_time
        save_locks(self.locks)


async def setup(bot: commands.Bot):
    await bot.add_cog(LockdownCog(bot))