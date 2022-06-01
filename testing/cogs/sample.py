import os
import sys
import aiohttp
import asyncio
import discord
import traceback
import src.extlib as extlib


async def check(ctx: extlib.Context):
    return True


class Sample(extlib.cog):

    def __init__(self, bot: extlib.Bot):
        self.bot = bot

    @extlib.cog.listener
    async def on_app_command_error(self, ctx: extlib.Context, error: Exception):
        if ctx.responded:
            await ctx.send_followup(f'**Error:** *{error}*')
        else:
            await ctx.send_response(f'**Error:** *{error}*')

    @extlib.cog.default_permission(discord.Permissions.manage_guild)
    @extlib.cog.command(
        name='greet', description='greet the user', dm_access=True,
        category=extlib.CommandType.SLASH,
    )
    async def greet(self, ctx: extlib.Context):
        pass

    @greet.subcommand(name='hi', description='greet the user with hi')
    async def hello(self, ctx: extlib.Context):
        await ctx.send_response(f'Hi {ctx.author.mention}')

    @greet.subcommand(name='bye', description='greet the user with bye')
    async def bye(self, ctx: extlib.Context):
        await ctx.send_response(f'Bye {ctx.author.mention}')

    @extlib.cog.command(
        name='modal', description='sends a cool modal', dm_access=False,
        category=extlib.CommandType.SLASH
    )
    async def modal(self, ctx: extlib.Context):
        select = discord.ui.Select(
            custom_id='gender',
            placeholder='select gender',
            max_values=1,
            min_values=1,
            options=[
                discord.SelectOption(label='Male', value='m'),
                discord.SelectOption(label='Female', value='f'),
                discord.SelectOption(label='Others', value='o'),
            ]
        )
        select_x = discord.ui.Select(
            custom_id='os',
            placeholder='select os',
            max_values=1,
            min_values=1,
            options=[
                discord.SelectOption(label='iOS', value='ios'),
                discord.SelectOption(label='Android', value='android'),
                discord.SelectOption(label='MacOS', value='macos'),
                discord.SelectOption(label='Windows', value='windows'),
                discord.SelectOption(label='Linux', value='linux'),
            ]
        )
        modal = extlib.Modal(f'{ctx.author}\'s Selection Modal')
        modal.add_field(label='Name', custom_id='name', required=True)
        modal.add_field(label='Age', custom_id='age', required=True)
        modal.add_component(select)
        modal.add_component(select_x)
        await ctx.send_modal(modal)

        @modal.callback(self.bot)
        async def on_submit(mcx: extlib.Context, name: str, age: str, gender: tuple, os: tuple):
            await mcx.send_response(f'**Name:** {name}'
                                    f'\n**Age:** {age}'
                                    f'\n**Gender:** {gender[0]}'
                                    f'\n**Operating system:** {os[0]}')

    @extlib.cog.command(name='perms', description='handles permissions', category=extlib.CommandType.SLASH)
    async def perms(self, ctx: extlib.Context):
        pass

    @perms.subcommand_group(name='add', description='adds a permission')
    async def add(self, ctx: extlib.Context):
        pass

    @perms.subcommand_group(name='remove', description='removes a permission')
    async def remove(self, ctx: extlib.Context):
        pass

    @add.subcommand(name='role', description='adds a role permission')
    async def add_role(self, ctx: extlib.Context, role: discord.Role):
        pass

    @remove.subcommand(name='role', description='removes a role permission')
    async def remove_role(self, ctx: extlib.Context, role: discord.Role):
        pass


async def setup(bot: extlib.Bot):
    await bot.add_application_cog(Sample(bot))
