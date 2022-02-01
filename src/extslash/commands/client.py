import discord
import json
import asyncio
import traceback
from ..builder import SlashCommand
from discord.http import Route
from functools import wraps
from .context import ApplicationContext
from .base import Interaction, BaseAppCommand
from typing import Callable, Optional, Any, Union
from discord.ext.commands import Bot
from importlib.machinery import SourceFileLoader
from .cog import SlashCog
from .errors import *


class Client(Bot):
    def __init__(
            self,
            command_prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[discord.ext.commands.HelpCommand] = None,
    ):
        super().__init__(
            intents=intents,
            command_prefix=command_prefix,
            enable_debug_events=True,
            help_command=help_command,
        )
        self._check = False
        self._reg_queue = []
        self._command_pool = {}
        self._slash_commands = {}

    def slash_command(self, command: SlashCommand, guild_id: Optional[int] = None):
        self._reg_queue.append((guild_id, command.to_dict()))

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._command_pool[command.name] = wrapper()
        return decorator

    async def _register(self):
        await self.wait_until_ready()
        if not self._check:
            self._check = True
            for guild_id, payload in self._reg_queue:
                if guild_id:
                    route = Route('POST', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
                else:
                    route = Route('POST', f'/applications/{self.user.id}/commands')

                resp = await self.http.request(route, json=payload)
                self._slash_commands[payload.get("name")] = resp

                prompt = f'[{"GLOBAL" if not guild_id else "GUILD"}] registered /{payload.get("name")}'
                print(f'{prompt} ... ID: {resp.get("id")} ... Guild: {guild_id if guild_id else "NA"}')

    async def _invoke(self, appctx: ApplicationContext):
        cmd = self._command_pool.get(appctx.name)
        if cmd:
            try:
                await cmd(appctx)
            except Exception:
                traceback.print_exc()

    async def on_socket_raw_receive(self, payload: Any):
        asyncio.ensure_future(self._register())
        response = json.loads(payload)
        if response.get('t') == 'INTERACTION_CREATE':
            interaction = Interaction(**response.get('d'))
            if interaction.type == 2:
                await self._invoke(ApplicationContext(interaction, self))

    def add_slash_cog(self, cog: SlashCog, guild_id:  Optional[int] = None):
        cog_name = cog.__class__.__name__
        if isinstance(cog, SlashCog):
            reg_obj = cog.register()
            cmd = cog.command
            if asyncio.iscoroutinefunction(cmd):
                self._reg_queue.append((guild_id, reg_obj.to_dict()))
                self._command_pool[reg_obj.name] = cmd
            else:
                raise TypeError(f'Command inside cog `{cog_name}` must be a coroutine')
        else:
            raise TypeError(f'Custom cog `{cog_name}` must be a subclass of SlashCog')

    def load_slash_extension(self, name: str):
        fp = name.replace('.', '/') + '.py'
        try:
            module = SourceFileLoader('setup', fp).load_module()
        except FileNotFoundError:
            raise CogNotFound(f'Slash extension not found at {fp}')
        except AttributeError:
            raise SetupNotFound(f'Setup function not found in {fp}')
        else:
            try:
                module.setup(self)
            except TypeError:
                raise InvalidCog('Custom cog must have methods `register` and `command [coro]`')

    async def fetch_global_slash_commands(self):
        await self.wait_until_ready()
        route = Route('GET', f'/applications/{self.user.id}/commands')
        resp = await self.http.request(route)
        return [BaseAppCommand(**cmd) for cmd in resp]

    async def fetch_guild_slash_commands(self, guild_id: int):
        await self.wait_until_ready()
        route = Route('GET', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
        resp = await self.http.request(route)
        return [BaseAppCommand(**cmd) for cmd in resp]

    async def fetch_slash_command(self, command_id: int, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('GET', f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('GET', f'/applications/{self.user.id}/commands/{command_id}')

        resp = await self.http.request(route)

        return BaseAppCommand(**resp)

    def get_slash_commands(self):
        return [BaseAppCommand(**cmd) for cmd in self._slash_commands.values()]

    async def delete_slash_command(self, command_id: int, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('DELETE', f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('DELETE', f'/applications/{self.user.id}/commands/{command_id}')

        await self.http.request(route)
