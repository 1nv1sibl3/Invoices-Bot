import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
from datetime import datetime, timedelta
from configs import *
from discord.app_commands import checks

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
intents.dm_messages = True

LOGS_FILE = 'logs.json'
INVOICES_FILE = 'invoices.json'

bot = commands.Bot(command_prefix="-", intents=intents)

product_prices = {
    "celestia": 199,
    "eldrin": 149,
    "phantom": 99,
    "titan": 49,
}

INVOICE_CHANNEL_ID = INVOICE_CHANNEL_ID
LOG_CHANNEL_ID = INVOICE_CHANNEL_ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    send_reminders.start()

def load_invoices():
    try:
        with open(INVOICES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_invoices(data):
    with open(INVOICES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_logs():
    try:
        with open(LOGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_logs(data):
    with open(LOGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@tasks.loop(minutes=1)
async def send_reminders():
    now = datetime.utcnow()
    invoices = load_invoices()
    logs = load_logs()  # Load existing logs

    for user_id, data in invoices.copy().items():
        try:
            reminder_time = datetime.strptime(data['reminder'], '%Y-%m-%d %H:%M:%S')

            if now >= reminder_time:
                user = await bot.fetch_user(int(user_id))
                embed = discord.Embed(
                    title="⏳ Payment Reminder",
                    description="This is a reminder for your pending payment. Please complete the payment before the due date to avoid any delays or penalties.",
                    color=discord.Color.red()
                )

                embed.add_field(name="👤 Buyer", value=f"{user.mention}", inline=False)
                embed.add_field(name="🆔 Buyer ID", value=f"{data['UserID']}", inline=False)
                embed.add_field(name="🎮 Buyer In-Game Name", value=f"{data['ingame_name']}", inline=False)
                embed.add_field(name="🛠 Staff Handler", value=f"<@{data['staff']}>", inline=False)
                embed.add_field(name="🛒 Service", value=f"{data['service']}", inline=False)
                embed.add_field(name="💰 Amount", value=f"Rs. {data['amount']}", inline=False)
                embed.add_field(name="⌛ Payment Date", value=f"<t:{int(reminder_time.timestamp())}:D>", inline=False)
                embed.add_field(name="⚠ Status", value="**Pending Payment**", inline=False)

                embed.add_field(
                    name="📌 Payment Instructions",
                    value=f"Please make the payment using `UPI` on the same UPI ID and send proof as soon as possible to Modmail.\n\n"
                          "In case you forgot the UPI ID, please open Modmail for the same.",
                    inline=False
                )

                await user.send(embed=embed)

                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                log_embed = discord.Embed(
                    description=f"📢 Reminder sent to {user.mention}, handled by <@{data['staff']}>.",
                    color=discord.Color.green()
                )
                await log_channel.send(embed=log_embed)

                # Move the invoice entry to logs.json instead of deleting it
                logs[user_id] = data
                save_logs(logs)  # Save the updated logs

                del invoices[user_id]  # Remove from invoices.json
                save_invoices(invoices)  # Save the updated invoices.json

        except Exception as e:
            print(f"Error sending reminder for user {user_id}: {e}")

@bot.tree.command(name="invoice", description="Generate an invoice for a user")
@app_commands.describe(
    buyer="The buyer",
    in_game_name="The buyer's in-game name",
    service="The service/rank to purchase",
    duration="The duration (e.g., 28d, 2h, 30m)",
    reminder_time="Time before invoice expires to send a reminder (e.g., 1d, 12h, 30m)",
    attachment="Proof of payment (mandatory)"
)
@app_commands.checks.has_role(1337080845718126673)
async def invoice(interaction: discord.Interaction, buyer: discord.Member, in_game_name: str, service: str, duration: str, reminder_time: str, attachment: discord.Attachment):
    service = service.lower()
    if service not in product_prices:
        await interaction.response.send_message("❌ Invalid service! Choose from: Celestia, Eldrin, Phantom, Titan.", ephemeral=True)
        return

    amount = product_prices[service]

    # Parse duration
    duration_days = 0
    if duration.endswith('d'):
        duration_days = int(duration[:-1])
    elif duration.endswith('h'):
        duration_days = int(duration[:-1]) / 24
    elif duration.endswith('m'):
        duration_days = int(duration[:-1]) / 1440
    else:
        await interaction.response.send_message("❌ Invalid duration format! Use 'd' for days, 'h' for hours, or 'm' for minutes.", ephemeral=True)
        return

    # Calculate expiration time
    expiration_time = datetime.utcnow() + timedelta(days=duration_days)

    # Parse reminder time
    reminder_offset = 0
    if reminder_time.endswith('d'):
        reminder_offset = int(reminder_time[:-1])
    elif reminder_time.endswith('h'):
        reminder_offset = int(reminder_time[:-1]) / 24
    elif reminder_time.endswith('m'):
        reminder_offset = int(reminder_time[:-1]) / 1440
    else:
        await interaction.response.send_message("❌ Invalid reminder time format! Use 'd' for days, 'h' for hours, or 'm' for minutes.", ephemeral=True)
        return

    # Calculate reminder time
    reminder_time_final = expiration_time - timedelta(days=reminder_offset)

    # Convert timestamps
    expiration_timestamp = f"<t:{int(expiration_time.timestamp())}:R>"
    reminder_timestamp = f"<t:{int(reminder_time_final.timestamp())}:R>"
    invoice_gen_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Invoice embed
    embed = discord.Embed(
        title="📜 Payment Invoice",
        description="Thank you for your purchase! Contact support for any issues.",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Buyer", value=buyer.mention, inline=False)
    embed.add_field(name="🆔 Buyer ID", value=str(buyer.id), inline=True)
    embed.add_field(name="🎮 Buyer In-Game Name", value=in_game_name, inline=False)
    embed.add_field(name="🛠️ Staff Handler", value=interaction.user.mention, inline=False)
    embed.add_field(name="🛒 Service", value=service.capitalize(), inline=False)
    embed.add_field(name="💰 Amount", value=f"Rs. {amount}", inline=True)
    embed.add_field(name="📅 Date & Time", value=invoice_gen_time, inline=False)
    embed.add_field(name="⏳ Duration", value=f"{duration_days} Day(s) ({expiration_timestamp})", inline=False)
    embed.add_field(name="🔔 Auto Reminder", value=f"Reminder will be sent {reminder_timestamp}", inline=False)
    embed.add_field(name="📄 Proof:", value=f"[Attachment]({attachment.url})", inline=False)

    embed.set_footer(text="Thank you for your purchase! Contact support for any issues.")

    invoices = load_invoices()
    if str(buyer.id) in invoices:
        await interaction.response.send_message("❌ This user already has an active invoice. Remove the previous invoice first.", ephemeral=True)
        return

    invoice_channel = bot.get_channel(INVOICE_CHANNEL_ID)
    await invoice_channel.send(embed=embed)

    try:
        await buyer.send(embed=embed)
        await interaction.response.send_message(f"✅ Invoice sent to {buyer.mention} via DM!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"⚠️ Could not DM {buyer.mention}. They might have DMs disabled!", ephemeral=True)

    invoices[str(buyer.id)] = {
        "UserID": buyer.id,
        "service": service.capitalize(),
        "amount": amount,
        "expiration": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
        "reminder": reminder_time_final.strftime("%Y-%m-%d %H:%M:%S"),
        "ingame_name": in_game_name,
        "staff": str(interaction.user.id),
        "proof": attachment.url
    }
    save_invoices(invoices)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("❌ You do not have permission to use this command!", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ An error occurred while processing the command.", ephemeral=True)


bot.run(BOT_TOKEN)
