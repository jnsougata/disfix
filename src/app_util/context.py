import sys
import asyncio
import json
import discord
from discord.http import Route
from discord.utils import MISSING
from .base import InteractionData, InteractionDataOption, Resolved
from .enums import ApplicationCommandType, OptionType
from typing import Optional, Any, Union, Sequence, Iterable, NamedTuple, List


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
            payload['content'] = str(content)  # type: ignore
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
    def __init__(self, action: discord.Interaction, client: discord.Client):
        self._ia = action
        self._client = client
        self._deferred = False


    @property
    def type(self):
        raw_type = self._ia.data.get('type')
        if raw_type == ApplicationCommandType.CHAT_INPUT.value:
            return ApplicationCommandType.CHAT_INPUT
        elif raw_type == ApplicationCommandType.USER.value:
            return ApplicationCommandType.USER
        elif raw_type == ApplicationCommandType.MESSAGE.value:
            return ApplicationCommandType.MESSAGE

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
    def command(self):
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
    def resolved(self):
        """
        returns the resolved data of the interaction
        :return:
        """
        d = self.data.resolved
        return Resolved(d, self) if d else None

    @property
    def resolved_message(self):
        """
        returns the resolved message of the MESSAGE COMMAND
        :return:
        """
        if self.type is ApplicationCommandType.MESSAGE:
            return self.resolved.message[0]

    @property
    def resolved_user(self):
        """
        returns the resolved user of the USER COMMAND
        :return:
        """
        if self.type is ApplicationCommandType.USER:
            return self.resolved.users[0]

    @property
    def str_options(self) -> List[str]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            options = self.data.options
            return [option.get('value') for option in options if option.get('type') == OptionType.STRING.value]

    @property
    def int_options(self) -> List[int]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            options = self.data.options
            return [option.get('value') for option in options if option.get('type') == OptionType.INTEGER.value]

    @property
    def bool_options(self) -> List[bool]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            options = self.data.options
            return [option.get('value') for option in options if option.get('type') == OptionType.BOOLEAN.value]

    @property
    def number_options(self) -> List[Union[int, float]]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            options = self.data.options
            return [option.get('value') for option in options if option.get('type') == OptionType.NUMBER.value]

    @property
    def attachment_options(self) -> List[discord.Attachment]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            attachment_ids = [option.get('value') for option in self.data.options
                              if option.get('type') == OptionType.ATTACHMENT.value]
            return [self.resolved.attachments[int(_id)] for _id in attachment_ids]

    @property
    def channel_options(self) -> List[discord.abc.GuildChannel]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            channel_ids = [option.get('value') for option in self.data.options
                           if option.get('type') == OptionType.CHANNEL.value]
            return [self.resolved.channels[int(_id)] for _id in channel_ids]

    @property
    def role_options(self) -> List[discord.Role]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            role_ids = [option.get('value') for option in self.data.options
                        if option.get('type') == OptionType.ROLE.value]
            return [self.resolved.roles[int(_id)] for _id in role_ids]

    @property
    def user_options(self) -> List[discord.User]:
        if self.type is ApplicationCommandType.CHAT_INPUT:
            user_ids = [option.get('value') for option in self.data.options
                        if option.get('type') == OptionType.USER.value]
            return [self.resolved.users[int(_id)] for _id in user_ids]

    @property
    def member_options(self) -> List[discord.Member]:
        if self.type is ApplicationCommandType.CHAT_INPUT and self.guild:
            member_ids = [option.get('value') for option in self.data.options
                          if option.get('type') == OptionType.USER.value]
            return [self.resolved.members[int(_id)] for _id in member_ids]



    @property
    def options(self):
        """
        returns the options of the interaction
        :return: InteractionDataOption
        """
        if self.type is ApplicationCommandType.USER:
            return None
        if self.type is ApplicationCommandType.MESSAGE:
            return None
        options = self.data.options
        if options:
            return [
                InteractionDataOption(
                    option, self.guild, self._client, self.resolved) for option in options]

    @property
    def application_id(self):
        """
        returns the application id / bot id of the interaction
        :return:
        """
        return self._ia.application_id

    @property
    def responded(self):
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
            await self.defer(ephemeral=ephemeral)
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
            allowed_mentions=allowed_mentions,
            view=view,
            stickers=stickers,
            reference=reference,
            nonce=nonce,
            delete_after=delete_after,
            mention_author=mention_author)

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
            allowed_mentions=allowed_mentions,
            view=view,
            views=views,
            ephemeral=ephemeral)
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
        # getting message for storing view
        # getting this message is a bit of a hack, but it works if you want to refresh the view
        re_route = Route('GET', f'/webhooks/{self.application_id}/{self.token}/messages/@original')
        original = await self._client.http.request(re_route)
        message_id = int(original.get('id'))
        if view:
            self._client._connection.store_view(view, message_id)
        if views:
            for view in views:
                self._client._connection.store_view(view, message_id)

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
            allowed_mentions=allowed_mentions,
            view=view,
            views=views,
            ephemeral=ephemeral)

        payload['wait'] = True

        data = {
                'name': 'payload_json',
                'value': json.dumps(payload),
            }
        form.insert(0, data)  # type: ignore

        r = Route('POST', f'/webhooks/{self.application_id}/{self.token}')
        if self._deferred:
            resp = await self._client.http.request(r, form=form, files=files)
        else:
            await self.defer()
            resp = await self._client.http.request(r, form=form, files=files)

        message_id = int(resp.get('id'))

        if view:
            self._client._connection.store_view(view, message_id)
        if views:
            for view in views:
                self._client._connection.store_view(view, message_id)

        return Followup(self, resp, ephemeral)

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
    def __init__(self, parent: Context, payload: dict, ephemeral: bool = False):
        self._data = payload
        self._parent = parent
        self._eph = ephemeral
        self.message_id = int(payload.get('id'))
        self.application_id = parent.application_id
        self.token = parent.token

    async def delete(self):
        route = Route('DELETE', f'/webhooks/{self.application_id}/{self.token}/messages/{self.message_id}')
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
        route = Route('PATCH', f'/webhooks/{self.application_id}/{self.token}/messages/{self.message_id}')
        resp = await self._parent._client.http.request(route, form=form, files=files)
        if view is not MISSING and view is not None:
            self._parent._client._connection.store_view(view, self.message_id)
        elif views is not MISSING and views is not None:
            for view in views:
                self._parent._client._connection.store_view(view, self.message_id)
