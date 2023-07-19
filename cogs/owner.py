""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="sync",
        description="Synchronizes the slash commands (admin only)",
    )
    @app_commands.describe(scope="The scope of the sync.")
    @app_commands.choices(scope=[
        discord.app_commands.Choice(name="Global", value="global"),
        discord.app_commands.Choice(name="Server", value="server"),
    ])
    @checks.is_owner()
    async def sync(self, interaction, scope: discord.app_commands.Choice[str]) -> None:
        """Synchronizes the slash commands

        Args:
            interaction (Interaction): Users interaction
            scope (discord.app_commands.Choice[str]): The scope to sync, can be global or server
        """
        try:

            if scope.value == "global":
                cmds = await self.bot.tree.sync()
                self.save_ids(cmds)

                embed = discord.Embed(
                    description="Slash commands have been globally synchronized.",
                    color=self.bot.succesColor,
                )
                await interaction.response.send_message(embed=embed)
                return
            
            elif scope.value == "server":

                # context.bot.tree.copy_global_to(guild=context.guild)
                cmds = await self.bot.tree.sync(guild=interaction.guild)
                self.save_ids(cmds)

                embed = discord.Embed(
                    description="Slash commands have been synchronized in this server.",
                    color=self.bot.succesColor,
                )
                await interaction.response.send_message(embed=embed)
                return
            embed = discord.Embed(
                description="The scope must be `global` or `server`.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)

            

        except discord.HTTPException as e:
            self.bot.logger.warning(e)
            embed = discord.Embed(
                description="HTTPException, most likely daily application command limits.",
                color=self.bot.errorColor,
            )
            await interaction.response.send_message(embed=embed)



    def save_ids(self, cmds):
        """Saves the ids of commands

        Args:
            cmds (Command)
        """
        for cmd in cmds:
            if cmd.guild_id is None:  # it's a global slash command
                self.bot.tree._global_commands[cmd.name].id = cmd.id
            else:  # it's a guild specific command
                self.bot.tree._guild_commands[cmd.guild_id][cmd.name].id = cmd.id




    @app_commands.command(
        name="load",
        description="Load a cog (admin only)",
    )
    @app_commands.describe(cog="The name of the cog to load")
    @checks.is_owner()
    async def load_cog(self, interaction, cog: str) -> None:
        """Load a given cog

        Args:
            interaction (Interaction): users interaction
            cog (str): The cog to load
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            self.bot.loaded.add(cog)
            self.bot.unloaded.discard(cog)
        except Exception:
            embed = discord.Embed(
                description=f"Could not load the `{cog}` cog.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        embed = discord.Embed(
            description=f"Successfully loaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="unload",
        description="Unloads a cog (admin only)",
    )
    @app_commands.describe(cog="The name of the cog to unload")
    @checks.is_owner()
    async def unload_cog(self, interaction, cog: str) -> None:
        """Unloads a cog

        Args:
            interaction (Interaction): Users Interaction
            cog (str): The cog to unload
        """
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            self.bot.loaded.discard(cog)
            self.bot.unloaded.add(cog)
        except Exception:
            embed = discord.Embed(
                description=f"Could not unload the `{cog}` cog.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        embed = discord.Embed(
            description=f"Successfully unloaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="reload",
        description="Reloads a cog (admin only)",
    )
    @app_commands.describe(cog="The name of the cog to reload")
    @checks.is_owner()
    async def reload_cog(self, interaction, cog: str) -> None:
        """Reloads a cog

        Args:
            interaction (Interaction): Users interaction
            cog (str): The cog to reload
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        
        except Exception:
            embed = discord.Embed(
                description=f"Could not reload the `{cog}` cog.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            description=f"Successfully reloaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="cogs",
        description="See loaded/unloaded cogs (admin only)",
    )
    @checks.is_owner()
    async def cogs(self, interaction) -> None:
        """Shows which cogs are loaded/unloaded

        Args:
            interaction (Interaction): users interaction
        """
        
        embed = discord.Embed(
            title="Cog info",
            color=self.bot.defaultColor
        )
        loaded_fields = "\n".join(list(self.bot.loaded))
        embed.add_field(
            name="Loaded", value=f'```\n{loaded_fields}```', inline=False
        )

        unloaded_fields = "\n".join(list(self.bot.unloaded))
        if len(unloaded_fields) > 0:
            embed.add_field(
                name="Unloaded", value=f"```\n{unloaded_fields}```", inline=False
            )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="restart",
        description="Make the bot restart (admin only)",
    )
    @checks.is_owner()
    async def restart(self, interaction) -> None:
        """Restarts the bot

        Args:
            interaction (Interaction): Users Interaction
        """
        embed = discord.Embed(description="Restarting. brb :wave:", color=self.bot.defaultColor)
        await interaction.response.send_message(embed=embed)

        # We shut down the bot, but heroku will automatically restart it.
        await self.bot.close()
        


    @app_commands.command(
        name="blacklistshow",
        description="Shows the list of all blacklisted users (admin only)",
    )
    @checks.is_owner()
    async def blacklist_show(self, interaction) -> None:
        """Shows list of all blacklisted users

        Args:
            interaction (Interaction): Users Interaction
        """
        blacklisted_users = await db_manager.get_blacklisted_users()
        
        # Geen blacklisted users
        if len(blacklisted_users) == 0:
            embed = discord.Embed(
                description="There are currently no blacklisted users.", color=self.bot.defaultColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # error
        elif blacklisted_users[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=blacklisted_users[1],
                color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return

        # alles is ok
        embed = discord.Embed(title="Blacklisted Users", color=self.bot.defaultColor)
        users = []
        for bluser in blacklisted_users:
            user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(
                int(bluser[0])
            )
            users.append(f"• {user.mention} ({user}) - Blacklisted at {bluser[1].strftime('%d/%m/%Y - %H:%M:%S')}")
        embed.description = "\n".join(users)
        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="blacklistadd",
        description="Lets you add a user from not being able to use the bot (admin only)",
    )
    @app_commands.describe(user="The user that should be added to the blacklist")
    @checks.is_owner()
    async def blacklist_add(self, interaction, user: discord.User) -> None:
        """Adds a user to the blacklist

        Args:
            interaction (Interaction): Users Interaction
            user (discord.User): Which user to add
        """
        user_id = user.id
        if await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is already in the blacklist.",
                color=self.bot.errorColor,
            )
            await interaction.response.send_message(embed=embed)
            return
        total = await db_manager.add_user_to_blacklist(user_id)

        # error
        if total == -1:
            embed = discord.Embed(
                description=f"Er is iets misgegaan.",
                color=self.bot.errorColor,
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # alles oke
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully added to the blacklist",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="blacklistremove",
        description="Lets you remove a user from not being able to use the bot (admin only)",
    )
    @app_commands.describe(user="The user that should be removed from the blacklist.")
    @checks.is_owner()
    async def blacklist_remove(self, interaction, user: discord.User) -> None:
        """Removes a user from the blacklist

        Args:
            interaction (Interaction): Users interaction
            user (discord.User): WHich user to remove
        """
        user_id = user.id
        if not await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is not in the blacklist.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        total = await db_manager.remove_user_from_blacklist(user_id)

        #error
        if total == -1:
            embed = discord.Embed(
                description=f"Er is iets misgegaan.", color=self.bot.errorColor
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # alles ok
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully removed from the blacklist",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await interaction.response.send_message(embed=embed)



async def setup(bot):
    await bot.add_cog(Owner(bot))
