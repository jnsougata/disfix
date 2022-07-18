disfix
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

    import asyncio
    import discord
    import neocrod


    class Sample(neocrod.Cog):

        def __init__(self, bot: neocrod.Bot):
            self.bot = bot

        # slash command named `book`
        @neocrod.Cog.command(
            name='book',
            description='get a sample book',
            category=neocrod.CommandType.SLASH,
            options=[
                neocrod.StrOption(
                    name='book_name',
                    description='the name of the book you want to get',
                    required=True,
                ),
                neocrod.IntOption(
                    name='page',
                    description='the page number to look for',
                    max_value=10,
                    min_value=1,
                    required=True,
                )
            ],
            guild_id=1234567890
            # if None, available for all guilds
        )
        async def book(self, ctx: neocrod.Context, book_name: str, page: int):
            await ctx.defer(ephemeral=True)
            page_content = await imaginary_api.fetch(book_name, page)
            embed = discord.Embed(
                title=f'{book_name}',
                description=page_content,
                color=ctx.author.color
            )
            embed.set_footer(text=f'Page {page_number}')
            await ctx.send_followup(embed=embed)

    def setup(bot: neocrod.Bot):
        bot.add_application_cog(Sample(bot))

User Command Example
--------------------

.. code:: py

        @neocrod.Cog.command(name='Bonk', category=neocrod.CommandType.USER)
        async def bonk(self, ctx: neocrod.Context, user: discord.User):
            await ctx.send_response(f'{ctx.author.mention} just bonked {user.mention}!')

Message Command Example
-----------------------

.. code:: py

        @neocrod.Cog.command(name='Pin', category=neocrod.CommandType.MESSAGE))
        async def pin(self, ctx: neocrod.Context, message: discord.Message):
            await message.pin()
            await ctx.send_response(f'Message pinned by {ctx.author}', ephemeral=True)

Sending Modal Example
---------------------

.. code:: py

        @neocrod.Cog.command(
            name='modal',
            description='sends a placeholder modal',
            category=neocrod.CommandType.SLASH,
            guild_id=1234567890
        )
        async def modal_command(self, ctx: neocrod.Context):

            # creating a modal with author's name

            modal = neocrod.Modal(title=f'A Super Modal for {ctx.author.name}')
            modal.add_field(
                label='About',
                custom_id='about',
                style=neocrod.TextInputStyle.PARAGRAPH,
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

        @neocrod.Cog.default_permission(discord.Permissions.manage_guild)
        @neocrod.Cog.command(
            name='greet', description='greet the user', dm_access=False,
            category=neocrod.CommandType.SLASH,
            guild_id=877399405056102431
        )
        async def greet(self, ctx: neocrod.Context):
            pass

        @greet.subcommand(name='hi', description='greet the user with hi')
        async def hello(self, ctx: neocrod.Context):
            await ctx.send_response(f'Hi {ctx.author.mention}')

        @greet.subcommand(name='bye', description='greet the user with bye')
        async def bye(self, ctx: neocrod.Context):
            await ctx.send_response(f'Bye {ctx.author.mention}')

Error Handler Example
---------------------

.. code:: py

        @neocrod.Cog.listener
        async def on_command_error(self, ctx: neocrod.Context, error: Exception):
            await ctx.send_followup(f'Something went wrong!')