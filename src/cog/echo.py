from src.application.commands import SlashCog, ApplicationContext
from src.application import *


class Echo(SlashCog):
    def __init__(self, bot):
        self.bot = bot

    def register(self):
        return SlashCommand(
            name='echo',
            description='repeats a phrase',
            options=[StrOption('phrase', 'The message to echo', required=True)]
        )

    async def command(self, appctx: ApplicationContext):
        message = appctx.options[0].value
        await appctx.respond(f'**{message}**')


def setup(bot):
    return Echo(bot)
