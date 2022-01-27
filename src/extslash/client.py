import sys
import discord
import json
import asyncio
import traceback
from .type import Slash
from dataclasses import dataclass
from discord.http import Route
from functools import wraps
from discord.utils import _to_json
from .context import SlashContext
from .converter import BaseInteraction, BaseInteractionData, BaseSlashOption
from typing import Callable, Optional, Any, Union, List, Sequence, Iterable


class SlashBot(discord.ext.commands.Bot):
    def __init__(
            self,
            prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[discord.ext.commands.HelpCommand] = None,
            guild_id: Optional[int] = None,
    ):
        super().__init__(
            command_prefix=prefix,
            intents=intents,
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

    async def _register(self):
        await self.wait_until_ready()
        if self.guild_id and not self._check:
            self._check = True
            for command in self._reg_queue:
                route = Route('POST', f'/applications/{self.user.id}/guilds/{self.guild_id}/commands')
                self.slash_commands[command['name']] = await self.http.request(route, json=command)

    async def _call_to(self, ctx: SlashContext):
        func_name = ctx.name
        pool = self._command_pool
        func = pool.get(func_name)
        if func:
            try:
                await func(ctx)
            except Exception:
                traceback.print_exception(*sys.exc_info())

    async def on_socket_raw_receive(self, payload: Any):
        asyncio.ensure_future(self._register())
        response = json.loads(payload)
        if response.get('t') == 'INTERACTION_CREATE':
            interaction = BaseInteraction(**response.get('d'))
            if interaction.type == 2:
                await self._call_to(SlashContext(interaction, self))
