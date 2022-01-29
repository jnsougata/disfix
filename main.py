import os
import discord
from discord.ext import commands, tasks
from src.extslash import ExtendedClient, SlashCommand, ApplicationCommand


intents = discord.Intents.default()
intents.members = True


class MyBot(ExtendedClient):
    def __init__(self):
        super().__init__(command_prefix='-', help_command=None, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()


@bot.slash_command(
    command=SlashCommand(
        name='echo',
        description='Echo a message',
        options=[
            SlashCommand.str_option('message', 'The message to echo', required=True),
            SlashCommand.int_option('times', 'The number of times to echo the message', required=True),
            SlashCommand.bool_option('upper', 'Whether to uppercase the message', required=True),
            SlashCommand.user_option('user', 'The user to echo to', required=True),
        ]),
    guild_id=877399405056102431)
async def test(appctx: ApplicationCommand):
    message = appctx.options[0].value
    user_id = appctx.options[3].value
    await appctx.defer()
    user = appctx.guild.get_member(int(user_id))
    await appctx.followup.send(f'{user.mention} said: {message}')


bot.run(os.getenv('DISCORD_TOKEN'))
