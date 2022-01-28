import os
import discord
from discord.ext import commands, tasks
from src.extslash import SlashBot, Slash, SlashInteraction
from cmds import echo, setup


intents = discord.Intents.default()
intents.members = True


class MyBot(SlashBot):
    def __init__(self):
        super().__init__(prefix='-', help_command=None, intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MyBot()


@bot.slash_command(command=setup, guild_id=877399405056102431)
async def setup(interaction: SlashInteraction):

    class BaseView(discord.ui.View):

        def __init__(self):
            super().__init__()
            self.timeout = 30
            self.value = None
            self.message = None

        async def on_timeout(self):
            try:
                await self.message.delete()
            except Exception:
                return

    class CommandMenu(discord.ui.Select):

        def __init__(self, ctx, bot: discord.Client):

            self.bot = bot
            self.ctx = ctx

            options = [
                discord.SelectOption(label='​', value='100'),
                discord.SelectOption(label='Prefix', value='0'),
                discord.SelectOption(label='YouTube', value='2'),
                discord.SelectOption(label='Receiver', value='1'),
                discord.SelectOption(label='Reception', value='3'),
                discord.SelectOption(label='Alert Role', value='5'),
                discord.SelectOption(label='Welcome Card', value='4'),
            ]

            super().__init__(
                min_values=1,
                max_values=1,
                options=options,
                placeholder='select a command'
            )

        async def callback(self, interaction: discord.Interaction):

            if interaction.user == self.ctx.author:
                await interaction.message.delete()
            else:
                await interaction.response.send_message('You are not allowed to control this message!', ephemeral=True)

    emd = discord.Embed(description='\n> use command from the menu below', colour=0x005aef)
    emd.set_author(name=interaction.author.name, icon_url=interaction.author.avatar.url)
    view = BaseView()
    view.add_item(CommandMenu(interaction, bot))
    await interaction.respond(embed=emd)
    await interaction.send('\u200e', view=view)


bot.load_extension('cogs.example')
bot.run(os.getenv('DISCORD_TOKEN'))
