import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
from datetime import datetime, timedelta
from configs import *
from discord.app_commands import checks
import typing
from typing import Optional


intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
intents.dm_messages = True

LOGS_FILE = 'logs.json'
INVOICES_FILE = 'invoices.json'
ROLE_ID_MV = [1218583488710840432, 1302868010855436360, 1310020946106777723]

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
        await interaction.response.defer(ephemeral=True)  # Defer response to prevent timeout
        await buyer.send(embed=embed)
        await interaction.followup.send(f"✅ Invoice sent to {buyer.mention} via DM!", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send(f"⚠️ Could not DM {buyer.mention}. They might have DMs disabled!", ephemeral=True)


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

from datetime import datetime, timedelta

@bot.tree.command(name="reminder", description="Manually send a payment reminder to a user")
@app_commands.describe(
    buyer="The buyer who needs a reminder",
    buyer_id="Buyer’s Discord ID",
    ingame_name="Buyer’s in-game name",
    staff="Staff member handling the payment (mention them)",
    service="Service name",
    amount="Amount in Rs.",
    expiration="Expiration time (e.g., 1d, 2h, 30m)"
)
@app_commands.checks.has_role(1337080845718126673)
async def reminder(
    interaction: discord.Interaction,
    buyer: discord.Member,
    buyer_id: str,
    ingame_name: str,
    staff: discord.Member,
    service: str,
    amount: int,
    expiration: str
):
    logs = load_logs()
    invoices = load_invoices()

    # Convert expiration time (e.g., "1d", "2h", "30m") to a Unix timestamp
    time_units = {"d": "days", "h": "hours", "m": "minutes"}
    try:
        num, unit = int(expiration[:-1]), expiration[-1]
        if unit not in time_units:
            raise ValueError
        delta = timedelta(**{time_units[unit]: num})
        expiration_timestamp = int((datetime.now() + delta).timestamp())
    except (ValueError, TypeError):
        await interaction.response.send_message("❌ Invalid expiration format. Use `1d`, `2h`, `30m` etc.", ephemeral=True)
        return

    # Delete existing entry in invoices.json if found
    if buyer_id in invoices:
        del invoices[buyer_id]
        save_invoices(invoices)

    # Create the embed for the reminder
    embed = discord.Embed(
        title="⏳ Manual Payment Reminder",
        description="This is a manual reminder for your pending payment. Please complete it before the due date.",
        color=discord.Color.red()
    )

    embed.add_field(name="👤 Buyer", value=f"{buyer.mention}", inline=False)
    embed.add_field(name="🆔 Buyer ID", value=f"{buyer_id}", inline=False)
    embed.add_field(name="🎮 Buyer In-Game Name", value=f"{ingame_name}", inline=False)
    embed.add_field(name="🛠 Staff Handler", value=f"{staff.mention}", inline=False)
    embed.add_field(name="🛒 Service", value=f"{service}", inline=False)
    embed.add_field(name="💰 Amount", value=f"Rs. {amount}", inline=False)
    embed.add_field(name="⌛ Payment Date", value=f"<t:{expiration_timestamp}:D>", inline=False)
    embed.add_field(name="⚠ Status", value="**Pending Payment**", inline=False)
    embed.add_field(
        name="📌 Payment Instructions",
        value="Please make the payment via UPI and send proof in Modmail.\nIf you forgot the UPI ID, contact Modmail.",
        inline=False
    )

    # Send the reminder
    try:
        await buyer.send(embed=embed)
        await interaction.response.send_message(f"✅ Reminder sent to {buyer.mention} via DM!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"⚠️ Could not DM {buyer.mention}. They might have DMs disabled!", ephemeral=True)

    # Log the reminder action
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    log_embed = discord.Embed(
        description=f"📢 Manual reminder sent to {buyer.mention}, handled by {interaction.user.mention}.",
        color=discord.Color.green()
    )
    await log_channel.send(embed=log_embed)

    # Save log entry
    logs[buyer_id] = {
        "status": "Manual Reminder Sent",
        "buyer": buyer.mention,
        "ingame_name": ingame_name,
        "staff": staff.mention,
        "service": service,
        "amount": amount,
        "expiration": expiration
    }
    save_logs(logs)


@bot.tree.command(name="reload", description="Reload a specific command")
@app_commands.describe(command_name="The name of the command to reload")
@app_commands.checks.has_role(1218583488710840432)  # Restrict to specific role
async def reload(interaction: discord.Interaction, command_name: str):
    try:
        bot.tree.remove_command(command_name)  # Remove old version
        await bot.tree.sync()  # Sync changes
        await interaction.response.send_message(f"✅ Command `{command_name}` has been reloaded.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to reload `{command_name}`: `{e}`", ephemeral=True)

@bot.tree.command(name="move", description="Move a player to another user or voice channel")
@app_commands.describe(
    player="The player to be moved",
    target_user="The user whose voice channel they should be moved to (optional)",
    target_channel="The voice channel they should be moved to (optional)"
)
async def move_slash(
    interaction: discord.Interaction,
    player: discord.Member,
    target_user: Optional[discord.Member] = None,
    target_channel: Optional[discord.VoiceChannel] = None
):
    await move_logic(interaction, player, target_user, target_channel, is_slash=True)


@bot.command(name="move", aliases=["mv"])
async def move_prefix(ctx: commands.Context, player: discord.Member, target: Optional[discord.Member | discord.VoiceChannel] = None):
    # Check if the target is a user or a channel
    target_user = target if isinstance(target, discord.Member) else None
    target_channel = target if isinstance(target, discord.VoiceChannel) else None

    await move_logic(ctx, player, target_user, target_channel, is_slash=False)


async def move_logic(ctx, player, target_user, target_channel, is_slash: bool):
    """Handles the move logic for both slash and prefix commands"""
    
    # Check if the command user has at least one required role
    user = ctx.user if is_slash else ctx.author
    if not any(role.id in ROLE_ID_MV for role in user.roles):
        await send_message(ctx, "❌ You don't have permission to use this command!", is_slash)
        return

    # Check if player is in a voice channel
    if not player.voice or not player.voice.channel:
        await send_message(ctx, f"❌ {player.name} is not in a voice channel!", is_slash)
        return

    # Determine where to move the player
    if target_user and target_user.voice and target_user.voice.channel:
        destination = target_user.voice.channel
    elif target_channel:
        destination = target_channel
    else:
        await send_message(ctx, "❌ You must specify either a user in a voice channel or a voice channel!", is_slash)
        return

    # Move the player
    try:
        await player.move_to(destination)
        await send_message(ctx, f"✅ Moved {player.name} to `{destination.name}`!", is_slash)
    except discord.Forbidden:
        await send_message(ctx, f"⚠️ I don't have permission to move {player.name}!", is_slash)
    except Exception as e:
        await send_message(ctx, f"⚠️ Error moving player: `{e}`", is_slash)


async def send_message(ctx, message: str, is_slash: bool):
    """Handles sending messages for both slash and prefix commands"""
    if is_slash:
        await ctx.response.send_message(message, ephemeral=False)
    else:
        await ctx.send(message)



bot.run(BOT_TOKEN)
