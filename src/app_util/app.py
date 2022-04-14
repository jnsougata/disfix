import json
import discord
from .modal import Modal
from discord.utils import MISSING
from discord.http import Route
from .enums import ApplicationCommandType, PermissionType
from typing import List, Optional, Union, Dict
from typing import Optional, Any, Union, Sequence, Iterable, NamedTuple, List, Dict



class ApplicationCommandOrigin:
    def __init__(self, name: str, type: ApplicationCommandType):
        self.name = name
        self.type = type
        if self.type is ApplicationCommandType.MESSAGE:
            self._qual = '__MESSAGE__' + name  # name for mapping
        elif self.type is ApplicationCommandType.USER:
            self._qual = '__USER__' + name  # name for mapping
        elif self.type is ApplicationCommandType.CHAT_INPUT:
            self._qual = '__CHAT__' + name


class Overwrite:
    def __init__(self, entity_id: int, entity_type: Union[discord.Role, discord.User], *, allow: bool = True):
        if isinstance(entity_type, discord.Role):
            type_value = PermissionType.ROLE.value
        elif isinstance(entity_type, discord.User):
            type_value = PermissionType.USER.value
        else:
            raise TypeError('entity type must be a discord.Role or discord.User')
        self._payload = {'id': str(id), 'type': type_value, 'permission': allow}

    def to_dict(self):
        return self._payload


# send / edit parameter handlers
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
            raise discord.errors.InvalidArgument('A message can have at most 10 embeds.')
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
                'name': 'file', 'value': file_.fp, 'filename': file_.filename,
                'content_type': 'application/octet-stream'
            }
        )
    else:
        for index, file_ in enumerate(fs):
            form.append(
                {
                    'name': f'file{index}', 'value': file_.fp, 'filename': file_.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return payload, form


def _handle_send_prams(
        *,
        content: Optional[Union[str, Any]] = MISSING,
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

    if content is not MISSING:
        payload['content'] = str(content)

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
        action_rows = [view.to_components() for view in views]
        for row in action_rows:
            container.extend(row)
        payload['components'] = container

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
                'name': 'file', 'value': file_.fp, 'filename': file_.filename,
                'content_type': 'application/octet-stream',
            }
        )
    else:
        for index, file_ in enumerate(fs):
            form.append(
                {
                    'name': f'file{index}', 'value': file_.fp, 'filename': file_.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return payload, form


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
