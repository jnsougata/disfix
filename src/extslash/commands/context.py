import sys
import asyncio
import json
import discord
from .base import InteractionData, InteractionDataOption, InteractionDataResolved
from discord.http import Route
from typing import Optional, Any, Union, Sequence, Iterable, NamedTuple, List


def _handle_message_prams(
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
        wait: bool = None,
):
    if files and file:
        raise TypeError('Cannot mix file and files keyword arguments.')
    if embeds and embed:
        raise TypeError('Cannot mix embed and embeds keyword arguments.')
    if views and view:
        raise TypeError('Cannot mix view and views keyword arguments.')

    payload = {}

    if wait:
        payload['wait'] = True  # for followups only

    if tts:
        payload['tts'] = tts

    if content:
        payload['content'] = content

    if embed:
        payload['embeds'] = [embed.to_dict()]

    if embeds:
        if len(embeds) > 10:
            raise discord.errors.InvalidArgument('embeds has a maximum of 10 elements.')
        payload['embeds'] = [embed.to_dict() for embed in embeds]

    if allowed_mentions:
        payload['allowed_mentions'] = allowed_mentions

    if view:
        payload['components'] = view.to_components()

    if views:
        components = []
        views_ = [view.to_components() for view in views]
        for view_ in views_:
            components.extend(view_)
        payload['components'] = components

    if ephemeral:
        payload['flags'] = 64

    if file:
        files_ = [file]
    else:
        files_ = []

    if files:
        files_ = files
    else:
        files_ = []

    form = []

    if len(files_) == 1:
        file_ = files_[0]
        form.append(
            {
                'name': 'file',
                'value': file_.fp,
                'filename': file_.filename,
                'content_type': 'application/octet-stream',
            }
        )
    else:
        for index, file_ in enumerate(files_):
            form.append(
                {
                    'name': f'file{index}',
                    'value': file_.fp,
                    'filename': file_.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return payload, form


class ApplicationContext:
    def __init__(self, action: discord.Interaction, client: discord.Client):
        self._ia = action
        self._client = client
        self._deferred = False

    @property
    def token(self):
        return self._ia.token

    @property
    def id(self):
        return self._ia.id

    @property
    def command_id(self):
        """
        returns the command id of the application command
        :return:
        """
        return self._ia.data.get('id')

    @property
    def command_name(self) -> str:
        """
        returns the command name used to invoke the interaction
        :return:
        """
        return self._ia.data.get('name')

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
        if d:
            return InteractionDataResolved(**d)

    @property
    def options(self):
        """
        returns the options of the interaction
        :return: InteractionDataOption
        """
        options = self.data.options
        if options:
            return [InteractionDataOption(option, self.guild, self._client, self.resolved) for option in options]

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

    @property
    def channel(self):
        """
        returns the channel where the interaction was created
        :return:
        """
        return self._ia.channel

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

        await self.channel.send(
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
            views: Optional[List[discord.ui.View]] = None
    ):
        payload, form = _handle_message_prams(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            view=view,
            views=views,
            ephemeral=ephemeral,
        )
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
        return Response(self, ephemeral=ephemeral)

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
        payload, form = _handle_message_prams(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            view=view,
            views=views,
            ephemeral=ephemeral,
            wait=True,
        )
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

    async def defer(self):
        route = Route('POST', f'/interactions/{self._ia.id}/{self._ia.token}/callback')
        await self._client.http.request(route, json={'type': '5'})
        self._deferred = True

    async def think_for(self, time: float):
        if not self._deferred:
            await self.defer()
            await asyncio.sleep(time)

    @property
    def permissions(self):
        return self._ia.permissions

    @property
    def me(self):
        if self.guild:
            return self.guild.me


# noinspection PyTypeChecker
class Response:
    def __init__(self, parent: ApplicationContext, ephemeral=False):
        self._parent = parent
        self._eph = ephemeral

    async def delete(self):
        route = Route('DELETE', f'/webhooks/{self._parent.application_id}/{self._parent.token}/messages/@original')
        if self._eph is not True:
            await self._parent._client.http.request(route)

    async def edit(
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
            views: Optional[List[discord.ui.View]] = None,
    ):
        payload, form = _handle_message_prams(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            view=view,
            views=views,
            ephemeral=ephemeral,
        )
        data = {
            'name': 'payload_json',
            'value': json.dumps({
                'type': 3,
                'data': payload
            })
        }
        form.insert(0, data)  # type: ignore
        r = Route('PATCH', f'/webhooks/{self._parent.application_id}/{self._parent.token}/messages/@original')
        payload = await self._parent._client.http.request(r, form=form, files=files)
        message_id = int(payload.get('id'))
        if view:
            self._parent._client._connection.store_view(view, message_id)
        if views:
            for view in views:
                self._parent._client._connection.store_view(view, message_id)
        return discord.Message(
            state=self._parent._client._connection, data=payload, channel=self._parent.channel)


class Followup:
    def __init__(self, parent: ApplicationContext, payload: dict, ephemeral: bool = False):
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
            views: Optional[List[discord.ui.View]] = None,
    ):
        payload, form = _handle_message_prams(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            view=view,
            views=views,
            ephemeral=ephemeral,
            wait=True,
        )

        data = {
                'name': 'payload_json',
                'value': json.dumps(payload)
        }
        form.insert(0, data)  # type: ignore
        route = Route('PATCH', f'/webhooks/{self.application_id}/{self.token}/messages/{self.message_id}')
        resp = await self._parent._client.http.request(route, form=form, files=files)
        if view:
            self._parent._client._connection.store_view(view, self.message_id)
        if views:
            for view in views:
                self._parent._client._connection.store_view(view, self.message_id)
