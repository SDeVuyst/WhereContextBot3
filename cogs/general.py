""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import asyncio
import os
import dateparser
import re
import random
from openai import OpenAI

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

import embeds

from reactionmenu import ViewMenu, ViewSelect, ViewButton

from helpers import checks, db_manager, ArtBuilder



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

        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
        cog_to_title = {
            "audio": "🎙️ Audio",
            "general": "🤖 General",
            "stats": "📊 Statistics",
            "outofcontext": "📸 Out Of Context",
            "admin": "👨‍🔧 Admin"
        }

        page_numbers = {}
        
        for i, c in enumerate(self.bot.cogs):

            embed = embeds.DefaultEmbed(
                f"**Help - {cog_to_title.get(c.lower())}**", 
                f"🔗 [Invite bot](https://discord.com/api/oauth2/authorize?client_id={os.environ.get('APPLICATION_ID')}&permissions=8&redirect_uri=https%3A%2F%2Fgithub.com%2FSDeVuyst%2FWhereContextBot3&response_type=code&scope=identify%20applications.commands%20applications.commands.permissions.update%20bot%20guilds.join%20guilds.members.read)  •  [Support Server](https://discord.gg/PBsUeB9fP3)  •  [More Info](https://github.com/SDeVuyst/WhereContextbot3) 🔗", 
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
            embed = embeds.OperationSucceededEmbed(
                f" Time till {os.environ.get('COUNTDOWN_TITLE')}", 
                f"{os.environ.get('COUNTDOWN_TITLE')} IS NU UIT!",
                emoji="⌛"
            )
        else:
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            embed = embeds.DefaultEmbed(
                f"⏳ Time till {os.environ.get('COUNTDOWN_TITLE')}",
                f"Nog {diff.days} dagen, {hours} uur, {minutes} minuten en {seconds} seconden te gaan!"
            )
            
        embed.set_thumbnail(
            url=os.environ.get('COUNTDOWN_URL')
        )

 
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="podium", description="generate a podium", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @checks.is_owner()
    @checks.not_in_dm()
    async def podium(self, interaction, first_podium: discord.User, second_podium: discord.User, third_podium: discord.User, first_character: discord.User = None, second_character: discord.User = None, third_character: discord.User = None) -> None:

        await interaction.response.defer()

        message = await interaction.followup.send(embed=embeds.DefaultEmbed(
            "⏳ Loading...", "This can take a while."
        ))

        builder = ArtBuilder.PodiumBuilder(self.bot)
        characters = [
            second_character.id  if second_character is not None else None,
            first_character.id if first_character is not None else None, 
            third_character.id if third_character is not None else None
        ]

        # create task to add image of available poses
        loop = asyncio.get_event_loop()
        loop.create_task(
            builder.async_set_all_podiums_image_file(loop, message, [first_podium.id, second_podium.id, third_podium.id], characters)
        )
                
        

    @app_commands.command(name="dm", description="let the bot DM a user", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=1, per=8, key=lambda i: (i.user.id))
    @checks.not_in_dm()
    @app_commands.describe(user="What user to DM")
    @app_commands.describe(content="What to DM to the user")
    async def dm(self, interaction, user: discord.User, content: str) -> None:
        """Let the bot DM a user

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user to dm
            content (str): What to dm the user
        """
        await interaction.response.defer()

        # stuur dm naar gebruiker
        await user.send(content=content)

        # stuur dm naar admin
        owner = int(list(os.environ.get("OWNERS").split(","))[0])
        admin = await self.bot.fetch_user(owner)
        await admin.send(content=f"{interaction.user.display_name} dm'd {user.display_name}: {content}")
        
        # stuur confirmatie
        await interaction.followup.send(embed=embeds.OperationSucceededEmbed(
            "Done!"
        ), ephemeral=True)
   


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
            'TIMEZONE': 'CET',
            'PREFER_DAY_OF_MONTH': 'first',
            'PREFER_DATES_FROM': 'future',
            'DEFAULT_LANGUAGES': ["en", "nl"]
        })

        if t is None or t < datetime.now():
            return await interaction.response.send_message(embed=embeds.OperationFailedEmbed(
                "Geen geldig tijdstip"
            ))
        
        # zet reminder in db
        succes = await db_manager.set_reminder(interaction.user.id, subject=waarover, time=t.strftime('%d/%m/%y %H:%M:%S'))

        
        desc = f"I will remind you at ```{t.strftime('%d/%m/%y %H:%M:%S')} CEST``` for ```{waarover}```" if succes else "Something went wrong!"

        await interaction.response.send_message(
            embed=embeds.OperationSucceededEmbed(
                "Reminder set!", desc, emoji="⏳"
            ) if succes else embeds.OperationFailedEmbed(
                "Oops!", desc
            ))


    @app_commands.command(name="impersonate", description="Send a message diguised as a user", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @checks.not_in_dm()
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

        # stuur het antwoord
        await interaction.response.send_message(embed=embeds.OperationSucceededEmbed(
            "Done!", "😈"
        ), ephemeral=True)


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

        embed = embeds.DefaultEmbed(
            "Build your poll!"
        )
        embed.add_field(name='❓ Question', value=question, inline=False)
        embed.set_footer(text=f"Poll started by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

        view = PollMenuBuilder(question, embed, interaction.user.id, anoniem.value, self.bot)
        await interaction.edit_original_response(embed=embed, view=view)



    @app_commands.command(name="summary", description="Generate a summary of the latest conversation", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @app_commands.checks.cooldown(rate=1, per=20, key=lambda i: (i.user.id))
    @checks.not_in_dm()
    async def summary(self, interaction) -> None:
        """Let the bot DM a user

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user to dm
            content (str): What to dm the user
        """
        await interaction.response.defer()

        messages_str = ""
        amount_of_messages = 0
        # get last messages from channel
        messages = [message async for message in interaction.channel.history(limit=20)]
        messages = messages[::-1]
        message_sent_time = messages[0].created_at

        # iterate over messsages and format in a string
        i = 0
        while i < len(messages) and i < 250:

            message = messages[i]

            # mark end of conversation if too big of time difference with previous message
            time_difference = divmod((message_sent_time - message.created_at).total_seconds(), 60)
            if time_difference[0] >= 2 and i > 20:
                break
            else: 
                message_sent_time = message.created_at 

            # message cannot be from bot
            if not message.author.bot:
                messages_str += f"{message.author}: {message.clean_content}\n"
                amount_of_messages += 1

            # check if needed to fetch more messages
            if i == len(messages) -1:
                extra_messages = [m async for m in interaction.channel.history(limit=20, before=message)]
                messages.extend(extra_messages)

            i += 1

        # ask gpt to summarize
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate a concise, professional summary of the following conversation."},
                {"role": "user", "content": messages_str},
            ],

        )

        summary_response = response.choices[0].message.content

        # send summary
        await interaction.followup.send(embed=embeds.DefaultEmbed(
            f"🗒️ Summary of last {amount_of_messages} messages", summary_response, user=interaction.user
        ), ephemeral=True)
        


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
        msg = await interaction.message.edit(embed=self.embed)

        # create view to add to message
        view = discord.ui.View(timeout=None)
        # add end poll button
        view.add_item(EndPollButton(interaction.user.id, msg, self.anonymous))
        # add see votes button if not anoymous
        if not self.anonymous:
            view.add_item(DynamicVotesButton(interaction.user.id))
        
        # we have to edit twice because the end poll button needs the new embed
        await msg.edit(view=view)
        
        # save poll to db
        rcts = ('{' + (len(self.options) * '{"placeholder"}') + '}').replace("}{", "},{")
        await db_manager.create_poll(msg.id, rcts)

        # add reactions
        for i in range(len(self.options)):
            await msg.add_reaction(self.reactions[i])

        # send confirmation
        await interaction.response.send_message(embed=embeds.OperationSucceededEmbed(
            "Poll is live!", emoji="🗳️"
        ), ephemeral=True)


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
        await interaction.response.send_message(embed=embeds.DefaultEmbed(
            "🛑 Stopped!"
        ), ephemeral=True)


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
        embed = await get_poll_votes_embed(interaction.message.id)
        await interaction.response.send_message(embed=embed, ephemeral=True)



class EndPollButton(discord.ui.Button):
    def __init__(self, user_id: int, message, anonymous) -> None:
        super().__init__(
            label='End Poll',
            style=discord.ButtonStyle.red,
            custom_id=f'button:userb:{user_id}',
            emoji='⌛',
        )
        self.user_id: int = user_id
        self.message = message
        self.anonymous = anonymous

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        responses = [
            f"<@{interaction.user.id}> shatap lil bro",
            f"<@{interaction.user.id}> you are NOT him",
            f"<@{interaction.user.id}> blud thinks he's funny",
            f"<@{interaction.user.id}> imma touch you lil nigga",
            f"<@{interaction.user.id}> it's on sight now",
        ]

        
        # can only be triggered by the profile owner or an owner
        is_possible = (interaction.user.id == self.user_id) or str(interaction.user.id) in list(os.environ.get("OWNERS").split(","))
        
        # send message if usr cannot interact with button
        if not is_possible:
            await interaction.response.send_message(random.choice(responses))
        
        return is_possible
    

    async def callback(self, interaction: discord.Interaction) -> None:
        # respond to original message with the final results
        response = None
        if not self.anonymous:
            result_embed = await get_poll_votes_embed(self.message.id, True)
            response = await self.message.reply(embed=result_embed)

        # edit message to show that poll is closed
        embed = self.message.embeds[0]
        has_desc = embed.description is not None
        if response is not None:
            embed.description = f"***Closed*** - [See Final Votes]({response.jump_url})\n" + (embed.description if has_desc else "")
        else:
            embed.description = f"***Closed***\n" + (embed.description if has_desc else "")
       
        await self.message.edit(embed=embed, view=None)

        # remove all reactions from poll
        await self.message.clear_reactions()

        # remove poll from db
        await db_manager.delete_poll(self.message.id)

        # respond with confirmation
        await interaction.response.send_message(embed=embeds.OperationSucceededEmbed(
            "Closed Poll!"
        ), ephemeral=True)



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
        await interaction.response.send_message(embed=embeds.OperationSucceededEmbed(
            "Option added!", f'```{self.answer.value}```', emoji="💾"
        ), ephemeral=True)



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
        await interaction.response.send_message(embed=embeds.OperationSucceededEmbed(
            "Description set!", f'```{self.answer.value}```', emoji="💾"
            
        ), ephemeral=True)



async def get_poll_votes_embed(message_id, is_poll_end=False):
    # get votes from db
    reactions = await db_manager.get_poll_reactions(message_id)
    reactions = [[ subelt for subelt in elt if subelt not in ['placeholder', "'placeholder'"] ] for elt in reactions[0][0]]

    # create embed
    embed = embeds.DefaultEmbed(
        "🗳️ Final Votes" if is_poll_end else "🗳️ Votes"
    )

    numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
    
    # check if poll has votes
    total_reactions = sum([len(x) for x in reactions])
    if total_reactions == 0:
        embed.description = '**The poll ended without votes' if is_poll_end else '**This poll has no votes...**'
        return embed

    no_votes_str = 'No votes' if is_poll_end else 'No votes yet'
    for i, react in enumerate(reactions):
        # generate description per reaction
        desc = ''
        for r in react:
            r = r.replace("'", "")
            desc += f'\n<@{int(r)}>'

        embed.add_field(
            name=f'**{numbers[i]}**',
            value=desc if len(desc) > 0 else no_votes_str,
            inline=True
        )

    return embed



async def setup(bot):
    await bot.add_cog(General(bot))
