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
from .errors import InvalidCog, CogNotFound


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
        self._command_pool = {}
        self._reg_queue = []
        self.slash_commands = {}

    def slash_command(self, command: SlashCommand, guild_id: Optional[int] = None):
        self._reg_queue.append((guild_id, command.to_dict()))

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._command_pool[command.to_dict().get('name')] = wrapper()
        return decorator

    async def _register(self):
        await self.wait_until_ready()
        if not self._check:
            self._check = True
            for guild_id, payload in self._reg_queue:
                if guild_id:
                    route = Route('POST', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
                    prompt = f'[GUILD] registered /{payload.get("name")}'
                else:
                    route = Route('POST', f'/applications/{self.user.id}/commands')
                    prompt = f'[GLOBAL] registered /{payload.get("name")}'

                resp = await self.http.request(route, json=payload)
                print(f'{prompt} ... ID: {resp.get("id")}')
                self.slash_commands[payload['name']] = resp

    async def _invoke(self, interaction: ApplicationContext):
        pool = self._command_pool
        func = pool.get(interaction.name)
        if func:
            try:
                await func(interaction)
            except Exception:
                traceback.print_exc()

    async def on_socket_raw_receive(self, payload: Any):
        asyncio.ensure_future(self._register())
        response = json.loads(payload)
        if response.get('t') == 'INTERACTION_CREATE':
            interaction = Interaction(**response.get('d'))
            if interaction.type == 2:
                await self._invoke(ApplicationContext(interaction, self))

    def load_slash(self, path: str, guild_id:  Optional[int] = None):
        src = path.replace('.', '/') + '.py'
        try:
            module = SourceFileLoader('setup', src).load_module()
        except FileNotFoundError:
            raise CogNotFound(f'Slash extension not found at {src}')
        else:
            try:
                obj = module.setup(self)
            except TypeError:
                raise InvalidCog(
                    f'Extension must be a subclass of SlashCog and must have `register` and `async command` method')
            cog_name = obj.__class__.__name__
            if isinstance(obj, list):
                pass
            elif isinstance(obj, SlashCog):
                slash_obj = obj.register()
                slash_cmd = obj.command
                if asyncio.iscoroutinefunction(slash_cmd):
                    self._reg_queue.append((guild_id, slash_obj.to_dict()))
                    self._command_pool[slash_obj.name] = slash_cmd
                else:
                    raise TypeError(f'Command inside cog `{cog_name}` must be a coroutine')

    async def fetch_application_commands(self, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('GET', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
        else:
            route = Route('GET', f'/applications/{self.user.id}/commands')
        resp = await self.http.request(route)
        return [BaseAppCommand(**cmd) for cmd in resp]

    async def delete_application_command(self, command_id: int, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('DELETE', f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('DELETE', f'/applications/{self.user.id}/commands/{command_id}')
        try:
            await self.http.request(route)
        except discord.errors.NotFound:
            print(f'[ERROR] /command with (ID:{command_id}) and (GUILD:{guild_id}) not found')
