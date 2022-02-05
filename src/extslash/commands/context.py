import sys
import asyncio
import json
import discord
from .base import InteractionData, InteractionDataOption, InteractionDataResolved
from discord.http import Route
from discord.utils import _to_json
from typing import Optional, Any, Union, Sequence, Iterable, NamedTuple


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
    def responded(self):
        """
        returns whether the interaction is deferred
        :return: bool
        """
        return self._deferred

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

    async def send_response(
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
        """
        sends a response to the interaction
        :param content: (str) the content of the message
        :param tts: (book) whether the message should be read aloud
        :param file: (discord.File) a file to send
        :param files: (Sequence[discord.File]) a list of files to send
        :param embed: (discord.Embed) an embed to send
        :param embeds: (Iterable[discord.Embed]) a list of embeds to send
        :param allowed_mentions: (discord.AllowedMentions) the mentions to allow
        :param view: (discord.ui.View) a view to send
        :param views: (Iterable[discord.ui.View]) a list of views to send
        :param ephemeral: (bool) whether the message should be sent as ephemeral
        :return: None
        """
        form = []
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
        route = Route('POST', f'/interactions/{self._ia.id}/{self._ia.token}/callback')
        await self._client.http.request(route, form=form, files=files)
        self._deferred = True
        return Response(self, ephemeral=ephemeral)

    async def send_followup(
            self,
            content: str = None,
            *,
            tts: bool = False,
            ephemeral: bool = False,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[list[discord.Embed]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            file: Optional[discord.File] = None,
            files: Sequence[discord.File] = None,
            view: Optional[discord.ui.View] = None
    ):
        if files and file:
            raise TypeError('Cannot mix file and files keyword arguments.')
        if embeds and embed:
            raise TypeError('Cannot mix embed and embeds keyword arguments.')

        payload = {}

        payload['content'] = str(content) if content else None

        if embeds:
            if len(embeds) > 10:
                raise discord.errors.InvalidArgument('embeds has a maximum of 10 elements.')
            payload['embeds'] = [e.to_dict() for e in embeds]
        if embed:
            payload['embeds'] = [embed.to_dict()]
        else:
            payload['embeds'] = []

        if view:
            payload['components'] = view.to_components()
        else:
            payload['components'] = []

        payload['tts'] = tts

        if ephemeral:
            payload['flags'] = 64

        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions.to_dict()

        payload['wait'] = True

        form = []
        if file:
            files = [file]
        if not files:
            files = []

        form.append(
            {
                'name': 'payload_json',
                'value': _to_json(payload),
            }
        )

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
        r = Route('POST', f'/webhooks/{self.application_id}/{self.token}')
        if self._deferred:
            resp = await self._client.http.request(r, form=form, files=files)
            return FollowupResponse(self, resp, ephemeral)
        else:
            await self.defer()
            resp = await self._client.http.request(r, form=form, files=files)
            return FollowupResponse(self, resp, ephemeral)

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
    ):
        """
        edits an interaction response message
        :param content: (str) the content of the message
        :param tts: (book) whether the message should be read aloud
        :param file: (discord.File) a file to send
        :param files: (Sequence[discord.File]) a list of files to send
        :param embed: (discord.Embed) an embed to send
        :param embeds: (Iterable[discord.Embed]) a list of embeds to send
        :param allowed_mentions: (discord.AllowedMentions) the mentions to allow
        :param view: (discord.ui.View) a view to send
        :param views: (Iterable[discord.ui.View]) a list of views to send
        :return: None
        """
        form = []

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

        if file:
            files = [file]
        if not files:
            files = []

        # handling non-attachment data
        form.append(
            {
                'name': 'payload_json',
                'value': json.dumps({'data': json.loads(_to_json(payload)), 'type': 3})
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
        r = Route('PATCH', f'/webhooks/{self._parent.application_id}/{self._parent.token}/messages/@original')
        payload = await self._parent._client.http.request(r, form=form, files=files)
        return discord.Message(
            state=self._parent._client._connection, data=payload, channel=self._parent.channel)


class FollowupResponse:
    def __init__(self, parent: ApplicationContext, payload: dict, ephemeral: bool = False):
        self._data = payload
        self._parent = parent
        self._eph = ephemeral
        self.id = payload['id']
        self.application_id = parent.application_id
        self.token = parent.token

    async def delete(self):
        route = Route('DELETE', f'/webhooks/{self.application_id}/{self.token}/messages/{self.id}')
        if not self._eph:
            await self._parent._client.http.request(route)

    async def edit(
            self,
            content: str = None,
            *,
            tts: bool = False,
            ephemeral: bool = False,
            embed: Optional[discord.Embed] = None,
            embeds: Optional[list[discord.Embed]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            file: Optional[discord.File] = None,
            files: Sequence[discord.File] = None,
            view: Optional[discord.ui.View] = None
    ):
        if files and file:
            raise TypeError('Cannot mix file and files keyword arguments.')
        if embeds and embed:
            raise TypeError('Cannot mix embed and embeds keyword arguments.')

        payload = {}

        payload['content'] = str(content) if content else None

        if embeds:
            if len(embeds) > 10:
                raise discord.errors.InvalidArgument('embeds has a maximum of 10 elements.')
            payload['embeds'] = [e.to_dict() for e in embeds]
        if embed:
            payload['embeds'] = [embed.to_dict()]
        else:
            payload['embeds'] = []

        if view:
            payload['components'] = view.to_components()
        else:
            payload['components'] = []

        payload['tts'] = tts

        if ephemeral:
            payload['flags'] = 64

        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions.to_dict()

        payload['wait'] = True

        form = []
        if file:
            files = [file]
        if not files:
            files = []

        form.append(
            {
                'name': 'payload_json',
                'value': _to_json(payload),
            }
        )

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
        route = Route('PATCH', f'/webhooks/{self.application_id}/{self.token}/messages/{self.id}')
        await self._parent._client.http.request(route, form=form, files=files)
