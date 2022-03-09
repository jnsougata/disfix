from __future__ import annotations
import asyncio
import json
import discord
from discord.http import Route
from discord.utils import MISSING
from discord.ext import commands
from .modal import Modal
from .input_chat import Choice
from .enums import ApplicationCommandType, OptionType, try_enum
from discord import Message, PartialMessage, MessageReference
from .app import _handle_edit_params, _handle_send_prams, Adapter
from .core import InteractionData, SlashCommandOption, Resolved, ApplicationCommand, DummyOption
from typing import Optional, Any, Union, Sequence, Iterable, NamedTuple, List, Dict, Tuple, Coroutine



class Context:
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        self._deferred = False
        self._invisible = False
        self.original_message: Optional[discord.Message] = None

    def __repr__(self):
        return self.name

    @property
    def client(self) -> discord.Client:
        """
        Returns the client of the interaction
        """
        return self.interaction.client

    @property
    def _adapter(self):
        return Adapter(self.interaction)


    @property
    def type(self) -> ApplicationCommandType:
        """
        Returns the type of the invoked application command
        """
        return try_enum(ApplicationCommandType, self.interaction.data['type'])

    @property
    def name(self) -> str:
        """
        Returns the name of the invoked application command
        """
        return self.interaction.data['name']

    @property
    def description(self) -> str:
        """
        Returns the description of the invoked application command
        """
        return self.interaction.data['description']

    @property
    def token(self) -> str:
        """
        Returns the token of the application command interaction
        """
        return self.interaction.token

    @property
    def id(self) -> int:
        """
        Returns the id of the interaction
        """
        return int(self.interaction.data['id'])

    @property
    def command(self) -> ApplicationCommand:
        """
        Returns the invoked application command object
        """
        return self.client.get_application_command(self.id)

    @property
    def version(self) -> int:
        """
        Returns the version of the interaction
        """
        return self.interaction.version

    @property
    def data(self) -> InteractionData:
        """
        Returns the application command data
        """
        return InteractionData(**self.interaction.data)

    @property
    def _modal_values(self):
        options = {}
        for comp in self.data.components:
            for sub_comp in comp['components']:
                options[sub_comp['custom_id']] = sub_comp['value']
        return options


    @property
    def _resolved(self):
        r_data = self.data.resolved
        return Resolved(r_data, self) if r_data else None

    @property
    def _target_message(self):
        if self.type is ApplicationCommandType.MESSAGE:
            message_id = int(self.data.target_id)
            return self._resolved.messages[message_id]

    @property
    def _target_user(self):
        if self.type is ApplicationCommandType.USER:
            user_id = int(self.data.target_id)
            return self._resolved.users[user_id]

    @property
    def options(self) -> Dict[str, SlashCommandOption]:
        """
        Returns the dictionary of the options of the invoked application command
        if the command is a message/user command, this will return an empty dictionary
        """
        if self.type is ApplicationCommandType.USER:
            return {}  # type: ignore
        if self.type is ApplicationCommandType.MESSAGE:
            return {}  # type: ignore
        return self._parsed_options

    @property
    def _parsed_options(self) -> Dict[str, SlashCommandOption]:
        container = {}
        options = self.data.options
        if options:
            for option in options:
                type = option['type']
                name = option['name']
                if type > OptionType.SUBCOMMAND_GROUP.value:
                    container[name] = SlashCommandOption(self, option)
                if type == OptionType.SUBCOMMAND.value:
                    family = option['name']
                    container[family] = DummyOption
                    new_options = option['options']
                    parsed = SlashCommandOption._hybrid(family, new_options)
                    for new in parsed:
                        container[new['name']] = SlashCommandOption(self, new)
                if type == OptionType.SUBCOMMAND_GROUP.value:
                    origin = option['name']
                    container[origin] = DummyOption
                    for new_option in option['options']:
                        family = f"{origin}_{new_option['name']}"
                        parsed = SlashCommandOption._hybrid(family, new_option['options'])
                        for new in parsed:
                            container[new['name']] = SlashCommandOption(self, new)
            return container
        return {}

    @property
    def application_id(self) -> int:
        """
        Returns the application id or client id of the application command
        """
        return self.interaction.application_id

    @property
    def responded(self) -> bool:
        """
        Returns whether the application command interaction is deferred
        """
        return self._deferred

    async def defer(self, ephemeral: bool = False) -> None:
        """
        Defers the application command interaction for responding later
        """
        if self._deferred:
            raise discord.ClientException('Cannot defer already deferred or responded interaction')
        await self._adapter.post_to_delay(ephemeral)
        self._deferred = True
        self._invisible = ephemeral

    def thinking(self, time: float, author_only: bool = False):
        """
        Returns async context manager for controlling the thinking state
        during the application command and the visibility of the response
        """
        return _Thinking(self, time, author_only)


    @property
    def permissions(self) -> discord.Permissions:
        """
        Returns the permissions of the user who used the command
        for the channel on which the command was used
        """
        return self.interaction.permissions

    @property
    def me(self) -> discord.Member:
        """
        Returns the client user in member form if guild is available
        """
        if self.guild:
            return self.guild.me

    @property
    def channel(self) -> discord.abc.GuildChannel:
        """
        Returns the channel on which the command was used
        """
        channel = self.interaction.channel

        if not self.guild:
            return channel  # type: ignore

        return self.guild.get_channel(channel.id)

    @property
    def guild(self) -> discord.Guild:
        """
        Returns the guild where the command was used
        """
        return self.interaction.guild

    @property
    def author(self) -> discord.Member:
        """
        Returns the author of the application command as discord.Member
        If the author is not in the guild, returns the discord.User
        """
        return self.interaction.user

    async def send_modal(self, modal: Modal):
        """
        Sends a modal as a response to the application command
        """
        await self._adapter.post_modal(modal=modal)

    async def send_automated_choices(self, choices: List[Choice]):
        """
        Sends an automated choices list to application command UI
        """
        await self._adapter.post_autocomplete_response(choices)


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
        """
        Sends a message to the channel on which the application command was used
        """
        if embed and embeds:
            raise ValueError('Can not mix embed and embeds')
        if file and files:
            raise ValueError('Can not mix file and files')
        if view and views:
            raise ValueError('Can not mix view and views')

        return await self.interaction.channel.send(
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
            delete_after: Optional[float] = None,
    ) -> discord.Message:
        """
        Sends a response to the application command
        """
        if self._deferred:
            raise discord.ClientException('Cannot send response for already (deferred / responded) interaction')

        await self._adapter.post_response(
            tts=tts, view=view, file=file, files=files, views=views, embed=embed,
            embeds=embeds, content=content, ephemeral=ephemeral, allowed_mentions=allowed_mentions)
        self._deferred = True
        self._invisible = ephemeral
        self.original_message = await self._adapter.original_message()
        if delete_after:
            await self.original_message.delete(delay=delete_after)
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
            views: Optional[List[discord.ui.View]] = None,
            delete_after: Optional[float] = None,
    ) -> Followup:
        """
        Sends a followup to the responded or deferred application command
        """
        if not self._deferred:
            raise discord.ClientException('Cannot send followup to a non (deferred / responded) interaction')

        data = await self._adapter.post_followup(
            tts=tts, file=file, view=view, files=files, embed=embed, views=views,
            embeds=embeds, content=content, ephemeral=ephemeral, allowed_mentions=allowed_mentions)

        followup_message = Followup(self, data)

        async def delay_delete(time: float):
            await asyncio.sleep(time)
            try:
                await followup_message.delete()
            except discord.HTTPException:
                pass
        if delete_after:
            asyncio.create_task(delay_delete(delete_after))

        return followup_message


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
            views: Optional[List[discord.ui.View]] = MISSING,
            delete_after: Optional[float] = None,
    ):
        """
        Edits the original response to the application command
        """
        data = await self._adapter.patch_response(
            content=content, file=file, files=files, embed=embed,
            embeds=embeds, view=view, views=views, allowed_mentions=allowed_mentions)
        if delete_after:
            await self.original_message.delete(delay=delete_after)
        return discord.Message(
            state=self.client._connection, data=data, channel=self.channel)  # type: ignore

    async def delete_response(self):
        """
        Deletes the original response to the application command
        if the original message is ephemeral, it can't be deleted
        """
        if not self._invisible:
            await self._adapter.delete_response()


