""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""

import discord
import os
from discord import app_commands
from discord.ext import commands
from discord import errors
from discord.ext.commands import Context

from helpers import checks, db_manager


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="sync",
        description="Synchronizes the slash commands (admin only)",
    )
    @app_commands.describe(scope="The scope of the sync.")
    @app_commands.choices(scope=[
        discord.app_commands.Choice(name="Global", value="global"),
        discord.app_commands.Choice(name="Server", value="server"),
    ])
    @checks.is_owner()
    async def sync(self, context: Context, scope: discord.app_commands.Choice[str]) -> None:
        """
        Synchronizes the slash commands.

        :param context: The command context.
        """
        try:

            if scope.value == "global":
                await context.bot.tree.sync()
                embed = discord.Embed(
                    description="Slash commands have been globally synchronized.",
                    color=self.bot.succesColor,
                )
                await context.send(embed=embed)
                return
            
            elif scope.value == "server":

                # context.bot.tree.copy_global_to(guild=context.guild)
                await context.bot.tree.sync(guild=context.guild)
                embed = discord.Embed(
                    description="Slash commands have been synchronized in this server.",
                    color=self.bot.succesColor,
                )
                await context.send(embed=embed)
                return
            embed = discord.Embed(
                description="The scope must be `global` or `server`.", color=self.bot.errorColor
            )
            await context.send(embed=embed)

        except discord.HTTPException as e:
            self.bot.logger.warning(e)
            embed = discord.Embed(
                description="HTTPException, most likely daily application command limits.",
                color=self.bot.errorColor,
            )
            await context.send(embed=embed)
            

    @commands.hybrid_command(
        name="load",
        description="Load a cog (admin only)",
    )
    @app_commands.describe(cog="The name of the cog to load")
    @checks.is_owner()
    async def load_cog(self, context: Context, cog: str) -> None:
        """
        The bot will load the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            self.bot.loaded.add(cog)
            self.bot.unloaded.discard(cog)
        except Exception:
            embed = discord.Embed(
                description=f"Could not load the `{cog}` cog.", color=self.bot.errorColor
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Successfully loaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="unload",
        description="Unloads a cog (admin only)",
    )
    @app_commands.describe(cog="The name of the cog to unload")
    @checks.is_owner()
    async def unload_cog(self, context: Context, cog: str) -> None:
        """
        The bot will unload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to unload.
        """
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            self.bot.loaded.discard(cog)
            self.bot.unloaded.add(cog)
        except Exception:
            embed = discord.Embed(
                description=f"Could not unload the `{cog}` cog.", color=self.bot.errorColor
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description=f"Successfully unloaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="reload",
        description="Reloads a cog (admin only)",
    )
    @app_commands.describe(cog="The name of the cog to reload")
    @checks.is_owner()
    async def reload_cog(self, context: Context, cog: str) -> None:
        """
        The bot will reload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to reload.
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        
        except Exception:
            embed = discord.Embed(
                description=f"Could not reload the `{cog}` cog.", color=self.bot.errorColor
            )
            await context.send(embed=embed)
            return
        
        embed = discord.Embed(
            description=f"Successfully reloaded the `{cog}` cog.", color=self.bot.succesColor
        )

        await context.send(embed=embed)


    @commands.hybrid_command(
        name="cogs",
        description="See loaded/unloaded cogs (admin only)",
    )
    @checks.is_owner()
    async def cogs(self, context: Context) -> None:
        """
        See which cogs are loaded and which are unloaded 

        :param context: The hybrid command context.
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

        await context.send(embed=embed)


    @commands.hybrid_command(
        name="restart",
        description="Make the bot restart (admin only)",
    )
    @checks.is_owner()
    async def restart(self, context: Context) -> None:
        """
        Shuts down the bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(description="Restarting. brb :wave:", color=self.bot.defaultColor)
        await context.send(embed=embed)

        # We shut down the bot, but heroku will automatically restart it.
        await self.bot.close()
        


    @commands.hybrid_group(
        name="blacklist",
        description="Get the list of all blacklisted users (admin only)",
    )
    @checks.is_owner()
    async def blacklist(self, context: Context) -> None:
        """
        Lets you add or remove a user from not being able to use the bot.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n`add` - Add a user to the blacklist.\n`remove` - Remove a user from the blacklist.",
                color=self.bot.errorColor,
            )
            await context.send(embed=embed)



    @blacklist.command(
        base="blacklist",
        name="show",
        description="Shows the list of all blacklisted users (admin only)",
    )
    @checks.is_owner()
    async def blacklist_show(self, context: Context) -> None:
        """
        Shows the list of all blacklisted users.

        :param context: The hybrid command context.
        """
        blacklisted_users = await db_manager.get_blacklisted_users()
        
        # Geen blacklisted users
        if len(blacklisted_users) == 0:
            embed = discord.Embed(
                description="There are currently no blacklisted users.", color=self.bot.defaultColor
            )
            await context.send(embed=embed)
            return
        
        # error
        elif blacklisted_users[0] == -1:
            embed = discord.Embed(
                title=f"Something went wrong",
                description=blacklisted_users[1],
                color=self.bot.errorColor
            )
            await context.send(embed=embed)
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
        await context.send(embed=embed)



    @blacklist.command(
        base="blacklist",
        name="add",
        description="Lets you add a user from not being able to use the bot (admin only)",
    )
    @app_commands.describe(user="The user that should be added to the blacklist")
    @checks.is_owner()
    async def blacklist_add(self, context: Context, user: discord.User) -> None:
        """
        Lets you add a user from not being able to use the bot.

        :param context: The hybrid command context.
        :param user: The user that should be added to the blacklist.
        """
        user_id = user.id
        if await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is already in the blacklist.",
                color=self.bot.errorColor,
            )
            await context.send(embed=embed)
            return
        total = await db_manager.add_user_to_blacklist(user_id)

        # error
        if total == -1:
            embed = discord.Embed(
                description=f"Er is iets misgegaan.",
                color=self.bot.errorColor,
            )
            await context.send(embed=embed)
            return
        
        # alles oke
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully added to the blacklist",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await context.send(embed=embed)

    @blacklist.command(
        base="blacklist",
        name="remove",
        description="Lets you remove a user from not being able to use the bot (admin only)",
    )
    @app_commands.describe(user="The user that should be removed from the blacklist.")
    @checks.is_owner()
    async def blacklist_remove(self, context: Context, user: discord.User) -> None:
        """
        Lets you remove a user from not being able to use the bot.

        :param context: The hybrid command context.
        :param user: The user that should be removed from the blacklist.
        """
        user_id = user.id
        if not await db_manager.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is not in the blacklist.", color=self.bot.errorColor
            )
            await context.send(embed=embed)
            return
        total = await db_manager.remove_user_from_blacklist(user_id)

        #error
        if total == -1:
            embed = discord.Embed(
                description=f"Er is iets misgegaan.", color=self.bot.errorColor
            )
            await context.send(embed=embed)
            return
        
        # alles ok
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully removed from the blacklist",
            color=self.bot.succesColor,
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Owner(bot))
