import discord
from discord import app_commands
from discord.ext import commands
import DiscordUtils
from discord.ui import Button, View
import sqlite3
from discord.utils import get


class Verify(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    def create_users_table(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        # Creating table in database.
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users(id TEXT, coin INTEGER, messages INTEGER, invites INTEGER, spent_coin INTEGER)")

    def create_referral_table(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        # Creating table in database.
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS referral(id TEXT, inviter TEXT)")

    def create_invite_tracker_table(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        # Creating table in database.
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS invite_tracker(id TEXT, inviter TEXT)")

    def create_leader_board_table(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        # Creating table in database.
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS leader_board(id TEXT, point INTEGER)")

    def get_data_in_database(self, table, data, user_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        with conn:
            search_command = "SELECT {} FROM {} WHERE id = '{}' "
            cursor.execute(search_command.format(data, table, user_id))
            result = cursor.fetchone()[0]
            conn.commit()
            return result

    def update_data_in_database(self, table, data, amount, user_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        # Creating table in database.
        with conn:
            cursor.execute("UPDATE {} SET {} = {} + {} WHERE id='{}'".format(table, data, data, amount, user_id))
            conn.commit()

    def search_data_in_database(self, table, data, user_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        with conn:
            search_command = "SELECT {} FROM {} WHERE id = '{}' "
            cursor.execute(search_command.format(data, table, user_id))
            result = cursor.fetchone()
            conn.commit()
            return result

    # With this function, register new user to database and giving fresh datas to them (data: coin amount, message amount, etc.).
    def register_to_database(self, user_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        with conn:
            cursor.execute(
                "INSERT INTO users(id,coin,messages,invites,spent_coin) VALUES ('{}', 0, 1, 0, 0)".format(user_id))
            conn.commit()

    @discord.ui.button(label="Register", style=discord.ButtonStyle.green, emoji="✅", custom_id="register")
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user  # Get username who clicked the button.
        if self.search_data_in_database(table="users", data="*", user_id=user) == None:
            if self.search_data_in_database(table="referral", data="*", user_id=user) != None:
                inviter = self.get_data_in_database(table="referral", data="inviter", user_id=user)
                self.update_data_in_database(table="users", user_id=inviter, data="invites", amount=1)
                self.update_data_in_database(table="users", user_id=inviter, data="coin", amount=100)
        # Check user is he/she in database, if yes send him warning, only user can see this warning message.
        if self.search_data_in_database(table="users", user_id=user, data="*") != None:
            await interaction.response.send_message(content=f"{user.mention} You already registered!",
                                                    ephemeral=True)
        else:
            # Register user to database who clicked to button.
            self.register_to_database(user_id=user)
            self.update_data_in_database(table="users", data="coin", amount=500, user_id=user)
            await interaction.response.send_message(
                content=f"{user.mention} You successfully registered to database!",
                ephemeral=True)  # Ephemeral provide that only user can see this message.

    @discord.ui.button(label="See Stats", style=discord.ButtonStyle.blurple, emoji="📈", custom_id="see_stats")
    async def see_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user  # Get username who clicked the button.
        coin_amount = int(self.get_data_in_database(user_id=user, table="users", data="coin"))
        message_amount = int(self.get_data_in_database(user_id=user, table="users", data="messages"))
        invite_amount = int(self.get_data_in_database(user_id=user, table="users", data="invites"))
        spent_coin_amount = int(self.get_data_in_database(user_id=user, table="users", data="spent_coin"))
        detail_embed = discord.Embed(title=f"{user}", description=f""":coin: **Coin**: {coin_amount}\n
                        :speech_balloon: **Message:** {message_amount}\n
                        :envelope: **Invite:** {invite_amount}\n
                        :money_mouth: **Spent Coin:** {spent_coin_amount}""")

        await interaction.response.send_message(embed=detail_embed, ephemeral=True)


class test(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.Verify = Verify()

    @app_commands.command(
        name="introduce",
        description="Introduce Yourself")
    async def introduce(self, interaction: discord.Interaction, name: str, age: int) -> None:
        await interaction.response.send_message(f"my name is: **{name}** and my age is: **{age}**")

    @app_commands.command(
        name="verify_menu",
        description="Create Verify Menu")
    async def verify_menu(self, interaction: discord.Interaction, title: str, description: str) -> None:
        self.Verify.create_users_table()
        self.Verify.create_referral_table()
        self.Verify.create_invite_tracker_table()
        self.Verify.create_leader_board_table()
        embed = discord.Embed(title=title, description=description)
        await interaction.response.send_message(embed=embed, view=self.Verify)


async def setup(bot: commands.Bot) -> None:
    # Add cog to bot.
    await bot.add_cog(test(bot), guilds=[discord.Object(id=1068249104406290572)])
