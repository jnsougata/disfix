import os
import sys
import aiohttp
import asyncio
import discord
import traceback
from aiotube import Search
import src.extlib as extlib


async def check(ctx: extlib.Context):
    if not ctx.options:
        await ctx.send_response(f'{ctx.author.mention} please select any valid option')
    else:
        return True


class Sample(extlib.Cog):

    def __init__(self, bot: extlib.Bot):
        self.bot = bot

    @extlib.Cog.listener
    async def on_app_command_error(self, ctx: extlib.Context, error: Exception):
        if ctx.responded:
            await ctx.send_followup(f'**Error:** *{error}*')
        else:
            await ctx.send_response(f'**Error:** *{error}*')

    @extlib.Cog.default_permission(discord.Permissions.manage_guild)
    @extlib.Cog.command(
        name='greet', description='greet the user', dm_access=False,
        category=extlib.CommandType.SLASH,
        guild_id=877399405056102431
    )
    async def greet(self, ctx: extlib.Context):
        pass

    @greet.subcommand(name='hi', description='greet the user with hi')
    async def hello(self, ctx: extlib.Context):
        await ctx.send_response(f'Hi {ctx.author.mention}')

    @greet.subcommand(name='bye', description='greet the user with bye')
    async def bye(self, ctx: extlib.Context):
        await ctx.send_response(f'Bye {ctx.author.mention}')

    @extlib.Cog.command(
        name='search',
        description='search youtube video',
        dm_access=False,
        options=[
            extlib.StrOption(name='query', description='query to search', required=True),
        ],
        category=extlib.CommandType.SLASH
    )
    async def search(self, ctx: extlib.Context, query: str):
        video = Search.video(query)
        await ctx.send_response(f'{video.url}')

    @extlib.Cog.command(
        name='modal', description='sends a cool modal', dm_access=False,
        category=extlib.CommandType.SLASH
    )
    async def modal(self, ctx: extlib.Context):
        modal = extlib.Modal(f'Cool modal for {ctx.author.name}')
        modal.add_field(label='Name', custom_id='name')
        modal.add_field(label='Age', custom_id='age')
        modal.add_field(label='Gender', custom_id='gender')
        modal.add_field(label='Religion', custom_id='religion')
        await ctx.send_modal(modal)

        @modal.callback(self.bot)
        async def on_submit(mcx: extlib.Context, name: str, age: str, gender: str, religion: str):
            await mcx.send_response(f'**Name:** {name}'
                                    f'\n**Age:** {age}'
                                    f'\n**Gender:** {gender}'
                                    f'\n**Religion:** {religion}')


async def setup(bot: extlib.Bot):
    await bot.add_application_cog(Sample(bot))
