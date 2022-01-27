import sys
import discord
from discord.ext import commands
import json
import asyncio
import traceback
from .type import Slash
from dataclasses import dataclass
from discord.http import Route
from functools import wraps
from discord.utils import _to_json
from typing import Callable, Optional, Any, Union, List, Sequence, Iterable


@dataclass(frozen=True)
class _BaseInteraction:
    id: int
    version: int
    token: str
    type: int
    data: dict
    application_id: int
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
    resolved: Optional[dict] = None
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
    def __init__(self, interaction: _BaseInteraction, client: discord.Client):
        self._interaction = interaction
        self._client = client

    @property
    def name(self):
        return self._interaction.data.get('name')

    @property
    def id(self):
        return self._interaction.id

    @property
    def version(self):
        return self._interaction.version

    @property
    def data(self):
        return _BaseInteractionData(**self._interaction.data)

    @property
    def options(self):
        return [_BaseSlashOption(**option) for option in self.data.options]

    @property
    def application_id(self):
        return self._interaction.application_id

    @property
    def locale(self):
        return self._interaction.locale

    @property
    def guild_locale(self):
        return self._interaction.guild_locale

    @property
    def channel(self):
        channel_id = self._interaction.channel_id
        if channel_id:
            return self._client.get_channel(int(channel_id))

    @property
    def guild(self):
        guild_id = self._interaction.guild_id
        if guild_id:
            return self._client.get_guild(int(guild_id))

    @property
    def author(self):
        if self._interaction.member:
            member_id = self._interaction.member.get('user').get('id')
            return self._client.get_user(int(member_id))

    @property
    def user(self):
        if self._interaction.user:
            user_id = self._interaction.user.get('id')
            return self._client.get_user(int(user_id))

    async def respond(
            self,
            content: Union[str, Any] = None,
            *,
            tts: bool = False,
            file: Optional[discord.File] = None,
            files: Sequence[discord.File] = None,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[Iterable[Optional[discord.Embed]]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            components: Optional[List[discord.Component]] = None,
            ephemeral: bool = False
    ):
        form = []
        route = Route('POST', f'/interactions/{self._interaction.id}/{self._interaction.token}/callback')

        payload: Dict[str, Any] = {'tts': tts}
        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed]
        if embeds:
            payload['embeds'] = embeds
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        if components:
            payload['components'] = components
        if ephemeral:
            payload['flags'] = 64
        if file:
            files = [file]
        if not files:
            files = []

        # handling non-attachment data
        form.append(
            {
                'name': 'payload_json',
                'value': json.dumps({
                    'type': 4,
                    'data': json.loads(_to_json(payload))
                })
            }
        )

        # handling attachment data
        if len(files) == 1:
            file = files[0]
            form.append(
                {
                    'name': 'file',
                    'value': file.fp,
                    'filename': file.filename,
                    'content_type': 'application/octet-stream',
                }
            )
        else:
            for index, file in enumerate(files):
                form.append(
                    {
                        'name': f'file{index}',
                        'value': file.fp,
                        'filename': file.filename,
                        'content_type': 'application/octet-stream',
                    }
                )
        return await self._client.http.request(route, form=form, files=files)

    async def send(
            self,
            content: Optional[str] = None,
            *,
            file: Optional[discord.File] = None,
            files: Sequence[discord.File] = None,
            tts: bool = False,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[Iterable[Optional[discord.Embed]]] = None,
            nonce: Optional[str] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            message_reference: Optional[discord.MessageReference] = None,
            stickers: Optional[List[discord.StickerItem]] = None,
            components: Optional[List[discord.Component]] = None,
    ):
        if file:
            files = [file]
        if not files:
            files = []
        ack_route = Route('POST', f'/interactions/{self._interaction.id}/{self._interaction.token}/callback')
        channel_route = Route('POST', f'/channels/{self.channel.id}/messages')
        await self._client.http.request(ack_route, json={'type': 4, 'data': {'content': '\u200e', 'ephemeral': True}})
        return await self._client.http.send_multipart_helper(
            route=channel_route,
            content=content,
            files=files,
            tts=tts,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            stickers=stickers,
            components=components,
        )


class SlashBot(commands.Bot):
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
            interaction = _BaseInteraction(**response.get('d'))
            if interaction.type == 2:
                await self._call_to(SlashContext(interaction, self))
