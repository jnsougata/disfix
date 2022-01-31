import asyncio
import json
import discord
from discord.webhook.async_ import Webhook
from .base import (
    Interaction,
    InteractionData,
    InteractionDataOption,
    InteractionDataResolved
)
from discord.http import Route
from discord.utils import _to_json
from typing import Optional, Any, Union, Sequence, Iterable


class ApplicationContext:
    def __init__(self, ia: Interaction, client: discord.Client):
        self._ia = ia
        self._client = client

    @property
    def client(self):
        return self._client

    @property
    def name(self):
        return self._ia.data.get('name')

    @property
    def id(self):
        return self._ia.id

    @property
    def version(self):
        return self._ia.version

    @property
    def data(self):
        return InteractionData(**self._ia.data)

    @property
    def resolved(self):
        if self.data.resolved:
            return InteractionDataResolved(**self.data.resolved)

    @property
    def options(self):
        options = self.data.options
        if options:
            return [InteractionDataOption(**option) for option in options]

    @property
    def application_id(self):
        return self._ia.application_id

    @property
    def locale(self):
        return self._ia.locale

    @property
    def guild_locale(self):
        return self._ia.guild_locale

    @property
    def channel(self):
        channel_id = self._ia.channel_id
        if channel_id:
            return self._client.get_channel(int(channel_id))

    @property
    def guild(self):
        guild_id = self._ia.guild_id
        if guild_id:
            return self._client.get_guild(int(guild_id))

    @property
    def author(self):
        if self._ia.guild_id:
            user_id = self._ia.member.get('user').get('id')
            return self.guild.get_member(int(user_id))

    @property
    def user(self):
        user_id = self._ia.user.get('id')
        if user_id:
            return self._client.get_user(int(user_id))

    @property
    def send(self):
        return self.channel.send

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
            view: Optional[discord.ui.View] = None,
            views: Optional[Iterable[discord.ui.View]] = None,
            ephemeral: bool = False
    ):
        form = []
        route = Route('POST', f'/interactions/{self._ia.id}/{self._ia.token}/callback')

        payload: Dict[str, Any] = {'tts': tts}
        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed.to_dict()]
        if embeds:
            payload['embeds'] = [embed.to_dict() for embed in embeds]
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        if view:
            payload['components'] = view.to_components()
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
                    'content_type': 'extslash/octet-stream',
                }
            )
        else:
            for index, file in enumerate(files):
                form.append(
                    {
                        'name': f'file{index}',
                        'value': file.fp,
                        'filename': file.filename,
                        'content_type': 'extslash/octet-stream',
                    }
                )
        await self._client.http.request(route, form=form, files=files)

    async def defer(self):
        route = Route('POST', f'/interactions/{self._ia.id}/{self._ia.token}/callback')
        return await self._client.http.request(route, json={'type': '5'})

    @property
    def thinking(self):
        return _ThinkingState(self)

    @property
    def followup(self):
        payload = {
            'type': 3,
            'token': self._ia.token,
            'id': self.application_id
        }
        return Webhook.from_state(data=payload, state=self._client._connection)

    @property
    def typing(self):
        return self.channel.typing


class _ThinkingState:
    def __init__(self, _obj: ApplicationContext):
        self._obj = _obj

    async def __aenter__(self):
        await self._obj.defer()

    async def __aexit__(self, exc_type, exc, tb):
        pass
