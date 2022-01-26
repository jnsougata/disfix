import discord
import json
import asyncio
from .slash import Slash
from typing import Callable, Optional, Any, Union
from dataclasses import dataclass
from discord.http import Route
from functools import wraps


class Bot(discord.Client):
    def __init__(
            self,
            prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[discord.ext.commands.HelpCommand] = None,
            guild_id: Optional[int] = None,
    ):
        super().__init__(
            prefix=prefix,
            intents=discord.Intents.all(),
            enable_debug_events=True,
            help_command=help_command,
        )
        self._check = False
        self._command_pool = {}
        self._reg_queue = []
        self.guild_id = guild_id
        self.slash_commands = {}

    def slash_command(self, command: Slash):
        self._reg_queue.append(command.object)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._command_pool[command.object["name"]] = wrapper()
        return decorator

    async def on_socket_raw_receive(self, payload: Any):
        asyncio.ensure_future(self.__register())
        response = json.loads(payload)
        if response.get('t') == 'INTERACTION_CREATE':
            interaction = _BaseInteraction(**response.get('d'))
            data = _BaseInteractionData(**interaction.data)
            options = [_BaseSlashOption(**option) for option in data.options]
            #ctx = _BaseSlashContext()
            #executor = await _BaseExecutor(ctx, self._command_pool).execute()

    async def __register(self):
        await self.wait_until_ready()
        if self.guild_id and not self._check:
            self._check = True
            for command in self._reg_queue:
                route = Route('POST', f'/applications/{self.user.id}/guilds/{self.guild_id}/commands')
                self.slash_commands[command['name']] = await self.http.request(route, json=command)
                print(self.slash_commands)


@dataclass(frozen=True)
class _BaseInteraction:
    id: int
    token: str
    type: int
    data: dict
    application_id: int
    version: int
    guild_id: Union[int, str]
    channel_id: Union[int, str]
    message: Optional[dict] = None
    member: Optional[dict] = None
    user: Optional[dict] = None
    locale: Optional[str] = None
    guild_locale: Optional[str] = None


@dataclass(frozen=True)
class _BaseInteractionData:
    id: Union[int, str]
    name: str
    type: int
    resolved: dict
    custom_id: Optional[str] = None
    options: Optional[dict] = None
    component_type: Optional[int] = None
    values: Optional[list] = None
    target_id: Optional[str] = None


@dataclass(frozen=True)
class _BaseSlashOption:
    name: str
    type: int
    value: Union[str, int, float, bool]
    options: Optional[list] = None
    focused: Optional[bool] = None


class SlashContext:
    name: str
    pass


class _BaseExecutor:
    def __init__(self, context: SlashContext, pool: dict):
        self.ctx = context
        self.pool = pool

    async def execute(self):
        name = self.ctx.name
        func = self.pool.get(name)
        if func:
            try:
                await func(self.ctx)
            except Exception:
                traceback.print_exc(*sys.exc_info())
