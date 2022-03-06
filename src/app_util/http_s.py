import discord
from .core import ApplicationCommand
from discord.http import Route


async def fetch_permissions(client, command_id: int, guild_id: int):
    r = Route('GET', f'/applications/{client.application_id}/guilds/{guild_id}/commands/{command_id}/permissions')
    return await client.http.request(r)


async def sync_local(client, command, guild_id):
    if guild_id:
        r = Route('POST', f'/applications/{client.application_id}/guilds/{guild_id}/commands')
        resp = await client.http.request(r, json=command.to_dict())
        command_id = int(resp['id'])
        if command.overwrites:
            r = Route(
                'PUT',
                f'/applications/{client.application_id}/guilds/{guild_id}/commands/{resp["id"]}/permissions')
            perms = await client.http.request(r, json=command.overwrites)
            resp['permissions'] = {guild_id: {int(p['id']): p['permission'] for p in perms['permissions']}}
        else:
            try:
                x = await fetch_permissions(client, command_id, guild_id)
            except discord.errors.NotFound:
                pass
            else:
                resp['permissions'] = {guild_id: x['permissions']}
    else:
        r = Route('POST', f'/applications/{client.application_id}/commands')
        resp = await client.http.request(r, json=command.to_dict())
    client._application_commands[int(resp['id'])] = ApplicationCommand(client, resp)


async def sync_global(client):
    r = Route('GET', f'/applications/{client.application_id}/commands')
    resp = await client.http.request(r)
    for data in resp:
        apc = ApplicationCommand(client, data)
        client._application_commands[apc.id] = apc


async def guild_specific_sync(client, guild: discord.Guild):
    r = Route('GET', f'/applications/{client.application_id}/guilds/{guild.id}/commands')
    resp = await self.http.request(r)
    for data in resp:
        apc = ApplicationCommand(client, data)
        client._application_commands[apc.id] = apc


async def fetch_any(client, command_id: int, guild_id: int = None):
    if guild_id:
        route = Route('GET', f'/applications/{client.application_id}/guilds/{guild_id}/commands/{command_id}')
    else:
        route = Route('GET', f'/applications/{client.application_id}/commands/{command_id}')
    resp = await client.http.request(route)
    return ApplicationCommand(client, resp)


async def fetch_by_guild(client, guild_id: int):
    r = Route('GET', f'/applications/{client.application_id}/guilds/{guild_id}/commands')
    return await client.http.request(r)
