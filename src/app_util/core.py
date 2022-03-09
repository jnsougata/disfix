from __future__ import annotations
import sys
import discord
from .errors import *
from discord.ext import commands
from discord.http import Route
from .http_s import *
from dataclasses import dataclass
from .app import Overwrite, ApplicationCommandOrigin
from typing import List, Optional, Union, Any, Dict
from .enums import OptionType, ApplicationCommandType, PermissionType, try_enum


def _try_flake(snowflake: str) -> Union[int, None]:
    try:
        return int(snowflake)
    except TypeError:
        return None


def _make_qual(name: str, guild_id: Optional[int], ctype: ApplicationCommandType, ) -> str:
    if guild_id:
        partial = f'{name}_{guild_id}'
    else:
        partial = name

    if ctype is ApplicationCommandType.CHAT_INPUT:
        return '__CHAT__' + partial
    if ctype is ApplicationCommandType.MESSAGE:
        return '__MESSAGE__' + partial
    if ctype is ApplicationCommandType.USER:
        return '__USER__' + partial


@dataclass(frozen=True)
class InteractionData:
    name: str = None
    type: int = None
    id: Union[int, str] = None
    resolved: Optional[dict] = None
    options: Optional[List[dict]] = None
    # below are only used for type != 2
    custom_id: Optional[str] = None
    component_type: Optional[int] = None
    values: Optional[list] = None
    # only used for User Command & Message Command
    target_id: Optional[str] = None
    # only used for modals
    components: Optional[List[dict]] = None


class Resolved:
    def __init__(self, payload: dict, ctx):
        self._ctx = ctx
        self._payload = payload
        self._client = ctx.client

    @property
    def users(self) -> Dict[int, discord.User]:
        if self._payload.get('users'):
            return {
                int(key): discord.User(
                    data=payload,
                    state=self._client._connection)
                for key, payload in self._payload['users'].items()}

    @property
    def members(self) -> Dict[int, discord.Member]:
        if self._payload.get('members'):
            return {
                int(key): self._ctx.guild.get_member(int(key))
                for key, _ in self._payload['members'].items()}

    @property
    def roles(self) -> Dict[int, discord.Role]:
        if self._payload.get('roles'):
            return {
                int(key): discord.Role(
                    guild=self._ctx.guild,
                    data=payload,
                    state=self._client._connection)
                for key, payload in self._payload['roles'].items()}

    @property
    def channels(self) -> Dict[int, discord.abc.GuildChannel]:
        if self._payload.get('channels'):
            return {
                int(key): self._ctx.guild.get_channel(int(key))
                for key, _ in self._payload['channels'].items()
            }

    @property
    def messages(self) -> Dict[int, discord.Message]:
        if self._payload.get('messages'):
            return {
                int(key): discord.Message(
                    data=payload,
                    state=self._client._connection,
                    channel=self._ctx.channel)
                for key, payload in self._payload['messages'].items()}

    @property
    def attachments(self) -> Dict[int, discord.Attachment]:
        if self._payload.get('attachments'):
            return {
                int(key): discord.Attachment(
                    data=payload,
                    state=self._client._connection)
                for key, payload in self._payload['attachments'].items()}


class DummyOption:
    value = True


class SlashCommandOption:

    def __init__(self, parent, data: Dict[str, Any]):
        self._data = data
        self._guild = parent.guild
        self._client = parent.client
        self._resolved = parent._resolved

    def __repr__(self):
        return f'<SlashCommandOption name={self.name} type={self.type}>'

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def type(self):
        value = self._data['type']
        return try_enum(OptionType, value)

    @staticmethod
    def _hybrid(family: str, options: List[Dict[str, Any]]):
        return [
            {
                'type': generic['type'],
                'value': generic['value'],
                'name': f'{family}_{generic["name"]}'
            } for generic in options
        ]

    @property
    def value(self) -> Any:

        if self.type is OptionType.STRING:
            return self._data.get('value')

        elif self.type is OptionType.INTEGER:
            return self._data.get('value')

        elif self.type is OptionType.BOOLEAN:
            return self._data.get('value')

        elif self.type is OptionType.USER:
            user_id = int(self._data.get('value'))
            return self._resolved.users[user_id]

        elif self.type is OptionType.CHANNEL:
            channel_id = int(self._data.get('value'))
            return self._resolved.channels[channel_id]

        elif self.type is OptionType.ROLE:
            role_id = int(self._data.get('value'))
            return self._resolved.roles[role_id]

        elif self.type is OptionType.MENTIONABLE:
            target_id = int(self._data.get('value'))
            map = {}
            if not self._guild:
                if self._resolved.users:
                    map.update(self._resolved.users)
                if self._resolved.roles:
                    map.update(self._resolved.roles)
            else:
                if self._resolved.users:
                    map.update(self._resolved.users)
                if self._resolved.roles:
                    map.update(self._resolved.roles)
                if self._resolved.members:
                    map.update(self._resolved.members)
            return map[target_id]

        elif self.type is OptionType.NUMBER:
            return self._data['value']

        elif self.type is OptionType.ATTACHMENT:
            attachment_id = int(self._data['value'])
            return self._resolved.attachments[attachment_id]
        else:
            return self._data.get('value')

    @property
    def focused(self) -> bool:
        return self._data.get('focused')


