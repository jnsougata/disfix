Neocord
==========

Latest feature addons for discord.py 2.0

Installing
----------

**Python 3.8 or higher is required**

.. code:: sh

    # Linux/macOS
    python3 -m pip install git+https://github.com/jnsougata/neocord

.. code:: sh

    # Windows
    py -3 -m pip install git+https://github.com/jnsougata/neocrod

Quick Example
--------------

.. code:: py

    import discord
    import neocrod


    intents = discord.Intents.default()


    class SampleBot(neocrod.Bot):
        def __init__(self):
            super().__init__(command_prefix='-', intents=intents)

        async def on_ready(self):
            print(f'Logged in as {self.user} (ID: {self.user.id})')
            print('------')

    bot = SampleBot()

    bot.load_extension('extension_name')
    bot.run('YOUR_TOKEN')

Cog Example
------------

.. code:: py

    import discord
    import neocord as nc


    class Test(nc.cog):

        def __init__(self, bot):
            self.bot = bot


        # general slash command
        @nc.cog.command(name="ping", description="shows client latency", category=nc.CommandType.SLASH)
        async def ping(self, ctx: nc.Context):
            await ctx.send_response(f"Pong: {round(self.bot.latency * 100)}ms")


    async def setup(bot):
        await bot.add_application_cog(Test(bot))


User Command Example
--------------------

.. code:: py

        @neocrod.cog.command(name='Bonk', category=nc.CommandType.USER)
        async def bonk(self, ctx: nc.Context, user: discord.User):
            await ctx.send_response(f'{ctx.author.mention} just bonked {user.mention}!')

Message Command Example
-----------------------

.. code:: py

        @neocrod.cog.command(name='Pin', category=nc.CommandType.MESSAGE))
        async def pin(self, ctx: neocrod.Context, message: discord.Message):
            await message.pin()
            await ctx.send_response(f'Message pinned by {ctx.author}', ephemeral=True)

Sending Modal Example
---------------------

.. code:: py

        @neocrod.cog.command(
            name='modal',
            description='sends a placeholder modal',
            category=neocrod.CommandType.SLASH,
            guild_id=1234567890
        )
        async def modal_command(self, ctx: nc.Context):

            # creating a modal with author's name

            modal = nc.Modal(title=f'A Super Modal for {ctx.author.name}')
            modal.add_field(
                label='About',
                custom_id='about',
                style=nc.TextInputStyle.PARAGRAPH,
                required=False,
                hint='Write something about yourself...',
            )
            modal.add_field(
                label='Tip',
                custom_id='tip',
                style=neocrod.TextInputStyle.SHORT,
                required=True,
                hint='Give me some tips to improve...',
                max_length=100,
            )
            await ctx.send_modal(modal)  # sending the modal

            @modal.callback(self.bot)  # in-place callback for the modal
            async def on_submit(mcx: neocrod.Context, about: str, tip: str):
                embed = discord.Embed(
                    description=f'**About:** {about}\n**Tip:** {tip}')
                embed.set_author(name=f'{mcx.author.name}', icon_url=mcx.author.avatar.url)
                await mcx.send_response(embed=embed)

Subcommand Example
------------------

.. code:: py

        @nc.cog.default_permission(discord.Permissions.manage_guild)
        @nc.cog.command(name='math', description='does some arithmatic operations', dm_access=True)
        async def math(self, ctx):
            pass

        @math.subcommand(name='add', description='adds two number')
        @nc.cog.option(nc.NumberOption(name='a', description='first number', required=True))
        @nc.cog.option(nc.NumberOption(name='b', description='second number', required=True))
        async def add(self, ctx, a: float, b: float):
            await ctx.send_response(f'The result of {a} + {b}: `{a + b}`')

        @math.subcommand(name='mul', description='multiplies two number')
        @nc.cog.option(nc.NumberOption(name='a', description='first number', required=True))
        @nc.cog.option(nc.NumberOption(name='b', description='second number', required=True))
        async def add(self, ctx, a: float, b: float):
            await ctx.send_response(f'The result of {a} * {b}: `{a * b}`')

Error Handler Example
---------------------

.. code:: py

        @nc.cog.listener
        async def on_command_error(self, ctx: neocrod.Context, error: Exception):
            await ctx.send_followup(f'Something went wrong!')