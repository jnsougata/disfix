# app_util 
A module to integrate Slash Commands into your bot written in *discord.py 2.0*

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
bot.load_extension('your_extension_name')
bot.run('YOUR_TOKEN')
```