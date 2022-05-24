import os
import sys
import aiohttp
import asyncio
import discord
import traceback
from aiotube import Search
import src.app_util as app_util


async def check(ctx: app_util.Context):
    if not ctx.options:
        await ctx.send_response(f'{ctx.author.mention} please select any valid option')
    else:
        return True


class Sample(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    @app_util.Cog.listener
    async def on_app_command_error(self, ctx: app_util.Context, error: Exception):
        if ctx.responded:
            await ctx.send_followup(f'**Error:** *{error}*')
        else:
            await ctx.send_response(f'**Error:** *{error}*')

    @app_util.Cog.default_permission(discord.Permissions.manage_guild)
    @app_util.Cog.command(
        name='greet', description='greet the user', dm_access=False,
        category=app_util.ApplicationCommandType.CHAT_INPUT,
        guild_id=877399405056102431
    )
    async def greet(self, ctx: app_util.Context):
        pass

    @greet.subcommand(name='hi', description='greet the user with hi')
    async def hello(self, ctx: app_util.Context):
        await ctx.send_response(f'Hi {ctx.author.mention}')

    @greet.subcommand(name='bye', description='greet the user with bye')
    async def bye(self, ctx: app_util.Context):
        await ctx.send_response(f'Bye {ctx.author.mention}')

    @app_util.Cog.command(
        name='search',
        description='search youtube video',
        dm_access=False,
        options=[
            app_util.StrOption(name='query', description='query to search', required=True),
        ],
        category=app_util.ApplicationCommandType.CHAT_INPUT
    )
    async def search(self, ctx: app_util.Context, query: str):
        video = Search.video(query)
        await ctx.send_response(f'{video.url}')

    @app_util.Cog.command(
        name='modal', description='sends a cool modal', dm_access=False,
        category=app_util.ApplicationCommandType.CHAT_INPUT
    )
    async def modal(self, ctx: app_util.Context):
        modal = app_util.Modal(f'Cool modal for {ctx.author.name}')
        modal.add_field(label='Name', custom_id='name')
        modal.add_field(label='Age', custom_id='age')
        modal.add_field(label='Gender', custom_id='gender')
        modal.add_field(label='Religion', custom_id='religion')
        await ctx.send_modal(modal)

        @modal.callback(self.bot)
        async def on_submit(mcx: app_util.Context, name: str, age: str, gender: str, religion: str):
            await mcx.send_response(f'**Name:** {name}'
                                    f'\n**Age:** {age}'
                                    f'\n**Gender:** {gender}'
                                    f'\n**Religion:** {religion}')


async def setup(bot: app_util.Bot):
    await bot.add_application_cog(Sample(bot))
