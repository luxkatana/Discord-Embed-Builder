
import discord
from discord.ext import commands
import os
import random
import math
from datetime import datetime 
from typing import Union
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ["TOKEN"]
TEST_GUILDS = [] # set here nothing if you want to make the slash command global
'''
In case you want to test this bot on a specific guild then set the guild ID in the TEST_GUILDS list

NOTE THAT IF YOU DONT SET ANY GUILD IN TEST_GUILDS IT WILL COST TIME TO REGISTER THE SLASH COMMAND
'''
bot = commands.Bot(command_prefix="./", intents=discord.Intents.all(),
        activity=discord.Game(name="Creating embeds...")
        )


class EmbedModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(title="Create your own embed")
        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.long, label="Title", max_length=256, required=True)

        )
        self.add_item(
            discord.ui.InputText(
                required=True, style=discord.InputTextStyle.short, label="description", max_length=256)
        )
        self.add_item(
            discord.ui.InputText(style=discord.InputTextStyle.short,
                                 label="footer", required=False, max_length=2048)

        )
        self.add_item(discord.ui.InputText(
            label="amount of fields", required=False, value="0"))
        self.add_item(
            discord.ui.InputText(style=discord.InputTextStyle.short, label="color(in rgb)(set randomForRandom)", max_length=9, value="0", required=False, placeholder="0")
        )
        # stealing my code bruh?
        # never gonna give you up
        #never gonna let you down
        #nveer gonna run around and deserve you
        
    async def callback(self, interaction: discord.Interaction) -> None:
        embed = None
        if self.children[4].value.isnumeric() and self.children[4].value != "0" and int(self.children[4].value) < 16777215:
            embed = discord.Embed(title=self.children[0].value, description=self.children[1].value, colour=int(self.children[4].value))
        elif self.children[4].value.lower() == "random":
            embed = discord.Embed(title=self.children[4].value, description=self.children[1].value, colour=discord.Color.random())
            
        else:
            embed = discord.Embed(
                title=self.children[0].value, description=self.children[1].value)
        embed.set_footer(
            text=self.children[2].value, icon_url=interaction.user.avatar.url)
        
        if self.children[3].value != "0" and self.children[3].value.isnumeric():
            cast = int(self.children[3].value)
            view = discord.ui.View()
            btn = discord.ui.Button(label="Add fields", style=discord.ButtonStyle.green)
            async def btn_callback(inner_interaction: discord.Interaction) -> None:
                if not inner_interaction.user == interaction.user:
                    await inner_interaction.response.send_message("This was not meant for you.. but for {}".format(interaction.user), ephemeral=True)
                    return
                m = FieldsModal(cast, embed)
                await inner_interaction.response.send_modal(m)
                return
            btn.callback = btn_callback
            view.add_item(btn)
            await interaction.response.send_message(embed=embed, view=view)
            
        else:
            await interaction.response.send_message(embed=embed, view=extrasView(embed))

