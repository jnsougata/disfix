from extslash import *
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
        await appctx.respond(f'**{appctx.options[0].value}**')


def setup(bot: Client):
    return Echo(bot)
