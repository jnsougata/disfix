import json
import os
import discord
from discord.ext import commands, tasks
from src.extslash import (
    Client,
    SlashCommand,
    ApplicationContext,
    StrOption,
    IntOption,
    BoolOption,
    ChannelOption,
    RoleOption,
    UserOption,
    NumberOption,
    MentionableOption,
    Choice,
)


intents = discord.Intents.default()
intents.members = True


class MyBot(Client):
    def __init__(self):
        super().__init__(command_prefix='-', help_command=None, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()


@bot.slash_command(
    command=SlashCommand(
        name='echo',
        description='repeats a phrase',
        options=[StrOption('phrase', 'The message to echo', required=True)]),
    guild_id=877399405056102431)
async def test(appctx: ApplicationContext):
    message = appctx.options[0].value
    await appctx.respond(f'**{appctx.author}** said: {message}')


@bot.command(name='delcmd')
async def appcmd_(ctx: commands.Context, command_name: str):
    cmds = await bot.fetch_application_commands()
    for cmd in cmds:
        if cmd.name == command_name:
            await bot.delete_application_command(cmd.id)
            await ctx.send(f'Done, Application Command Deleted: **{cmd}**')
            return
    else:
        await ctx.send(f'Command not found: **{command_name}**')

bot.run(os.getenv('DISCORD_TOKEN'))
