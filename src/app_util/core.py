from __future__ import annotations
import sys
import discord
from .errors import *
from .http_s import *
from discord.http import Route
from discord.ext import commands
from dataclasses import dataclass
from .origin import ApplicationCommandOrigin
from typing import List, Optional, Union, Any, Dict
from .enums import OptionType, ApplicationCommandType, try_enum


def _try_flake(snowflake: str) -> Union[int, None]:
    try:
        return int(snowflake)
    except TypeError:
        return None


def _make_qual(name: str, guild_id: Optional[int], ctype: ApplicationCommandType, ) -> str:
    if guild_id:
        post_fix = f'{name}_{guild_id}'
    else:
        post_fix = name

    if ctype is ApplicationCommandType.CHAT_INPUT:
        return '__CHAT__' + post_fix
    if ctype is ApplicationCommandType.MESSAGE:
        return '__MESSAGE__' + post_fix
    if ctype is ApplicationCommandType.USER:
        return '__USER__' + post_fix


@dataclass(frozen=True)
class InteractionData:
    name: str = None
    type: int = None
    guild_id: Optional[str] = None
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
    def __init__(self, data: dict, c):
        self.__c = c
        self.data = data
        self.client = c.client

    @property
    def users(self) -> Dict[int, discord.User]:
        if self.data.get('users'):
            return {int(key): discord.User(data=payload, state=self.client._connection)
                    for key, payload in self.data['users'].items()}

    @property
    def members(self) -> Dict[int, discord.Member]:
        if self.data.get('members'):
            return {int(key): self.__c.guild.get_member(int(key)) for key, _ in self.data['members'].items()}

    @property
    def roles(self) -> Dict[int, discord.Role]:
        if self.data.get('roles'):
            return {int(key): discord.Role(guild=self.__c.guild, data=payload, state=self.client._connection)
                    for key, payload in self.data['roles'].items()}

    @property
    def channels(self) -> Dict[int, discord.abc.GuildChannel]:
        if self.data.get('channels'):
            return {int(key): self.__c.guild.get_channel(int(key)) for key, _ in self.data['channels'].items()}

    @property
    def messages(self) -> Dict[int, discord.Message]:
        if self.data.get('messages'):
            return {int(key): discord.Message(data=payload, state=self.client._connection, channel=self.__c.channel)
                    for key, payload in self.data['messages'].items()}

    @property
    def attachments(self) -> Dict[int, discord.Attachment]:
        if self.data.get('attachments'):
            return {int(key): discord.Attachment(data=payload, state=self.client._connection)
                    for key, payload in self.data['attachments'].items()}


class DummyOption:
    value = True


class SlashCommandOption:

    def __init__(self, p, data: Dict[str, Any]):
        self.data = data
        self.guild = p.guild
        self.client = p.client
        self._resolved = p._resolved

    def __repr__(self):
        return f'<SlashCommandOption name={self.name} type={self.type}>'

    @property
    def name(self) -> str:
        return self.data['name']

    @property
    def type(self):
        value = self.data['type']
        return try_enum(OptionType, value)

    @staticmethod
    def _hybrid(family: str, options: List[Dict[str, Any]]):
        return [{'type': generic['type'], 'value': generic['value'], 'name': f'{family}_{generic["name"]}'}
                for generic in options]

    @property
    def value(self) -> Any:

        if self.type is OptionType.STRING:
            return self.data.get('value')

        elif self.type is OptionType.INTEGER:
            return self.data.get('value')

        elif self.type is OptionType.BOOLEAN:
            return self.data.get('value')

        elif self.type is OptionType.USER:
            user_id = int(self.data.get('value'))
            return self._resolved.users[user_id]

        elif self.type is OptionType.CHANNEL:
            channel_id = int(self.data.get('value'))
            return self._resolved.channels[channel_id]

        elif self.type is OptionType.ROLE:
            role_id = int(self.data.get('value'))
            return self._resolved.roles[role_id]

        elif self.type is OptionType.MENTIONABLE:
            target_id = int(self.data.get('value'))
            map_ = {}
            if not self.guild:
                if self._resolved.users:
                    map_.update(self._resolved.users)
                if self._resolved.roles:
                    map_.update(self._resolved.roles)
            else:
                if self._resolved.users:
                    map_.update(self._resolved.users)
                if self._resolved.roles:
                    map_.update(self._resolved.roles)
                if self._resolved.members:
                    map_.update(self._resolved.members)
            return map_[target_id]

        elif self.type is OptionType.NUMBER:
            return self.data['value']

        elif self.type is OptionType.ATTACHMENT:
            attachment_id = int(self.data['value'])
            return self._resolved.attachments[attachment_id]
        else:
            return self.data.get('value')

    @property
    def focused(self) -> bool:
        return self.data.get('focused')


class ApplicationCommand:

    def __init__(self, client: commands.Bot, data: dict):
        self.__payload = data
        self._client = client
        self.id = int(data['id'])
        self.guild_id = _try_flake(data.get('guild_id'))
        self.name = data['name']
        self.description = data['description']
        self.type = try_enum(ApplicationCommandType, data['type'])
        self.qualified_name = _make_qual(self.name, self.guild_id, self.type)
        self.application_id = int(data['application_id'])
        self.version = int(data['version'])
        self.options = data.get('options')
        self.dm_allowed = data.get('dm_permission') or False
        self.permissions = data.get('default_member_permissions')
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

    async def delete(self):
        await delete_command(self._client, self.id, self.guild_id)

        await self._client.http.request(route)
        self._client._application_commands.pop(self.id)

    async def update(self, new: ApplicationCommandOrigin) -> ApplicationCommand:
        if new.type is self.type:
            try:
                data = await patch_existing_command(self._client, self, new)
            except discord.errors.HTTPException as e:
                raise e
            else:
                updated = self._from_data(self._client, data)
                self._client._application_commands.pop(updated.id)
                self._client._application_commands[updated.id] = updated
                return updated
        raise CommandTypeMismatched(
            f'Type mismatched while editing command `{self.name}`. Expected: {self.type} & got: {new.type}')
