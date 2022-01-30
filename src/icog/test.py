from src.application.commands import SlashCog, ApplicationContext
from src.application import *


class Test(SlashCog):
    def __init__(self, bot):
        self.bot = bot

    def register(self):
        return SlashCommand(
            name='test',
            description='Test command',
            options=[
                StrOption(name='message', description='Test option'),
            ]
        )

    async def command(self, ctx: ApplicationContext):
        await ctx.respond(f'{ctx.name} {ctx.options[0].value}')


def setup(bot):
    return Test(bot)
