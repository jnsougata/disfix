import sys
import discord
import json
import asyncio
import traceback
from .errors import *
from .cog import Cog
from .parser import _build_prams
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
        self.__aux = {}
        self.__jobs = {}
        self.__queue = {}
        self._application_commands: Dict[int, ApplicationCommand] = {}
        self.__route = Route.BASE = f'https://discord.com/api/v10'

    @property
    def application_commands(self):
        return list(self._application_commands.values())


    async def _invoke_app_command(self, interaction: discord.Interaction):
        if interaction.type == InteractionType.application_command:
            c = Context(interaction, self)
            if c.type is ApplicationCommandType.CHAT_INPUT:
                qual = 'SLASH_' + c.name.upper()
            elif c.type is ApplicationCommandType.MESSAGE:
                qual = 'MESSAGE_' + c.name.replace(' ', '_').upper()
            elif c.type is ApplicationCommandType.USER:
                qual = 'USER_' + c.name.replace(' ', '_').upper()
            else:
                raise TypeError(f'Unknown command type: {c.type}')
            try:
                try:
                    cog = self.__aux[qual]
                    func = self._connection.hooks[qual]
                except KeyError:
                    raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.')
                args, kwargs = _build_prams(c.options, func)
                job = self.__jobs.get(func.__name__)
                if job:
                    try:
                        is_done = await job(c)
                    except Exception as e:
                        raise JobFailure(f'Before invoke job named `{job.__name__}` raised an exception: ({e})')
                    if is_done:
                        try:
                            await self._connection.call_hooks(qual, cog, c, *args, **kwargs)
                        except Exception as e:
                            raise ApplicationCommandError(f'Application Command `{c!r}` raised an exception: ({e})')
                else:
                    try:
                        await self._connection.call_hooks(qual, cog, c, *args, **kwargs)
                    except Exception as e:
                        raise ApplicationCommandError(f'Application Command `{c!r}` raised an exception: ({e})')
            except Exception as e:
                handler = self._connection.hooks.get('on_command_error')
                if handler:
                    await handler(self.__aux['handler'], c, e)
                    return
                print(f'Ignoring exception while invoking command `{c!r}`\n', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


    def _walk_app_commands(self, cog: Cog):

        for name, job in cog.__mapped_checks__.items():
            if asyncio.iscoroutinefunction(job):
                self.__jobs[name] = job
            else:
                raise NonCoroutine(f'Job function `{name}` must be a coroutine.')

        for qual, data in cog.__mapped_container__.items():
            self.__aux[qual] = data['parent']
            m = cog.__method_container__[qual]
            if asyncio.iscoroutinefunction(m):
                self.__queue[qual] = (data['object'], data['guild_id'])
                self._connection.hooks[qual] = m
                eh = cog.__error_listener__.get('callable')
                if eh:
                    if asyncio.iscoroutinefunction(eh):
                        self._connection.hooks[eh.__name__] = eh
                        self.__aux['handler'] = cog.__error_listener__.get('parent')
                    else:
                        raise NonCoroutine(f'listener `{eh.__name__}` must be a coroutine function')
            else:
                raise NonCoroutine(f'`{m.__name__}` must be a coroutine function')

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
