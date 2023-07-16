from discord.ext import commands
from discord.ext.commands import Context
import discord
import os
from discord import app_commands
from helpers import checks, db_manager


# Here we name the cog and create a new class for the cog.
class OutOfContext(commands.Cog, name="context"):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu_add = app_commands.ContextMenu(
            name='Add Context',
            callback=self.context_add,
        )
        self.bot.tree.add_command(self.ctx_menu_add)

        self.ctx_menu_remove = app_commands.ContextMenu(
            name='Remove Context',
            callback=self.context_remove,
        )
        self.bot.tree.add_command(self.ctx_menu_remove)

        self.currently_playing = False

 # COMMANDS
    @checks.not_blacklisted()
    async def context_add(self, interaction: discord.Interaction, message:discord.Message):
        """
        Lets you add a message to the OOC game.

        """
        submitted_id = interaction.user.id

        # check als message uit OOC komt
        if message.channel.id != int(os.environ.get('channel')):
            embed = discord.Embed(
                description="Bericht moet in #out-of-context staan!",
                color=self.bot.errorColor,
            )
            embed.set_footer(text=f"{message.id}")
            await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)
            return

        # check als bericht al in db staat
        if await db_manager.is_in_ooc(message.id):
            embed = discord.Embed(
                description=f"Message is already in the game.",
                color=self.bot.errorColor,
            )
            embed.set_footer(text=f"{message.id}")
            await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)
            return
        
        # voeg toe
        total = await db_manager.add_message_to_ooc(message.id, submitted_id)

        # error
        if total == -1:
            embed = discord.Embed(
                description=f"Er is iets misgegaan.",
                color=self.bot.errorColor,
            )
            embed.set_footer(text=f"{message.id}")
            await interaction.response.send_message(embed=embed)
            return
        
        # alles oke
        embed = discord.Embed(
            description=f"[Message]({message.jump_url}) has been added to the game",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'message' if total == 1 else 'messages'} in the game"
        )
        await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)


    @checks.not_blacklisted()
    async def context_remove(self, interaction: discord.Interaction, message:discord.Message):
        """
        Lets you remove a message to the OOC game.

        """
        embed = await self.remove(message.id, interaction.guild)
        await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)


    @commands.hybrid_command(
        name="context_debug",
        description="debug stats for /play-game (admin only)",
    )
    @checks.is_owner()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def context_debug(self, context: Context):

        embed = discord.Embed(
            title="Debug",
            color=self.bot.defaultColor,
            description=f"""Amount of messages: {len(self.menu.messages)}\n\n
                Current index: {self.menu.currentIndex}\n\n
                Messages played: {self.menu.messagesPlayed}\n\n
                Messages deleted: {self.menu.messagesDeleted}\n\n
                Author: {self.menu.author.display_name if self.currently_playing else "None"}\n\n
                Currently playing: {self.currently_playing}"""
        )

        await context.send(embed=embed)


    @commands.hybrid_command(
        name="play-game",
        description="Play the out of context game",
    )
    @app_commands.describe(groep="Toon het spel ook aan andere personen")
    @checks.not_blacklisted()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def play(self, context: Context, groep: bool) -> None:
        """
        Play the out of context game

        :param context: The hybrid command context.
        """
        if self.currently_playing:
            embed = discord.Embed(
                description=f"Er is al iemand het spel aan het spelen.",
                color=self.bot.errorColor,
            )
            await context.send(embed=embed, delete_after=10)
            return
        
        self.menu = Menu(self)
        
        embed, sendView = await self.getRandomMessage(context.guild)
        await self.menu.reset()
        self.menu.author = context.author

        self.menu.message = await context.send(embed=embed, view= self.menu if sendView else None, ephemeral=not groep)
        self.currently_playing = True



