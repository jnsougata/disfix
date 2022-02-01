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
from src.extslash.commands import Client, SlashCog, ApplicationContext


class Echo(SlashCog):
    def __init__(self, bot: Client):
        self.bot = bot

    def register(self):
        return SlashCommand(
            name='echo',
            description='echos back a given message',
            options=[
                UserOption('anything', 'something user based'),
            ],
            permissions=[
                SlashPermission.for_user(516649677001719819),
                SlashPermission.for_role(921001978916642856, allow=False),
            ],
        )

    async def command(self, appctx: ApplicationContext):
        async with appctx.thinking:
            # doing some heavy task
            # maximum time is 15min ig
            # await asyncio.sleep(900)
            # sending followup after
            value = appctx.options[0].value
            await appctx.followup.send(value.avatar.url)


def setup(bot: Client):
    bot.add_slash_cog(Echo(bot), 877399405056102431)
    # add guild if you want to limit the command to a specific guild
    # if you to register the command to all guilds, you can leave it empty
    # global commands take 1hour to register for the first time for all guilds
