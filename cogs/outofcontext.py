from discord.ext import commands
import discord
import os
import embeds
from discord import app_commands
from helpers import checks, db_manager


# Here we name the cog and create a new class for the cog.
class OutOfContext(commands.Cog, name="outofcontext"):
    def __init__(self, bot):
        self.bot = bot
        self.addcontext_contextmenu = app_commands.ContextMenu(
            name='Add Context',
            callback=self.context_add,
        )
        self.bot.tree.add_command(self.addcontext_contextmenu)
        
        self.removecontext_contextmenu = app_commands.ContextMenu(
            name='Remove Context',
            callback=self.context_remove,
        )
        self.bot.tree.add_command(self.removecontext_contextmenu)

        self.currently_playing = False


    @app_commands.command(
        name="play_game",
        description="Play the out of context game",
        extras={'cog': 'outofcontext'}
    )
    @app_commands.describe(groep="Toon het spel ook aan andere personen")
    @checks.not_blacklisted()
    @checks.in_correct_server()
    @checks.not_in_dm()
    async def play_game(self, interaction, groep: bool=True):
        """Play the out of context game

        Args:
            interaction (Interaction): Users interaction
            groep (bool): If the game has to be ephemeral or not
        """
        if self.currently_playing:
            return await interaction.response.send_message(embed=embeds.OperationFailedEmbed(
                "Er is al iemand het spel aan het spelen.",
            ), delete_after=10)
        
        self.menu = Menu(self)
        
        embed, sendView = await self.get_random_message(interaction.guild)
        await self.menu.reset()
        self.menu.author = interaction.user

        self.menu.message = await interaction.response.send_message(embed=embed, view= self.menu if sendView else None, ephemeral=not groep)
        self.currently_playing = True



