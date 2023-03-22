import discord
import requests
from discord.ext import commands
import asyncio
import json


class atomichub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_link = "https://wax.api.atomicassets.io/atomicassets/v1/collections?page=1&limit=10&order=desc&sort=created"
        self.data = self.read_file("atomic_new.json")

    def get_api(self):
        response = requests.get(self.api_link)
        api_data = response.json()
        with open("atomic_api.json", "w") as file:
            json.dump(api_data, file)

    def read_file(self, file):
        with open(f"{file}") as file:
            data = json.load(file)
        return data

    def add_new_collection(self, collection_name: str):
        data_copy = self.data.copy()  # self.data'nın bir kopyası oluşturulur
        new_collection = {"collection_name": collection_name}
        data_copy["data"].insert(0, new_collection)
        self.data = data_copy  # self.data kopya ile güncellenir

    def update_new_collection(self):
        while len(self.data["data"]) >= 20:
            self.data["data"].pop()
        with open("atomic_new.json", "w") as file:
            json.dump(self.data, file)

    def get_collection_names(self, file):
        data = self.read_file(file=f"{file}")
        name_list = []
        name_count = len([item for item in data["data"] if "collection_name" in item])
        for id in range(name_count):
            collection_name = data["data"][id]["collection_name"]
            name_list.append(collection_name)
        return name_list

    def is_new_collection(self, collection_name):
        new_collection_list = self.get_collection_names(file="atomic_new.json")
        for name in new_collection_list:
            if name == collection_name:
                return False
        return True

    # data = collection_name, url
    def get_collection_data(self, collection_name):
        api = self.read_file(file="atomic_api.json")
        for collection in api["data"]:
            if collection["collection_name"] == collection_name:
                try:
                    url = collection["data"]["url"]
                except KeyError:
                    url = ""
                try:
                    img = collection["img"]
                except KeyError:
                    img = ""
                try:
                    socials = eval(collection["data"]["socials"])
                except KeyError:
                    socials = ""

                return url, img, socials

    def collection_info(self, collection_name, get: str):
        media = ['twitter', 'medium', 'facebook', 'github', 'discord', 'youtube', 'telegram']
        data = self.get_collection_data(collection_name)
        url = data[0]
        img = data[1]
        socials = data[2]
        if get == "url":
            return url
        elif get == "img":
            return img
        elif get in media:
            if get in socials:
                try:
                    get_index = socials.index(f"{get}")
                    return socials[get_index]
                except KeyError or ValueError:
                    return ""

    async def send(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.get_api()
            medias = ['url', 'twitter', 'medium', 'facebook', 'github', 'discord', 'youtube', 'telegram']
            collections = self.get_collection_names(file="atomic_api.json")
            collections.reverse()
            for name in collections:
                if self.is_new_collection(collection_name=name):
                    self.add_new_collection(collection_name=name)
                    self.update_new_collection()
                    img = self.collection_info(collection_name=name, get="img")
                    logo = f"https://resizer.atomichub.io/images/v1/preview?ipfs={img}&size=370"
                    common_logo = "https://resizer.atomichub.io/images/v1/preview?ipfs=QmRX56ttsvciSiDieq9LRA1hejx6nXjrz4pv4QC2cGvgNx&size=370"

                    if img != None:
                        image = logo
                    else:
                        image = common_logo

                    guild = self.bot.get_guild(1015168172753702912)
                    channel = discord.utils.get(guild.channels, name="atomichub")
                    embed = discord.Embed(
                        title=f"NEW ATOMICHUB LISTING",
                        description=f"`Please double-check the collection name and do your own research about the project before making your purchase.`",
                        color=0xe67e22)
                    embed.add_field(name="_ _", value=f"```yaml\n"
                                                      f"Collection Name: "
                                                      f"{name}```\n",
                                    inline=True)
                    embed.set_thumbnail(url=f"{image}")
                    embed.add_field(name="_Atomichub_",
                                    value=f"https://wax.atomichub.io/explorer/collection/wax-mainnet/{name}",
                                    inline=False)
                    for media in medias:
                        media_link = self.collection_info(collection_name=name, get=f"{media}")
                        if media_link != "" and media_link != "None" and media_link != None:
                            embed.add_field(name=f"{media}", value=media_link, inline=False)
                    await channel.send(embed=embed)
            self.update_new_collection()
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.send())


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(atomichub(bot))
