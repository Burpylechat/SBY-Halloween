import discord
from discord.ext import commands
import bot_package.Custom_Func as Cf
import bot_package.data as data

class Commands(commands.Cog):
    """
    """

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="start")
    async def fusion(self, ctx:commands.Context):
        """
        Permet de commencer l'event
        """

        inventory = await Cf.get_inv(ctx.author.id)
        inventory = data.default_inventory.copy()
        inventory["last_reset"] = Cf.get_midnight()
        await Cf.save_inv(inventory, ctx.author.id)


async def setup(bot) -> None:
    await bot.add_cog(Commands(bot))