class Followup:
    """
    Represents a followup to an application command
    """
    def __init__(self, parent: Context, data: dict):
        self._data = data
        self._parent = parent
        self.message_id = int(data['id'])


    @property
    def message(self):
        """
        Returns the message object for this followup
        """
        return discord.Message(
            state=self._parent.client._connection, data=self._data, channel=self._parent.channel)  # type: ignore

    async def delete(self):
        """
        Deletes this followup if it is not ephemeral
        """
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
            delete_after: Optional[float] = None,
    ):
        """
        Edits this followup, does not care if it is ephemeral or not
        """
        data = await self._parent._adapter.patch_followup(
            message_id=self.message_id, content=content, file=file, files=files,
            embed=embed, embeds=embeds, view=view, views=views, allowed_mentions=allowed_mentions)

        async def delay_delete(time: float):
            await asyncio.sleep(time)
            try:
                await self.message.delete()
            except discord.HTTPException:
                pass
        if delete_after:
            asyncio.create_task(delay_delete(delete_after))

        return discord.Message(
            state=self._parent.client._connection, data=data, channel=self._parent.channel)  # type: ignore


class _Thinking:
    """
    Represents a contextmanager for controlling the thinking indicator
    """
    def __init__(self, ctx, time, ep):
        self.ep = ep
        self.ctx = ctx
        self.time = time

    async def __aenter__(self):
        try:
            await self.ctx.defer(self.ep)
        finally:
            await asyncio.sleep(self.time)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
