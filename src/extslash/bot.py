import sys
import discord
import json
import asyncio
import traceback
from .errors import *
from .cog import Cog
from .builder import SlashCommand, SlashOverwrite
from discord.http import Route
from functools import wraps
from .context import ApplicationContext
from .base import AppCommand, Overwrite
from typing import Callable, Optional, Any, Union
from discord.ext import commands
from discord.enums import InteractionType


__all__ = ['Bot']


class Bot(commands.Bot):

    def __init__(
            self,
            command_prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[discord.ext.commands.HelpCommand] = discord.ext.commands.DefaultHelpCommand(),
            description: Optional[str] = None,
            **options
    ):
        super().__init__(
            intents=intents,
            command_prefix=command_prefix,
            help_command=help_command,
            description=description,
            **options
        )
        self.__parent = {}
        self.__cmd_queue = {}
        self.__cached_commands = {}


    def slash_command(self, command: SlashCommand, guild_id: Optional[int] = None):
        """
        Decorator for registering a slash command
        :param command:
        :param guild_id:
        :return:
        """
        self.__cmd_queue[command.name] = (command, guild_id)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._connection.hooks[command.name] = wrapper()
        return decorator

    async def _invoke_slash(self, interaction: discord.Interaction):
        if interaction.type == InteractionType.application_command:
            ctx = ApplicationContext(interaction, self)
            try:
                name = ctx.command_name
                await self._connection.call_hooks(name, self.__parent[name], ctx)
            except Exception as error:
                handler = self._connection.hooks.get('on_command_error')
                if handler:
                    await handler(ctx, error)
                else:
                    print(f'Ignoring exception in `{ctx.command_name}`', file=sys.stderr)
                    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def _walk_slash_commands(self, cog: Cog):
        for name, data in cog.__cog_based_commands__.items():
            self.__parent[name] = data['class']
            func = cog.__cog_functions__[name]
            if asyncio.iscoroutinefunction(func):
                self.__cmd_queue[name] = (data['command'], data['guild_id'])
                self._connection.hooks[name] = func
                error_handler = cog.__cog_listener__
                if error_handler:
                    if asyncio.iscoroutinefunction(error_handler):
                        self._connection.hooks[error_handler.__name__] = error_handler
                    else:
                        raise NonCoroutine(f'listener `{error_handler.__name__}` must be a coroutine function')
            else:
                raise NonCoroutine(f'`{func.__name__}` must be a coroutine function')

    def add_slash_cog(self, cog: Cog):
        self._walk_slash_commands(cog)

    async def sync_slash(self):
        for slash_command, guild_id in self.__cmd_queue.values():
            if guild_id:
                route = Route('POST', f'/applications/{self.application_id}/guilds/{guild_id}/commands')
                resp = await self.http.request(route, json=slash_command.to_dict())
                if slash_command.overwrites:
                    perm_route = Route(
                        'PUT',
                        f'/applications/{self.application_id}/guilds/{guild_id}/commands/{resp.get("id")}/permissions')
                    perms = await self.http.request(perm_route, json=slash_command.overwrites)
                    resp['permissions'] = perms
            else:
                route = Route('POST', f'/applications/{self.application_id}/commands')
                resp = await self.http.request(route, json=slash_command.to_dict())

            cmd = AppCommand(resp)
            self.__cached_commands[cmd.id] = cmd

            prompt = f'[{"GLOBAL" if not guild_id else "GUILD"}] registered /{slash_command.name}'
            print(f'{prompt} ... ID: {resp.get("id")} ... Guild: {guild_id if guild_id else "NA"}')

    async def _cache_global_commands(self):
        route = Route('GET', f'/applications/{self.application_id}/commands')
        resp = await self.http.request(route)
        for data in resp:
            cmd = AppCommand(data)
            self.__cached_commands[cmd.id] = cmd

    async def _cache_guild_commands(self):
        await self.wait_until_ready()
        ids = [guild.id for guild in self.guilds]
        for guild_id in ids:
            route = Route('GET', f'/applications/{self.application_id}/guilds/{guild_id}/commands')
            resp = await self.http.request(route)
            for data in resp:
                cmd = AppCommand(data)
                self.__cached_commands[cmd.id] = cmd

    async def fetch_slash_command(self, command_id: int, guild_id: int = None):
        if guild_id:
            route = Route('GET', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('GET', f'/applications/{self.application_id}/commands/{command_id}')
        resp = await self.http.request(route)
        return AppCommand(resp)

    async def delete_slash_command(self, command_id: int, guild_id: int = None):
        if guild_id:
            route = Route('DELETE', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('DELETE', f'/applications/{self.application_id}/commands/{command_id}')
        await self.http.request(route)

    async def update_slash_command(self, command_id: int, updated: SlashCommand, guild_id: int = None):
        if guild_id:
            route = Route('PATCH', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('PATCH', f'/applications/{self.application_id}/commands/{command_id}')
        resp = await self.http.request(route, json=updated.to_dict())
        cmd = AppCommand(resp)
        self.__cached_commands[cmd.id] = cmd
        return cmd

    async def update_slash_permission(self, guild_id: int, command_id: int, overwrites: [SlashOverwrite]):
        payload = [perm.to_dict() for perm in overwrites]
        route = Route('PATCH',
                      f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}/permissions')
        return await self.http.request(route, json=payload)


    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.add_listener(self._invoke_slash, 'on_interaction')
        await self.login(token)
        app_info = await self.application_info()
        self._connection.application_id = app_info.id
        await self._cache_global_commands()
        await self.sync_slash()
        await self.connect(reconnect=reconnect)
