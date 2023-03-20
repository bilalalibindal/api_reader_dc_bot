import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import DiscordUtils
from discord.ui import Button, View
import os
from random import randint as rand
from discord import Permissions


class BombGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def Bomb_Game_exe(self):
        if self.bot.is_bomb_game_active:
            channel = await self.bot.fetch_channel(self.bot.bomb_game_channel)
            bomber = rand(0, len(self.bot.players) - 1)
            self.bot.bomb_game_code = rand(1000, 9999)
            self.bot.bomber = self.bot.players[bomber]
            user = await self.bot.fetch_user(self.bot.bomber)
            await channel.set_permissions(user, send_messages=True)
            await channel.send(
                f"💣🧨 <@{self.bot.bomber}> 🧨💣\n\n**Defuse the bomb**\n\n**`Code:`** **{self.bot.bomb_game_code}**")

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.is_bomb_game_active:
            if message.channel.id == self.bot.bomb_game_channel:
                if message.content == f"{self.bot.bomb_game_code}":
                    channel = await self.bot.fetch_channel(self.bot.bomb_game_channel)
                    user = message.author
                    await channel.set_permissions(user, send_messages=False)
                    await message.channel.send(f"🕵️ <@{self.bot.bomber}> defused the bomb\n")
                    await self.Bomb_Game_exe()

    async def start_round(self):
        channel = await self.bot.fetch_channel(self.bot.bomb_game_channel)
        if len(self.bot.players) > 1:
            await channel.send(f"New Round has been started!")
            await self.Bomb_Game_exe()
            await asyncio.sleep(rand(15, 35))
            self.bot.bomb_game_code = rand(1000, 9999)
            user = await self.bot.fetch_user(self.bot.bomber)
            await channel.set_permissions(user, send_messages=False)
            self.bot.players.remove(self.bot.bomber)
            embed = discord.Embed(title=f"💥 💥 💥", description=f"☠️ 🪦 <@{self.bot.bomber}> 🪦  ☠️\n"
                                                                 f"\n**`Alives:`** **{len(self.bot.players)}**")
            await channel.send(embed=embed)
            
            if len(self.bot.players) > 1:
                await channel.send(f"⌛ **Next Round Will Start in 3 Seconds** ⏳")
                await asyncio.sleep(3)
                await self.start_round()
            else:
                winner = self.bot.players[0]
                await channel.send(f"<@{winner}> Won the game!")
                self.bot.is_bomb_game_active = False


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(BombGame(bot))
