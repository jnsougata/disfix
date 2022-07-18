from __future__ import annotations
import sys
import time
import asyncio
import traceback
from .errors import *
from .cog import Cog
from .https import *
from .context import Context
from discord.ext import commands
from .core import ApplicationCommand
from .enums import CommandType
from discord.enums import InteractionType
from typing import Callable, Optional, Any, Union, List, Dict
from .parser import _build_prams, _build_ctx_menu_param, _build_modal_prams, _build_autocomplete_prams
from .mod import ModerationRule


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
        return list(self._application_commands.values())  # type: ignore # linter gone nuts

    async def _handle_interaction(self, interaction: discord.Interaction):

        if interaction.type is InteractionType.autocomplete:
            c = Context(interaction)
            qualified_name = c.command.qualified_name
            try:
                self.__origins[qualified_name]
            except KeyError:
                raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.') from None
            auto = self._automatics[qualified_name]
            args, kwargs = _build_autocomplete_prams(c._parsed_options, auto)
            self.loop.create_task(auto(c, *args, **kwargs))

        if interaction.type is InteractionType.modal_submit:
            m = Context(interaction)
            target = interaction.data['custom_id']
            if target in self._modals:
                callback = self._modals.pop(target)
                args, kwargs = _build_modal_prams(m._modal_values, callback)
                await callback(m, *args, **kwargs)

        if interaction.type == InteractionType.application_command:
            c = Context(interaction)
            try:
                cog = self.__origins[c.command.id]
            except KeyError:
                print(f'CommandNotImplemented: Application Command `{c!r}` is not implemented', file=sys.stderr)
            else:
                try:
                    cog = self.__origins[c.command.id]
                    main_handler = self._connection.hooks[str(c.command.id)]
                    check = self.__checks.get(c.command.id)
                    on_invoke = self._connection.hooks.get('on_app_command')
                    before_invoke_job = self.__before_invoke_jobs.get(c.command.id)
                    after_invoke_job = self.__after_invoke_jobs.get(c.command.id)

                    if on_invoke:
                        self.loop.create_task(on_invoke(cog, c))
                    if check is not None:
                        try:
                            done = await check(c)
                        except Exception as e:
                            raise CheckFailure(f'Check named `{check.__name__}` raised an exception: ({e})')
                        else:
                            if type(done) is not bool:
                                raise CheckFailure(f'Check named `{check.__name__}` did not return a boolean.')
                            if done:
                                if before_invoke_job:
                                    self.loop.create_task(before_invoke_job(c))

                                main_options = {k: v for k, v in c._parsed_options.items() if not k.startswith("*")}
                                args, kwargs = _build_prams(main_options, main_handler)
                                self.loop.create_task(main_handler(cog, c, *args, **kwargs))

                                options = c._parsed_options
                                for name, option in options.items():
                                    if name.startswith('*'):
                                        handler = self._connection.hooks.get(f'{c.command.id}{name}')
                                        if handler:
                                            args, kwargs = _build_prams(option, handler)
                                            self.loop.create_task(handler(cog, c, *args, **kwargs))
                                    else:
                                        pass
                    else:
                        if before_invoke_job:
                            self.loop.create_task(before_invoke_job(c))

                        main_options = {k: v for k, v in c._parsed_options.items() if not k.startswith("*")}
                        args, kwargs = _build_prams(main_options, main_handler)
                        self.loop.create_task(main_handler(cog, c, *args, **kwargs))

                        options = c._parsed_options
                        for name, option in options.items():
                            if name.startswith('*'):
                                handler = self._connection.hooks.get(f'{c.command.id}{name}')
                                if handler:
                                    args, kwargs = _build_prams(option, handler)
                                    self.loop.create_task(handler(cog, c, *args, **kwargs))
                            else:
                                pass

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

        for map_hash, listener in cog.__listeners__.items():
            if asyncio.iscoroutinefunction(listener):
                self._connection.hooks[map_hash] = listener
            else:
                raise NonCoroutine(f'listener `{map_hash}` must be a coroutine function') from None

        for map_hash, auto in cog.__automatics__.items():
            if asyncio.iscoroutinefunction(auto):
                self._automatics[map_hash] = auto
            else:
                raise NonCoroutine(f'Autocomplete function `{auto.__name__}` must be a coroutine.') from None

        for map_hash, check in cog.__checks__.items():
            if asyncio.iscoroutinefunction(check):
                self.__checks[map_hash] = check
            else:
                raise NonCoroutine(f'Check function `{check.__name__}` must be a coroutine.') from None

        for map_hash, job in cog.__before_invoke__.items():
            if asyncio.iscoroutinefunction(job):
                self.__before_invoke_jobs[map_hash] = job
            else:
                raise NonCoroutine(f'Before invoke function `{job.__name__}` must be a coroutine.') from None

        for map_hash, job in cog.__after_invoke__.items():
            if asyncio.iscoroutinefunction(job):
                self.__after_invoke_jobs[map_hash] = job
            else:
                raise NonCoroutine(f'After invoke function `{job.__name__}` must be a coroutine.') from None

        for mapping_hash, data in cog.__commands__.items():
            app_command, guild_id = data
            self.__origins[mapping_hash] = cog.__self__
            handler = cog.__methods__[mapping_hash]
            perms = cog.__permissions__.get(mapping_hash)
            app_command._inject_permission(perms)
            sub_command_map = {}
            for alias, sub_handler, subcommand in cog.__subcommands__.values():
                if asyncio.iscoroutinefunction(sub_handler):
                    if app_command.type == CommandType.SLASH and alias == f'{mapping_hash}*{subcommand.name}':
                        app_command._inject_subcommand(subcommand)
                        sub_command_map[alias] = sub_handler
                else:
                    raise NonCoroutine(f'`{sub_handler.__name__}` must be a coroutine function') from None
            if asyncio.iscoroutinefunction(handler):
                self._connection.hooks[mapping_hash] = handler
                self._queue[mapping_hash] = app_command, guild_id, handler, sub_command_map
            else:
                raise NonCoroutine(f'`{handler.__name__}` must be a coroutine function') from None

    async def add_application_cog(self, cog: Cog) -> None:
        """
        Adds a neocord cog to the application
        """
        await self._walk_app_commands(cog)

    async def sync_current_commands(self) -> None:
        """
        Synchronize the currently implemented application commands for the specified guild or global.
        This method is called automatically when the bot is ready. however, you can call it manually
        to ensure that the bot is up-to-date with the latest commands.
        """
        for map_hash, value in self._queue.items():
            data = await post_command(self, value[0], value[1])
            command_id = int(data['id'])
            self._connection.hooks[str(command_id)] = value[2]
            self._connection.hooks.pop(map_hash, None)
            for alias, sub_handler in value[3].items():
                hook_name = str(command_id) + '*' + alias.split('*')[1]
                self._connection.hooks[hook_name] = sub_handler
                self._connection.hooks.pop(alias, None)
            self.__checks[command_id] = self.__checks.pop(map_hash, None)
            self.__before_invoke_jobs[command_id] = self.__before_invoke_jobs.pop(map_hash, None)
            self.__after_invoke_jobs[command_id] = self.__after_invoke_jobs.pop(map_hash, None)
            self.__origins[command_id] = self.__origins.pop(map_hash, None)
            self._application_commands[command_id] = ApplicationCommand(self, data)

    async def sync_global_commands(self) -> None:
        """
        Syncs the global commands of the application.
        It does this automatically when the bot is ready.
        """
        payloads = await fetch_global_commands(self)
        for data in payloads:
            command = ApplicationCommand(self, data)
            self._application_commands[command.id] = command

    async def sync_for(self, guild: discord.Guild) -> None:
        """
        Automatically sync all commands for a specific guild.
        """
        cmd_ls = await fetch_guild_commands(self, guild.id)
        for cmd in cmd_ls:
            command = ApplicationCommand(self, cmd)
            self._application_commands[command.id] = command

    async def fetch_command(self, command_id: int, guild_id: int = None) -> ApplicationCommand:
        """
        Fetch an application command by its id
        """
        data = await fetch_any_command(self, command_id, guild_id)
        return ApplicationCommand(self, data)

    def get_application_command(self, command_id: int) -> ApplicationCommand:
        return self._application_commands.get(command_id)

    async def create_rule(self, rule: ModerationRule, guild_id: int):
        await create_auto_mod_rule(self, rule.to_dict(), guild_id)

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
