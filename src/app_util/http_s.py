import discord
from discord.http import Route
from .core import ApplicationCommand
from .app import BaseApplicationCommand



async def post_command(client, command, guild_id: int = None):
    if guild_id:
        r = Route('POST', f'/applications/{client.application_id}/guilds/{guild_id}/commands')
    else:
        r = Route('POST', f'/applications/{client.application_id}/commands')
    return await client.http.request(r, json=command.to_dict())


async def fetch_any_command(client, command_id: int, guild_id: int = None):
    if guild_id:
        r = Route('GET', f'/applications/{client.application_id}/guilds/{guild_id}/commands/{command_id}')
    else:
        r = Route('GET', f'/applications/{client.application_id}/commands/{command_id}')
    resp = await client.http.request(r)
    return ApplicationCommand(client, resp)


async def fetch_global_commands(client):
    r = Route('GET', f'/applications/{client.application_id}/commands')
    return await client.http.request(r)


async def fetch_guild_commands(client, guild_id: int):
    r = Route('GET', f'/applications/{client.application_id}/guilds/{guild_id}/commands')
    return await client.http.request(r)


async def fetch_overwrites(client, command_id: int, guild_id: int):
    r = Route('GET', f'/applications/{client.application_id}/guilds/{guild_id}/commands/{command_id}/permissions')
    return await client.http.request(r)


async def put_overwrites(client, command_id: int, guild_id: int, overwrites: dict):
    r = Route('PUT',
              f'/applications/{client.application_id}/guilds/{guild_id}/commands/{command_id}/permissions')
    return await client.http.request(r, json=overwrites)


async def delete_command(client, command_id: int, guild_id: int = None):
    if guild_id:
        r = Route('DELETE', f'/applications/{client.application_id}/guilds/{guild_id}/commands/{command_id}')
    else:
        r = Route('DELETE', f'/applications/{client.application_id}/commands/{command_id}')
    return await client.http.request(r)


async def patch_existing_command(client, old: ApplicationCommand, new: BaseApplicationCommand):
    if old.guild_specific:
        r = Route('PATCH', f'/applications/{old.application_id}/guilds/{old.guild_id}/commands/{old.id}')
    else:
        r = Route('PATCH', f'/applications/{old.application_id}/commands/{old.id}')
    return await client.http.request(r, json=new.to_dict())
