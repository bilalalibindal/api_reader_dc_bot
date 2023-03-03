import discord
import requests
import json
from discord.ext import commands
import asyncio


class dappradar(commands.Cog):
    def __init__(self, bot, code):
        self.data = self.read_file("new_dapps_id.json")
        self.bot = bot
        self.code = code
        self.api_keys = ['wWzvYIAFMIDlLZwMRgCx7OXw3nx4wBi5', 'C8PpeLAUGkNXFFotMwsuS5Pa4PDoF1PN',
                         'fVI0vvwfkEb2AA7DlCppvwcrLSsAMBPs', 'arZjtkqPVeNbc7L9njg6S1YGFXwVSTvJ',
                         'pR8kMTOmBQRM3MsVhr0G2l6TQANqi1Uv', 'bLeFkKwLOEOs1ZK75HsuVU80R52ToXsu',
                         'RsjFJWOM7laVaB4vtYLX7hYxlM4l5XvS', 'zZsNwI6JuhGSCfogmNrflqvw10ysvZBS',
                         'HxWWgpxjq6QCmyFrOs68b82HLv0jMZqX']

    # With this function getting project infos from dapp radar api.
    # with page_count parameter we access to last page to se new projects.
    def update_api(self):
        try:
            self.api_keys[self.code]
        except IndexError:
            self.code = 0
        except KeyError:
            self.code += 1

        url = f"https://api.dappradar.com/4tsxo4vuhotaojtl/dapps?page={self.last_page()}&resultsPerPage=10"
        headers = {
            "X-BLOBR-KEY": f"{self.api_keys[self.code]}"
        }

        response = requests.get(url, headers=headers)
        api = response.json()
        if api["success"] != None and api["success"] == True:
            with open("dappradar_api.json", "w") as file:
                json.dump(api, file)
        else:
            self.code += 1
            self.update_api()

        with open("dappradar_api.json", "w") as file:
            json.dump(api, file)

    def read_file(self, file):
        with open(f"{file}") as file:
            data = json.load(file)
        return data

    def last_page(self):
        data = self.read_file("dappradar_api.json")
        if data["success"] == True:
            self.page_result = data["pageCount"]
            return self.page_result
        else:
            return self.page_result

    def get_projects_id(self, file):
        data = self.read_file(file=f"{file}")
        id_list = []
        id_count = len([item for item in data["results"] if "dappId" in item])
        for id in range(id_count):
            project_id = data["results"][id]["dappId"]
            id_list.append(project_id)
        return id_list

    def is_new_project(self, dapp_id):
        id_list = self.get_projects_id("new_dapps_id.json")
        if dapp_id not in id_list:
            return True
        else:
            return False

    def add_new_id(self, id):
        data_copy = self.data.copy()
        new_id = {"dappId": id}
        data_copy["results"].append(new_id)
        self.data = data_copy

    def update_new_id(self):
        while len(self.data["results"]) >= 20:
            self.data["results"].pop(0)
        with open("new_dapps_id.json", "w") as file:
            json.dump(self.data, file)

    # data = ['name', 'description', 'logo', 'link', 'website', 'chains', 'categories']
    def get_dapp_data(self, dapp_id):
        api = self.read_file(file="dappradar_api.json")
        for dapp in api["results"]:
            if dapp["dappId"] == dapp_id:
                return dapp

    def get_dapp_info(self, dapp_id, get):
        media = ['description', 'link', 'website', 'chains', 'categories']
        data = self.get_dapp_data(dapp_id)
        if get == "name":
            return data["name"]
        elif get == "logo":
            return data["logo"]
        elif get in media:
            return data[f"{get}"]
        else:
            return None

    async def dapp_radar_send(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            medias = ['description', 'link', 'website', 'chains', 'categories']
            self.update_api()
            dapps_id = self.get_projects_id(file="dappradar_api.json")
            for id in dapps_id:
                if self.is_new_project(dapp_id=id):
                    self.add_new_id(id=id)
                    name = self.get_dapp_info(dapp_id=id, get="name")
                    logo = self.get_dapp_info(dapp_id=id, get="logo")
                    guild = self.bot.get_guild(1015168172753702912)
                    channel = discord.utils.get(guild.channels, name="dappradar")
                    embed = discord.Embed(
                        title=f"NEW DAPP RADAR LISTING",
                        description=f"`Please double-check the collection name and do your own research about the project before making your purchase.`",
                        color=0xe67e22)
                    embed.add_field(name="_ _", value=f"```yaml\n"
                                                      f"Project Name: "
                                                      f"{name}```\n",
                                    inline=True)
                    embed.set_thumbnail(url=f"{logo}")
                    for media in medias:
                        media_link = self.get_dapp_info(dapp_id=id, get=f"{media}")
                        if media_link != "":
                            if media == "link":
                                embed.add_field(name="Dapp Radar", value=media_link, inline=False)
                            if media == "chains" or media == "categories":
                                embed.add_field(name=f"{media}", value=media_link[0], inline=True)
                            else:
                                embed.add_field(name=f"{media}", value=media_link, inline=False)
                    await channel.send(embed=embed)
            self.update_new_id()
            await asyncio.sleep(480)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.dapp_radar_send())


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(dappradar(bot, code=0))
