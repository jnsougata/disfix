# app_util 
A module to integrate Application Commands into your bot written with *discord.py 2.0*

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
intents.members = True


class MyBot(app_util.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
bot = MyBot()
# here you can pass in both command cog and slash cog extension
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
    
    # example slash command named `all`
    @app_util.Cog.command(
        command=app_util.SlashCommand(
            name='all',
            description='get all commands',
            options=[
                app_util.IntOption(
                    name='page',
                    description='page number',
                    max_value=10,
                    min_value=1,
                    required=True,
                )
            ]
        ),
        guild_id=877399405056102431 
        # if guild_id is not provided
        # it will be available globally
    )
    async def all_command(self, ctx: app_util.Context):
        await ctx.defer()
        await self.bot.sync_global_commands()
        await ctx.send_followup(f'```py\n{self.bot.application_commands}\n```')
    
    # example application user command named `Promote It`
    # this command will dm the target user with the phrase if possible
    @app_util.Cog.command(
        command=app_util.UserCommand(
            name='Promote It',
        ),
        guild_id=877399405056102431
    )
    async def promote_command(self, ctx: app_util.Context):
        await ctx.defer(ephemeral=True)
        await ctx.resolved_user.send('You have been promoted! LOL')
        await ctx.send_followup('Done!')
    
    # example application message command named `Pin`
    # this command will pin the message to the channel
    @app_util.Cog.command(
        command=app_util.MessageCommand(
            name='Pin',
        ),
        guild_id=877399405056102431
    )
    async def pin_command(self, ctx: app_util.Context):
        await ctx.resolved_message.pin()
        await ctx.send_response(f'Message pinned by {ctx.author.mention}')


def setup(bot: app_util.Bot):
    bot.add_application_cog(Sample(bot))
```