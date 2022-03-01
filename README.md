# app_util 
A module to integrate Application Commands into your bot written with *discord.py 2.0*

This includes **Slash Commands** **User Commands** **Message Command** 

### Installation:
Before working with it, you need to install the core dependency - **discord.py(2.0)**

`pip install -U git+https://github.com/Rapptz/discord.py`

Then you can install the module:

`pip install app_util`

### Create a new instance of the bot:

```python
import discord
import app_util


intents = discord.Intents.default()


class SampleBot(app_util.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
bot = SampleBot()

# here you can pass in 
# both dpy cog[path/extension] and app_util cog[path]
bot.load_extension('extension_name')
bot.run('YOUR_TOKEN')
```

### Making a cog for Application Commands:

```python
import sys
import asyncio
import traceback
import discord
import app_util


class Sample(app_util.Cog):

    def __init__(self, bot: app_util.Bot):
        self.bot = bot

    # this is default the application command error handler
    @app_util.Cog.listener
    async def on_command_error(self, ctx: app_util.Context, error: Exception):
        stack = traceback.format_exception(type(error), error, error.__traceback__)
        tb = ''.join(stack)
        await ctx.send_followup(f'```py\n{tb}\n```')

    # example slash command named `book`
    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='book',
            description='get a sample book',
            options=[
                app_util.StrOption(
                    name='book_name',
                    description='the name of the book you want to get',
                    required=True,
                ),
                app_util.IntOption(
                    name='page',
                    description='the page number to look for',
                    max_value=10,
                    min_value=1,
                    required=True,
                )
            ]
        ),
        guild_id=1234567890
        # if guild_id is not provided
        # it will be available globally
    )
    async def book(self, ctx: app_util.Context, book_name: str, page: int):
        page_content = await imaginary_api.fetch(book_name, page)
        embed = discord.Embed(
            title=f'{book_name}', 
            description=page_content, 
            color=ctx.author.color
        )
        embed.set_footer(text=f'Page {page_number}')
        await ctx.send_followup(embed=embed)

    # example application user command named `Bonk`
    # this command will dm the target user with the phrase if possible
    @app_util.Cog.command(
        command=app_util.UserCommand(name='Bonk'),
        guild_id=None
        # if guild_id is not provided
        # the command will be available globally
    )
    async def bonk(self, ctx: app_util.Context, user: discord.User):
        await ctx.send_response(f'{ctx.author.mention} just bonked {user.mention}!')

    # example application message command named `Pin`
    # this command will pin the message to the channel
    @app_util.Cog.command(
        command=app_util.MessageCommand(name='Pin'),
        guild_id=877399405056102431
    )
    async def pin(self, ctx: app_util.Context, message: discord.Message):
        await message.pin()
        await ctx.send_response(f'Message pinned by {ctx.author}')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Sample(bot))
```