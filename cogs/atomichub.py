import discord
import requests
from discord.ext import commands
import asyncio


# B367D9FE06ABAECA9E5B097185F4E1

class alcor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.atomichub_collection_url = "https://wax.atomichub.io/explorer/collection/wax-mainnet/"
        self.atomichub_api_url = "https://wax.api.atomicassets.io/atomicassets/v1/collections?page=1&limit=1&order=desc&sort=created"
        self.common_img_url = "https://resizer.atomichub.io/images/v1/preview?ipfs=QmYeWdTRTEePZasagQaT4UkuRbfe1sPvyw47PZrroba9tH&size=370"
        self.collection_img_url = "https://resizer.atomichub.io/images/v1/preview?ipfs="
        self.collection_name = ""
        self.old_collection_name = "a"
        self.collection_url = ""
        self.collection_img = ""
        self.collection_name2 = ""

    def check_name(self):
        url = f"{self.atomichub_api_url}"
        response = requests.get(url)
        data = response.text
        self.collection_name = data.split("collection_name")[1][3:].split(",")[0][:-1]
        return self.collection_name

    def check_name2(self):
        url = f"{self.atomichub_api_url}"
        response = requests.get(url)
        data = response.text
        self.collection_name2 = data.split("name")[2][3:].split(",")[0][:-1]
        return self.collection_name2

    def check_url(self):
        try:
            url = f"{self.atomichub_api_url}"
            response = requests.get(url)
            data = response.text
            self.collection_url = data.split("url")[1][3:].split(",")[0][:-1]
            return self.collection_url
        except IndexError:
            return "**NULL**"

    def check_img(self):
        url = f"{self.atomichub_api_url}"
        response = requests.get(url)
        data = response.text
        self.collection_img = data.split("img")[1][3:].split(",")[0][:-1]
        return self.collection_img

    async def send(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():

            self.collection_name = self.check_name()
            if self.collection_name != self.old_collection_name:
                self.collection_img = self.check_img()
                self.collection_url = self.check_url()
                guild = self.bot.get_guild(1068249104406290572)
                channel = discord.utils.get(guild.channels, name="atomichub")
                embed = discord.Embed(
                    title=f"NEW ATOMICHUB LISTING",
                    description=f"`Please double-check the collection name and do your own research about the project before making your purchase.`",
                    color=0xe67e22)
                # We can get profile picture of member who joined server.
                if len(self.collection_img) < 3:
                    embed.set_thumbnail(
                        url=f"{self.common_img_url}")
                else:
                    embed.set_thumbnail(
                        url=f"{self.collection_img_url}{self.collection_img}&size=370")
                embed.add_field(name="_ _", value=f"```yaml\n"
                                                  f"Collection Name: "
                                                  f"{self.collection_name}```\n", inline=True)
                embed.add_field(name="Atomichub",
                                value=f"{self.atomichub_collection_url}{self.collection_name}",
                                inline=False)
                embed.add_field(name="URL", value=self.collection_url, inline=False)

                await channel.send(embed=embed)
                self.old_collection_name = self.collection_name
            await asyncio.sleep(3)  # sleep for 5 minutes

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.send())


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(alcor(bot))


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(alcor(bot))
