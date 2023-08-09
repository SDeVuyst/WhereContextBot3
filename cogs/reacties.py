
import random
from discord.ext import commands
import os
from discord import app_commands
import discord
from helpers import checks, db_manager 
from exceptions import MissingNwords


# Here we name the cog and create a new class for the cog.
class Reacties(commands.Cog, name="reacties"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wholesquadlaughing", description="damn bro you got the whole squad laughing (1🇳)", extras={'cog': 'reacties'})
    @checks.not_blacklisted()
    @checks.cost_nword(1)
    async def wholesquadlaughing(self, interaction):
        """Sends the 'whole squad laughing' reaction

        Args:
            interaction (Interaction): users interaction
        """
        file, embed = await self.get_reactie_embed("wholesquadlaughing.jpg", interaction.user.id, "Squad is laughing")
        await interaction.response.send_message(file=file, embed=embed)



    @app_commands.command(name="notfunny", description="bro that wasn't even funny (1🇳)", extras={'cog': 'reacties'})
    @checks.not_blacklisted()
    @checks.cost_nword(1)
    async def notfunny(self, interaction):
        """Sends the 'not funny' reaction

        Args:
            interaction (Interaction): users interaction
        """
        file, embed = await self.get_reactie_embed("notfunny.jpg", interaction.user.id, "Not funny")
        await interaction.response.send_message(file=file, embed=embed)



    @app_commands.command(name="uthought", description="sike u thought (1🇳)", extras={'cog': 'reacties'})
    @checks.not_blacklisted()
    @checks.cost_nword(1)
    async def uthought(self, interaction):
        """Sends the 'u thought' reaction

        Args:
            interaction (Interaction): users interaction
        """
        file, embed = await self.get_reactie_embed("uthought.jpg", interaction.user.id, "U thought")
        await interaction.response.send_message(file=file, embed=embed)
 


    async def get_reactie_embed(self, name, userid, title):
        """Creates an embed for a reaction

        Args:
            name (str): Name of reaction
            userid (str): id of user who requested the reaction
            title (str): Title of reaction

        Returns:
            File, Embed: File of reaction and embed
        """
        embed = discord.Embed(
            title=title, 
            description=f"Requested by <@{int(userid)}>", 
            color=self.bot.defaultColor
        )
        file = discord.File(f"{os.path.realpath(os.path.dirname(__file__))}/../reactions/{name}", filename="image.png")
        embed.set_image(url="attachment://image.png")
        return file, embed


    def get_muur_embed(self, title, footer):
        """Generates embed for a 'muur' reaction

        Args:
            title (str): Title of reaction
            footer (str): footer of reaction

        Returns:
            Embed
        """
        embed = discord.Embed(
            title=title,
            color=self.bot.defaultColor
        )
        embed.set_footer(text=footer)
        return embed
    


    @app_commands.command(
        name="golden_rule",
        description="Keleos golden rule (2🇳)",
        extras={'cog': 'reacties'}
    )
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    async def golden_rule(self, interaction) -> None:
        """Sends the 'golden rule' muur reaction

        Args:
            interaction (Interaction): users interaction
        """
        await interaction.response.send_message(embed=self.get_muur_embed(
            "You only need 3 things in life, happiness and good weather", 
            "-Keleo (golden rule)"
        ))
        


    @app_commands.command(
        name="laten_doen",
        description="laten doen (2🇳)",
        extras={'cog': 'reacties'}
    )
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    async def laten_doen(self, interaction) -> None:
        """Sends the 'laten doen' muur reaction

        Args:
            interaction (Interaction): users interaction
        """
        await interaction.response.send_message(embed=self.get_muur_embed(
            "Jij laat je toch ook altijd doen hé", 
            "-jeroentje pompoentje"
        ))



    @app_commands.command(
        name="limieten",
        description=":skull: (2🇳)",
        extras={'cog': 'reacties'}
    )
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    async def limieten(self, interaction) -> None:
        """Sends the 'limieten' muur reaction

        Args:
            interaction (Interaction): users interaction
        """
        await interaction.response.send_message(embed=self.get_muur_embed(
            "ik ken mijn limieten", 
            "-Yours truly"
        ))



    @app_commands.command(
        name="danny",
        description="the danny special (2🇳)",
        extras={'cog': 'reacties'}
    )
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    async def danny(self, interaction) -> None:
        """Sends the 'danny' muur reaction

        Args:
            interaction (Interaction): users interaction
        """
        await interaction.response.send_message(embed=self.get_muur_embed(
            "ik vertrouw je voor geen haar!!", 
            "-danny vande fucking veire"
        ))



    @app_commands.command(
        name="bozo",
        description="L bozo (2🇳)",
        extras={'cog': 'reacties'}
    )
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    async def bozo(self, interaction) -> None:
        """Sends the 'L bozo' muur reaction

        Args:
            interaction (Interaction): users interaction
        """
        await interaction.response.send_message(embed=self.get_muur_embed(
            "L bozo", 
            "-bozarius III"
        ))



    @app_commands.command(
        name="gible",
        description="gibby aka. smikkel aka capybara_Lover123 (2🇳)",
        extras={'cog': 'reacties'}
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="rip base", value=0),
        app_commands.Choice(name="tnt", value=1),
        app_commands.Choice(name="kkrbek", value=2),
        app_commands.Choice(name="dans", value=3),
        app_commands.Choice(name="so fine", value=4),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    @app_commands.describe(choices="Choose the reaction you want to send")
    async def gible(self, interaction, choices: app_commands.Choice[int]):
        """Send the 'gible' naam reaction

        Args:
            interaction (Interaction): Users Interaction
            choices (app_commands.Choice[int]): Choices of possible reactions
        """
        messages = ["daar gaat je base gible", "wapz tnt over gible z'n base", "KAAANKEERRRBEK GIBLE", "dans", "so fine"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        if m == "dans":
            embed = discord.Embed(
                color=self.bot.defaultColor
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1114464141508345906/1115720385070121000/ezgif.com-video-to-gif.gif")
        
        elif m == "so fine":
            file, embed = await self.get_reactie_embed("giblereact.jpg", interaction.user.id, "Sexy giby")
            return await interaction.response.send_message(file=file, embed=embed)
        
        else:
            embed = discord.Embed(
                title=m,
                color=self.bot.defaultColor,
            )

        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="nootje",
        description="nootje aka lil_kid_lover69 aka tough_guy_04 (2🇳)",
        extras={'cog': 'reacties'}
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="intelligent", value=0),
        app_commands.Choice(name="reels", value=1),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    @app_commands.describe(choices="Choose the reaction you want to send")
    async def nootje(self, interaction, choices: app_commands.Choice[int]):
        """Send the 'nootje' naam reaction

        Args:
            interaction (Interaction): Users Interaction
            choices (app_commands.Choice[int]): Choices of possible reactions
        """
        messages = ["meest intelligente nootje opmerking:", "stop met je fk reels"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="pingy",
        description="pingy aka pingy1 aka pongy aka Lol (2🇳)",
        extras={'cog': 'reacties'}
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="Lol", value=0),
        app_commands.Choice(name="njom", value=1),
        app_commands.Choice(name="dolfein", value=2),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    @app_commands.describe(choices="Choose the reaction you want to send")
    async def pingy(self, interaction, choices: app_commands.Choice[int]):
        """Send the 'pingy' naam reaction

        Args:
            interaction (Interaction): Users Interaction
            choices (app_commands.Choice[int]): Choices of possible reactions
        """
        messages = ["Lol", "Njom", "dolfein"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="ba",
        description="ba duy aka ba aka duy aka badwie (2🇳)",
        extras={'cog': 'reacties'}
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="ba", value=0),
        app_commands.Choice(name="schattig", value=1),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    @app_commands.describe(choices="Choose the reaction you want to send")
    async def ba(self, interaction, choices: app_commands.Choice[int]):
        """Send the 'ba' naam reaction

        Args:
            interaction (Interaction): Users Interaction
            choices (app_commands.Choice[int]): Choices of possible reactions
        """
        messages = ["ba", "zo schattig :smiling_face_with_3_hearts:"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]

        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="meng",
        description="meng aka mongwong aka da GOAT (2🇳)",
        extras={'cog': 'reacties'}
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="shatap", value=0),
        app_commands.Choice(name="pun", value=1),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    @app_commands.describe(choices="Choose the reaction you want to send")
    async def meng(self, interaction, choices: app_commands.Choice[int]):
        """Send the 'meng' naam reaction

        Args:
            interaction (Interaction): Users Interaction
            choices (app_commands.Choice[int]): Choices of possible reactions
        """
        messages = ["meng shut the fuck up", "nog 1 pun en ik SNAP"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]
       
        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="broodman",
        description="jasman aka yachini aka yashja (2🇳)",
        extras={'cog': 'reacties'}
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="mening", value=0),
    ])
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    @app_commands.describe(choices="Choose the reaction you want to send")
    async def broodman(self, interaction, choices: app_commands.Choice[int]):
        """Send the 'broodman' naam reaction

        Args:
            interaction (Interaction): Users Interaction
            choices (app_commands.Choice[int]): Choices of possible reactions
        """
        messages = [f"retarded ass mening nr. {random.randint(194892084, 294892084)}"]
        m = random.choice(messages) if choices.value == -1 else messages[choices.value]
       
        embed = discord.Embed(
            title=m,
            color=self.bot.defaultColor,
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="keleo",
        description="the one and only (2🇳)",
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="random", value=-1),
        app_commands.Choice(name="rooftop madness", value=0),
    ])
    @checks.not_blacklisted()
    @checks.cost_nword(2)
    @app_commands.describe(choices="Choose the reaction you want to send")
    async def keleo(self, interaction, choices: app_commands.Choice[int]):
        """Send the 'keleo' naam reaction

        Args:
            interaction (Interaction): Users Interaction
            choices (app_commands.Choice[int]): Choices of possible reactions
        """
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


