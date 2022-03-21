from __future__ import annotations
import sys
import discord
import asyncio
import traceback
from .errors import *
from .cog import Cog
from .http_s import *
from .app import Overwrite
from discord.http import Route
from .context import Context
from discord.ext import commands
from .core import ApplicationCommand
from .input_chat import SlashCommand
from .input_user import UserCommand
from .input_msg import MessageCommand
from .enums import ApplicationCommandType
from discord.enums import InteractionType
from typing import Callable, Optional, Any, Union, List, Dict, Tuple
from .parser import _build_prams, _build_ctx_menu_param, _build_modal_prams, _build_autocomplete_prams


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
        self._queue = {}
        self._modals = {}
        self.__checks = {}
        self._automatics = {}
        self._application_commands: Dict[int, ApplicationCommand] = {}
        self.tree.error(self.__supress)   # type: ignore


    async def __supress(self, a, b, c):
        pass

    @property
    def application_commands(self) -> List[ApplicationCommand]:
        """
        Returns a list of all the application commands from cache
        """
        return list(self._application_commands.values())


    async def _handle_interaction(self, interaction: discord.Interaction):

        if interaction.type is InteractionType.autocomplete:
            c = Context(interaction)
            qual = c.command._qual
            try:
                self._aux[qual]
            except KeyError:
                raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.')
            auto = self._automatics[qual]
            args, kwargs = _build_autocomplete_prams(c._parsed_options, auto)
            self.loop.create_task(auto(c, *args, **kwargs))

        if interaction.type is InteractionType.modal_submit:
            m = Context(interaction)
            target = interaction.data['custom_id']
            if target in self._modals:
                func = self._modals.pop(target)
                args, kwargs = _build_modal_prams(m._modal_values, func)
                self.loop.create_task(func(m, *args, **kwargs))

        if interaction.type == InteractionType.application_command:
            c = Context(interaction)
            qual = c.command._qual
            try:
                try:
                    cog = self._aux[qual]
                except KeyError:
                    raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.')
                check = self.__checks.get(qual)
                func = self._connection.hooks[qual]
                if check is not None:
                    try:
                        done = await check(c)
                    except Exception as e:
                        raise CheckFailure(f'Check named `{check.__name__}` raised an exception: ({e})')
                    if done is True:
                        if c.type is ApplicationCommandType.CHAT_INPUT:
                            args, kwargs = _build_prams(c._parsed_options, func)
                            self.loop.create_task(self._connection.call_hooks(qual, cog, c, *args, **kwargs))
                        else:
                            param = _build_ctx_menu_param(c)
                            self.loop.create_task(self._connection.call_hooks(qual, cog, c, param))
                else:
                    if c.type is ApplicationCommandType.CHAT_INPUT:
                        args, kwargs = _build_prams(c._parsed_options, func)
                        self.loop.create_task(self._connection.call_hooks(qual, cog, c, *args, **kwargs))
                    else:
                        param = _build_ctx_menu_param(c)
                        self.loop.create_task(self._connection.call_hooks(qual, cog, c, param))

            except Exception as e:
                error_handler = self._connection.hooks.get('on_command_error')
                if error_handler:
                    return self.loop.create_task(error_handler(c, e))
                print(f'Ignoring exception while invoking application command `{c!r}`\n', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

    async def _walk_app_commands(self, cog: Cog):

        for name, auto in cog.__automatics__.items():
            if asyncio.iscoroutinefunction(auto):
                self._automatics[name] = auto
            else:
                raise NonCoroutine(f'Autocomplete function `{auto.__name__}` must be a coroutine.')

        for name, check in cog.__checks__.items():
            if asyncio.iscoroutinefunction(check):
                self.__checks[name] = check
            else:
                raise NonCoroutine(f'Check function `{check.__name__}` must be a coroutine.')

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

    async def add_application_cog(self, cog: Cog) -> None:
        """
        Adds an app_util cog to the application
        """

        await self._walk_app_commands(cog)

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
        app = await self.application_info()
        self._connection.application_id = app.id
        await self.sync_global_commands()
        await self.sync_current_commands()
        await self.connect(reconnect=reconnect)
