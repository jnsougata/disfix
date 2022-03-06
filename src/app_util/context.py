from __future__ import annotations
import asyncio
import json
import discord
from discord.http import Route
from discord.utils import MISSING
from discord.ext import commands
from discord import Message, PartialMessage, MessageReference
from .app import _handle_edit_params, _handle_send_prams, Adapter
from .core import InteractionData, ChatInputOption, Resolved, ApplicationCommand, DummyOption
from .enums import ApplicationCommandType, OptionType, try_enum
from typing import Optional, Any, Union, Sequence, Iterable, NamedTuple, List, Dict


class Context:
    def __init__(self, client: commands.Bot, ia: discord.Interaction):
        self._ia = ia
        self.client = client
        self._deferred = False
        self._invisible = False
        self.original_message: Optional[discord.Message] = None

    def __repr__(self):
        return self.name

    @property
    def _adapter(self):
        return Adapter(self._ia, self.client)


    @property
    def type(self):
        return try_enum(ApplicationCommandType, self._ia.data['type'])

    @property
    def name(self) -> str:
        return self._ia.data['name']

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
        return self.client.get_application_command(self.id)

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
                    container[name] = ChatInputOption(option, self.guild, self.client, self._resolved)
                if type == OptionType.SUBCOMMAND.value:
                    family = option['name']
                    container[family] = DummyOption
                    new_options = option['options']
                    parsed = ChatInputOption._hybrid(family, new_options)
                    for new in parsed:
                        container[new['name']] = ChatInputOption(new, self.guild, self.client, self._resolved)
                if type == OptionType.SUBCOMMAND_GROUP.value:
                    origin = option['name']
                    container[origin] = DummyOption
                    for new_option in option['options']:
                        family = f"{origin}_{new_option['name']}"
                        parsed = ChatInputOption._hybrid(family, new_option['options'])
                        for new in parsed:
                            container[new['name']] = ChatInputOption(new, self.guild, self.client, self._resolved)
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
        if self._deferred:
            raise discord.ClientException('Cannot think for already (deferred / responded) interaction')
        await self._adapter.post_to_delay(ephemeral)
        self._deferred = True
        self._invisible = ephemeral

    async def think_for(self, time: float, ephemeral: bool = False):
        if self._deferred:
            raise discord.ClientException('Cannot think for already (deferred / responded) interaction')
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
            content: Optional[Union[str, Any]] = MISSING,
            *,
            tts: bool = False,
            nonce: Optional[int] = None,
            mention_author: bool = False,
            file: Optional[discord.File] = None,
            delete_after: Optional[float] = None,
            files: Sequence[discord.File] = None,
            embed: Optional[discord.Embed] = None,
            view: Optional[discord.ui.View] = None,
            views: Optional[List[discord.ui.View]] = None,
            stickers: Optional[List[discord.Sticker]] = None,
            embeds: Optional[List[Optional[discord.Embed]]] = None,
            allowed_mentions: Optional[discord.AllowedMentions] = None,
            reference: Optional[Union[Message, PartialMessage, MessageReference]] = None,
    ):
        if embed and embeds:
            raise TypeError('Can not mix embed and embeds')
        if file and files:
            raise TypeError('Can not mix file and files')
        if view and views:
            raise TypeError('Can not mix view and views')

        return await self._ia.channel.send(
            content=str(content), mention_author=mention_author, tts=tts,
            file=file, files=files, embed=embed, embeds=embeds, view=view, stickers=stickers,
            reference=reference, nonce=nonce, delete_after=delete_after, allowed_mentions=allowed_mentions)

    async def send_response(
            self,
            content: Optional[Union[str, Any]] = MISSING,
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
        if self._deferred:
            raise discord.ClientException('Cannot send response for already (deferred / responded) interaction')

        await self._adapter.post_response(
            tts=tts, view=view, file=file, files=files, views=views, embed=embed,
            embeds=embeds, content=content, ephemeral=ephemeral, allowed_mentions=allowed_mentions)
        self._deferred = True
        self._invisible = ephemeral
        self.original_message = await self._adapter.original_message()
        return self.original_message

    async def send_followup(
            self,
            content: Optional[Union[str, Any]] = MISSING,
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
        if not self._deferred:
            raise discord.ClientException('Cannot send followup to a non (deferred / responded) interaction')

        data = await self._adapter.post_followup(
            tts=tts, file=file, view=view, files=files, embed=embed, views=views,
            embeds=embeds, content=content, ephemeral=ephemeral, allowed_mentions=allowed_mentions)
        return Followup(self, data)


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
        data = await self._adapter.patch_response(
            content=content, file=file, files=files, embed=embed,
            embeds=embeds, view=view, views=views, allowed_mentions=allowed_mentions)
        return discord.Message(
            state=self.client._connection, data=data, channel=self.channel)  # type: ignore

    async def delete_response(self):
        if not self._invisible:
            await self._adapter.delete_response()


class Followup:
    def __init__(self, parent: Context, data: dict):
        self._data = data
        self._parent = parent
        self.message_id = int(data['id'])



    @property
    def message(self):
        return discord.Message(
            state=self._parent.client._connection, data=self._data, channel=self._parent.channel)

    async def delete(self):
        if not self._parent._invisible:
            await self._parent._adapter.delete_followup_message(self.message_id)

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
        data = await self._parent._adapter.patch_followup(
            message_id=self.message_id, content=content, file=file, files=files,
            embed=embed, embeds=embeds, view=view, views=views, allowed_mentions=allowed_mentions)

        return discord.Message(
            state=self._parent.client._connection, data=data, channel=self._parent.channel)
