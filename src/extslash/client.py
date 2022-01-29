import sys
import discord
import json
import asyncio
import traceback
from .builder import SlashCommand
from dataclasses import dataclass
from discord.http import Route
from functools import wraps
from discord.utils import _to_json
from .interaction import ApplicationCommand
from .core import BaseInteraction, BaseInteractionData, BaseSlashOption
from typing import Callable, Optional, Any, Union, List, Sequence, Iterable
import importlib
from discord.ext.commands import Bot


class ExtendedClient(Bot):
    def __init__(
            self,
            command_prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[discord.ext.commands.HelpCommand] = None,
    ):
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            enable_debug_events=True,
            help_command=help_command,
        )
        self._check = False
        self._command_pool = {}
        self._reg_queue = []
        self.slash_commands = {}

    def slash_command(self, command: SlashCommand, guild_id: Optional[int] = None):
        self._reg_queue.append((guild_id, command.object))

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._command_pool[command.object["name"]] = wrapper()
        return decorator

    async def _register(self):
        await self.wait_until_ready()
        global_route = Route('POST', f'/applications/{self.user.id}/commands')
        if not self._check:
            self._check = True
            for guild_id, command in self._reg_queue:
                if guild_id:
                    route = Route('POST', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
                else:
                    route = global_route
                self.slash_commands[command['name']] = await self.http.request(route, json=command)

    async def _call_to(self, interaction: ApplicationCommand):
        func_name = interaction.name
        pool = self._command_pool
        func = pool.get(func_name)
        if func:
            try:
                await func(interaction)
            except Exception:
                traceback.print_exc()

    async def on_socket_raw_receive(self, payload: Any):
        asyncio.ensure_future(self._register())
        response = json.loads(payload)
        if response.get('t') == 'INTERACTION_CREATE':
            interaction = BaseInteraction(**response.get('d'))
            if interaction.type == 2:
                await self._call_to(ApplicationCommand(interaction, self))

    def add_slash(self, command: SlashCommand, function: Callable, guild_id:  Optional[int] = None):
        self._reg_queue.append((guild_id, command.object))
        self._command_pool[command.name] = function

    async def get_guild_application_commands(self, guild_id: int):
        await self.wait_until_ready()
        route = Route('GET', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
        return await self.http.request(route)

    async def get_global_application_commands(self):
        await self.wait_until_ready()
        route = Route('GET', f'/applications/{self.user.id}/commands')
        return await self.http.request(route)
