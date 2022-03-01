import sys
import discord
import json
import asyncio
import traceback
from .errors import *
from .cog import Cog
from .chat_input import SlashCommand
from .user_input import UserCommand
from .msg_input import MessageCommand
from .app import Overwrite
from discord.http import Route
from .context import Context
from .enums import ApplicationCommandType
from .core import ApplicationCommand, BaseOverwrite
from .parser import _build_prams, _build_qual
from typing import Callable, Optional, Any, Union, List, Dict, Tuple
from discord.ext import commands
from discord.http import Route
from discord.enums import InteractionType


__all__ = ['Bot']


class Bot(commands.Bot):

    def __init__(
            self,
            command_prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[commands.HelpCommand] = commands.DefaultHelpCommand(),
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
            qual = _build_qual(c)
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
                        raise JobFailure(f'Job named `{job.__name__}` raised an exception: ({e})')
                    if is_done:
                        await self._connection.call_hooks(qual, cog, c, *args, **kwargs)
                else:
                    await self._connection.call_hooks(qual, cog, c, *args, **kwargs)
            except Exception as e:
                handler = self._connection.hooks.get('on_command_error')
                if handler:
                    await handler(self.__aux['handler'], c, e)
                    return
                print(f'Ignoring exception while invoking application command `{c!r}`\n', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


    def _walk_app_commands(self, cog: Cog):

        for name, job in cog.__mapped_jobs__.items():
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
        """
        Synchronize the currently implemented application commands for the specified guild or global.
        This method is called automatically when the bot is ready. however, you can call it manually
        to ensure that the bot is up-to-date with the latest commands.
        :return: None
        """
        for command, guild_id in self.__queue.values():
            if guild_id:
                route = Route('POST', f'/applications/{self.application_id}/guilds/{guild_id}/commands')
                resp = await self.http.request(route, json=command.to_dict())
                command_id = int(resp['id'])
                if command.overwrites:
                    r = Route(
                        'PUT',
                        f'/applications/{self.application_id}/guilds/{guild_id}/commands/{resp["id"]}/permissions')
                    perms = await self.http.request(r, json=command.overwrites)
                    resp['permissions'] = {guild_id: {int(p['id']): p['permission'] for p in perms['permissions']}}
                else:
                    try:
                        x = await self.__sync_permissions(command_id, guild_id)
                    except discord.errors.NotFound:
                        pass
                    else:
                        resp['permissions'] = {
                            guild_id: {int(p['id']): p['permission'] for p in x['permissions']}
                        }
            else:
                route = Route('POST', f'/applications/{self.application_id}/commands')
                resp = await self.http.request(route, json=command.to_dict())
            self._application_commands[int(resp['id'])] = ApplicationCommand(self, resp)

    async def __sync_permissions(self, command_id: int, guild_id: int):
        r = Route('GET', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}/permissions')
        return await self.http.request(r)

    async def sync_global_commands(self):
        """
        Syncs the global commands of the application.
        It does this automatically when the bot is ready.
        :return: None
        """
        r = Route('GET', f'/applications/{self.application_id}/commands')
        resp = await self.http.request(r)
        for data in resp:
            apc = ApplicationCommand(self, data)
            self._application_commands[apc.id] = apc

    async def sync_for(self, guild: discord.Guild):
        """
        Automatically sync all commands for a specific guild.
        :param guild: the guild to sync commands for
        :return: None
        """
        r = Route('GET', f'/applications/{self.application_id}/guilds/{guild.id}/commands')
        resp = await self.http.request(r)
        for data in resp:
            apc = ApplicationCommand(self, data)
            self._application_commands[apc.id] = apc

    async def fetch_command(self, command_id: int, guild_id: int = None):
        """
        Fetch an application command by its ID.
        :param command_id: the command id to fetch
        :param guild_id: the guild id where the command is located
        :return: ApplicationCommand
        """
        if guild_id:
            route = Route('GET', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('GET', f'/applications/{self.application_id}/commands/{command_id}')
        resp = await self.http.request(route)
        return ApplicationCommand(self, resp)

    def get_application_command(self, command_id: int):
        return self._application_commands.get(command_id)


    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.add_listener(self._invoke_app_command, 'on_interaction')
        await self.login(token)
        app_info = await self.application_info()
        self._connection.application_id = app_info.id
        await self.sync_global_commands()
        await self.sync_current_commands()
        await self.connect(reconnect=reconnect)
