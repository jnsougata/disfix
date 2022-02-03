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
from .base import Interaction, BaseAppCommand, SlashOverwrite
from typing import Callable, Optional, Any, Union
from discord.ext.commands import Bot


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
        self._slash_commands = {}  # for caching - implement later
        self.__parent = 'on_socket_raw_receive'
        self.__child = self.__slash_create
        self.add_listener(self.__child, self.__parent)

    def slash_command(self, command: SlashCommand, guild_id: Optional[int] = None):
        self._reg_queue.append((guild_id, command))

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func
            self._command_pool[command.name] = wrapper()
        return decorator

    async def _invoke(self, appctx: ApplicationContext):
        cmd = self._command_pool.get(appctx.command)
        if cmd:
            try:
                await cmd(appctx)
            except Exception:
                traceback.print_exc()

    async def __slash_create(self, payload: Any):
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
                self._reg_queue.append((guild_id, reg_obj))
                self._command_pool[reg_obj.name] = cmd
            else:
                raise NonCoroutine(f'command method inside cog `{cog_name}` must be a coroutine')
        else:
            raise InvalidCog(f'cog `{cog_name}` must be a subclass of SlashCog')

    async def _register(self):
        await self.wait_until_ready()
        if not self._check:
            self._check = True
            for guild_id, reg_obj in self._reg_queue:
                if guild_id:
                    route = Route('POST', f'/applications/{self.user.id}/guilds/{guild_id}/commands')
                    resp = await self.http.request(route, json=reg_obj.to_dict())
                    command = BaseAppCommand(**resp)
                    if reg_obj.permissions:
                        perm_route = Route(
                            'PUT',
                            f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command.id}/permissions'
                        )
                        await self.http.request(perm_route, json=reg_obj.permissions)
                else:
                    route = Route('POST', f'/applications/{self.user.id}/commands')
                    resp = await self.http.request(route, json=reg_obj.to_dict())
                    command = BaseAppCommand(**resp)

                prompt = f'[{"GLOBAL" if not guild_id else "GUILD"}] registered /{reg_obj.name}'
                print(f'{prompt} ... ID: {resp.get("id")} ... Guild: {guild_id if guild_id else "NA"}')

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

    async def delete_slash_command(self, command_id: int, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('DELETE', f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('DELETE', f'/applications/{self.user.id}/commands/{command_id}')

        await self.http.request(route)

    async def update_slash_command(self, command_id: int, modified: SlashCommand, guild_id: int = None):
        await self.wait_until_ready()
        if guild_id:
            route = Route('PATCH', f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command_id}')
        else:
            route = Route('PATCH', f'/applications/{self.user.id}/commands/{command_id}')

        resp = await self.http.request(route, json=modified.to_dict())

        return BaseAppCommand(**resp)

    async def update_slash_permission(self, guild_id: int, command_id: int, permissions: [SlashPermission]):
        await self.wait_until_ready()
        payload = [perm.to_dict() for perm in permissions]
        route = Route('PATCH', f'/applications/{self.user.id}/guilds/{guild_id}/commands/{command_id}/permissions')
        resp = await self.http.request(route, json=payload)
        return SlashOverwrite(**resp)

    async def batch_update_slash_permission(
            self,
            guild_id: int,
            command_ids: [int],
            permissions: [[SlashPermission]]
    ):

        await self.wait_until_ready()
        if len(command_ids) != len(permissions):
            raise ValueError('Command IDs and Permissions must be the same length')
        payload = []
        for command_id, perm_list in zip(command_ids, permissions):
            payload.append({
                "id": command_id,
                "permissions": [perm.to_dict() for perm in perm_list]
            })

        route = Route('PATCH', f'/applications/{self.user.id}/guilds/{guild_id}/commands/permissions')
        resp = await self.http.request(route, json=payload)
        return [SlashOverwrite(**overwrite) for overwrite in resp]
