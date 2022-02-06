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
from src.extslash.commands import Bot


intents = discord.Intents.default()
intents.members = True


class MyBot(Bot):
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
# this import for showing the options
# use: from extslash import *
# for cleaner code
from extslash import (
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
    Choice)
from extslash.commands import Bot, SlashCog, ApplicationContext

# Create a new cog class subclassing from SlashCog
class Echo(SlashCog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    # method register is an abstract method that must be implemented
    # in the subclass. This will be called by the bot to register
    # the commands
    def register(self):
        # Create a new SlashCommand
        command =  SlashCommand(
            name='echo',
            description='echos back a given message',
            # inside options, you can add any pre-defined option you want
            # for example, using a string option
            options=[
                StrOption(name='anything', description='message to echo back')
                # you can add choices to these options too 
            ],
            # adding permissions to the command
            # by default, this will be accessible to everyone
            # if you limit the command to certain roles/users, you can add them here,
            # for example,
            permissions=[
                SlashPermission.for_user(516649677001719819),
                SlashPermission.for_role(921001978916642856),
            ],
        )
        # you must return the command object
        return command
    
    # method command is an abstract method that must be implemented
    # this method is called when the command is executed
    # the context object contains all the information about the command
    # and the user that executed it
    # you can use it to get the arguments, the message, the channel, etc.
    async def command(self, ctx: ApplicationContext):
        # as we used on option we will receive only one argument
        # we can get all options by calling `ctx.options`
        # and then get the first one by calling `ctx.options[0]`
        # every option contains a `value` property that contains the value
        # now we are echoing back the value of the first option
        # by using method `send_response`
        # it will respond to the user that executed the command
        await ctx.send_response(f'{ctx.options[0].value}')


# this setup method is mandatory for loading the cog
def setup(bot: Bot):
    # `add_slash_cog` will add the cog to the bot
    # it takes the cog class as an argument and guild_id as an optional argument
    # guild_id is the id of the guild where the command will be available
    # if you don't pass it, the command will be available in all guilds i.e. globally
    bot.add_slash_cog(Echo(bot), 877399405056102431)

```
