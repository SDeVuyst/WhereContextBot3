""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import os
import openai
import dateparser
import re

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions

from reactionmenu import ViewMenu, ViewSelect, ViewButton

from helpers import checks, db_manager


openai.api_key = os.environ.get("OPENAI_SECRET")


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="help", description="List all commands the bot has loaded", extras={'cog': 'general'})
    @checks.not_blacklisted()
    async def help(self, interaction) -> None:
        """ Sends info about all available commands

        Args:
            interaction (Interaction): Users Interaction

        Returns:
            None: Nothing
        """

        admin = list(os.environ.get("OWNERS").split(","))

        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
        cog_to_title = {
            "audio": "🎙️ Audio",
            "general": "🤖 General",
            "stats": "📊 Statistics",
            "outofcontext": "📸 Out Of Context",
            "reacties": "💭 Reacties",
            "admin": "👨‍🔧 Admin"
        }

        page_numbers = {}
        
        for i, c in enumerate(self.bot.cogs):

            embed = discord.Embed(
                title=f"**Help - {cog_to_title.get(c.lower())}**", 
                description=f"🔗 [Invite bot](https://discord.com/api/oauth2/authorize?client_id={os.environ.get('APPLICATION_ID')}&permissions=8&redirect_uri=https%3A%2F%2Fgithub.com%2FSDeVuyst%2FWhereContextBot3&response_type=code&scope=identify%20applications.commands%20applications.commands.permissions.update%20bot%20guilds.join%20guilds.members.read)  •  [Support Server](https://discord.gg/PBsUeB9fP3)  •  [More Info](https://github.com/SDeVuyst/WhereContextbot3) 🔗", 
                color=self.bot.defaultColor
            )

            cog = self.bot.get_cog(c.lower())
            commands = cog.get_app_commands()

            page_numbers[i+1] = cog_to_title.get(c.lower()).split(" ")[0]

            data = []
            for command in commands:
                try:
                    description = command.description.partition("\n")[0]
                    data.append(f"</{command.name}:{command.id}> - {description}")
                except:
                    pass

            if c == "outofcontext":
                data.append("Rechtermuisklik -> Apps -> Add Context - Add message")
                data.append("Rechtermuisklik -> Apps -> Remove Context - Remove message")
            
            elif c == "general":
                embed.add_field(
                    name = "🪙 N-Word Cost",
                    value="Sommige commands kosten N-Words, bv. voor een command dat 2 N-Words kost, staat er (2🪙) bij de beschrijving",
                    inline=False
                )

            help_text = "\n".join(data)
            if len(help_text) > 0:
                embed.add_field(
                    name="✅ Available commands", value=help_text, inline=False
                )

            menu.add_page(embed)

        menu.add_go_to_select(ViewSelect.GoTo(
            title="Ga naar onderverdeling...", 
            page_numbers=page_numbers
        ))
        menu.add_button(ViewButton.back())
        menu.add_button(ViewButton.next())
        return await menu.start()


    @app_commands.command(name="lien",description="LIEN LOCKDOWN (admin only)", extras={'cog': 'general'})
    @has_permissions(ban_members=True)
    @app_commands.checks.cooldown(rate=1, per=180)
    @checks.in_correct_server()
    @checks.not_in_dm()
    @checks.not_blacklisted()
    async def lien(self, interaction) -> None:
        """Kicks Jerome in case of emergency

        Args:
            interaction (Interaction): Users Interaction
        """

        # kick grom
        try:
            gromID = int(os.environ.get("GROM"))
            grom = await interaction.guild.fetch_member(gromID)
            await grom.kick(reason=":warning: ***LIEN LOCKDOWN*** :warning:")
        # grom kick error
        except:
            pass
        # stuur lockdown bericht
        embed = discord.Embed(
            title=":warning: ***LIEN LOCKDOWN*** :warning:",
            description="<@464400950702899211> has been kicked.",
            color=self.bot.errorColor
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="minecraft",description="Minecraft server info", extras={'cog': 'general'})
    @checks.not_blacklisted()
    async def modlist(self, interaction) -> None:

        embed = discord.Embed(
            title="⛏ Minecraft",
            description=f"IP: ```mc.silasdevuyst.com```",
            color=self.bot.defaultColor
        )
        mods = [
            "[**🌐 Forge**](https://files.minecraftforge.net/net/minecraftforge/forge/)",
            "[**⚙️ Create**](https://www.curseforge.com/minecraft/mc-mods/create/download/4835191)",
            "[**🪄 Create Enchantment Industry**](https://www.curseforge.com/minecraft/mc-mods/create-enchantment-industry/download/4836884)",
            "[**🚄 Create: Steam 'n' Rails**](https://www.curseforge.com/minecraft/mc-mods/create-steam-n-rails/download/4836196)",
            "[**📖 JEI**](https://www.curseforge.com/minecraft/mc-mods/jei/download/4712868)",
            "[**🗺️ JourneyMap**](https://www.curseforge.com/minecraft/mc-mods/journeymap/download/4841242)",
            "[**🍎 AppleSkin**](https://www.curseforge.com/minecraft/mc-mods/appleskin/download/4770828)",
            "[**🌉 Macaw's Bridges**](https://www.curseforge.com/minecraft/mc-mods/macaws-bridges/download/4605466)",
            "[**🛰️ Citadel**](https://www.curseforge.com/minecraft/mc-mods/citadel/download/4848887)",
            "[**🌙 Moonlight Lib**](https://www.curseforge.com/minecraft/mc-mods/selene/download/4856807)",
            "[**🖼️ Supplementaries**](https://www.curseforge.com/minecraft/mc-mods/supplementaries/download/4836493)",
            "[**🐘 Alex's Mobs**](https://www.curseforge.com/minecraft/mc-mods/alexs-mobs/download/4745999)",
            "[**⚰️ Corpse**](https://www.curseforge.com/minecraft/mc-mods/alexs-mobs/download/4745999)",
        ]
        mods_formatted = '\n'.join(mods)
        embed.add_field(
            name="Mods", value=mods_formatted, inline=False
        )
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="countdown", description=f"Countdown till {os.environ.get('COUNTDOWN_TITLE')}", extras={'cog': 'general'})
    @checks.not_blacklisted()
    async def countdown(self, interaction) -> None:
        """Countdown till agiven moment in time

        Args:
            interaction (Interaction): Users Interaction
        """

        deadline = datetime.strptime(os.environ.get("COUNTDOWN"), "%d/%m/%y %H:%M:%S")
        diff = deadline - datetime.now()

        if int(diff.total_seconds()) < 0:
            desc = f"{os.environ.get('COUNTDOWN_TITLE')} IS NU UIT!"
            kleur = self.bot.succesColor
        else:
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            desc = f"Nog {diff.days} dagen, {hours} uur, {minutes} minuten en {seconds} seconden te gaan!"    
            kleur = self.bot.defaultColor
            

        embed = discord.Embed(
            title=f"⏳ Time till {os.environ.get('COUNTDOWN_TITLE')}",
            description=desc,
            color=kleur
        )

        embed.set_thumbnail(
            url=os.environ.get('COUNTDOWN_URL')
        )

        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="dm", description="let the bot DM a user (3🪙)", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=1, per=20)
    @checks.not_in_dm()
    @checks.cost_nword(3)
    @app_commands.describe(user="What user to DM")
    @app_commands.describe(content="What to DM to the user")
    async def dm(self, interaction, user: discord.User, content: str) -> None:
        """Let the bot DM a user

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user to dm
            content (str): What to dm the user
        """

        # stuur dm naar gebruiker
        await user.send(content=content)

        # stuur dm naar admin
        owner = int(list(os.environ.get("OWNERS").split(","))[0])
        admin = await self.bot.fetch_user(owner)
        await admin.send(content=f"{interaction.user.display_name} dm'd {user.display_name}: {content}")

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -3)
        
        # stuur confirmatie
        embed = discord.Embed(
            title="✅ done.",
            description=f"I dm'd {user.display_name}",
            color=self.bot.succesColor
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)



    @app_commands.command(name="chat", description="Chat with the bot (3🪙)", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=2, per=30)
    @checks.cost_nword(3)
    @app_commands.describe(prompt="Your question/conversation piece")
    async def chat(self, interaction, prompt: app_commands.Range[str, 1, 200]) -> None:
        """Chat with the bot using AI

        Args:
            interaction (Interaction): Users Interaction
            prompt (app_commands.Range[str, 1, 200]): The users question
        """
        await interaction.response.defer()

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a discord bot named Where-Context-Bot-3. You are a helpful, but very sarcastic bot who is not afraid to trash-talk. You were made by solos."},
                    {"role": "user", "content": f'Mijn naam is  {interaction.user.display_name}. Anwser the question delimited by triple quotes in about 75 words. """{prompt}"""'},

                ],
                temperature=0.5,
                max_tokens=150
            )
            embed = discord.Embed(
                title=None,
                description=response['choices'][0]['message']['content'],
                color=self.bot.defaultColor
            )

        except Exception as e:
            self.bot.logger.warning(e)
            embed = discord.Embed(
                title="Er ging iets mis",
                description=e,
                color=self.bot.errorColor
            )

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -3)

        # stuur het antwoord
        await interaction.followup.send(embed=embed)



    @app_commands.command(name="image", description="Create an image (5🪙)", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @checks.cost_nword(5)
    @app_commands.checks.cooldown(rate=5, per=120) # 3 per 10 minutes
    @app_commands.describe(prompt="A detailed description of what to create")
    async def image(self, interaction, prompt: app_commands.Range[str, 1, 200]) -> None:
        """Create an image using Ai

        Args:
            interaction (Interaction): Users Interaction
            prompt (app_commands.Range[str, 1, 200]): Information about what to create
        """

        await interaction.response.defer()

        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            
            image_url = response['data'][0]['url']
            
            embed = discord.Embed(
                title=None,
                color=self.bot.defaultColor
            )
            embed.set_image(url=image_url)

        except Exception as e:
            self.bot.logger.warning(e)
            embed = discord.Embed(
                title="Er ging iets mis",
                description=e,
                color=self.bot.errorColor
            )
        
        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -5)

        # stuur het antwoord
        await interaction.followup.send(embed=embed)



    @app_commands.command(name="remindme", description="Remind me of an event", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @app_commands.describe(wanneer="When should the bot send you a reminder")
    @app_commands.describe(waarover="What should the bot remind you for")
    async def remindme(self, interaction, wanneer: str, waarover: app_commands.Range[str, 1, 100]) -> None:
        """Sets a reminder

        Args:
            interaction (Interaction): Users Interaction
            wanneer (str): When to send the reminder
            waarover (app_commands.Range[str, 1, 100]): What the reminder is about
        """
        
        t = dateparser.parse(wanneer, settings={
            'DATE_ORDER': 'DMY',
            'TIMEZONE': 'CEST',
            'PREFER_DAY_OF_MONTH': 'first',
            'PREFER_DATES_FROM': 'future',
            'DEFAULT_LANGUAGES': ["en", "nl"]
        })

        if t is None:
            embed = discord.Embed(
                title="⏰ Geen geldig tijdstip",
                description=f"{wanneer} is geen geldig tijdstip",
                color=self.bot.errorColor
            )
        elif t < datetime.now():
            embed = discord.Embed(
                title="⏰ Geen geldig tijdstip",
                description=f"{wanneer} is in het verleden",
                color=self.bot.errorColor
            )
        else:

            # zet reminder in db
            succes = await db_manager.set_reminder(interaction.user.id, subject=waarover, time=t.strftime('%d/%m/%y %H:%M:%S'))

            
            desc = f"I will remind you at ```{t.strftime('%d/%m/%y %H:%M:%S')} CEST``` for ```{waarover}```" if succes else "Something went wrong!"
            embed = discord.Embed(
                title="⏳ Reminder set!" if succes else "Oops!",
                description=desc,
                color=self.bot.succesColor if succes else self.bot.errorColor
            )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="status", description="Set the status of the bot for 1 hour (10🪙)", extras={'cog': 'general'})
    @app_commands.checks.cooldown(rate=1, per=300) # 1 per 5 minutes
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @checks.cost_nword(10)
    @app_commands.describe(status="What do you want the status of the bot to be")
    async def status(self, interaction, status: app_commands.Range[str, 1, 50]) -> None:
        """Set the status of the bot

        Args:
            interaction (Interaction): Users Interaction
            status (app_commands.Range[str, 1, 50]): status
        """

        await interaction.response.defer()

        # set the status
        self.bot.statusManual = datetime.now()
        await self.bot.change_presence(activity=discord.Game(status))

        embed = discord.Embed(
            title="✅ Status changed!",
            description=f"Changed status to ```{status}```",
            color=self.bot.succesColor
        )

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -10)
        
        # stuur het antwoord
        await interaction.followup.send(embed=embed)


    @app_commands.command(name="anti_gif", description="Prevent a user from using gifs for 1 hour (125🪙)", extras={'cog': 'general'})
    @app_commands.checks.cooldown(rate=1, per=30) # 1 per 30 sec
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @checks.cost_nword(125)
    @app_commands.describe(user="Who to block")
    async def anti_gif(self, interaction, user: discord.User) -> None:
        """Prevent a user from using gifs for 1 hour

        Args:
            interaction (Interaction): Users Interaction
            user (User): who to block
        """

        await interaction.response.defer()

        # add user to block list
        self.bot.gif_prohibited.append(
            (user.name, datetime.now())
        )

        embed = discord.Embed(
            title="✅ Done!",
            description=f"<@{user.id}> is now banned from using gifs.",
            color=self.bot.succesColor
        )

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -125)

        # stuur het antwoord
        await interaction.followup.send(embed=embed)


    @app_commands.command(name="impersonate", description="Send a message diguised as a user (10🪙)", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @checks.cost_nword(10)
    @app_commands.describe(user="Who to impersonate")
    @app_commands.describe(message="What to say")
    async def impersonate(self, interaction, user: discord.User, message: str) -> None:
        """Send a message diguised as a user

        Args:
            interaction (Interaction): Users Interaction
            user (User): who to impersonate
            messate (str): what to say
        """

        # creeer webhook en stuur via die webhook impersonatie
        webhook = await interaction.channel.create_webhook(name=user.name)
        await webhook.send(
            str(message), username=user.display_name, avatar_url=user.display_avatar.url
        )

        await webhook.delete()

        embed = discord.Embed(
            title="✅ Done!",
            description=f"😈",
            color=self.bot.succesColor
        )

        #update ncount
        await db_manager.increment_or_add_nword(interaction.user.id, -10)
        # stuur het antwoord
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="poll", description="Create a poll", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @app_commands.choices(anoniem=[
        discord.app_commands.Choice(name="Yes", value=1),
        discord.app_commands.Choice(name="No", value=0),
    ])
    @app_commands.describe(question="Title of your poll")
    async def poll(self, interaction, question: str, anoniem: discord.app_commands.Choice[int]) -> None:
        """Create a poll

        Args:
            interaction (Interaction): Users interaction
            question (str): Title of poll
            options (str): possible answers
        """

        embed = discord.Embed(
            title=f'Build your poll!', 
            color = self.bot.defaultColor,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name='❓ Question', value=question, inline=False)
        embed.set_footer(text=f"Poll started by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

        view = PollMenuBuilder(question, embed, interaction.user.id, anoniem.value, self.bot)
        await interaction.edit_original_response(embed=embed, view=view)
        


# behandelt alle knoppen van poll builder
class PollMenuBuilder(discord.ui.View):
    def __init__(self, title, embed, author_id, anonymous, bot):
        self.anonymous = anonymous
        self.title = title
        self.author_id = author_id
        self.embed = embed
        self.description = None
        self.bot = bot
        self.options = []

        self.reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        super().__init__(timeout=500)
        


    @discord.ui.button(label="Add Option", emoji='📋', style=discord.ButtonStyle.blurple, disabled=False)
    async def add_option(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add a possible answer

        Args:
            interaction (discord.Interaction): Users Interaction
            button (discord.ui.Button): the button
        """

        # send modal
        modal = AddResponseModal(self)
        await interaction.response.send_modal(modal)

        # wait till modal finishes
        await modal.wait()

        
        # add options to embed
        opts = '\n'.join(f'**{self.reactions[index]}: {val}**' for index, val in enumerate(self.options))
        self.embed.remove_field(index=1)
        self.embed.add_field(name="**📋 Options**", value=opts + "\n\u200b", inline=False)
        
        
        for b in self.children:
            # enable finish button if 2 or more options
            if len(self.options) >= 2:
                if b.label == "Finish":
                    b.disabled = False

            # disable button if 9 options
            if len(self.options) >= 9:
                if b.label == "Add Option":
                    b.disabled = True
        
        # edit poll builder
        msg = await interaction.original_response()
        await msg.edit(embed=self.embed, view=self)


    @discord.ui.button(label="Add Description", emoji='📜', style=discord.ButtonStyle.blurple, disabled=False)
    async def add_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add/change description of poll

        Args:
            interaction (discord.Interaction): Users Interaction
            button (discord.ui.Button): the button
        """
        # send modal
        modal = AddDescriptionModal(self)
        await interaction.response.send_modal(modal)

        # wait till modal finishes
        await modal.wait()

        # set description to embed
        self.embed.description = f"**{self.description}**"
        
        # change button label
        button.label = "Change Description"

        # edit poll builder
        msg = await interaction.original_response()
        await msg.edit(embed=self.embed, view=self)

        


    @discord.ui.button(label="Finish", emoji='✅', style=discord.ButtonStyle.green, disabled=True)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Finish building the poll

        Args:
            interaction (discord.Interaction): Users Interaction
            button (discord.ui.Button): the button
        """

        vals = '\u200b'
        for i in range(len(self.options)):
            vals += f'**{self.reactions[i]}: 0 votes - 0%**\n'

        self.embed.remove_field(index=0)

        # result field
        self.embed.add_field(
            name='**🏁 Results**',
            value=vals,
            inline=False
        )

        self.embed.title = f'***{self.title}***'      

        # edit original message
        msg = interaction.message
        view = discord.ui.View(timeout=None)
        view.add_item(DynamicVotesButton(interaction.user.id))
        await msg.edit(embed=self.embed, view=view if not self.anonymous else None)
        
        # save poll to db
        rcts = ('{' + (len(self.options) * '{"placeholder"}') + '}').replace("}{", "},{")
        await db_manager.create_poll(msg.id, rcts)

        # add reactions
        for i in range(len(self.options)):
            await msg.add_reaction(self.reactions[i])

        # send confirmation
        embed = discord.Embed(
            title="🗳️ Poll is live!",
            color=self.bot.succesColor
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @discord.ui.button(label="Stop", emoji='✖️', style=discord.ButtonStyle.danger, disabled=False)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop building poll

        Args:
            interaction (discord.Interaction): Users Interaction
            button (discord.ui.Button): the button
        """

        # delete original message
        await interaction.message.delete()

        # send confirmation
        embed = discord.Embed(
            title="🛑 Stopped!",
            color=self.bot.defaultColor
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id and str(interaction.user.id) not in list(os.environ.get("OWNERS").split(",")):
            await interaction.response.send_message('shatap lil bro, you are not him', ephemeral=True)
            return False
        return True



class DynamicVotesButton(discord.ui.DynamicItem[discord.ui.Button], template=r'button:user:(?P<id>[0-9]+)'):
    def __init__(self, user_id: int) -> None:
        super().__init__(
            discord.ui.Button(
                label='See votes',
                style=discord.ButtonStyle.blurple,
                custom_id=f'button:user:{user_id}',
                emoji='🗳️',
            )
        )
        self.user_id: int = user_id

    # This is called when the button is clicked and the custom_id matches the template.
    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match, /):
        user_id = int(match['id'])
        return cls(user_id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # anyone can view
        return True

    async def callback(self, interaction: discord.Interaction) -> None:
        # get votes from db
        try:
            reactions = await db_manager.get_poll_reactions(interaction.message.id)
            reactions = [[ subelt for subelt in elt if subelt not in ['placeholder', "'placeholder'"] ] for elt in reactions[0][0]]
        except:
            return await interaction.response.send_message("poll is not active...")

        # create embed
        embed = discord.Embed(
            title="🗳️ Votes",
            color=0xF4900D
        )

        numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        
        # check if poll has votes
        total_reactions = sum([len(x) for x in reactions])
        if total_reactions == 0:
            embed.description = '**This poll has no votes yet...**'
        
        else:
            for i, react in enumerate(reactions):
                # generate description per reaction
                desc = ''
                for r in react:
                    r = r.replace("'", "")
                    desc += f'\n<@{int(r)}>'

                embed.add_field(
                    name=f'**{numbers[i]}**',
                    value=desc if len(desc) > 0 else 'No votes yet',
                    inline=True
                )

        # respond
        await interaction.response.send_message(embed=embed, ephemeral=True)



class AddResponseModal(discord.ui.Modal, title='Add Option'):

    def __init__(self, poll_builder):
        self.poll_builder = poll_builder
        super().__init__(timeout=None)

    answer = discord.ui.TextInput(
        label='Option', 
        required=True,
        max_length=15
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.poll_builder.options.append(self.answer.value)
        embed = discord.Embed(
            title="💾 Option added!",
            description=f'```{self.answer.value}```',
            color=self.poll_builder.bot.succesColor
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)



class AddDescriptionModal(discord.ui.Modal, title='Add/Change Description'):

    def __init__(self, poll_builder):
        self.poll_builder = poll_builder
        super().__init__(timeout=None)

    answer = discord.ui.TextInput(
        label='Description', 
        required=True,
        max_length=75
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.poll_builder.description = self.answer.value
        embed = discord.Embed(
            title="💾 Description set!",
            description=f'```{self.answer.value}```',
            color=self.poll_builder.bot.succesColor
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(General(bot))
