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


class BaseView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = 0
        self.timeout = 10

    @discord.ui.button(label='DELETE', style=discord.ButtonStyle.red)
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = 1
        self.stop()

    @discord.ui.button(label='EDIT', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = 2
        self.stop()


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
            view = BaseView()
            resp = await ctx.send_followup(f'Value: **{value}**', view=view)
            await view.wait()
            if view.value == 1:
                await resp.delete()
            elif view.value == 2:
                view.clear_items()
                await resp.edit(content=f'Edited: **{value}**', view=view)
        else:
            await ctx.send_response('you are not allowed to use this command')


def setup(bot: Bot):
    bot.add_slash_cog(Echo(bot), 877399405056102431)
    # add guild if you want to limit the command to a specific guild
    # if you to register the command to all guilds, you can leave it empty
    # global commands take 1hour to register for the first time for all guilds
