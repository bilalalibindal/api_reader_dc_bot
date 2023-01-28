import asyncio
import discord
from discord.ext import commands
import os
import aiohttp
import asyncio

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".",
                         intents=discord.Intents.all(),
                         application_id=980452938256379934)

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await bot.tree.sync(guild=discord.Object(id=1068249104406290572))

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')


bot = MyBot()
bot.run(os.environ["DISCORD_TOKEN"])
