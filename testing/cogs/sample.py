import os
import sys
import asyncio
import discord
import traceback
import src.extlib as extlib
from src.extlib import ModerationRule


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
                discord.SelectOption(label='Male', value='Male'),
                discord.SelectOption(label='Female', value='Female'),
                discord.SelectOption(label='Others', value='Others'),
            ]
        )
        select_x = discord.ui.Select(
            custom_id='os_',
            placeholder='select os',
            max_values=1,
            min_values=1,
            options=[
                discord.SelectOption(label='iOS', value='iOS'),
                discord.SelectOption(label='Android', value='Android'),
                discord.SelectOption(label='MacOS', value='MacOS'),
                discord.SelectOption(label='Windows', value='Windows'),
                discord.SelectOption(label='Linux', value='Linux'),
            ]
        )
        modal = extlib.Modal(f'{ctx.author}\'s Selection Modal')
        modal.add_field(label='Name', custom_id='name', required=True)
        modal.add_field(label='Age', custom_id='age', required=True)
        modal.add_component(select)
        modal.add_component(select_x)
        await ctx.send_modal(modal)

        @modal.callback(self.bot)
        async def on_submit(mcx: extlib.Context, name: str, age: str, gender: tuple, os_: tuple):
            await mcx.send_response(f'**Name:** {name}'
                                    f'\n**Age:** {age}'
                                    f'\n**Gender:** {gender[0]}'
                                    f'\n**Operating system:** {os_[0]}')

    @extlib.cog.command(
        name='automod',
        description='adds moderation rule to server',
        category=extlib.CommandType.SLASH,
        dm_access=False
    )
    async def auto_mod(self, ctx: extlib.Context):

        rule = ModerationRule(
            name=f'{self.bot.user.name.lower()}-moderation-rule',
            event_type=extlib.AutoModEvent.MESSAGE_SEND,
            trigger_type=extlib.AutoModTrigger.KEYWORD_PRESET,
        )
        rule.add_action(extlib.AutoModAction.block_message())
        rule.add_action(extlib.AutoModAction.send_alert_message(987173252306702346))
        rule.add_trigger_metadata(extlib.TriggerMetadata.keyword_preset_filter(
            [extlib.KeywordPresets.SEXUAL_CONTENT, extlib.KeywordPresets.SLURS, extlib.KeywordPresets.PROFANITY]
        ))
        await self.bot.create_rule(rule, ctx.guild.id)
        await ctx.send_response(f'Auto moderation `{rule.to_dict()["name"]}` added to this server!')


async def setup(bot: extlib.Bot):
    await bot.add_application_cog(Sample(bot))
