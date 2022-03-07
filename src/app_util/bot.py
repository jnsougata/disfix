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
from discord.ext import commands
from discord.http import Route
from discord.enums import InteractionType
from typing import Callable, Optional, Any, Union, List, Dict, Tuple
from .parser import _build_prams, _build_ctx_menu_arg, _build_modal_prams


__all__ = ['Bot']


class Bot(commands.Bot):
    """
    This is the main class that is used to run the bot.
    As this has been subclassed from the discord.ext.commands.Bot class
    so all functionality of the discord.ext.commands.Bot class is available
    """

    def __init__(
            self,
            command_prefix: Union[Callable, str],
            intents: discord.Intents = None,
            help_command: Optional[commands.HelpCommand] = None,
            description: Optional[str] = None,
            **options
    ):
        super().__init__(
            intents=intents or discord.Intents.default(),
            command_prefix=command_prefix,
            help_command=help_command or commands.DefaultHelpCommand(),
            description=description,
            **options
        )
        self._aux = {}
        self.__jobs = {}
        self._queue = {}
        self._modals = {}
        self._application_commands: Dict[int, ApplicationCommand] = {}
        self.__route = Route.BASE = f'https://discord.com/api/v10'

    @property
    def application_commands(self) -> List[ApplicationCommand]:
        """
        Returns a list of all the application commands from cache
        """
        return list(self._application_commands.values())


    async def _handle_interaction(self, interaction: discord.Interaction):
        if interaction.type is InteractionType.modal_submit:
            mc = Context(interaction)
            callback_id = interaction.data['custom_id']
            if callback_id in self._modals:
                func = self._modals.pop(callback_id)
                args, kwargs = _build_modal_prams(mc._modal_values, func)
                await func(mc, *args, **kwargs)
        if interaction.type == InteractionType.application_command:
            c = Context(interaction)
            qual = c.command._qual
            try:
                try:
                    cog = self._aux[qual]
                except KeyError:
                    raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.')
                before_invoke = self.__jobs.get(qual)
                func = self._connection.hooks[qual]
                if before_invoke:
                    try:
                        is_done = await before_invoke(c)
                    except Exception as e:
                        raise JobFailure(f'Job named `{before_invoke.__name__}` raised an exception: ({e})')
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

    def add_application_cog(self, cog: Cog) -> None:
        """
        Adds an app_util cog to the application
        """

        self._walk_app_commands(cog)

    async def sync_current_commands(self) -> None:
        """
        Synchronize the currently implemented application commands for the specified guild or global.
        This method is called automatically when the bot is ready. however, you can call it manually
        to ensure that the bot is up-to-date with the latest commands.
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


    async def sync_global_commands(self) -> None:
        """
        Syncs the global commands of the application.
        It does this automatically when the bot is ready.
        """
        data_arr = await fetch_global_commands(self)
        for data in data_arr:
            command = ApplicationCommand(self, data)
            self._application_commands[command.id] = command

    async def sync_for(self, guild: discord.Guild) -> None:
        """
        Automatically sync all commands for a specific guild.
        :param guild: the guild to sync commands for
        :return: None
        """
        data_arr = await fetch_guild_commands(self, guild.id)
        for data in data_arr:
            command = ApplicationCommand(self, data)
            client._application_commands[command.id] = command

    async def fetch_command(self, command_id: int, guild_id: int = None) -> ApplicationCommand:
        """
        Fetch an application command by its id
        """
        data = await fetch_any_command(self, command_id, guild_id)
        return ApplicationCommand(self, data)

    def get_application_command(self, command_id: int) -> ApplicationCommand:
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
        """
        Does the login and command registrations
        """
        self.add_listener(self._handle_interaction, 'on_interaction')
        self.add_listener(self._sync_overwrites, 'on_ready')
        await self.login(token)
        app_info = await self.application_info()
        self._connection.application_id = app_info.id
        await self.sync_global_commands()
        await self.sync_current_commands()
        await self.connect(reconnect=reconnect)