# HELPER FUNCTIONS

    async def getRandomMessage(self, guild):
        # krijg random bericht uit db
        messages = await db_manager.get_ooc_messages(1)
        if len(messages) > 0:
            worked = await db_manager.increment_times_played(messages[0][0])

        # Geen berichten
        if len(messages) == 0:
            embed = discord.Embed(
                description="There are no messages.", color=self.bot.defaultColor
            )
            
            return (embed, False)
        
        # error
        elif messages[0] == -1 or not worked:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=messages[1],
                color=self.bot.errorColor
            )
            return (embed, False)

        # alles is ok
        embed = await self.getEmbed(int(messages[0][0]), guild, int(messages[0][2]), int(messages[0][3]))
        return (embed, True)
    

    async def getMessage(self, guild, id):
        # krijg bekend bericht uit db
        messages = await db_manager.get_ooc_message(id)

        # Geen berichten
        if len(messages) == 0:
            embed = discord.Embed(
                description="There are no messages.", color=self.bot.defaultColor
            )
            
            return (embed, False)
        
        # error
        elif messages[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=messages[1],
                color=self.bot.errorColor
            )
            return (embed, False)

        # alles is ok
        embed = await self.getEmbed(int(messages[0][0]), guild, int(messages[0][2]), int(messages[0][3]))
        return (embed, True)
        

    async def getEmbed(self, id, guild, added_by, times_played):
        # haal bericht op van discord
        m = await guild.get_channel(int(os.environ.get("channel"))).fetch_message(id)
        desc = f"[Go to message]({m.jump_url})" if len(m.content) == 0 else f"**{m.content}**\n[Go to message]({m.jump_url})"
        embed = discord.Embed(
            title="**Out of Context**", 
            color=self.bot.defaultColor,
            description=desc
        )

        if m.attachments:
            # als er meerdere attachments zijn, tonen we enkel de eerste
            embed.set_image(url=m.attachments[0].url)

            # check als er video in message zit
            for attch in m.attachments:
                try:
                    embed.description += f"\n**Contains {attch.content_type if attch.content_type else 'unknown attachment'}!**"

                # attachement type is onbekend
                except TypeError:
                    embed.description += "\n**Contains unknown attachment!**"

        try:

            embed.add_field(
                name="Times played",
                value=f"```{times_played}```",
                inline=True
            )

            # embed.add_field(
            #     name="Added by",
            #     # value=f"<@{int(added_by)}>",
            #     value = f"```{user.name}```",
            #     inline=True
            # )

            embed.add_field(
                name="Added at",
                value=f"```{m.created_at.strftime('%d/%m/%Y - %H:%M:%S')}```",
                inline=True
            )

            embed.set_footer(
                text=f"message id: {id}"
            )

            user = await self.bot.fetch_user(int(added_by))
            embed.set_thumbnail(
                url=str(user.avatar.url)
            )

            embed.set_author(
                name=user.name, 
                icon_url=str(user.avatar.url)
            )

        except Exception as e:
            embed.add_field(
                name="User error",
                value=e,
                inline=False
            )
        
        
        # voeg id toe aan messages indien nodig
        if self.menu.currentIndex == len(self.menu.messages):
            self.menu.messages.append(m.id)

        return embed


    async def remove(self, id, guild):
        # check als bericht bestaat
        if not await db_manager.is_in_ooc(id):
            embed = discord.Embed(
                description=f"**{id}** is not in the game.",
                color=self.bot.errorColor,
            )
            return embed
        
        # verwijder bericht
        total = await db_manager.remove_message_from_ooc(id)
    
        # error
        if total == -1:
            embed = discord.Embed(
                description=f"Er is iets misgegaan.",
                color=self.bot.errorColor,
            )
            return embed
        
        m = await guild.get_channel(int(os.environ.get("channel"))).fetch_message(id)
        
        # alles oke
        embed = discord.Embed(
            description=f"[Message]({m.jump_url}) has been removed from the game",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'message' if total == 1 else 'messages'} in the game"
        )
        return embed