class extrasView(discord.ui.View):
    def __init__(self, embed: discord.Embed) -> None:
        self.embed = embed
        super().__init__()
    @discord.ui.select(placeholder="extras", options=[
        discord.SelectOption(label="datetime", value="datetime", description="the datetime of the embed footer"),
        discord.SelectOption(label="Thumbnail URL", value="TURL", description="the thumbnail url"),
        discord.SelectOption(label="Image URL", value="IURL", description="the image URL"),
        discord.SelectOption(label="Change title", value="title", description="changes the title of the embed"),
        discord.SelectOption(label="change description", value="description", description="Change description of embed"),
        discord.SelectOption(label="change embed color", value="color", description="change the color the embed"),      
        discord.SelectOption(label="add author to embed", description="add author to the embed(or change)", value="author")
        ])
    async def callback(self, select, interaction: discord.Interaction) -> None:
        choice = self.children[0].values[0]
        match choice.lower():
            case "datetime":
                d = self.embed.to_dict()
                time_stamp = discord.ui.Modal(title="Timestamp")
                time_val = discord.ui.InputText(label="Time", style=discord.InputTextStyle.short, max_length=10, placeholder="year-month-day", required=True)
                time_hours_min = discord.ui.InputText(label="Hours and minutes", placeholder="format: 12:00 23:12 etc", style=discord.InputTextStyle.short, max_length=5, required=True) # 12:00
                time_stamp.add_item(time_val)
                time_stamp.add_item(time_hours_min)
                async def modal_callback(inner_interaction: discord.Interaction) -> None:
                    casted = []
                    number_mins = []
                    if not ":" in time_hours_min.value or not "-" in time_val.value:
                        await interaction.response.send_message("Invalid format", ephemeral=True)
                        return
                    for v in time_hours_min.value.split(":"):
                        if v.isnumeric():
                            number_mins.append(int(v))
                    for value in time_val.value.split("-"):
                        if value.isnumeric():
                            casted.append(int(value))
                    if len(casted) < 3 or len(number_mins) < 2:
                        await inner_interaction.response.send_message("some numbers were not valid", ephemeral=True)
                        return
                    if casted[1] > 12 or casted[2] > 31 or casted[0] < 0:
                        await interaction.response.send_message("Impossible date!", ephemeral=True)
                        return
                    time_ob = datetime(casted[0], casted[1], casted[2], number_mins[0], number_mins[1])
                    embed = None
                    if d.get("fields") == []:
                        embed = discord.Embed(title=d.get("title"), description=d.get("description"), colour=d.get("color", discord.Embed.Empty), timestamp=time_ob)
                    else:
                        embed = discord.Embed(title=d.get("title"), description=d.get("description"), colour=d.get("color", discord.Embed.Empty), timestamp=time_ob, fields=
                                              [discord.EmbedField(field.get("name"), value=field.get("value"), inline=field.get("inline"))for field in d.get("fields")])
                    self.embed = embed
                    await inner_interaction.response.send_message(embed=embed, view=self)
                time_stamp.callback = modal_callback 
                await interaction.response.send_modal(time_stamp)
            case "turl":
                tmodal = discord.ui.Modal(title="Set thumbnail")
                async def tmodal_callback(innner_interaction: discord.Interaction) -> None:
                    if not innner_interaction.user == interaction.user:
                        await innner_interaction.response.send_message("This was meant for {}".format(interaction.user), ephemeral=True)
                        return
                    URL_VAL = URL.value
                    self.embed.set_thumbnail(url=URL_VAL)
                    await innner_interaction.response.send_message(embed=self.embed, view=self) 
                tmodal.callback = tmodal_callback
                URL = discord.ui.InputText(label="url", style=discord.InputTextStyle.short, max_length=100, required=True, placeholder="Note that it wont be checked if its valid")
                tmodal.add_item(URL)
                await interaction.response.send_modal(tmodal)
            case "iurl":
                iurl_modal = discord.ui.Modal(title="Image modal")
                URL = discord.ui.InputText(label="the url", placeholder="note that it will be not validated  the url", required=True, max_length=100, style=discord.InputTextStyle.short)
                iurl_modal.add_item(URL)
                async def iurl_callback(inner_interaction: discord.Interaction) -> None:
                    val = URL.value
                    self.embed.set_image(url=val)
                    
                    await inner_interaction.response.send_message(embed=self.embed, view=self)
                iurl_modal.callback = iurl_callback
                await interaction.response.send_modal(iurl_modal)
            case "title":
                modal = discord.ui.Modal(title="Change title")
                old_embed = self.embed
                title_input = discord.ui.InputText(label="New title", placeholder="New title here", max_length=256, required=True)
                modal.add_item(title_input)
                async def title_callback(inner_interaction: discord.Interaction) -> None:
                    if inner_interaction.user != interaction.user:
                        await inner_interaction.response.send_message("This was not meant for you!", ephemeral=True)
                        return
                    
                    to_d = old_embed.to_dict()
                    new_title = title_input.value
                    formatted_text = await parse_my_shit(new_title, self.embed, inner_interaction.user)
                    to_d["title"] = formatted_text
                    self.embed = discord.Embed.from_dict(to_d)
                    await inner_interaction.response.send_message(embed=self.embed, view=self)
                    return
                modal.callback = title_callback
                await interaction.response.send_modal(modal)
            case "description":
                modal = discord.ui.Modal(title="Change description")
                description_input = discord.ui.InputText(style=discord.InputTextStyle.long, required=True, max_length=3999, label="New description")
                async def description_callback(inner_interaction: discord.Interaction) -> None:
                    if inner_interaction.user != interaction.user:
                        await inner_interaction.response.send_message("This was not meant for you!", ephemeral=True)
                        return
                    to_d = self.embed.to_dict()
                    formatted_shit = await parse_my_shit(description_input.value, self.embed, inner_interaction.user)
                    to_d["description"] = formatted_shit
                    self.embed = discord.Embed.from_dict(to_d)
                    
                    await inner_interaction.response.send_message(embed=self.embed, view=self)
                    return 
                modal.callback = description_callback
                modal.add_item(description_input)
                await interaction.response.send_modal(modal)
            case "color":
                modal = discord.ui.Modal(title="Change embed color")
                color_input = discord.ui.InputText(label="New embed color(SetRandomForRandom)", required=True, placeholder="rgb set random for random color", max_length=8)
                modal.add_item(color_input)
                async def modal_callback(inner_interaction: discord.Interaction) -> None:
                    value = color_input.value
                    # 16777215
                    print(value.isnumeric())
                    print(value)
                    if value.isnumeric() and  int(value) < 16777215:
                        to_d = self.embed.to_dict()
                        if to_d.get("color") != None:
                            to_d["color"] = int(value)
                            self.embed = discord.Embed.from_dict(to_d)
                            await inner_interaction.response.send_message(embed=self.embed, view=self)
                            
                        else:
                            to_d.update({"color": int(value)})
                            self.embed = discord.Embed.from_dict(to_d)
                            await inner_interaction.response.send_message(embed=self.embed, view=self)
                    elif value.lower() == "random":
                        to_d = self.embed.to_dict()
                        if to_d.get("fields") == []:
                            
                            n = discord.Embed(title=to_d["title"], description=to_d["description"], colour=discord.Color.random(), fields=[])
                            self.embed = n
                            await inner_interaction.response.send_message(embed=self.embed, view=self)
                        else:
                            all_fields = [discord.EmbedField(field["name"], field["value"], field["inline"]) for field in to_d.get("fields")]
                            self.embed = discord.Embed(title=to_d.get("title"), description=to_d.get("description"), colour=discord.Color.random(), fields=all_fields)
                            await interaction.response.send_message(embed=self.embed, view=self)
                            return
                    else:
                        await inner_interaction.response.send_message("Failed, could be that the rgb value is higher than **16777215** or the answer was not a number", ephemeral=True)
                modal.callback = modal_callback 
                await interaction.response.send_modal(modal)
            case "author":
                modal = discord.ui.Modal(title="Change the author")
                async def modal_callback(inner_interaction: discord.Interaction) -> None:
                    text  = await parse_my_shit(author_input.value, self.embed, inner_interaction.user)
                    url_input_val = URL_INPUT.value if URL_INPUT.value != "None" else discord.Embed.Empty
                    if url_input_val.lower() == "{{avatar_url}}":
                        url_input_val = inner_interaction.user.avatar.url
                    icon_url_val = icon_url.value if icon_url.value != "None" else discord.Embed.Empty
                    if isinstance(icon_url_val, str) or icon_url_val.lower() == "{{avatar_url}}":
                        icon_url_val = inner_interaction.user.avatar.url
                    if isinstance(url_input_val, str) and url_input_val.lower() == "{{avatar_url}}":
                        url_input_val = inner_interaction.user.avatar.url
                    self.embed.set_author(name=text, url=url_input_val, icon_url=icon_url_val)
                    await inner_interaction.response.send_message(embed=self.embed, view=self)
                modal.callback = modal_callback
                author_input = discord.ui.InputText(label="text", required=True, style=discord.InputTextStyle.long, max_length=256)
                URL_INPUT = discord.ui.InputText(label="redirectURL(starts with http(s)://", required=False, max_length=100, value="None")
                icon_url = discord.ui.InputText(label="iconURL(starts with http(s)://", required=False, max_length=100, value="None")
                modal.add_item(author_input)
                
                modal.add_item(URL_INPUT)
                modal.add_item(icon_url)
                await interaction.response.send_modal(modal)
    @discord.ui.button(label="shortcuts", style=discord.ButtonStyle.green)
    async def shortcuts(self, button, interaction: discord.Interaction) -> None:
        e = discord.Embed(title="Shortcuts", 
                          colour=discord.Color.random(),
                          description='''
Hey man if you see this i made some \"shortcuts\" for getting data from the embed the shortcuts are: \n{{title}} -> gets the title of the embed\n{{description}} -> gets the description of the embed\n{{thumbnail_link}} -> gets the thumbnail link(if the embed doesnt have a thumbnail then it wont replace)\n{{footer}} -> gets the footer of embed
{{pi}} -> returns the digits of PI\n
{{author}} -> gets your account's name + tag\n
{{author_id}} -> gets your account ID\n
{{author_name}} -> gets your account name **without the tag**\n
{{author_discrim}} -> gets the discriminator/tag of your account\n
{{author_avatar}} -> returns the URL of your avatar\n
{{color}} -> returns the embed's color in rgb\n
{{server_name}} -> returns the current guild's/server's name\n
{{guild}} -> returns the guild name\n
{{random_number}} -> returns a random number between the 1 and the 1000                      
                      \n\n
**to use those shortcuts insert it in a modal dialog between a sentence(doesnt work at the setup of the embed) such as  Title -> ``this embed was made by {{author}}``**    
    ''')
        await interaction.response.send_message(embed=e, ephemeral=True)
        
