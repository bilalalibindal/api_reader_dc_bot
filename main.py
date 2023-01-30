import discord
from discord.ext import commands
import os
import aiohttp


class MyBot(commands.Bot):
    def __init__(self):
        self.discord_server = 1015168172753702912
        self.application_id = 1004415803703177247
        super().__init__(command_prefix=".",
                         intents=discord.Intents.all(),
                         application_id=self.application_id)

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
