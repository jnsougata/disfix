import sys
import discord
import json
import asyncio
import traceback
from .errors import *
from .cog import Cog
from .slash_input import SlashCommand
from .user_input import UserCommand
from .msg_input import MessageCommand
from .app import Overwrite
from discord.http import Route
from functools import wraps
from .context import Context
from .enums import ApplicationCommandType
from .base import ApplicationCommand, BaseOverwrite
from typing import Callable, Optional, Any, Union, List, Dict, Tuple
from discord.ext import commands
from discord.http import Route
from discord.enums import InteractionType


__all__ = ['Bot']

#  # override the default route


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
        self.__queue = {}
        self.__checks = {}
        self.__parent = {}
        self._application_commands: Dict[int, ApplicationCommand] = {}
        self.__route = Route.BASE = f'https://discord.com/api/v10'

    @property
    def application_commands(self):
        return list(self._application_commands.values())


    async def _invoke_app_command(self, interaction: discord.Interaction):
        if interaction.type == InteractionType.application_command:
            ctx = Context(interaction, self)
            if ctx.type is ApplicationCommandType.CHAT_INPUT:
                lookup_name = 'SLASH_' + ctx.name.upper()
            elif ctx.type is ApplicationCommandType.MESSAGE:
                lookup_name = 'MESSAGE_' + ctx.name.replace(' ', '_').upper()
            elif ctx.type is ApplicationCommandType.USER:
                lookup_name = 'USER_' + ctx.name.replace(' ', '_').upper()
            else:
                raise TypeError(f'Unknown command type: {ctx.type}')
            try:
                func = self._connection.hooks[lookup_name]
                check = self.__checks.get(func.__name__)
                if check:
                    try:
                        is_checked = await check(ctx)
                    except Exception as e:
                        raise CheckFailure('Check failed.')
                    if is_checked:
                        try:
                            await self._connection.call_hooks(lookup_name, self.__parent[lookup_name], ctx)
                        except Exception:
                            raise ApplicationCommandError(f'Application Command `{ctx.name}` encountered an error.')
                else:
                    try:
                        await self._connection.call_hooks(lookup_name, self.__parent[lookup_name], ctx)
                    except Exception:
                        raise ApplicationCommandError(f'Application Command `{ctx.name}` encountered an error.')
            except KeyError:
                raise CommandNotImplemented(f'Application Command `{ctx.name}` is not implemented.')
            except Exception as e:
                handler = self._connection.hooks.get('on_command_error')
                if handler:
                    await handler(self.__parent['handler'], ctx, e)
                    return
                print(f'Ignoring exception while invoking command `{ctx.name}`\n', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


    def _walk_app_commands(self, cog: Cog):

        for name, job in cog.__mapped_checks__.items():
            if asyncio.iscoroutinefunction(job):
                self.__checks[name] = job
            else:
                raise NonCoroutine(f'Job function `{name}` must be a coroutine.')

        for lookup_name, data in cog.__mapped_container__.items():
            self.__parent[lookup_name] = data['parent']
            method = cog.__method_container__[lookup_name]
            if asyncio.iscoroutinefunction(method):
                self.__queue[lookup_name] = (data['object'], data['guild_id'])
                self._connection.hooks[lookup_name] = method
                error_handler = cog.__error_listener__.get('callable')
                if error_handler:
                    if asyncio.iscoroutinefunction(error_handler):
                        self._connection.hooks[error_handler.__name__] = error_handler
                        self.__parent['handler'] = cog.__error_listener__.get('parent')
                    else:
                        raise NonCoroutine(f'listener `{error_handler.__name__}` must be a coroutine function')
            else:
                raise NonCoroutine(f'`{method.__name__}` must be a coroutine function')

    def add_application_cog(self, cog: Cog):
        self._walk_app_commands(cog)

    async def sync_current_commands(self):
        for command, guild_id in self.__queue.values():
            if guild_id:
                route = Route('POST', f'/applications/{self.application_id}/guilds/{guild_id}/commands')
                resp = await self.http.request(route, json=command.to_dict())
                if command.overwrites:
                    perm_route = Route(
                        'PUT',
                        f'/applications/{self.application_id}/guilds/{guild_id}/commands/{resp.get("id")}/permissions')
                    perms = await self.http.request(perm_route, json=command.overwrites)
                    resp['permissions'] = perms
            else:
                route = Route('POST', f'/applications/{self.application_id}/commands')
                resp = await self.http.request(route, json=command.to_dict())

            apc = ApplicationCommand(resp, self)
            self._application_commands[apc.id] = apc

    async def sync_global_commands(self):
        route = Route('GET', f'/applications/{self.application_id}/commands')
        resp = await self.http.request(route)
        for data in resp:
            cmd = ApplicationCommand(data, self)
            self._application_commands[cmd.id] = cmd

    async def sync_guild_commands(self, guild: discord.Guild):
        route = Route('GET', f'/applications/{self.application_id}/guilds/{guild.id}/commands')
        resp = await self.http.request(route)
        for data in resp:
            cmd = ApplicationCommand(data, self)
            self._application_commands[cmd.id] = cmd

    async def fetch_application_command(self, command_id: int, guild_id: int = None):
        if guild_id:
            route = Route('GET', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('GET', f'/applications/{self.application_id}/commands/{command_id}')
        resp = await self.http.request(route)
        return ApplicationCommand(resp, self)

    def get_application_command(self, command_id: int):
        return self._application_commands.get(command_id)

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
        cmd = ApplicationCommand(resp, self)
        self._application_commands[cmd.id] = cmd
        return cmd

    async def update_slash_permission(self, guild_id: int, command_id: int, overwrites: [Overwrite]):
        payload = [perm.to_dict() for perm in overwrites]
        route = Route('PATCH',
                      f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}/permissions')
        return await self.http.request(route, json=payload)


    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.add_listener(self._invoke_app_command, 'on_interaction')
        await self.login(token)
        app_info = await self.application_info()
        self._connection.application_id = app_info.id
        await self.sync_global_commands()
        await self.sync_current_commands()
        await self.connect(reconnect=reconnect)