# HELPER FUNCTIONS

    async def get_random_message(self, guild):
        """Gets a random message from the out of context game db

        Args:
            guild (Guild): Guild from the message

        Returns:
            Tuple with embed and bool if succesfull
        """

        # krijg random bericht uit db
        messages = await db_manager.get_ooc_messages(1)
        if len(messages) > 0:
            worked = await db_manager.increment_times_played(messages[0][0])

        # Geen berichten
        if len(messages) == 0:
            embed = embeds.OperationFailedEmbed(
                "There are no messages."
            )
            return (embed, False)
        
        # error
        elif messages[0] == -1 or not worked:
            raise Exception(messages[1])

        # alles is ok
        embed = await self.get_embed(int(messages[0][0]), guild, int(messages[0][2]), int(messages[0][3]))
        return (embed, True)
    

    async def get_message(self, guild, id):
        """Get specific message from the ooc db

        Args:
            guild (Guild): Guild from message
            id (int): ID from the message

        Returns:
            Tuple with embed and bool if succesfull
        """

        # krijg bekend bericht uit db
        messages = await db_manager.get_ooc_message(id)

        # Geen berichten
        if len(messages) == 0:
            embed = embeds.OperationFailedEmbed(
                "There are no messages."
            )
            
            return (embed, False)
        
        # error
        elif messages[0] == -1:
            raise Exception(messages[1])

        # alles is ok
        embed = await self.get_embed(int(messages[0][0]), guild, int(messages[0][2]), int(messages[0][3]))
        return (embed, True)
        

    async def get_embed(self, id, guild, added_by, times_played):
        """ Generates an embed

        Args:
            id (int): Id from message
            guild (Guild): Messages guild
            added_by (str): id of user who added the message        
            times_played (int): How many times the message has been played

        Returns:
            Embed
        """

        # haal bericht op van discord
        m = await guild.get_channel(int(os.environ.get("CHANNEL"))).fetch_message(id)
        desc = f"[Go to message]({m.jump_url})" if len(m.content) == 0 else f"**{m.content}**\n[Go to message]({m.jump_url})"
        
        user = await self.bot.fetch_user(int(added_by))
        embed = embeds.DefaultEmbed(
            "**Out of Context**", desc, user
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

            embed.add_field(
                name="Added at",
                value=f"```{m.created_at.strftime('%d/%m/%Y - %H:%M:%S')}```",
                inline=True
            )

            embed.set_footer(
                text=f"message id: {id}"
            )

            embed.set_author(
                name=user.name, 
                icon_url=str(user.avatar.url)
            )
            
            
        except Exception as e:
            embed = embeds.DefaultEmbed(
                title="**Out of Context**", 
                description="Message was deleted, you can remove this one from the game"
            )
        
        # voeg id toe aan messages indien nodig
        if self.menu.current_index == len(self.menu.messages):
            self.menu.messages.append(m.id)
            
        return embed
        
        


    async def remove(self, id, guild):
        """Removes a message from the ooc game

        Args:
            id (int): Id of message that has to be removed
            guild (Guild): Messages guild

        Returns:
            Embed
        """

        # check als bericht bestaat
        if not await db_manager.is_in_ooc(id):
            return embeds.OperationFailedEmbed("Message is not in the game.")
        
        # verwijder bericht
        total = await db_manager.remove_message_from_ooc(id)
    
        # error
        if total == -1:
            return embeds.OperationFailedEmbed(
                "Something went wrong..."
            )
        
        m = await guild.get_channel(int(os.environ.get("CHANNEL"))).fetch_message(id)
        
        # alles oke
        return embeds.OperationSucceededEmbed(
            f"[Message]({m.jump_url}) has been removed from the game"
        ).set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'message' if total == 1 else 'messages'} in the game"
        )



    @checks.not_blacklisted()
    @checks.in_correct_server()
    async def context_add(self, interaction: discord.Interaction, message:discord.Message):
        """
        Lets you add a message to the OOC game.

        """
        submitted_id = message.author.id

        # check als message uit OOC komt
        if message.channel.id != int(os.environ.get('CHANNEL')):
            embed = embeds.OperationFailedEmbed(
                "Bericht moet in #out-of-context staan!"
            )
            embed.set_footer(text=f"{message.id}")
            await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)
            return

        # check als bericht al in db staat
        if await db_manager.is_in_ooc(message.id):
            embed = embeds.OperationFailedEmbed(
                "Message is already in the game."
            )
            embed.set_footer(text=f"{message.id}")
            return await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)
        
        # voeg toe
        total = await db_manager.add_message_to_ooc(message.id, submitted_id)

        # error
        if total == -1:
            embed = embeds.OperationFailedEmbed(
                "Something went wrong..."
            ).set_footer(
                text=f"{message.id}"
            )
            return await interaction.response.send_message(embed=embed)
        
        # alles oke
        embed = embeds.OperationSucceededEmbed(
            title='Success!',
            description=f"[Message]({message.jump_url}) has been added to the game"
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'message' if total == 1 else 'messages'} in the game"
        )
        await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)



    @checks.not_blacklisted()
    @checks.in_correct_server()
    async def context_remove(self, interaction: discord.Interaction, message:discord.Message):
        """
        Lets you remove a message to the OOC game.

        """
        # check als bericht bestaat
        id = message.id
        if not await db_manager.is_in_ooc(id):
            
            return await interaction.response.send_message(embed=embeds.OperationFailedEmbed(
                f"**{id}** is not in the game."
            ), delete_after=10, ephemeral=True)
        
        # verwijder bericht
        total = await db_manager.remove_message_from_ooc(id)

        # error
        if total == -1:
            return await interaction.response.send_message(embed=embeds.OperationFailedEmbed(
                "Something went wrong..."
            ), delete_after=10, ephemeral=True)
        
        m = await interaction.guild.get_channel(int(os.environ.get("CHANNEL"))).fetch_message(id)
        
        # alles oke
        embed = embeds.OperationSucceededEmbed(
            f"[Message]({m.jump_url}) has been removed from the game"
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'message' if total == 1 else 'messages'} in the game"
        )
        return await interaction.response.send_message(embed=embed, delete_after=10, ephemeral=True)

