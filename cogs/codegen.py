"""
This is just an additional addon to this bot for generating
redeem codes for minecraft server and adding ad revenue
using atglinks
"""

import discord
from discord.ext import commands
from discord import app_commands
import pymysql
import requests
import random
import string
import os
import time
from utils.permissions import user_has_permission

db_config = {
    "host": "",
    "port": 3306,
    "user": "",
    "password": "",
    "database": "",
    "charset": ""
}

class GenerateCode(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.used_codes_file = "used_codes.txt"
        self.used_codes = set()
        if os.path.exists(self.used_codes_file):
            with open(self.used_codes_file, "r") as f:
                for line in f:
                    code = line.strip()
                    if code:
                        self.used_codes.add(code)

    def save_code(self, code: str):
        """Save generated code to a file and update the in-memory set."""
        with open(self.used_codes_file, "a") as f:
            f.write(f"{code}\n")
        self.used_codes.add(code)

    def retrieve_user_data(self, user_id: str):
        """
        Connect to MySQL and check if the user is linked.
        Assumes a table (discordsrv_accounts) with columns 'discord' and 'uuid'.
        Returns the uuid if linked, else None.
        """
        try:
            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                sql = "SELECT uuid FROM discordsrv_accounts WHERE discord = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
            connection.close()
            if result:
                return result[0]  
            else:
                return None
        except Exception as e:
            print(f"DB Error: {e}")
            return None

    def send_to_rcx_api(self, uuid: str):
        """
        Send a POST request to the RCX API with the given parameters.
        Payload:
            token: "xxx"
            digit: 6
            amount: 1
            template: "gencode"
            target: ""
            targetUUID: uuid
        Expects a JSON response like {"status": "ok", "redeemCode": "code"}.
        """
        rcx_url = "https://api.capitalrealm.fun/generateCode"  
        payload = {
            "token": "",
            "digit": 0,
            "amount": 0,
            "template": "",
            "target": "",
            "targetUUID": uuid
        }
        try:
            response = requests.post(rcx_url, data=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    redeem_code = data.get("redeemCode")
                    return redeem_code
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"RCX API Error: {e}")
            return None

    def generate_atglinks_url(self, redeem_code: str):
        """
        Generate a shortened URL via the AtgLinks API.
        A random alias (4-5 lowercase letters) is generated.
        The destination link embeds the redeem code.
        """
        alias_length = random.randint(4, 5)
        alias = ''.join(random.choices(string.ascii_lowercase, k=alias_length))
        destination = f"https://rcx.capitalrealm.fun/?code={redeem_code}"
        atglinks_api_key = ""
        atglinks_api_url = f"https://atglinks.com/api?api={atglinks_api_key}&url={destination}&alias={alias}"
        try:
            response = requests.get(atglinks_api_url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"AtgLinks API Error: {e}")
            return None

    @app_commands.checks.cooldown(1, 20*60, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="generate-code", description="Generate your redeem code")
    async def generate_code(self, interaction: discord.Interaction):
        """
        Slash command for generating a redeem code.
        1. Checks if the user is linked in the database.
        2. If not, instructs them to link their account using /discordsrv link.
        3. If linked, sends a POST to RCX API to generate a redeem code.
        4. Upon success, generates a shortened URL using AtgLinks and responds ephemerally.
        """

        if not user_has_permission("codegen", ctx.author):
            embed = discord.Embed(
                title="🚫 No Permission",
                description="You don't have permission to use this command.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, ephemeral=True if ctx.interaction else False)

        user_id = str(interaction.user.id)
        uuid = self.retrieve_user_data(user_id)
        if not uuid:
            await interaction.response.send_message(
                "You are not linked. Please link your account by doing `/discordsrv link` in-game and sending the code to <#1330846088864731146>.",
                ephemeral=True
            )
            return

        redeem_code = self.send_to_rcx_api(uuid)
        if not redeem_code:
            await interaction.response.send_message(
                "Failed to generate code via RCX API. Please try again later.",
                ephemeral=True
            )
            return

        self.save_code(redeem_code)

        shortened_url = self.generate_atglinks_url(redeem_code)
        if not shortened_url:
            await interaction.response.send_message(
                "Failed to generate shortened URL. Please try again later.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Here is your redeem link: {shortened_url}",
            ephemeral=True
        )

    @generate_code.error
    async def generate_code_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            end_time = int(time.time() + error.retry_after)
            await interaction.response.send_message(
                f"Command is on cooldown. Try again <t:{end_time}:R>.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(GenerateCode(bot))

