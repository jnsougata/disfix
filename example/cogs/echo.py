import asyncio
from extslash import (
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
    MentionableOption,)  # rather use: from extslash import *
from extslash.commands import SlashCog, ApplicationContext, Client


class Echo(SlashCog):
    def __init__(self, bot: Client):
        self.bot = bot

    def register(self):
        return SlashCommand(
            name='echo',
            description='echos back a given message',
            options=[
                StrOption(
                    name='message',
                    description='the message to echo back',
                    required=True
                )
            ]
        )

    async def command(self, appctx: ApplicationContext):
        async with appctx.thinking:
            # doing some heavy task
            # maximum time is 15min ig
            await asyncio.sleep(5)
            # sending followup message
            await appctx.followup.send(f'**{appctx.options[0].value}**')


def setup(bot: Client):
    bot.add_slash_cog(Echo(bot), 877399405056102431)
    # add guild if you want to limit the command to a specific guild
    # if you to register the command to all guilds, you can leave it empty
    # global commands take 1hour to register for the first time for all guilds
