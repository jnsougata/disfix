# ExtSlash 
A module to integrate Slash Commands into your bot written in *discord.py 2.0*

### Installation:
Before working with it, you need to install the core dependency - **discord.py(2.0)**

`pip install -U git+https://github.com/Rapptz/discord.py`

Then you can install the module:

`pip install extslash`

### Create a new instance of the bot:

```python
import discord
import extslash


intents = discord.Intents.default()
intents.members = True


class MyBot(extslash.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
bot = MyBot()
# here you can pass in both command cog and slash cog extension
bot.load_extension('your_extension_name')
bot.run('YOUR_TOKEN')
```
### Making a slash cog:

```python
import discord
import extslash


# Create a new cog class subclassing from app_utils.Cog
class Echo(extslash.Cog):

    @extslash.Cog.command(
        command=SlashCommand(
            name='echo',
            description='echos back a given message',
            options=[
                StrOption(name='anything', description='message to echo back')
                # you can add choices to these options too 
            ],
            # by default, command will be accessible to everyone
            # if you want to limit the command to certain roles/users, you can add them here,
            permissions=[
                SlashPermission.for_user(516649677001719819),
                SlashPermission.for_role(921001978916642856, allow=False),
            ],
        ),
        guild_id=None,  # None means it will be available globally
        # add guild id to restrict the command to certain guild
    )
    # you can use ctx to get the arguments, the message, the channel, etc.
    async def command(self, ctx: extslash.Context):
        await ctx.send_response(f'{ctx.options[0].value}')

    @extslash.Cog.listener
    async def on_command_error(self, ctx: extslash.Context, error):
        # this implements the global error handler for slash commands only 
        # you can use ctx to get the arguments, the message, the channel, etc.
        # you can use error to get the error
        # you can use ctx.send_response to send a message
        pass


# this setup method is mandatory for loading the cog
def setup(bot: extslash.Bot):
    # `add_slash_cog` will add the cog to the bot
    # it takes the SlashCog class as an argument
    bot.add_application_cog(Echo())

```
