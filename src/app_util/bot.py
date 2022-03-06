from __future__ import annotations
import sys
import discord
import asyncio
import traceback
from .errors import *
from .cog import Cog
from .http_s import *
from .input_chat import SlashCommand
from .input_user import UserCommand
from .input_msg import MessageCommand
from .app import Overwrite
from discord.http import Route
from .context import Context
from .enums import ApplicationCommandType
from .core import ApplicationCommand
from .parser import _build_prams, _build_qual, _build_ctx_menu_arg
from discord.ext import commands
from discord.http import Route
from discord.enums import InteractionType
from typing import Callable, Optional, Any, Union, List, Dict, Tuple


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
        self._aux = {}
        self.__jobs = {}
        self._queue = {}
        self._application_commands: Dict[int, ApplicationCommand] = {}
        self.__route = Route.BASE = f'https://discord.com/api/v10'

    @property
    def application_commands(self):
        return list(self._application_commands.values())


    async def _invoke_app_command(self, interaction: discord.Interaction):
        if interaction.type == InteractionType.application_command:
            c = Context(self, interaction)
            qual = _build_qual(c)
            try:
                try:
                    cog = self._aux[qual]
                except KeyError:
                    raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.')
                job = self.__jobs.get(qual)
                func = self._connection.hooks[qual]
                if job:
                    try:
                        is_done = await job(c)
                    except Exception as e:
                        raise JobFailure(f'Job named `{job.__name__}` raised an exception: ({e})')
                    if is_done:
                        if c.type is ApplicationCommandType.CHAT_INPUT:
                            args, kwargs = _build_prams(c._parsed_options, func)
                            await self._connection.call_hooks(qual, cog, c, *args, **kwargs)
                        else:
                            arg = _build_ctx_menu_arg(c)
                            await self._connection.call_hooks(qual, cog, c, arg)
                else:
                    if c.type is ApplicationCommandType.CHAT_INPUT:
                        args, kwargs = _build_prams(c._parsed_options, func)
                        await self._connection.call_hooks(qual, cog, c, *args, **kwargs)
                    else:
                        arg = _build_ctx_menu_arg(c)
                        await self._connection.call_hooks(qual, cog, c, arg)
            except Exception as e:
                eh = self._connection.hooks.get('on_command_error')
                if eh:
                    await eh(c, e)
                    return
                print(f'Ignoring exception while invoking application command `{c!r}`\n', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


    def _walk_app_commands(self, cog: Cog):

        for name, job in cog.__jobs__.items():
            if asyncio.iscoroutinefunction(job):
                self.__jobs[name] = job
            else:
                raise NonCoroutine(f'Job function `{name}` must be a coroutine.')

        for qual, data in cog.__commands__.items():
            apc, guild_id = data
            self._aux[qual] = cog.__this__
            hook = cog.__methods__[qual]
            if asyncio.iscoroutinefunction(hook):
                self._queue[qual] = apc, guild_id
                self._connection.hooks[qual] = hook
                eh = cog.__listener__
                if eh:
                    if asyncio.iscoroutinefunction(eh):
                        self._connection.hooks[eh.__name__] = eh
                        self._aux['exec'] = cog.__this__
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
        for command, guild_id in self._queue.values():
            if guild_id:
                data = await post_command(self, command, guild_id)
                if command.overwrites:
                    perms = await put_overwrites(self, data['id'], guild_id, command.overwrites)
                    data['permissions'] = {guild_id: {int(p['id']): p['permission'] for p in perms['permissions']}}
                else:
                    try:
                        perms = await fetch_overwrites(self, data['id'], guild_id)
                    except discord.errors.NotFound:
                        pass
                    else:
                        data['permissions'] = {guild_id: perms['permissions']}
            else:
                data = await post_command(self, command)

            command_id = int(data['id'])

            self._application_commands[command_id] = ApplicationCommand(self, data)


    async def sync_global_commands(self):
        """
        Syncs the global commands of the application.
        It does this automatically when the bot is ready.
        :return: None
        """
        data_arr = await fetch_global_commands(self)
        for data in data_arr:
            command = ApplicationCommand(self, data)
            self._application_commands[command.id] = command

    async def sync_for(self, guild: discord.Guild):
        """
        Automatically sync all commands for a specific guild.
        :param guild: the guild to sync commands for
        :return: None
        """
        data_arr = await fetch_guild_commands(self, guild.id)
        for data in data_arr:
            command = ApplicationCommand(self, data)
            client._application_commands[command.id] = command

    async def fetch_command(self, command_id: int, guild_id: int = None):
        """
        Fetch an application command by its ID.
        :param command_id: the command id to fetch
        :param guild_id: the guild id where the command is located
        :return: ApplicationCommand
        """
        return await fetch_any_command(self, command_id, guild_id)

    def get_application_command(self, command_id: int):
        return self._application_commands.get(command_id)

    async def _sync_overwrites(self):
        for guild in self.guilds:
            guild_id = guild.id
            try:
                resp = await fetch_guild_commands(self, guild_id)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                pass
            else:
                for data in resp:
                    if int(data['id']) not in self._application_commands:
                        apc = ApplicationCommand(self, data)
                        self._application_commands[apc.id] = apc
                        try:
                            ows = await fetch_overwrites(self, apc.id, guild_id)
                        except (discord.errors.NotFound, discord.errors.Forbidden):
                            pass
                        else:
                            apc._cache_permissions(ows, guild_id)

        guild_ids = [g.id for g in self.guilds]
        for command_id, command in self._application_commands.items():
            if not command.guild_id:
                for guild_id in guild_ids:
                    try:
                        ows = await fetch_overwrites(self, command_id, guild_id)
                    except (discord.errors.NotFound, discord.errors.Forbidden):
                        pass
                    else:
                        command._cache_permissions(ows, guild_id)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.add_listener(self._invoke_app_command, 'on_interaction')
        self.add_listener(self._sync_overwrites, 'on_ready')
        await self.login(token)
        app_info = await self.application_info()
        self._connection.application_id = app_info.id
        await self.sync_global_commands()
        await self.sync_current_commands()
        await self.connect(reconnect=reconnect)
