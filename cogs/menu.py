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

cogs_path = os.path.join(os.getcwd(), 'cogs')
sys.path.append(cogs_path)
from games import BombGame


# Define a class to create buttons.
class BombGameMenu(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__(timeout=None)
        self.game = BombGame(bot)
        self.bot = bot  # Define bot instance to use anywhere
        self.max_player = 0  # Player count who joined bomb game.

    # Create a register button to database, called as "Join".
    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji="✅", custom_id="join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user  # Get username who clicked the button.
        player_count = len(self.bot.players)  # Get player count from list.
        # if user already joined and registered to database table, tell him that with await function.
        if user.id in self.bot.players:
            await interaction.response.send_message(content=f"{user.mention} You already joined!",
                                                    ephemeral=True)
        # if player count has not reach to max player yet.
        if player_count < self.max_player:
            # if user not joined or registered to database table, tell him that with await function.
            if user.id not in self.bot.players:
                # Register user to database who clicked to button.
                self.bot.players.append(user.id)
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
            random.shuffle(self.bot.players)
            await self.game.start_round()
        # If user has not necessary role, tell him that you can't use this button.
        else:
            await interaction.response.send_message(content=f"{user.mention} You have no permission.", ephemeral=True)


# With that class we will create commands to create menus for our games.
# Commands will be slash(/) commands or we cann call that app_commands.
class Menu(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bombgame = BombGameMenu(bot)  # Define the class to put buttons we created for bomb game menu.

    # This is bombgame_menu command.
    @app_commands.command(name="bombgame_menu",
                          description="Create a Bomb Game Register Menu and choose player player_count.")
    @commands.has_permissions(administrator=True)
    # /bombgame_menu max_players = ?.
    async def bombgame_menu(self, interaction: discord.Interaction, max_players: int) -> None:
        self.bot.bomb_game_channel = interaction.channel_id
        self.bombgame.max_player = max_players  # Define max_player count to check it.
        self.bot.players = []
        embed = discord.Embed(title=f" REGISTER ",
                              description="➥ **Click to '✅Join' button to enter Bomb Game**\n"
                                          f"Max Player: {max_players}")
        await interaction.response.send_message(embed=embed, view=self.bombgame)


async def setup(bot: commands.Bot) -> None:
    # Add cog to bot.
    await bot.add_cog(Menu(bot), guilds=[discord.Object(id=1015168172753702912)])
