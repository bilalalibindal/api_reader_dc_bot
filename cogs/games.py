import asyncio
from discord.ext import commands
import psycopg2
from random import randint as rand



class BombGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bomber = 0

    def connect_db(self):
        conn = psycopg2.connect(
            host="localhost",
            database="Deep Dapp",
            user="postgres",
            password="19070900180.Seksen",
            port="5432"
        )
        return conn

    def create_db_table(self, table_name: str):
        conn = self.connect_db()
        cursor = conn.cursor()
        with conn:
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name}(id TEXT)')
            conn.commit()

    def delete_user(self, user_id: str):
        conn = self.connect_db()
        cursor = conn.cursor()
        with conn:
            cursor.execute(f"DELETE FROM bombgame WHERE id = '{user_id}'")
            conn.commit()

    async def Bomb_Game_exe(self):
        if self.bot.is_bomb_game_active:
            channel = await self.bot.fetch_channel(self.bot.bomb_game_channel)
            bomber = rand(0, len(self.bot.players) - 1)
            self.bot.bomb_game_code = rand(1000, 9999)
            self.bomber = self.bot.players[bomber]
            user = await self.bot.fetch_user(self.bomber)
            await channel.set_permissions(user, send_messages=True)
            await channel.send(f"🧨 <@{self.bomber}> 🧨\n\n**Code: {self.bot.bomb_game_code}**")

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.is_bomb_game_active:
            if message.channel.id == self.bot.bomb_game_channel:
                if message.content == f"{self.bot.bomb_game_code}":
                    channel = await self.bot.fetch_channel(self.bot.bomb_game_channel)
                    user = message.author
                    await channel.set_permissions(user, send_messages=False)
                    await message.channel.send("Bomb has been refused")
                    await self.Bomb_Game_exe()

    async def start_round(self):
        channel = await self.bot.fetch_channel(self.bot.bomb_game_channel)
        if len(self.bot.players) > 1:
            await channel.send(f"New Round has been started!")
            await self.Bomb_Game_exe()
            await asyncio.sleep(rand(15, 30))
            user = await self.bot.fetch_user(self.bomber)
            await channel.set_permissions(user, send_messages=False)
            self.bot.bomb_game_code = rand(1000, 9999)
            await channel.send(f"💥 💥 💥")
            await channel.send(f"☠️ 🪦 <@{self.bomber}> 🪦  ☠️")
            self.bot.players.remove(self.bomber)
            user = await self.bot.fetch_user(self.bomber)
            await channel.set_permissions(user, send_messages=False)
            if len(self.bot.players) > 1:
                await channel.send(f"Next Round Will Start in 3 Seconds")
                await asyncio.sleep(3)
                await self.start_round()
            else:
                winner = self.bot.players[0]
                await channel.send(f"<@{winner}> Won the game!")
                self.bot.is_bomb_game_active = False


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(BombGame(bot))