# behandelt alle knoppen
class Menu(discord.ui.View):
    def __init__(self, OOC):
        super().__init__(timeout=300)
        self.OOC = OOC
        self.messages = []
        self.current_index = 0
        self.messages_played = 0
        self.messages_deleted = 0
        self.author = None


    async def reset(self):
        """Resets the children
        """
        for b in self.children:
            b.disabled = False


    @discord.ui.button(label="Previous", style=discord.ButtonStyle.green, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Goes to the previous message

        Args:
            interaction (discord.Interaction): Users Interaction
            button (discord.ui.Button): the button
        """
        self.current_index -= 1
        self.current_index = self.current_index if self.current_index > 0 else 0

        # disable previous knop als we op eerste bericht zitten
        if self.current_index == 0:
            for b in self.children:
                b.disabled = b.label == "Previous"
                

        # Toon het vorige bericht
        embed, showView = await self.OOC.get_message(interaction.guild, self.messages[self.current_index])
        await interaction.response.edit_message(embed=embed, view = self if showView else None)


    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Goes to the next message

        Args:
            interaction (discord.Interaction): Users Interaction
            button (discord.ui.Button): button
        """
        self.current_index += 1
        # check als we bericht al hebben ingeladen of nieuw random bericht moeten opvragen
        if (self.current_index == len(self.messages)):
            embed, sendView = await self.OOC.get_random_message(interaction.guild)
            self.messages_played += 1

        else:
            embed, sendView = await self.OOC.get_message(interaction.guild, self.messages[self.current_index])

        # enable alle knoppen
        for c in self.children:
            c.disabled = False

        await interaction.response.edit_message(embed=embed, view = self if sendView else None)


    @discord.ui.button(label="Remove", style=discord.ButtonStyle.red)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Removes message from the game

        Args:
            interaction (discord.Interaction): Users interaction
            button (discord.ui.Button): button
        """

        # verwijder bericht
        embed = await self.OOC.remove(self.messages[self.current_index], interaction.guild)

        # zet index juist en verwijder bericht ook uit ingeladen berichten
        message_to_delete = self.messages[self.current_index]
        self.messages = [i for i in self.messages if i != message_to_delete]
        self.current_index = len(self.messages)-1 # if len(self.messages) > 0 else -1
        self.messages_deleted += 1

        # disable de verwijder knop
        for b in self.children:
            b.disabled = b.label == "Remove"
            # disable de previous knop als we op begin van lijst zitten
            if self.current_index == -1:
                b.disabled = b.label == "Previous" or b.label == "Remove"

        await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.button(label="Quit", style=discord.ButtonStyle.blurple)
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Exit the game

        Args:
            interaction (discord.Interaction): Users interaction
            button (discord.ui.Button): button
        """

        # stuur confirmatie bericht
        await interaction.response.edit_message(embed=embeds.DefaultEmbed(
            "Bye. :wave:", 
            f"You played {self.messages_played +1} {'message' if self.messages_played == 0 else 'messages'}."
        ), view=None)
        await self.reset_game()


    async def interaction_check(self, interaction: discord.Interaction):
        """Check that the game player is the one who is clicking buttons

        Args:
            interaction (discord.Interaction): Users Interaction

        Returns:
            bool
        """

        is_possible = interaction.user.id == self.author.id or str(interaction.user.id) in list(os.environ.get("OWNERS").split(","))
        # stuur dm naar user als niet author is
        if not is_possible:
            await interaction.user.send('nt')
        return is_possible
        
        

    async def on_timeout(self) -> None:
        """Exits the game on timeout
        """

        if self.message is None: return
        
        # stuur confirmatie bericht
        await self.message.edit(embed=embeds.DefaultEmbed(
            "Bye. :wave:", f"You played {self.messages_played +1} {'message' if self.messages_played == 0 else 'messages'}."
        ), view=None)
        await self.reset_game()
    

    async def reset_game(self):
        """Resets the game
        """
        # stats
        await db_manager.increment_or_add_command_count(self.author.id, "messages_played", self.messages_played+1)
        await db_manager.increment_or_add_command_count(self.author.id, "messages_deleted", self.messages_deleted)       

        # reset alle gegevens
        self.messages.clear()
        self.current_index = 0
        self.messages_played = 0
        self.messages_deleted = 0
        self.author = None
        self.message = None
        await self.reset()

        self.OOC.currently_playing = False



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(OutOfContext(bot))