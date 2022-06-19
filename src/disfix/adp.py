import json
import discord
from .modal import Modal
from discord.http import Route
from discord.utils import MISSING
from .utils import _handle_send_prams, _handle_edit_params
from typing import Optional, Any, Union, List, Dict, Sequence


class Adapter:
    def __init__(self, interaction: discord.Interaction):
        self.ia = interaction
        self.id = interaction.id
        self.token = interaction.token
        self.client = interaction.client
        self.application_id = interaction.application_id

    async def original_message(self):
        return await self.ia.original_message()

    async def post_modal(self, *, modal: Modal):
        r = Route('POST', f'/interactions/{self.id}/{self.token}/callback')
        await self.client.http.request(r, json=modal.to_payload())

    async def post_to_delay(self, ephemeral: bool = False):
        route = Route('POST', f'/interactions/{self.id}/{self.token}/callback')
        payload = {'type': 5}
        if ephemeral:
            payload['data'] = {'flags': 64}
        await self.client.http.request(route, json=payload)

    async def post_autocomplete_response(self, choices) -> None:
        r = Route('POST', f'/interactions/{self.id}/{self.token}/callback')
        payload = {'type': 8, 'data': {'choices': [c.data for c in choices]}}
        try:
            await self.client.http.request(r, json=payload)
        except discord.errors.NotFound:
            pass

    async def post_response(
            self, content:
            Optional[Union[str, Any]] = MISSING,
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
        payload, form = _handle_send_prams(
            content=content, tts=tts, file=file, files=files, embed=embed, embeds=embeds,
            view=view, views=views, ephemeral=ephemeral, allowed_mentions=allowed_mentions)

        data = {'name': 'payload_json', 'value': json.dumps({'type': 4, 'data': payload})}

        form.insert(0, data)  # type: ignore
        r = Route('POST', f'/interactions/{self.id}/{self.token}/callback')
        await self.client.http.request(r, form=form, files=files)

        message = await self.original_message()
        if view:
            self.client._connection.store_view(view, message.id)
        if views:
            for view in views:
                self.client._connection.store_view(view, message.id)

    async def post_followup(
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
        payload, form = _handle_send_prams(
            content=content, tts=tts, file=file, files=files, embed=embed, embeds=embeds,
            view=view, views=views, ephemeral=ephemeral, allowed_mentions=allowed_mentions)

        payload['wait'] = True
        data = {'name': 'payload_json', 'value': json.dumps(payload)}

        form.insert(0, data)  # type: ignore
        r = Route('POST', f'/webhooks/{self.application_id}/{self.token}')
        message_data = await self.client.http.request(r, form=form, files=files)
        message_id = int(message_data['id'])
        if view:
            self.client._connection.store_view(view, message_id)
        if views:
            for view in views:
                self.client._connection.store_view(view, message_id)
        return message_data

    async def patch_response(
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
            content=content, file=file, files=files, embed=embed,
            embeds=embeds, view=view, views=views, allowed_mentions=allowed_mentions)

        data = {'name': 'payload_json', 'value': json.dumps(payload)}

        form.insert(0, data)  # type: ignore
        r = Route('PATCH', f'/webhooks/{self.application_id}/{self.token}/messages/@original')
        message_data = await self.client.http.request(r, form=form, files=files)
        message_id = int(message_data['id'])
        if view is not MISSING and view is not None:
            self.client._connection.store_view(view, message_id)
        elif views is not MISSING and views is not None:
            for v in views:
                self.client._connection.store_view(v, message_id)
        return message_data

    async def delete_response(self):
        r = Route('DELETE', f'/webhooks/{self.application_id}/{self.token}/messages/@original')
        await self.client.http.request(r)

    async def patch_followup(
            self,
            message_id: int,
            *,
            content: Optional[Union[str, Any]] = MISSING,
            embed: Optional[discord.Embed] = MISSING,
            embeds: Optional[List[discord.Embed]] = MISSING,
            allowed_mentions: Optional[discord.AllowedMentions] = MISSING,
            file: Optional[discord.File] = MISSING,
            files: Optional[List[discord.File]] = MISSING,
            view: Optional[discord.ui.View] = MISSING,
            views: Optional[List[discord.ui.View]] = MISSING,
    ):
        payload, form = _handle_edit_params(
            content=content, file=file, files=files, embed=embed,
            embeds=embeds, view=view, views=views, allowed_mentions=allowed_mentions)

        payload['wait'] = True
        data = {'name': 'payload_json', 'value': json.dumps(payload)}

        form.insert(0, data)  # type: ignore
        route = Route('PATCH', f'/webhooks/{self.application_id}/{self.token}/messages/{message_id}')
        message_data = await self.client.http.request(route, form=form, files=files)
        if view is not MISSING and view is not None:
            self._parent.client._connection.store_view(view, message_id)
        elif views is not MISSING and views is not None:
            for view in views:
                self._parent.client._connection.store_view(view, message_id)
        return message_data

    async def delete_followup_message(self, message_id: int):
        r = Route('DELETE', f'/webhooks/{self.application_id}/{self.token}/messages/{message_id}')
        await self.client.http.request(r)
