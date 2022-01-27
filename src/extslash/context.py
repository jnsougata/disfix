import json
import discord
from .converter import BaseInteraction, BaseInteractionData, BaseSlashOption
from discord.http import Route
from discord.utils import _to_json
from typing import Callable, Optional, Any, Union, List, Sequence, Iterable


class SlashContext:
    def __init__(self, interaction: BaseInteraction, client: discord.Client):
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
        return BaseInteractionData(**self._interaction.data)

    @property
    def options(self):
        return [BaseSlashOption(**option) for option in self.data.options]

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
            payload['embeds'] = [embed.to_dict()]
        if embeds:
            payload['embeds'] = [embed.to_dict() for embed in embeds]
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

    @property
    def typing(self):
        return self.channel.typing