async def parse_my_shit(text: str, embed: discord.Embed, user: discord.Member) -> str:
    things = {
        "title": embed.title,
        "description": embed.description,
        "thumbnail_link": embed.thumbnail.url,
        "footer": embed.footer.text,
        "pi": math.pi,
        "author":  f"{user.name}#{user.discriminator}",
        "author_id": str(user.id),
        "author_name": user.name,
        "author_discrim": str(user.discriminator),
        "author_avatar": user.avatar.url,
        "color": "#{}".format(embed.to_dict().get("color", discord.Embed.Empty)),
        "server_name": user.guild.name,
        "guild": user.guild.name,
        "random_number": random.randint(1, 1000)
    }
    temp = text
    for key in things:
        if not isinstance(things[key], Union[str, discord.Member, int]):

            things[key] = "{{" + str(key) + "}}"
            
        temp = temp.replace("{{" + key + "}}", str(things.get(key)))
    return temp
class FieldsModal(discord.ui.Modal):
    def __init__(self, amount: int, embed):
        self.fields_amount = amount
        self.embed = embed
        super().__init__(title="Fields")
        for i in range(1, amount + 1):
            self.add_item(
                discord.ui.InputText(label="Field {}".format(
                    i), style=discord.InputTextStyle.long, max_length=256, required=True)
            )
            
    async def callback(self, interaction: discord.Interaction):
        for i in range(1, self.fields_amount + 1):
            self.embed.add_field(name="Field {}".format(i), value=str(self.children[i - 1].value), inline=False)
        await interaction.response.send_message(embed=self.embed, view=extrasView(self.embed))
        
                      
@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")



@bot.slash_command(name="embed", guild_ids=TEST_GUILDS, description="the start of the embed builder")
async def embBuilder(ctx: discord.ApplicationContext):
    
    
    await ctx.send_modal(EmbedModal())

bot.run(TOKEN)