class ApplicationCommand:

    def __init__(self, client: commands.Bot, data: dict):
        self.__payload = data
        self._client = client
        self.id = int(data['id'])
        self.guild_id = _try_flake(data.get('guild_id'))
        self.name = data['name']
        self.description = data['description']
        self.type = try_enum(ApplicationCommandType, data['type'])
        self._qual = _make_qual(self.name, self.guild_id, self.type)
        self.application_id = int(data['application_id'])
        self.options = data.get('options')
        self.version = int(data['version'])
        self.default_access = data['default_permission']
        self.dm_access = self.default_access or False
        self._permissions = data.get('permissions') or {}
        self.overwrites = {}
        self.__parse_permissions()
        self.name_locale = data.get('name_localizations')
        self.description_locale = data.get('description_localizations')

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f'<ApplicationCommand id = {self.id} name = {self.name}>'

    @classmethod
    def _from_data(cls, client: commands.Bot, data: dict):
        return cls(client, data)

    @property
    def guild_specific(self) -> bool:
        if self.guild_id:
            return True
        return False

    @property
    def guild(self):
        if self.guild_id:
            return self._client.get_guild(self.guild_id)
        return None

    def overwrite_for(self, guild: discord.Guild, entity: Union[discord.Role, discord.User]) -> bool:
        permission = self.overwrites.get(guild.id)
        if permission is None:
            return self.default_access
        for_entity = permission.get(entity.id)
        if for_entity is None:
            return self.default_access
        return for_entity['allowed']

    async def delete(self):
        await delete_command(self._client, self.id, self.guild_id)

        await self._client.http.request(route)
        self._client._application_commands.pop(self.id)

    def __parse_permissions(self):
        for guild_id, perms in self._permissions.items():
            for p in perms:
                self.overwrites[int(guild_id)] = {int(p['id']): {'allowed': p['permission'], 'type': p['type']}}

    def _cache_permissions(self, ows: dict, guild_id: int):
        self._permissions[guild_id] = ows['permissions']
        self.__parse_permissions()

    def _build_overwrites(self, guild_id: int):
        overwrites = self.overwrites.get(guild_id)
        if ows:
            return [{'id': str(entity_id), 'type': ovrt['type'], 'permission': ovrt['allowed']}
                    for entity_id, ovrt in ows.items()]

    async def edit_overwrites(self, guild: discord.Guild, overwrites: List[Overwrite]):
        payload = {'permissions': [o.to_dict() for o in overwrites]}
        data = await put_overwrites(self._client, self.id, guild.id, payload)
        self._cache_permissions(data, guild.id)

    async def edit_overwrite_for(self, guild: discord.Guild, overwrite: Overwrite):
        container = self._build_overwrites(guild.id)
        new = overwrite.to_dict()
        for ovrt in container:
            if ovrt['id'] == new['id']:
                container.remove(ovrt)
        container.append(new)
        payload = {'permissions': container}
        data = await put_overwrites(self._client, self.id, guild.id, payload)
        self._cache_permissions(data, guild.id)


    async def update(self, new_command: ApplicationCommandOrigin) -> ApplicationCommand:
        if new_command.type is self.type:
            try:
                data = await patch_existing_command(self._client, self, new_command)
            except discord.errors.HTTPException as e:
                raise e
            else:
                updated = self._from_data(self._client, data)
                self._client._application_commands.pop(updated.id)
                self._client._application_commands[updated.id] = updated
                return updated
        raise CommandTypeMismatched(
            f'Type mismatched while editing command `{self.name}`. Expected: {self.type} & got: {new_command.type}')
