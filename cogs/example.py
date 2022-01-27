import discord
from discord.ext import commands


class Test(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['test'])
    async def test_(self, ctx: commands.Context):
        emd = discord.Embed(
            description='\n> Testing ExtSlash Cogs',
            colour=0x005aef
        )
        emd.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=emd)


def setup(bot):
    bot.add_cog(Test(bot))
