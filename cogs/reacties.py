
import random
from discord.ext import commands
import os
from discord import app_commands
import discord
from helpers import checks


# Here we name the cog and create a new class for the cog.
class Reacties(commands.Cog, name="reacties"):
    def __init__(self, bot):
        self.bot = bot

    muur = commands.SlashCommandGroup("muur", "De OG muur")

    @app_commands.command(name="giblereact", description="OMG jonathan is so fine!!")
    @checks.not_blacklisted()
    async def giblereact(self, interaction):
        file, embed = await self.get_reactie_embed("giblereact.jpg", interaction.user.id, "Sexy giby")
        await interaction.response.send_message(file=file, embed=embed)

    @app_commands.command(name="wholesquadlaughing", description="damn bro you got the whole squad laughing")
    @checks.not_blacklisted()
    async def wholesquadlaughing(self, interaction):
        file, embed = await self.get_reactie_embed("wholesquadlaughing.jpg", interaction.user.id, "Squad is laughing")
        await interaction.response.send_message(file=file, embed=embed)

    @app_commands.command(name="notfunny", description="bro that wasn't even funny")
    @checks.not_blacklisted()
    async def notfunny(self, interaction):
        file, embed = await self.get_reactie_embed("notfunny.jpg", interaction.user.id, "Not funny")
        await interaction.response.send_message(file=file, embed=embed)

    @app_commands.command(name="uthought", description="sike u thought")
    @checks.not_blacklisted()
    async def uthought(self, interaction):
        file, embed = await self.get_reactie_embed("uthought.jpg", interaction.user.id, "U thought")
        await interaction.response.send_message(file=file, embed=embed)
 

    async def get_reactie_embed(self, name, userid, title):
        embed = discord.Embed(
            title=title, 
            description=f"Requested by <@{int(userid)}>", 
            color=self.bot.defaultColor
        )
        file = discord.File(f"{os.path.realpath(os.path.dirname(__file__))}/../reactions/{name}", filename="image.png")
        embed.set_image(url="attachment://image.png")
        return file, embed


    def get_muur_embed(self, title, footer):
        embed = discord.Embed(
            title=title,
            color=self.bot.defaultColor
        )
        embed.set_footer(text=footer)
        return embed
    


    @muur.command(
        name="golden_rule",
        description="Keleos golden rule",
    )
    @checks.not_blacklisted()
    async def muur_1(self, context) -> None:
        await context.send(embed=self.get_muur_embed(
            "You only need 3 things in life, happiness and good weather", 
            "-Keleo (golden rule)"
        ))
        

    @muur.command(
        name="laten_doen",
        description="laten doen",
    )
    @checks.not_blacklisted()
    async def muur_2(self, context) -> None:
        await context.send(embed=self.get_muur_embed(
            "Jij laat je toch ook altijd doen hé", 
            "-jeroentje pompoentje"
        ))

    @muur.command(
        name="limieten",
        description=":skull:",
    )
    @checks.not_blacklisted()
    async def muur_3(self, context) -> None:
        await context.send(embed=self.get_muur_embed(
            "ik ken mijn limieten", 
            "-Yours truly"
        ))

    @muur.command(
        name="danny",
        description="the danny special",
    )
    @checks.not_blacklisted()
    async def muur_4(self, context) -> None:
        await context.send(embed=self.get_muur_embed(
            "ik vertrouw je voor geen haar!!", 
            "-danny vande fucking veire"
        ))

    @muur.command(
        name="bozo",
        description="L bozo",
    )
    @checks.not_blacklisted()
    async def muur_5(self, context) -> None:
        await context.send(embed=self.get_muur_embed(
            "L bozo", 
            "-bozarius III"
        ))


    @app_commands.command(
        name="gible",
        description="gibby aka. smikkel aka capybara_Lover123",
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="rip base", value=0),
        app_commands.Choice(name="tnt", value=1),
        app_commands.Choice(name="kkrbek", value=2),
        app_commands.Choice(name="dans", value=3),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def gible(self, interaction, choices: app_commands.Choice[int]):
        messages = ["daar gaat je base gible", "wapz tnt over gible z'n base", "KAAANKEERRRBEK GIBLE", "dans"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        if m == "dans":
            embed = discord.Embed(
                color=self.bot.defaultColor
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1114464141508345906/1115720385070121000/ezgif.com-video-to-gif.gif")
        else:
            embed = discord.Embed(
                title=m,
                color=self.bot.defaultColor,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="nootje",
        description="nootje aka lil_kid_lover69 aka tough_guy_04",
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="intelligent", value=0),
        app_commands.Choice(name="reels", value=1),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def nootje(self, interaction, choices: app_commands.Choice[int]):
        messages = ["meest intelligente nootje opmerking:", "stop met je fk reels"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="pingy",
        description="pingy aka pingy1 aka pongy aka Lol",
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="Lol", value=0),
        app_commands.Choice(name="njom", value=1),
        app_commands.Choice(name="dolfein", value=2),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def pingy(self, interaction, choices: app_commands.Choice[int]):
        messages = ["Lol", "Njom", "dolfein"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="ba",
        description="ba duy aka ba aka duy aka badwie",
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="ba", value=0),
        app_commands.Choice(name="schattig", value=1),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def ba(self, interaction, choices: app_commands.Choice[int]):
        messages = ["ba", "zo schattig :smiling_face_with_3_hearts:"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="meng",
        description="meng aka mongwong aka da GOAT"
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="shatap", value=0),
        app_commands.Choice(name="pun", value=1),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def meng(self, interaction, choices: app_commands.Choice[int]):
        messages = ["meng shut the fuck up", "nog 1 pun en ik SNAP"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]
       
        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="broodman",
        description="jasman aka yachini aka yashja"
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="mening", value=0),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    async def broodman(self, interaction, choices: app_commands.Choice[int]):
        messages = [f"retarded ass mening nr. {random.randint(194892084, 294892084)}"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]
       
        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="keleo",
        description="the one and only",
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="rooftop madness", value=0),
    ])
    @checks.not_blacklisted()
    async def keleo(self, interaction, choices: app_commands.Choice[int]):
        messages = ["rooftop"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        if m == "rooftop":
            embed = discord.Embed(
                color=self.bot.defaultColor
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/727476894106386504/1117027462015107164/keleo_gif.gif")
        else:
            embed = discord.Embed(
                title=m,
                color=self.bot.defaultColor,
            )
        await interaction.response.send_message(embed=embed)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Reacties(bot))
