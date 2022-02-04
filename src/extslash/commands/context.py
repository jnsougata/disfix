import asyncio
import json
import discord
from discord.webhook.async_ import Webhook
from .base import InteractionData, InteractionDataOption, InteractionDataResolved
from discord.http import Route
from discord.utils import _to_json
from typing import Optional, Any, Union, Sequence, Iterable


class ApplicationContext:
    def __init__(self, action: discord.Interaction, client: discord.Client):
        self._action = action
        self._client = client
        self._is_deferred = False

    @property
    def is_deferred(self):
        """
        returns whether the interaction is deferred
        :return: bool
        """
        return self._is_deferred

    @property
    def command(self) -> str:
        """
        returns the command name used to invoke the interaction
        :return:
        """
        return self._action.data.get('name')

    @property
    def id(self):
        """
        returns the interaction id
        :return:
        """
        return self._action.id

    @property
    def version(self):
        """
        returns the version of the interaction
        :return:
        """
        return self._action.version

    @property
    def data(self):
        """
        returns the interaction data
        :return: InteractionData
        """
        return InteractionData(**self._action.data)

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
            return [
                InteractionDataOption(
                    option, self.guild, self._client, self.resolved
                ) for option in options]

    @property
    def application_id(self):
        """
        returns the application id / bot id of the interaction
        :return:
        """
        return self._action.application_id

    @property
    def channel(self):
        """
        returns the channel where the interaction was created
        :return:
        """
        return self._action.channel

    @property
    def guild(self):
        """
        returns the guild where the interaction was created
        :return:
        """
        return self._action.guild

    @property
    def author(self):
        """
        returns the author of the interaction
        :return: discord.Member
        """
        return self._action.user

    @property
    def send(self):
        """
        sends a message to the channel
        where the interaction was created
        use `respond` to respond to that interaction
        :return:
        """
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
        route = Route('POST', f'/interactions/{self._action.id}/{self._action.token}/callback')

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
        route = Route('POST', f'/interactions/{self._action.id}/{self._action.token}/callback')
        await self._client.http.request(route, json={'type': '5'})
        self._is_deferred = True

    @property
    def thinking(self):
        """
        gives a context manager to invoke bot thinking to the interaction
        :return: _ThinkingState
        """
        return _ThinkingState(self)

    @property
    def followup(self):
        """
        sends follow up to a deferred interaction
        valid only for deferred interactions
        works until the interaction is token expired
        :return:
        """
        return self._action.followup

    @property
    def permissions(self):
        return self._action.permissions

    @property
    def me(self):
        if self.guild:
            return self.guild.me


class _ThinkingState:
    def __init__(self, _obj: ApplicationContext):
        self._obj = _obj

    async def __aenter__(self):
        await self._obj.defer()

    async def __aexit__(self, exc_type, exc, tb):
        return
