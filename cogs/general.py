""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import os
import openai
import dateparser

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context, has_permissions

from reactionmenu import ViewMenu, ViewSelect, ViewButton

from helpers import checks, db_manager


openai.api_key = os.environ.get("openaisecret")


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

        admin = list(os.environ.get("owners").split(","))

        menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
        cog_to_title = {
            "audio": "🎙️ Audio",
            "general": "🤖 General",
            "stats": "📊 Statistics",
            "outofcontext": "📸 Out Of Context",
            "reacties": "💭 Reacties",
            "owner": "👨‍🔧 Owner"
        }

        page_numbers = {}
        
        for i, c in enumerate(self.bot.cogs):
            
            cog = self.bot.get_cog(c.lower())
            commands = cog.get_app_commands()

            page_numbers[i+1] = cog_to_title.get(c.lower()).split(" ")[0]

            data = []
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"</{command.name}:{command.id}> - {description}")

            if c == "outofcontext":
                data.append("Rechtermuisklik -> Apps -> Add Context - Add message")
                data.append("Rechtermuisklik -> Apps -> Remove Context - Remove message")

            embed = discord.Embed(
                title=f"**Help - {cog_to_title.get(c.lower())}**", 
                description=f"Ask <@{int(admin[0])}> for more help.\n[Klik hier voor meer info](https://github.com/SDeVuyst/WhereContextbot3)\n", 
                color=self.bot.defaultColor
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
    @commands.cooldown(rate=1, per=180)
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def lien(self, interaction) -> None:
        """Kicks Jerome in case of emergency

        Args:
            interaction (Interaction): Users Interaction
        """

        # kick grom
        try:
            gromID = int(os.environ.get("grom"))
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
        


    @app_commands.command(name="ping", description="Check if the bot is alive", extras={'cog': 'general'})
    @checks.not_blacklisted()
    async def ping(self, interaction) -> None:
        """Check if the bot is alive

        Args:
            interaction (Interaction): Users Interaction
        """

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=self.bot.succesColor if (self.bot.latency * 1000) < 150 else self.bot.defaultColor
        )

        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="say", description="The bot will say anything you want", extras={'cog': 'general'})
    @app_commands.describe(message="The message that should be repeated by the bot")
    @checks.not_blacklisted()
    async def say(self, interaction, *, message: str) -> None:
        """Let the bot say anything you want

        Args:
            interaction (Interaction): Users Interaction
            message (str): What the bot has to say
        """

        await interaction.response.send_message(message)



    @app_commands.command(name="embed", description="The bot will say anything you want, but within embeds", extras={'cog': 'general'})
    @app_commands.describe(message="The message that should be repeated by the bot")
    @checks.not_blacklisted()
    async def embed(self, interaction, *, message: str) -> None:
        """Let the bot say anything you want, but in an embed

        Args:
            interaction (Interaction): Users Interaction
            message (str): What the bot has to say
        """

        embed = discord.Embed(title=message, color=self.bot.defaultColor)
        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="countdown", description=f"Countdown till {os.environ.get('countdown_title')}", extras={'cog': 'general'})
    @checks.not_blacklisted()
    async def countdown(self, interaction) -> None:
        """Countdown till agiven moment in time

        Args:
            interaction (Interaction): Users Interaction
        """

        deadline = datetime.strptime(os.environ.get("countdown"), "%d/%m/%y %H:%M:%S")
        diff = deadline - datetime.now()

        if int(diff.total_seconds()) < 0:
            desc = f"{os.environ.get('countdown_title')} IS NU UIT!"
            kleur = self.bot.succesColor
        else:
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            desc = f"Nog {diff.days} dagen, {hours} uur, {minutes} minuten en {seconds} seconden te gaan!"    
            kleur = self.bot.defaultColor
            

        embed = discord.Embed(
            title=f"Time till {os.environ.get('countdown_title')}",
            description=desc,
            color=kleur
        )

 
        await interaction.response.send_message(embed=embed)




    @app_commands.command(name="dm", description="let the bot DM a user", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @commands.cooldown(rate=1, per=20)
    @checks.not_in_dm()
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
        owner = int(list(os.environ.get("owners").split(","))[0])
        admin = await self.bot.fetch_user(owner)
        await admin.send(content=f"{interaction.user.display_name} dm'd {user.display_name}: {content}")

        # stuur confirmatie
        await interaction.response.send_message(content="done.", ephemeral=True)



    @app_commands.command(name="chat", description="Chat with the bot", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @commands.cooldown(rate=2, per=30)
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
        

        # stuur het antwoord
        await interaction.followup.send(embed=embed)



    @app_commands.command(name="image", description="Create an image", extras={'cog': 'general'})
    @checks.not_blacklisted()
    @checks.not_in_dm()
    @commands.cooldown(rate=5, per=120) # 3 per 10 minutes
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
        

        # stuur het antwoord
        await interaction.followup.send(embed=embed)



    @app_commands.command(name="invite", description="Create an invite", extras={'cog': 'general'})
    @checks.not_blacklisted()
    async def invite(self, interaction) -> None:
        """Send an invite to the main server

        Args:
            interaction (Interaction): Users Interaction
        """

        guild = await self.bot.fetch_guild(int(os.environ.get("guild_id")))
        channel = await guild.fetch_channel(int(os.environ.get("channel")))
        link = await channel.create_invite(max_age = 0, max_uses = 1)

        await interaction.response.send_message(link)



    @app_commands.command(name="remindme", description="Remind me of an event", extras={'cog': 'general'})
    @checks.is_owner()
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
                title="❌ Geen geldig tijdstip",
                description=f"{wanneer} is geen geldig tijdstip",
                color=self.bot.errorColor
            )
        elif t < datetime.now():
            embed = discord.Embed(
                title="❌ Geen geldig tijdstip",
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




async def setup(bot):
    await bot.add_cog(General(bot))