# behandelt alle knoppen
class Menu(discord.ui.View):
    def __init__(self, OOC):
        super().__init__(timeout=300)
        self.OOC = OOC
        self.messages = []
        self.currentIndex = 0
        self.messagesPlayed = 0
        self.messagesDeleted = 0
        self.author = None


    async def reset(self):
        for b in self.children:
            b.disabled = False


    @discord.ui.button(label="Previous", style=discord.ButtonStyle.green, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentIndex -= 1
        self.currentIndex = self.currentIndex if self.currentIndex > 0 else 0

        # disable previous knop als we op eerste bericht zitten
        if self.currentIndex == 0:
            for b in self.children:
                b.disabled = b.label == "Previous"
                

        # Toon het vorige bericht
        embed, showView = await self.OOC.getMessage(interaction.guild, self.messages[self.currentIndex])
        await interaction.response.edit_message(embed=embed, view = self if showView else None)


    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.currentIndex += 1
        # check als we bericht al hebben ingeladen of nieuw random bericht moeten opvragen
        if (self.currentIndex == len(self.messages)):
            embed, sendView = await self.OOC.getRandomMessage(interaction.guild)
            self.messagesPlayed += 1

        else:
            embed, sendView = await self.OOC.getMessage(interaction.guild, self.messages[self.currentIndex])

        # enable alle knoppen
        for c in self.children:
            c.disabled = False

        await interaction.response.edit_message(embed=embed, view = self if sendView else None)


    @discord.ui.button(label="Remove", style=discord.ButtonStyle.red)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        # verwijder bericht
        embed = await self.OOC.remove(self.messages[self.currentIndex], interaction.guild)

        # zet index juist en verwijder bericht ook uit ingeladen berichten
        messageToDelete = self.messages[self.currentIndex]
        self.messages = [i for i in self.messages if i != messageToDelete]
        self.currentIndex = len(self.messages)-1 # if len(self.messages) > 0 else -1
        self.messagesDeleted += 1

        # disable de verwijder knop
        for b in self.children:
            b.disabled = b.label == "Remove"
            # disable de previous knop als we op begin van lijst zitten
            if self.currentIndex == -1:
                b.disabled = b.label == "Previous" or b.label == "Remove"

        await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.button(label="Quit", style=discord.ButtonStyle.blurple)
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):

        # stuur confirmatie bericht
        embed = discord.Embed(
            title="Bye. :wave:",
            description=f"You played {self.messagesPlayed +1} {'message' if self.messagesPlayed == 0 else 'messages'}.",
            color=self.OOC.bot.defaultColor
        )
        await interaction.response.edit_message(embed=embed, view=None)
        await self.reset_game()


    async def interaction_check(self, interaction: discord.Interaction):
        try:
            is_possible = interaction.user.id == self.author.id or str(interaction.user.id) in list(os.environ.get("owners").split(","))
            # stuur dm naar user als niet author is
            if not is_possible:
                await interaction.user.send('nt')
            return is_possible
        
        except:
            return False
        

    async def on_timeout(self) -> None:

        if self.message is None: return
        # stuur confirmatie bericht
        embed = discord.Embed(
            title="Bye. :wave:",
            description=f"You played {self.messagesPlayed +1} {'message' if self.messagesPlayed == 0 else 'messages'}.",
            color=self.OOC.bot.defaultColor
        )
        await self.message.edit(embed=embed, view=None)
        await self.reset_game()
    

    async def reset_game(self):
        # stats
        await db_manager.increment_or_add_command_count(self.author.id, "messages_played", self.messagesPlayed+1)
        await db_manager.increment_or_add_command_count(self.author.id, "messages_deleted", self.messagesDeleted)       

        # reset alle gegevens
        self.messages.clear()
        self.currentIndex = 0
        self.messagesPlayed = 0
        self.messagesDeleted = 0
        self.author = None
        self.message = None
        await self.reset()

        self.OOC.currently_playing = False


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(OutOfContext(bot))