from __future__ import annotations
import sys
import asyncio
import json
import discord
from discord.http import Route
from discord.utils import MISSING
from discord.ext import commands
from .core import InteractionData, ChatInputOption, Resolved, ApplicationCommand, DummyOption
from .enums import ApplicationCommandType, OptionType, try_enum
from typing import Optional, Any, Union, Sequence, Iterable, NamedTuple, List, Dict


def _handle_edit_params(
        *,
        content: Optional[str] = MISSING,
        embed: Optional[discord.Embed] = MISSING,
        embeds: List[discord.Embed] = MISSING,
        view: Optional[discord.ui.View] = MISSING,
        views: List[discord.ui.View] = MISSING,
        file: Optional[discord.File] = MISSING,
        files: List[discord.File] = MISSING,
        allowed_mentions: Optional[discord.AllowedMentions] = MISSING,
):
    payload: Dict[str, Any] = {}

    if content is not MISSING:
        if content is not None:
            payload['content'] = content  # type: ignore
        else:
            payload['content'] = None

    if embed is not MISSING:
        if embed is None:
            payload['embeds'] = []
        else:
            payload['embeds'] = [embed.to_dict()]
    elif embeds is not MISSING:
        if len(embeds) > 10:
            raise discord.errors.InvalidArgument('embeds has a maximum of 10 elements.')
        payload['embeds'] = [e.to_dict() for e in embeds]

    if allowed_mentions is MISSING:
        payload['allowed_mentions'] = None  # type: ignore
    else:
        payload['allowed_mentions'] = allowed_mentions.to_dict()

    if view is not MISSING:
        if view:
            payload['components'] = view.to_components()
        else:
            payload['components'] = []
    elif views is not MISSING:
        container = []
        _all = [v.to_components() for v in views]
        for components in _all:
            container.extend(components)
        payload['components'] = container

    if file is not MISSING:
        fs = [file]
    elif files is not MISSING:
        fs = files
    else:
        fs = []

    form = []

    if len(fs) == 1:
        file_ = fs[0]
        form.append(
            {
                'name': 'file',
                'value': file_.fp,
                'filename': file_.filename,
                'content_type': 'application/octet-stream',
            }
        )
    else:
        for index, file_ in enumerate(fs):
            form.append(
                {
                    'name': f'file{index}',
                    'value': file_.fp,
                    'filename': file_.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return payload, form


def _handle_send_prams(
        *,
        content: Optional[Union[str, Any]] = None,
        tts: bool = False,
        ephemeral: bool = False,
        file: Optional[discord.File] = None,
        files: Sequence[discord.File] = None,
        embed: Optional[discord.Embed] = None,
        embeds: Optional[List[Optional[discord.Embed]]] = None,
        allowed_mentions: Optional[discord.AllowedMentions] = None,
        view: Optional[discord.ui.View] = None,
        views: Optional[List[discord.ui.View]] = None,
):
    if files and file:
        raise TypeError('Cannot mix file and files keyword arguments.')
    if embeds and embed:
        raise TypeError('Cannot mix embed and embeds keyword arguments.')
    if views and view:
        raise TypeError('Cannot mix view and views keyword arguments.')

    payload = {}

    if tts:
        payload['tts'] = tts

    if content:
        payload['content'] = content

    if embed:
        payload['embeds'] = [embed.to_dict()]
    elif embeds:
        if len(embeds) > 10:
            raise discord.errors.InvalidArgument('embeds has a maximum of 10 elements.')
        payload['embeds'] = [embed.to_dict() for embed in embeds]

    if allowed_mentions:
        payload['allowed_mentions'] = allowed_mentions

    if view:
        payload['components'] = view.to_components()
    elif views:
        container = []
        _all = [view.to_components() for view in views]
        for components in _all:
            container.extend(components)
        payload['components'] = concurrent

    if ephemeral:
        payload['flags'] = 64

    if file:
        fs = [file]
    elif files:
        fs = files
    else:
        fs = []

    form = []

    if len(fs) == 1:
        file_ = fs[0]
        form.append(
            {
                'name': 'file',
                'value': file_.fp,
                'filename': file_.filename,
                'content_type': 'application/octet-stream',
            }
        )
    else:
        for index, file_ in enumerate(fs):
            form.append(
                {
                    'name': f'file{index}',
                    'value': file_.fp,
                    'filename': file_.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return payload, form


class Context:
    def __init__(self, client: commands.Bot, interaction: discord.Interaction):
        self._ia = interaction
        self.bot = client
        self._client = client
        self._deferred = False
        self.original_message: Optional[discord.Message] = None

    def __repr__(self):
        return self.name


    @property
    def type(self):
        t = self._ia.data['type']
        return try_enum(ApplicationCommandType, t)

    @property
    def name(self) -> str:
        return self._ia.data.get('name')

    @property
    def description(self) -> str:
        return self._ia.data.get('description')

    @property
    def token(self):
        return self._ia.token

    @property
    def id(self):
        return int(self._ia.data['id'])

    @property
    def command(self) -> ApplicationCommand:
        return self._client.get_application_command(self.id)

    @property
    def version(self):
        """
        returns the version of the interaction
        :return:
        """
        return self._ia.version

    @property
    def data(self):
        """
        returns the interaction data
        :return: InteractionData
        """
        return InteractionData(**self._ia.data)

    @property
    def _resolved(self):
        """
        returns the resolved data of the interaction
        :return:
        """
        r_data = self.data.resolved
        return Resolved(r_data, self) if r_data else None

    @property
    def _target_message(self):
        """
        returns the resolved message of the MESSAGE COMMAND
        :return:
        """
        if self.type is ApplicationCommandType.MESSAGE:
            message_id = int(self.data.target_id)
            return self._resolved.messages[message_id]

    @property
    def _target_user(self):
        """
        returns the resolved user of the USER COMMAND
        :return:
        """
        if self.type is ApplicationCommandType.USER:
            user_id = int(self.data.target_id)
            return self._resolved.users[user_id]

    @property
    def options(self) -> Dict[str, ChatInputOption]:
        """
        returns the options of the interaction
        :return: InteractionDataOption
        """
        if self.type is ApplicationCommandType.USER:
            return {}  # type: ignore
        if self.type is ApplicationCommandType.MESSAGE:
            return {}  # type: ignore
        return self._parsed_options

    @property
    def _parsed_options(self) -> Dict[str, ChatInputOption]:
        container = {}
        options = self.data.options
        if options:
            for option in options:
                type = option['type']
                name = option['name']
                if type > OptionType.SUBCOMMAND_GROUP.value:
                    container[name] = ChatInputOption(option, self.guild, self._client, self._resolved)
                if type == OptionType.SUBCOMMAND.value:
                    family = option['name']
                    container[family] = DummyOption
                    new_options = option['options']
                    parsed = ChatInputOption._hybrid(family, new_options)
                    for new in parsed:
                        container[new['name']] = ChatInputOption(new, self.guild, self._client, self._resolved)
                if type == OptionType.SUBCOMMAND_GROUP.value:
                    origin = option['name']
                    container[origin] = DummyOption
                    for new_option in option['options']:
                        family = f"{origin}_{new_option['name']}"
                        parsed = ChatInputOption._hybrid(family, new_option['options'])
                        for new in parsed:
                            container[new['name']] = ChatInputOption(new, self.guild, self._client, self._resolved)
            return container
        return {}

    @property
    def application_id(self):
        """
        returns the application id / bot id of the interaction
        :return:
        """
        return self._ia.application_id

    @property
    def responded(self) -> bool:
        """
        returns whether the interaction is deferred
        :return: bool
        """
        return self._deferred

    async def defer(self, ephemeral: bool = False):
        route = Route('POST', f'/interactions/{self._ia.id}/{self._ia.token}/callback')
        payload = {'type': 5}
        if ephemeral:
            payload['data'] = {'flags': 64}
        await self._client.http.request(route, json=payload)
        self._deferred = True

    async def think_for(self, time: float, ephemeral: bool = False):
        if not self._deferred:
            await self.defer(ephemeral)
            await asyncio.sleep(time)

    @property
    def permissions(self):
        return self._ia.permissions

    @property
    def me(self):
        if self.guild:
            return self.guild.me

    @property
    def channel(self):
        channel = self._ia.channel
        # since the channel is partial messageable
        # we won't be able to check user/role permissions
        # rather we will use the channel id and get channel from cache
        return self.guild.get_channel(channel.id)

    @property
    def guild(self):
        """
        returns the guild where the interaction was created
        :return:
        """
        return self._ia.guild

    @property
    def author(self):
        """
        returns the author of the interaction
        :return: discord.Member
        """
        return self._ia.user

    async def send_message(
            self,
            content: Optional[Union[str, Any]] = None,
            *,
            tts: bool = False,
            file: Optional[discord.File] = None,
            files: Sequence[discord.File] = None,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[List[Optional[discord.Embed]]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            view: Optional[discord.ui.View] = None,
            views: Optional[List[discord.ui.View]] = None,
            stickers: Optional[List[discord.Sticker]] = None,
            reference: Optional[Union[discord.Message, discord.PartialMessage, discord.MessageReference]] = None,
            nonce: Optional[int] = None,
            delete_after: Optional[float] = None,
            mention_author: bool = False,
    ):
        if embed and embeds:
            raise TypeError('Can not mix embed and embeds')
        if file and files:
            raise TypeError('Can not mix file and files')
        if view and views:
            raise TypeError('Can not mix view and views')

        return await self._ia.channel.send(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            view=view,
            stickers=stickers,
            reference=reference,
            nonce=nonce,
            delete_after=delete_after,
            mention_author=mention_author,
            allowed_mentions=allowed_mentions)

    async def send_response(
            self,
            content: Optional[Union[str, Any]] = None,
            *,
            tts: bool = False,
            ephemeral: bool = False,
            file: Optional[discord.File] = None,
            files: Sequence[discord.File] = None,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[List[Optional[discord.Embed]]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            view: Optional[discord.ui.View] = None,
            views: Optional[List[discord.ui.View]] = None,
    ):
        payload, form = _handle_send_prams(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            view=view,
            views=views,
            ephemeral=ephemeral,
            allowed_mentions=allowed_mentions)

        data = {
                'name': 'payload_json',
                'value': json.dumps({
                    'type': 4,
                    'data': payload
                })
            }
        form.insert(0, data)  # type: ignore

        route = Route('POST', f'/interactions/{self._ia.id}/{self._ia.token}/callback')
        await self._client.http.request(route, form=form, files=files)
        self._deferred = True
        self.original_message = await self._ia.original_message()
        message_id = self.original_message.id
        if view:
            self._client._connection.store_view(view, message_id)
        if views:
            for view in views:
                self._client._connection.store_view(view, message_id)
        return self.original_message

    async def send_followup(
            self,
            content: Optional[Union[str, Any]] = None,
            *,
            tts: bool = False,
            ephemeral: bool = False,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[List[discord.Embed]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            file: Optional[discord.File] = None,
            files: Optional[List[discord.File]] = None,
            view: Optional[discord.ui.View] = None,
            views: Optional[List[discord.ui.View]] = None
    ):
        payload, form = _handle_send_prams(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            view=view,
            views=views,
            ephemeral=ephemeral,
            allowed_mentions=allowed_mentions)

        payload['wait'] = True

        data = {
                'name': 'payload_json',
                'value': json.dumps(payload),
            }
        form.insert(0, data)  # type: ignore

        r = Route('POST', f'/webhooks/{self.application_id}/{self.token}')

        if not self._deferred:
            await self.defer()

        data = await self._client.http.request(r, form=form, files=files)

        if view:
            self._client._connection.store_view(view, message_id)
        if views:
            for view in views:
                self._client._connection.store_view(view, message_id)

        follow_up = Followup(parent=self, payload=data, ephemeral=ephemeral)

        if self.original_message is None:
            self.original_message = follow_up.message
        return follow_up


    async def edit_response(
            self,
            content: Optional[Union[str, Any]] = MISSING,
            *,
            embed: Optional[discord.Embed] = MISSING,
            embeds: Optional[List[discord.Embed]] = MISSING,
            allowed_mentions: Optional[discord.AllowedMentions] = MISSING,
            file: Optional[discord.File] = MISSING,
            files: Optional[List[discord.File]] = MISSING,
            view: Optional[discord.ui.View] = MISSING,
            views: Optional[List[discord.ui.View]] = MISSING
    ):
        payload, form = _handle_edit_params(
            content=content,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            view=view,
            views=views)
        data = {
            'name': 'payload_json',
            'value': json.dumps(payload)
        }
        form.insert(0, data)  # type: ignore
        r = Route('PATCH', f'/webhooks/{self.application_id}/{self.token}/messages/@original')
        payload = await self._client.http.request(r, form=form, files=files)
        message_id = int(payload.get('id'))
        if view is not MISSING and view is not None:
            self._client._connection.store_view(view, message_id)
        elif views is not MISSING and views is not None:
            for v in views:
                self._client._connection.store_view(v, message_id)
        return discord.Message(
            state=self._client._connection, data=payload, channel=self.channel)  # type: ignore

    async def delete_response(self):
        route = Route('DELETE', f'/webhooks/{self.application_id}/{self.token}/messages/@original')
        await self._client.http.request(route)


class Followup:
    def __init__(self, *, parent: Context, payload: dict, ephemeral: bool = False):
        self._data = payload
        self._parent = parent
        self._eph = ephemeral
        self.token = parent.token
        self.channel = parent.channel
        self._client = parent._client
        self.application_id = parent.application_id

    @property
    def message(self):
        return discord.Message(
            state=self._client._connection, data=self._data, channel=self.channel)

    async def delete(self):
        route = Route('DELETE', f'/webhooks/{self.application_id}/{self.token}/messages/{self.message.id}')
        if not self._eph:
            await self._parent._client.http.request(route)

    async def edit(
            self,
            content: Optional[Union[str, Any]] = MISSING,
            *,
            embed: Optional[discord.Embed] = MISSING,
            embeds: Optional[List[discord.Embed]] = MISSING,
            allowed_mentions: Optional[discord.AllowedMentions] = MISSING,
            file: Optional[discord.File] = MISSING,
            files: Optional[List[discord.File]] = MISSING,
            view: Optional[discord.ui.View] = MISSING,
            views: Optional[List[discord.ui.View]] = MISSING,
    ):
        payload, form = _handle_edit_params(
            content=content,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            view=view,
            views=views,
            allowed_mentions=allowed_mentions)

        payload['wait'] = True

        data = {
                'name': 'payload_json',
                'value': json.dumps(payload)
        }
        form.insert(0, data)  # type: ignore
        route = Route('PATCH', f'/webhooks/{self.application_id}/{self.token}/messages/{self.message.id}')
        resp = await self._parent._client.http.request(route, form=form, files=files)
        if view is not MISSING and view is not None:
            self._parent._client._connection.store_view(view, self.message.id)
        elif views is not MISSING and views is not None:
            for view in views:
                self._parent._client._connection.store_view(view, self.message.id)
