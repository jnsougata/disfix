from __future__ import annotations
import sys
import time
import asyncio
import traceback
from .cog import Cog
from .https import *
from .errors import *
from .context import Context
from .enums import CommandType
from .mod import ModerationRule
from discord.ext import commands
from .core import ApplicationCommand
from discord.enums import InteractionType
from typing import Callable, Optional, Any, Union, List, Dict
from .parser import _build_prams, _build_ctx_menu_param, _build_modal_prams, _build_autocomplete_prams


__all__ = ['Bot']


async def _supress_tree_error(interaction: any, error: Any):
    pass


class Bot(commands.Bot):

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
        self._checks = {}
        self._origins = {}
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
                self._origins[c.command.id]
            except KeyError:
                raise CommandNotImplemented(f'Application Command `{c!r}` is not implemented.')
            args, kwargs = _build_autocomplete_prams(c._parsed_options, auto)
            self.loop.create_task(self._automatics[c.command.id](c, *args, **kwargs))

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
                cog = self._origins[c.command.id]
            except (KeyError, AttributeError):
                print(f'CommandNotImplemented: Application Command `{c!r}` is not implemented', file=sys.stderr)
            else:
                try:
                    cog = self._origins[c.command.id]

                    if c.type is CommandType.USER:
                        h = self._connection.hooks[str(c.command.id)]
                        return await h(cog, c, c._target_user)

                    if c.type is CommandType.MESSAGE:
                        h = self._connection.hooks[str(c.command.id)]
                        return await h(cog, c, c._target_message)

                    options = c._parsed_options
                    main_handler = self._connection.hooks[str(c.command.id)]
                    check = self._checks.get(c.command.id)
                    on_invoke = self._connection.hooks.get('on_app_command')
                    before_invoke_job = self.__before_invoke_jobs.get(c.command.id)
                    after_invoke_job = self.__after_invoke_jobs.get(c.command.id)

                    if on_invoke:
                        self.loop.create_task(on_invoke(cog, c))
                    if check is not None:
                        try:
                            done = await check(c)
                        except Exception as e:
                            raise CheckFailure(f'Check `{check.__name__}` raised an exception: ({e})')
                        else:
                            if type(done) is not bool:
                                raise CheckFailure(f'Check `{check.__name__}` should return a boolean.')
                            if done:
                                if before_invoke_job:
                                    self.loop.create_task(before_invoke_job(c))

                                main_options = {k: v for k, v in options.items() if not k.startswith("*")}
                                args, kwargs = _build_prams(main_options, main_handler)
                                self.loop.create_task(main_handler(cog, c, *args, **kwargs))

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

                        main_options = {k: v for k, v in options.items() if not k.startswith("*")}
                        args, kwargs = _build_prams(main_options, main_handler)
                        self.loop.create_task(main_handler(cog, c, *args, **kwargs))

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

        for name, method in cog.__listeners__.items():
            if asyncio.iscoroutinefunction(method):
                self._connection.hooks[name] = method
            else:
                raise NonCoroutine(f'Listener `{name}` must be a coroutine function')

        for custom_id, struct in cog.__container__.items():
            origin = struct['origin']
            cmd = struct['command']['object']
            check = struct['command']['check']
            subcommands = struct['subcommands']
            method = struct['command']['method']
            groupcommands = struct['groupcommands']
            perms = struct['command']['permissions']
            guild_id = struct['command']['guild_id']
            auto = struct['command']['autocompletes']
            after_invoke = struct['command']['after_invoke']
            before_invoke = struct['command']['before_invoke']

            if not asyncio.iscoroutinefunction(method):
                raise NonCoroutine(f'Application command handler `{method.__name__}` must be a coroutine function')

            if auto:
                if not asyncio.iscoroutinefunction(auto):
                    raise NonCoroutine(f'Autocomplete function `{auto.__name__}` must be a coroutine.')
                self._automatics[custom_id] = auto

            if check:
                if not asyncio.iscoroutinefunction(check):
                    raise NonCoroutine(f'Check function `{check.__name__}` must be a coroutine.')
                self._checks[custom_id] = check

            if before_invoke:
                if not asyncio.iscoroutinefunction(before_invoke):
                    raise NonCoroutine(f'Before invoke function `{before_invoke.__name__}` must be a coroutine.')
                self.__before_invoke_jobs[custom_id] = before_invoke

            if after_invoke:
                if not asyncio.iscoroutinefunction(after_invoke):
                    raise NonCoroutine(f'After invoke function `{after_invoke.__name__}` must be a coroutine.')
                self.__after_invoke_jobs[custom_id] = after_invoke

            if perms:
                cmd._inject_permission(perms)

            temp_map = {}
            if subcommands:
                for name, data in subcommands.items():
                    cmd._inject_subcommand(data['object'])
                    meth = data['method']
                    if not asyncio.iscoroutinefunction(meth):
                        raise NonCoroutine(f'Subcommand method `{meth.__name__}` must be a coroutine.')
                    temp_map[f'{custom_id}*{name}'] = meth

            self._origins[custom_id] = origin
            self._queue[custom_id] = cmd, guild_id, method, temp_map

    async def add_application_cog(self, cog: Cog) -> None:
        """
        Adds a neocord cog to the application
        """
        await self._walk_app_commands(cog)

    async def sync_current_commands(self) -> None:
        for map_hash, value in self._queue.items():
            command, guild_id, method, subcommands = value
            data = await post_command(self, command, guild_id)
            command_id = int(data['id'])
            self._connection.hooks[str(command_id)] = method
            self._connection.hooks.pop(map_hash, None)
            for alias, handler in subcommands.items():
                hook_name = str(command_id) + '*' + alias.split('*')[1]
                self._connection.hooks[hook_name] = handler
                self._connection.hooks.pop(alias, None)
            self._checks[command_id] = self._checks.pop(map_hash, None)
            self.__before_invoke_jobs[command_id] = self.__before_invoke_jobs.pop(map_hash, None)
            self.__after_invoke_jobs[command_id] = self.__after_invoke_jobs.pop(map_hash, None)
            self._origins[command_id] = self._origins.pop(map_hash, None)
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
