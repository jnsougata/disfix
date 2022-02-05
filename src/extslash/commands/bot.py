import discord
import json
import asyncio
import traceback
from .errors import *
from .cog import SlashCog
from ..builder import SlashCommand, SlashPermission
from discord.http import Route
from functools import wraps
from .context import ApplicationContext
from .base import BaseAppCommand, SlashOverwrite
from typing import Callable, Optional, Any, Union
from discord.ext import commands
from discord.enums import InteractionType


__all__ = ['Bot']


class Bot(commands.Bot):

    def __init__(
            self,
            command_prefix: Union[Callable, str],
            intents: discord.Intents = discord.Intents.default(),
            help_command: Optional[discord.ext.commands.HelpCommand] = None,
            description: Optional[str] = None,
            **options
    ):
        super().__init__(
            intents=intents,
            command_prefix=command_prefix,
            help_command=help_command,
            description=description,
            **options
        )
        self._reg_queue = []
        self._slash_commands = {}  # cache not implemented

    def slash_command(self, command: SlashCommand, guild_id: Optional[int] = None):
        """
        Decorator for registering a slash command
        :param command:
        :param guild_id:
        :return:
        """
        self._reg_queue.append((guild_id, command))

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._connection.hooks[command.name] = wrapper()
        return decorator

    async def _invoke_slash(self, interaction: discord.Interaction):
        if interaction.type == InteractionType.application_command:
            ctx = ApplicationContext(interaction, self)
            try:
                await self._connection.call_hooks(ctx.command_name, ctx)
            except Exception as exc:
                await self._connection.call_hooks(f'{ctx.command_name}_on_error', ctx, exc)

    def add_slash_cog(self, cog: SlashCog, guild_id:  Optional[int] = None):
        cog_name = cog.__class__.__name__
        if isinstance(cog, SlashCog):
            slash_obj = cog.register()
            cmd = cog.command
            cmd_error = cog.on_error
            if asyncio.iscoroutinefunction(cmd):
                self._reg_queue.append((guild_id, slash_obj))
                self._connection.hooks[slash_obj.name] = cmd
                self._connection.hooks[f'{slash_obj.name}_on_error'] = cmd_error
            else:
                raise NonCoroutine(f'command method inside cog `{cog_name}` must be a coroutine')
        else:
            raise InvalidCog(f'cog `{cog_name}` must be a subclass of SlashCog')

    async def sync_slash(self):
        for guild_id, slash_obj in self._reg_queue:
            if guild_id:
                route = Route('POST', f'/applications/{self.application_id}/guilds/{guild_id}/commands')
                resp = await self.http.request(route, json=slash_obj.to_dict())
                command = BaseAppCommand(**resp)
                if slash_obj.permissions:
                    perm_route = Route(
                        'PUT',
                        f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command.id}/permissions')
                    await self.http.request(perm_route, json=slash_obj.permissions)
            else:
                route = Route('POST', f'/applications/{self.application_id}/commands')
                resp = await self.http.request(route, json=slash_obj.to_dict())
                command = BaseAppCommand(**resp)

            prompt = f'[{"GLOBAL" if not guild_id else "GUILD"}] registered /{slash_obj.name}'
            print(f'{prompt} ... ID: {resp.get("id")} ... Guild: {guild_id if guild_id else "NA"}')

    async def fetch_global_slash_commands(self):
        route = Route('GET', f'/applications/{self.application_id}/commands')
        resp = await self.http.request(route)
        return [BaseAppCommand(**cmd) for cmd in resp]

    async def fetch_guild_slash_commands(self, guild_id: int):
        route = Route('GET', f'/applications/{self.application_id}/guilds/{guild_id}/commands')
        resp = await self.http.request(route)
        return [BaseAppCommand(**cmd) for cmd in resp]

    async def fetch_slash_command(self, command_id: int, guild_id: int = None):
        if guild_id:
            route = Route('GET', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('GET', f'/applications/{self.application_id}/commands/{command_id}')

        resp = await self.http.request(route)

        return BaseAppCommand(**resp)

    async def delete_slash_command(self, command_id: int, guild_id: int = None):
        if guild_id:
            route = Route('DELETE', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('DELETE', f'/applications/{self.application_id}/commands/{command_id}')

        await self.http.request(route)

    async def update_slash_command(self, command_id: int, modified: SlashCommand, guild_id: int = None):
        if guild_id:
            route = Route('PATCH', f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('PATCH', f'/applications/{self.application_id}/commands/{command_id}')

        resp = await self.http.request(route, json=modified.to_dict())

        return BaseAppCommand(**resp)

    async def update_slash_permission(self, guild_id: int, command_id: int, permissions: [SlashPermission]):
        payload = [perm.to_dict() for perm in permissions]
        route = Route('PATCH',
                      f'/applications/{self.application_id}/guilds/{guild_id}/commands/{command_id}/permissions')
        resp = await self.http.request(route, json=payload)
        return SlashOverwrite(**resp)

    async def batch_update_slash_permission(
            self,
            guild_id: int,
            command_ids: [int],
            permissions: [[SlashPermission]]
    ):
        if len(command_ids) != len(permissions):
            raise ValueError('Command IDs and Permissions must be the same length')
        payload = []
        for command_id, perm_list in zip(command_ids, permissions):
            payload.append({
                "id": command_id,
                "permissions": [perm.to_dict() for perm in perm_list]
            })

        route = Route('PATCH', f'/applications/{self.application_id}/guilds/{guild_id}/commands/permissions')
        resp = await self.http.request(route, json=payload)
        return [SlashOverwrite(**overwrite) for overwrite in resp]

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.add_listener(self._invoke_slash, 'on_interaction')
        await self.login(token)
        app_info = await self.application_info()
        self._connection.application_id = app_info.id
        await self.sync_slash()
        await self.connect(reconnect=reconnect)
