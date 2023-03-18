import discord
import DiscordUtils
from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands
import sqlite3
from discord.utils import get
import os
import psycopg2
import asyncio
import random
import sys

sys.path.append('C:/Users/bilal/Desktop/PYTHON/discordBotPrototype/cogs')
from games import BombGame


# Define a class to create buttons.
class BombGameMenu(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout=None)
        self.game = BombGame(bot)
        self.bot = bot  # Define bot instance to use anywhere
        self.conn = self.connect_db()  # Define database connection to use anywhere
        self.player_count = 0  # Player count who joined bomb game.

    # Connect to database
    def connect_db(self):
        conn = psycopg2.connect(
            host="localhost",
            database="Deep Dapp",
            user="postgres",
            password="19070900180.Seksen",
            port="5432"
        )
        return conn

    # Create a table inside of database with specific name
    def create_db_table(self, table_name: str):
        cursor = self.conn.cursor()
        with self.conn:
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name}(name TEXT, id TEXT)')
            self.conn.commit()

    def delete_db_table(self, table_name: str):
        cursor = self.conn.cursor()
        with self.conn:
            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')

    # Search specific data in specific table name
    def search_data_in_database(self, table, data, user_id):
        cursor = self.conn.cursor()
        with self.conn:
            search_command = "SELECT {} FROM {} WHERE id = '{}' "
            cursor.execute(search_command.format(data, table, user_id))
            result = cursor.fetchone()
            self.conn.commit()
            return result

    # Get count of users
    def user_count_of_database(self, table):
        cursor = self.conn.cursor()
        with self.conn:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
        return count

    # With this function, register new user to database and giving fresh datas to them (data: coin amount, message amount, etc.).
    def register_to_database(self, user_name, user_id):
        cursor = self.conn.cursor()
        with self.conn:
            cursor.execute(
                f"INSERT INTO bombgame(id,name) VALUES ('{user_id}','{user_name}')")
            self.conn.commit()

    def get_player_list(self):
        cursor = self.conn.cursor()
        with self.conn:
            cursor.execute('SELECT id FROM bombgame')
            self.bot.players = [row[0] for row in cursor.fetchall()]
            random.shuffle(self.bot.players)
            self.conn.commit()

    # Create a register button to database, called as "Join".
    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji="✅", custom_id="join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user  # Get username who clicked the button.
        table = "bombgame"  # Table name we create in database.
        player_count = self.user_count_of_database(table=table)  # Get player count from database table.
        # if user already joined and registered to database table, tell him that with await function.
        if self.search_data_in_database(table="bombgame", user_id=user.id, data="*") != None:
            await interaction.response.send_message(content=f"{user.mention} You already joined!",
                                                    ephemeral=True)

        # if player count has not reach to max player yet.
        if player_count < self.player_count:
            # if user not joined or registered to database table, tell him that with await function.
            if self.search_data_in_database(table="bombgame", user_id=user.id, data="*") == None:
                # Register user to database who clicked to button.
                self.register_to_database(user_name=user, user_id=user.id)
                # Is not possible to use response method for same condition.
                # Should use followup for one of them.
                # Information messages below.
                await interaction.response.edit_message(
                    content=f"{user.mention} has been joined.\n Player Count: **{player_count + 1}**")
                await interaction.followup.send(
                    content=f"{user.mention} You successfully joined to Bomb Game!",
                    ephemeral=True)  # Ephemeral provide that only user can see this message.
        # if player count has reached to max player, tell them that.
        else:
            await interaction.response.send_message(content=f"{user.mention} Lobi is full, please wait the next game.",
                                                    ephemeral=True)  # Ephemeral provide that only user can see this message.

    # Create a button to start game. Only admin role can use this button.
    @discord.ui.button(label="Start", style=discord.ButtonStyle.red, emoji="▶️", custom_id="start")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if "ADMIN" in [role.name for role in user.roles]:
            await interaction.message.delete()
            await interaction.response.send_message(content=f"BOMB GAME HAS BEEN STARTED\n\n"
                                                            f"**Moderator: **{user.mention}")
            self.bot.is_bomb_game_active = True  # Set bomb game as active.
            self.get_player_list()
            await self.game.start_round()
        # If user has not necessary role, tell him that you can't use this button.
        else:
            await interaction.response.send_message(content=f"{user.mention} You have no permission.", ephemeral=True)


# With that class we will create commands to create menus for our games.
# Commands will be slash(/) commands or we cann call that app_commands.
class Menu(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.register_channel_id = 1053656627632414790
        self.bombgame = BombGameMenu(bot)  # Define the class to put buttons we created for bomb game menu.

    # This is bombgame_menu command.
    @app_commands.command(name="bombgame_menu",
                          description="Create a Bomb Game Register Menu and choose player player_count.")
    @commands.has_permissions(administrator=True)
    # /bombgame_menu max_players = ?.
    async def bombgame_menu(self, interaction: discord.Interaction, max_players: int) -> None:
        self.bot.bomb_game_channel = interaction.channel_id
        self.bombgame.player_count = max_players  # Define max_player count to check it.
        self.bombgame.delete_db_table("bombgame")
        self.bombgame.create_db_table("bombgame")
        embed = discord.Embed(title=f" REGISTER ",
                              description="➥ **Click to '✅Join' button to enter Bomb Game**\n"
                                          f"Max Player: {max_players}")
        await interaction.response.send_message(embed=embed, view=self.bombgame)


async def setup(bot: commands.Bot) -> None:
    # Add cog to bot.
    await bot.add_cog(Menu(bot), guilds=[discord.Object(id=1015168172753702912)])
