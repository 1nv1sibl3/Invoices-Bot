import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, timedelta
from configs import *  

# Intents for the bot to work properly
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
intents.dm_messages = True

LOGS_FILE = 'logs.json'
INVOICES_FILE = 'invoices.json'

# Create the bot instance with prefix and intents
bot = commands.Bot(command_prefix="-", intents=intents)

# Define the product prices for different ranks
product_prices = {
    "celestia": 199,
    "eldrin": 149,
    "phantom": 99,
    "titan": 49,
}

# Channel where invoice logs are sent
INVOICE_CHANNEL_ID = INVOICE_CHANNEL_ID
LOG_CHANNEL_ID = INVOICE_CHANNEL_ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    send_reminders.start()  


# Load user data from invoices.json
def load_invoices():
    try:
        with open(INVOICES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save user data to invoices.json
def save_invoices(data):
    with open(INVOICES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Append user data to logs.json
def log_to_logs(data):
    try:
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
            if not isinstance(logs, list):  # Check if logs is not a list
                logs = []  # Initialize as an empty list if it's not
    except FileNotFoundError:
        logs = []

    logs.append(data)

    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

user_data = load_invoices()

for user_id, data in user_data.items():
    data['expiration'] = (datetime.now() + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')

save_invoices(user_data)

@tasks.loop(minutes=1)
async def send_reminders():
    now = datetime.now()
    invoices = load_invoices()
    
    for user_id, data in invoices.copy().items(): 
        try:
            
            reminder_time = datetime.strptime(data['expiration'], '%Y-%m-%d %H:%M:%S') - timedelta(minutes=1)

            if now >= reminder_time and now < datetime.strptime(data['expiration'], '%Y-%m-%d %H:%M:%S'):
                user = await bot.fetch_user(user_id)

                # Send a DM reminder to the user
                embed = discord.Embed(
                    title="📜 Your Payment Reminder",
                    description=f"Hello <@{user.id}>,\n\n"
                                f"🥇 **Rank:** {data['service']}\n"
                                f"💰 **Amount:** Rs. 199\n"
                                f"⌛ **Duration:** 28 Day\n"
                                f"📅 **Reminder Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                "Please ensure your payment is made soon!",
                    color=discord.Color.red()
                )
                await user.send(embed=embed)

                # Log the reminder to the invoice log channel
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                log_embed = discord.Embed(
                    title="📜 Reminder Sent",
                    description=f"Reminder was sent to <@{user.id}> about their invoice.\n\n"
                                f"🛠 **Staff:** <@{bot.user.id}>\n"
                                f"**Rank:** {data['service']}\n"
                                f"**In-Game Name:** {data['ingame_name']}\n"
                                f"**Reminder Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    color=discord.Color.green()
                )
                await log_channel.send(embed=log_embed)

                # Move the user data to logs.json after sending the reminder
                log_to_logs(data)

                # Remove the user from invoices.json
                del invoices[user_id]
                save_invoices(invoices)
        except Exception as e:
            print(f"Error processing reminder for user {user_id}: {e}")

# Command to generate invoice
@bot.command()
async def invoice(ctx, user: discord.Member, product: str, ingame_name: str):
    """Send a payment invoice in DM as an embed and log to a channel with possible attachment"""

    # Check if the product exists in the dictionary
    product = product.lower()
    if product not in product_prices:
        await ctx.send(f"❌ Invalid product! Choose from: Celestia, Eldrin, Phantom, Titan, Testproduct.", ephemeral=True)
        return

    amount = product_prices[product]

    duration_days = 28  
    expiration_time = datetime.utcnow() + timedelta(minutes=3)  
    timestamp = f"<t:{int(expiration_time.timestamp())}:R>" 
    invoice_gen_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") 
    
    # Create the embed message for the invoice
    embed = discord.Embed(
        title="📜 Your Payment Invoice",
        description=f"Hello {user.mention},\n\n"
                    f"🥇 **Rank:** {product.capitalize()} ranks\n"
                    f"💰 **Amount:** {amount} INR\n"
                    f"⌛ **Duration:** {duration_days} Day(s) ({timestamp})",
        color=discord.Color.blue()
    )

    # Create the log embed message
    log_embed = discord.Embed(
        title="📋 Invoice Generated",
        description=(f"**Buyer:** {user.mention}\n"
                     f"**In-game Name:** {ingame_name}\n"
                     f"**Staff:** {ctx.author.mention}\n"
                     f"**Service:** {product.capitalize()} rank\n"
                     f"**Paid Amount:** Rs. {amount}\n"
                     f"**Invoice Generated On:** {invoice_gen_time}\n"
                     f"**Time Remaining:** {timestamp}"),
        color=discord.Color.green()
    )

    # Check if the user is already in invoices.json (to avoid duplication)
    invoices = load_invoices()
    if user.id in invoices:
        await ctx.send(f"❌ This user already has an active invoice. Please remove the previous invoice first.")
        return

    # Send the log message in the specified channel as an embed
    invoice_channel = bot.get_channel(INVOICE_CHANNEL_ID)
    await invoice_channel.send(embed=log_embed)

    # Check if there are any attachments in the command message
    if ctx.message.attachments:
        # Send attachment to the invoice log channel
        for attachment in ctx.message.attachments:
            if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                await invoice_channel.send(f"**Attachment for Invoice:** {attachment.url}")

    # Try to send the DM to the user
    try:
        await user.send(embed=embed)
        await ctx.send(f"✅ Invoice sent to {user.mention} via DM!")
    except discord.Forbidden:
        await ctx.send(f"⚠️ Could not DM {user.mention}. They might have DMs disabled!")

    # Save the invoice data in the JSON file
    invoices[user.id] = {
        "service": product.capitalize(),
        "amount": amount,
        "expiration": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
        "ingame_name": ingame_name,
        "staff": str(ctx.author.id)
    }
    save_invoices(invoices)

bot.run(BOT_TOKEN)
