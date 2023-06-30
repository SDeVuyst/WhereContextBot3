""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import asyncio
import os
import platform
import random
import openai
import re

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context, has_permissions

from helpers import checks, db_manager


openai.api_key = os.environ.get("openaisecret")


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot



    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded"
    )
    @checks.not_blacklisted()
    async def help(self, context: Context) -> None:
        admin = list(os.environ.get("owners").split(","))
        embed = discord.Embed(
            title="**Help** :man_mechanic:", 
            description=f"Ask <@{int(admin[0])}> for help.\n[Klik hier voor meer info](https://github.com/SDeVuyst/WhereContextbot3)\nList of available commands:", 
            color=self.bot.defaultColor
        )
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()

            data = []
            for command in commands:
                description = command.description.partition("\n")[0]
                data.append(f"{command.name} - {description}")

            if i == "context":
                data.append("Rechtermuisklik -> Apps -> Add Context - Add message")
                data.append("Rechtermuisklik -> Apps -> Remove Context - Remove message")

            help_text = "\n".join(data)
            if len(help_text) > 0:
                embed.add_field(
                    name=i.capitalize(), value=f"```{help_text}```", inline=False
                )

        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "help", 1)
        
        await context.send(embed=embed)



    @commands.hybrid_command(
        name="lien",
        description="LIEN LOCKDOWN (admin only)",
    )
    @has_permissions(ban_members=True)
    @commands.cooldown(rate=1, per=180)
    async def lien(self, context: Context) -> None:
        # kick grom
        try:
            gromID = int(os.environ.get("grom"))
            grom = await context.guild.fetch_member(gromID)
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
        await context.send(embed=embed)
        


    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive",
    )
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=self.bot.succesColor if (self.bot.latency * 1000) < 150 else self.bot.defaultColor
        )
        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "ping", 1)

        await context.send(embed=embed)



    @commands.hybrid_command(
        name="say",
        description="The bot will say anything you want",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @checks.not_blacklisted()
    async def say(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "say", 1)

        await context.send(message)



    @commands.hybrid_command(
        name="embed",
        description="The bot will say anything you want, but within embeds",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @checks.not_blacklisted()
    async def embed(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want, but using embeds.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "embed", 1)

        embed = discord.Embed(title=message, color=self.bot.defaultColor)
        await context.send(embed=embed)



    @commands.hybrid_command(
        name="countdown",
        description=f"Countdown till {os.environ.get('countdown_title')}",
    )
    @checks.not_blacklisted()
    async def countdown(self, context: Context) -> None:

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

        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "countdown", 1)
        
        await context.send(embed=embed)



    @commands.hybrid_command(
        name="dm",
        description="let the bot DM a user",
    )
    @checks.not_blacklisted()
    @commands.cooldown(rate=1, per=20)
    async def dm(self, context: Context, user: discord.User, content: str) -> None:

        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "dm", 1)
        
        # stuur dm naar gebruiker
        await user.send(content=content)

        # stuur dm naar admin
        owner = int(list(os.environ.get("owners").split(","))[0])
        admin = await self.bot.fetch_user(owner)
        await admin.send(content=f"{context.author.display_name} dm'd {user.display_name}: {content}")

        # stuur confirmatie
        await context.send(content="done.", ephemeral=True)



    @commands.hybrid_command(
        name="chat",
        description="Chat with the bot",
    )
    @checks.not_blacklisted()
    @commands.cooldown(rate=2, per=30)
    async def chat(self, context: Context, prompt: app_commands.Range[str, 1, 200]) -> None:

        await context.defer()

        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "chat", 1)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a discord bot named Where-Context-Bot-3. You are a helpful, but very sarcastic bot who is not afraid to trash-talk. You were made by solos."},
                    {"role": "user", "content": f'Mijn naam is  {context.author.display_name}. Anwser the question delimited by triple quotes in about 75 words. """{prompt}"""'},

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
        await context.interaction.followup.send(embed=embed)



    @commands.hybrid_command(
        name="image",
        description="Create an image",
    )
    @checks.not_blacklisted()
    @commands.cooldown(rate=5, per=120) # 3 per 10 minutes
    async def image(self, context: Context, prompt: app_commands.Range[str, 1, 200]) -> None:

        await context.defer()

        # stats
        await db_manager.increment_or_add_command_count(context.author.id, "image", 1)

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
        await context.interaction.followup.send(embed=embed)



    @commands.hybrid_command(
        name="invite",
        description="Create an invite",
    )
    @checks.not_blacklisted()
    async def invite(self, context: Context) -> None:
        guild = await self.bot.get_guild(int(os.environ.get("guild_id")))
        channel = await guild.get_channel(int(os.environ.get("channel")))
        link = await channel.create_invite(xkcd=True, max_age = 0, max_uses = 1)

        await context.send(link)



async def setup(bot):
    await bot.add_cog(General(bot))
