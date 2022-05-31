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
            custom_id='select',
            placeholder='Select an option',
            max_values=1,
            min_values=1,
            options=[
                discord.SelectOption(label='OP1', value='1'),
                discord.SelectOption(label='OP2', value='2'),
                discord.SelectOption(label='OP3', value='3'),
            ]
        )
        modal = extlib.Modal(f'{ctx.author}\'s Selection Modal')
        modal.add_component(select)
        modal.add_field(label='Name', custom_id='name', required=True)
        await ctx.send_modal(modal)

        @modal.callback(self.bot)
        async def on_submit(mcx: extlib.Context, name: str, age: str, gender: str, religion: str):
            await mcx.send_response(f'**Name:** {name}'
                                    f'\n**Age:** {age}'
                                    f'\n**Gender:** {gender}'
                                    f'\n**Religion:** {religion}')

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
