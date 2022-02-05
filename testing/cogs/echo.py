import asyncio
import discord
from src.extslash import (
    SlashCommand,
    SubCommandGroup,
    SubCommand,
    StrOption,
    IntOption,
    BoolOption,
    RoleOption,
    UserOption,
    ChannelOption,
    NumberOption,
    MentionableOption,
    SlashPermission,
    Choice,
)  # rather use: from extslash import *
from src.extslash.commands import Bot, SlashCog, ApplicationContext
import traceback


class Echo(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def register(self):
        return SlashCommand(
            name='echo',
            description='echos back a given message',
            options=[
                StrOption('anything', 'something user based'),
            ],
            permissions=[
                SlashPermission.for_user(516649677001719819),
                SlashPermission.for_role(921001978916642856),
            ],
        )

    async def command(self, ctx: ApplicationContext):
        if ctx.permissions.administrator:
            value = ctx.options[0].value
            #resp = await ctx.send_response(f'You used `/{ctx.command_name}` (ID: {ctx.command_id})')
            resp = await ctx.send_followup(f'{value}')
            await asyncio.sleep(5)
            await resp.edit('This is an edited followup message', file=discord.File('cogs/echo.py'))

        else:
            await ctx.send_response('you are not allowed to use this command')


def setup(bot: Bot):
    bot.add_slash_cog(Echo(bot), 877399405056102431)
    # add guild if you want to limit the command to a specific guild
    # if you to register the command to all guilds, you can leave it empty
    # global commands take 1hour to register for the first time for all guilds
