import discord
from discord.ext import commands
import os
import aiohttp
import json


class MyBot(commands.Bot):
    def __init__(self):
        self.discord_server = 1015168172753702912
        # self.application_id = 1004415803703177247
        super().__init__(command_prefix=".",
                         intents=discord.Intents.all(),
                         application_id=1004415803703177247)
        self.is_bomb_game_active = False  # We can use this bool in any script.
        self.bomb_game_channel = 0
        self.bomb_game_code = 0
        self.players = []
        self.bomber = 0
        self.data = self.read_file("atomic_new.json")
        self.data2 = self.read_file("new_dapps_id.json")

    def read_file(self, file):
        with open(f"{file}") as file:
            data = json.load(file)
        return data

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await bot.tree.sync(guild=discord.Object(id=self.discord_server))

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')


bot = MyBot()
bot.run(os.environ["DISCORD_TOKEN"])
