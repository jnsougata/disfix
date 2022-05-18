from __future__ import annotations
import sys
import time
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


async def _supress_tree_error(interaction: any, error: Any):
    pass


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
        self._queue = {}
        self._modals = {}
        self.__checks = {}
        self.__origins = {}
        self._automatics = {}
        self.__after_invoke_jobs = {}
        self.__before_invoke_jobs = {}
        self.tree.error(_supress_tree_error)
        self._application_commands: Dict[int, ApplicationCommand] = {}

    @property
    def application_commands(self) -> List[ApplicationCommand]:
        """
        Returns a list of all the application commands from cache
        """
        return list(self._application_commands.values())

    async def _handle_interaction(self, interaction: discord.Interaction):

        if interaction.type is InteractionType.autocomplete:
            c = Context(interaction)
            qualified_name = c.command.qualified_name
            try:
                self.__origins[qualified_name]
            except KeyError:
                raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.')
            auto = self._automatics[qualified_name]
            args, kwargs = _build_autocomplete_prams(c._parsed_options, auto)
            self.loop.create_task(auto(c, *args, **kwargs))

        if interaction.type is InteractionType.modal_submit:
            m = Context(interaction)
            target = interaction.data['custom_id']
            if target in self._modals:
                on_submit = self._modals.pop(target)
                args, kwargs = _build_modal_prams(m._modal_values, on_submit)
                await on_submit(m, *args, **kwargs)

        if interaction.type == InteractionType.application_command:
            c = Context(interaction)
            qualified_name = c.command.qualified_name
            try:
                cog = self.__origins[qualified_name]
            except KeyError:
                print(f'CommandNotImplemented: Application Command `{c!r}` is not implemented', file=sys.stderr)
            else:
                try:
                    check = self.__checks.get(qualified_name)
                    on_invoke = self._connection.hooks.get('on_app_command')
                    before_invoke_job = self.__before_invoke_jobs.get(qualified_name)
                    after_invoke_job = self.__after_invoke_jobs.get(qualified_name)
                    hooked_method = self._connection.hooks[qualified_name]
                    exec_start = time.perf_counter()
                    if on_invoke:
                        self.loop.create_task(on_invoke(cog, c))
                    if check is not None:
                        try:
                            done = await check(c)
                        except Exception as e:
                            raise CheckFailure(f'Check named `{check.__name__}` raised an exception: ({e})')
                        else:
                            if type(done) is not bool:
                                raise ReturnNotBoolean('Check functions must return a boolean.')
                            elif done is True:
                                if before_invoke_job:
                                    self.loop.create_task(before_invoke_job(c))
                                if c.type is ApplicationCommandType.CHAT_INPUT:
                                    args, kwargs = _build_prams(c._parsed_options, hooked_method)
                                    await self._connection.call_hooks(qualified_name, cog, c, *args, **kwargs)
                                else:
                                    param = _build_ctx_menu_param(c)
                                    await self._connection.call_hooks(qualified_name, cog, c, param)
                    else:
                        if before_invoke_job:
                            self.loop.create_task(before_invoke_job(c))

                        if c.type is ApplicationCommandType.CHAT_INPUT:
                            args, kwargs = _build_prams(c._parsed_options, hooked_method)
                            await self._connection.call_hooks(qualified_name, cog, c, *args, **kwargs)
                        else:
                            param = _build_ctx_menu_param(c)
                            await self._connection.call_hooks(qualified_name, cog, c, param)
                    exec_end = time.perf_counter()
                    c.time_taken = exec_end - exec_start
                except Exception as e:
                    error_handler = self._connection.hooks.get('on_app_command_error')
                    if error_handler:
                        self.loop.create_task(error_handler(cog, c, e))
                    else:
                        print(f'Ignoring exception while invoking application command `{c!r}`\n', file=sys.stderr)
                        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                else:
                    if after_invoke_job:
                        self.loop.create_task(after_invoke_job(c))
                    on_completion = self._connection.hooks.get('on_app_command_completion')
                    if on_completion:
                        self.loop.create_task(on_completion(cog, c))

    async def _walk_app_commands(self, cog: Cog):

        for name, listener in cog.__listeners__.items():
            if asyncio.iscoroutinefunction(listener):
                self._connection.hooks[name] = listener
            else:
                raise NonCoroutine(f'listener `{name}` must be a coroutine function')

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

        for name, job in cog.__before_invoke__.items():
            if asyncio.iscoroutinefunction(job):
                self.__before_invoke_jobs[name] = job
            else:
                raise NonCoroutine(f'Before invoke function `{job.__name__}` must be a coroutine.')

        for name, job in cog.__after_invoke__.items():
            if asyncio.iscoroutinefunction(job):
                self.__after_invoke_jobs[name] = job
            else:
                raise NonCoroutine(f'After invoke function `{job.__name__}` must be a coroutine.')

        for mapping_name, data in cog.__commands__.items():
            app_command, guild_id = data
            self.__origins[mapping_name] = cog.__self__
            meth = cog.__methods__[mapping_name]
            perms = cog.__permissions__.get(mapping_name)
            app_command.inject_permission(perms)
            if asyncio.iscoroutinefunction(meth):
                self._connection.hooks[mapping_name] = meth
                self._queue[mapping_name] = app_command, guild_id
            else:
                raise NonCoroutine(f'`{meth.__name__}` must be a coroutine function')

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

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        """
        Does the login and command registrations
        """
        self.add_listener(self._handle_interaction, 'on_interaction')
        await self.login(token)
        app = await self.application_info()
        self._connection.application_id = app.id
        await self.sync_global_commands()
        await self.sync_current_commands()
        await self.connect(reconnect=reconnect)
