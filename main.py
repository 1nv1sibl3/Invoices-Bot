import discord
from discord.ext import commands
import os
from configs import BOT_TOKEN  

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="-", intents=intents)

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and file != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"Loaded cog: {file}")
            except Exception as e:
                print(f"Failed to load cog {file}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await load_cogs()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(BOT_TOKEN)
