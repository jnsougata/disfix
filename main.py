import json
import os
import discord
from discord.ext import commands, tasks
from src.application import (
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
    SubCommand,
    SubCommandGroup,
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


@bot.slash_command(
    command=SlashCommand(
        name='animal',
        description='gives an animal image',
        options=[
            SubCommandGroup(
                name='domestic',
                description='domestic animals',
                options=[
                    SubCommand(name='cat', description='gives a cat image'),
                    SubCommand(name='dog', description='gives a dog image'),
                    SubCommand(name='pig', description='gives a pig image'),
                    SubCommand(name='rabbit', description='gives a rabbit image')
                ]
            ),
            SubCommandGroup(
                name='wild',
                description='wild animals',
                options=[
                    SubCommand(name='fox', description='gives a fox image'),
                    SubCommand(name='panda', description='gives a panda image'),
                    SubCommand(name='tiger', description='gives a tiger image'),
                ]
            )
        ]),
    guild_id=877399405056102431)
async def app_cmd(appctx: ApplicationContext):
    message = appctx.options
    await appctx.respond(f'Received: {message}')


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
