import os
import sys
import asyncio
import discord
import traceback
import src.disfix as extlib
from src.disfix import ModerationRule


async def check(ctx: disfix.Context):
    return True


class Sample(disfix.cog):

    def __init__(self, bot: disfix.Bot):
        self.bot = bot

    @disfix.cog.listener
    async def on_app_command_error(self, ctx: disfix.Context, error: Exception):
        if ctx.responded:
            await ctx.send_followup(f'**Error:** *{error}*')
        else:
            await ctx.send_response(f'**Error:** *{error}*')

    @disfix.cog.default_permission(discord.Permissions.manage_guild)
    @disfix.cog.command(
        name='greet', description='greet the user', dm_access=True,
        category=disfix.CommandType.SLASH,
    )
    async def greet(self, ctx: disfix.Context):
        pass

    @greet.subcommand(name='hi', description='greet the user with hi')
    async def hello(self, ctx: disfix.Context):
        await ctx.send_response(f'Hi {ctx.author.mention}')

    @greet.subcommand(name='bye', description='greet the user with bye')
    async def bye(self, ctx: disfix.Context):
        await ctx.send_response(f'Bye {ctx.author.mention}')

    @disfix.cog.command(
        name='modal', description='sends a cool modal', dm_access=False,
        category=disfix.CommandType.SLASH
    )
    async def modal(self, ctx: disfix.Context):
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
        modal = disfix.Modal(f'{ctx.author}\'s Selection Modal')
        modal.add_field(label='Name', custom_id='name', required=True)
        modal.add_field(label='Age', custom_id='age', required=True)
        modal.add_component(select)
        modal.add_component(select_x)
        await ctx.send_modal(modal)

        @modal.callback(self.bot)
        async def on_submit(mcx: disfix.Context, name: str, age: str, gender: tuple, os_: tuple):
            await mcx.send_response(f'**Name:** {name}'
                                    f'\n**Age:** {age}'
                                    f'\n**Gender:** {gender[0]}'
                                    f'\n**Operating system:** {os_[0]}')

    @disfix.cog.command(
        name='automod',
        description='adds moderation rule to server',
        category=disfix.CommandType.SLASH,
        dm_access=False
    )
    async def auto_mod(self, ctx: disfix.Context):

        rule = ModerationRule(
            name=f'{self.bot.user.name.lower()}-moderation-rule',
            event_type=disfix.AutoModEvent.MESSAGE_SEND,
            trigger_type=disfix.AutoModTrigger.KEYWORD_PRESET,
        )
        rule.add_action(disfix.AutoModAction.block_message())
        rule.add_action(disfix.AutoModAction.send_alert_message(987173252306702346))
        rule.add_trigger_metadata(disfix.TriggerMetadata.keyword_preset_filter(
            [disfix.KeywordPresets.SEXUAL_CONTENT, disfix.KeywordPresets.SLURS, disfix.KeywordPresets.PROFANITY]
        ))
        await self.bot.create_rule(rule, ctx.guild.id)
        await ctx.send_response(f'Auto moderation `{rule.to_dict()["name"]}` added to this server!')


async def setup(bot: disfix.Bot):
    await bot.add_application_cog(Sample(bot))
