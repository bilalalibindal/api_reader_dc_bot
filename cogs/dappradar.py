# 1. Pull project infos from dapp radar api.
# 2. Save this pull request to json file.
# 3. Do your next research to dependents page count ( so we will see last page and last added  programs)
# 4. Create another json file to save last new projects.
# 5. Search project name in json file that I talked about above.
# 6. If project name not in that json file, add it to top, and delete last project in file.
# 7. Add few api keys, so when some of them used for 1000 times we will continue to use other api key.
# 8. Adapt this codes to discord.py.


import discord
import requests
import json
from discord.ext import commands
import asyncio


class dappradar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page_count = 1340
        self.api_counter = 0
        self.code = 0

    # With this function getting project infos from dapp radar api.
    # with page_count parameter we access to last page to se new projects.
    def get_api(self):
        self.api_counter += 1
        with open('api_codes.json', 'r') as file:
            codes = json.load(file)
        print(codes['code'][self.code]['apiCode'])
        if self.api_counter % 1000 == 0:
            self.code += 1
            try:
                codes[self.code]
            except IndexError:
                self.code = 0

        url = f"https://api.dappradar.com/4tsxo4vuhotaojtl/dapps?page={self.page_count}&resultsPerPage=10"
        headers = {
            "X-BLOBR-KEY": f"{codes['code'][self.code]['apiCode']}"
        }

        response = requests.get(url, headers=headers)
        project_list = response.json()
        # Write all datas to json file.
        with open("dapp_radar.json", "w") as file:
            json.dump(project_list, file)
        try:
            if self.read_api()['message'] != None:
                self.code += 1
                self.get_api()
        except KeyError:
            print("No problem")

    # Read datas from json file which we wrote api datas.
    def read_api(self):
        with open("dapp_radar.json", "r") as file:
            data = json.load(file)
        return data

    # get project names from json file with use read_api function.
    def get_project_names(self):
        name_list = []
        # Get name count from json.
        name_count = len([item for item in self.read_api()["results"] if "name" in item])
        # Look for name count and add all names to list.
        for i in range(name_count):
            # Search project name in json file.
            project_name = self.read_api()["results"][i]["dappId"]
            # Add project names to list.
            name_list.append(project_name)
        return name_list

    # get project id from json file with use read_api function.
    def get_project_ids(self):
        id_list = []
        # Get name count from json.
        id_count = len([item for item in self.read_api()["results"] if "dappId" in item])
        for i in range(id_count):
            dappId = self.read_api()["results"][i]["dappId"]
            id_list.append(dappId)
        return id_list

    def get_new_project_ids(self):
        id_list = []
        with open('new_projects_ids.json', 'r') as file:
            data = json.load(file)
        for item in (data["ID"]):
            id = item["dappId"]
            id_list.append(id)
        return id_list

    # With this function; checking is project new with using new_projects.json.
    # If project new; return True else return; False.
    def is_new_project(self, dapp_id):
        with open('new_projects_ids.json', 'r') as file:
            data = json.load(file)

        for item in (data["ID"]):
            id = item["dappId"]
            if dapp_id == id:
                return False
        return True

    # With this function, will update new project json file .
    def change_new_projects(self):
        id_list = self.get_project_ids()
        with open('new_projects_ids.json', 'r') as file:
            data = json.load(file)
        # With this for loop, look by id to see is any new project added.
        for id in id_list:
            # If it's new project add it to end of the list.
            if self.is_new_project(id):
                new_data = {"dappId": id}
                data["ID"].append(new_data)
        # With this while loop keep 10 index in new project list, will delete at top.
        while len(data["ID"]) > 10:
            data["ID"].pop(0)
        # Save last version of new project list to json file.
        with open('new_projects_ids.json', 'w') as file:
            json.dump(data, file)

    # Get specific value from json file by dappId parameter.
    # Variable = name,logo,link,website,chains,categories.
    def get_project_variable_by_dapp_id(self, dapp_id, variable):
        data = self.read_api()
        for project in data["results"]:
            if project["dappId"] == dapp_id:
                if variable == "categories" or variable == "chains":
                    result = project[f"{variable}"][0]
                    return result
                result = project[f"{variable}"]
                return result

    async def dapp_radar_send(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.get_api()
            project_id_list = self.get_project_ids()
            for id in project_id_list:
                if self.is_new_project(id):
                    guild = self.bot.get_guild(1015168172753702912)
                    channel = discord.utils.get(guild.channels, name="dappradar")
                    logo = self.get_project_variable_by_dapp_id(id, 'logo')
                    common_logo = "https://raw.githubusercontent.com/dappradar/tokens/main/ethereum/0x44709a920fccf795fbc57baa433cc3dd53c44dbe/logo.png"
                    embed = discord.Embed(
                        title=f"NEW DAPP RADAR LISTING",
                        description=f"`Please double-check the collection name and do your own research about the project before making your purchase.`",
                        color=0xe67e22)
                    if len(logo) < 3:
                        embed.set_thumbnail(
                            url=common_logo)
                    else:
                        embed.set_thumbnail(
                            url=logo)

                    # We can get profile picture of member who joined server.
                    embed.add_field(name="_ _", value=f"```yaml\n"
                                                      f"Collection Name: "
                                                      f"{self.get_project_variable_by_dapp_id(id, 'name')}```\n",
                                    inline=True)
                    embed.add_field(name="Dapp Radar",
                                    value=f"{self.get_project_variable_by_dapp_id(id, 'link')}",
                                    inline=False)
                    embed.add_field(name="Website", value=self.get_project_variable_by_dapp_id(id, 'website'),
                                    inline=False)
                    embed.add_field(name="Chain", value=self.get_project_variable_by_dapp_id(id, 'chains'), inline=True)
                    embed.add_field(name="Category", value=self.get_project_variable_by_dapp_id(id, 'categories'),
                                    inline=True)
                    await channel.send(embed=embed)
                else:
                    print("n")
            self.page_count = str(self.read_api()["pageCount"])
            self.change_new_projects()
            await asyncio.sleep(480)  # sleep for 5 minutes

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.dapp_radar_send())


async def setup(bot):
    # Add cog to bot.
    await bot.add_cog(dappradar(bot))
