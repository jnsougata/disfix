import json
import discord
from .modal import Modal
from discord.http import Route
from discord.utils import MISSING
from .enums import ApplicationCommandType
from typing import Optional, Any, Union, List, Dict, Sequence


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
