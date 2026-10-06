import discord
from discord import app_commands
from discord.ext import commands
import bot_package.Custom_Func as Cf
import bot_package.data as data


async def piece_autcomplete(interaction : discord.Interaction, current : str) -> list[app_commands.Choice[str]] :
    choices = data.pieces.copy()
    liste = [
        app_commands.Choice(name=choices, value=choices)
        for choices in choices if current.lower() in choices.lower()
    ]
    return liste

async def object_autcomplete(interaction : discord.Interaction, current : str) -> list[app_commands.Choice[str]] :
    choices = data.objets.copy()
    inv = await Cf.get_inv(interaction.user.id)
    liste = []
    for choice in choices:
        if choice in data.piece_property[inv["room"]]:
            liste.append(app_commands.Choice(name=choice, value=choice))
    return liste



class Commands(commands.Cog):
    """
    """

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="start")
    async def start(self, ctx:commands.Context):
        """
        Permet de commencer l'event
        """

        inventory = await Cf.get_inv(ctx.author.id)

        started = False

        try:
            inventory["started"]
            started = True
        except KeyError:
            started = False


        if not started:
            inventory = data.default_inventory.copy()
            inventory["last_reset"] = await Cf.get_midnight()
            await Cf.save_inv(inventory, ctx.author.id)
            started_embed = discord.Embed(
                title = "Vous commencer l'évènement",
                description = "Vous venez de commencer l'évènement.\nFaites /pièce {pièce} pour changer de pièce.\n\n\n Voici le plan du manoir:",
                color = discord.Color.green()
            )
            started_embed.set_image(url=data.images_piece["Manoir"])
            return await ctx.send(embed=started_embed)
        else:
            already_started_embed = discord.Embed(
                title = "Vous avez dékà commencer l'évènement",
                description = "Vous avez déjà commencer l'évènement.\nFaites /pièce {pièce} pour changer de pièce.",
                color = discord.Color.red()
            )
            return await ctx.send(embed=already_started_embed)


    @commands.hybrid_command(name="pièce")
    @app_commands.autocomplete(piece=piece_autcomplete)
    async def piece(self, ctx:commands.Context, piece:str):
        """
        Une commande vous permettant de changer de pièce
        """
        await Cf.energie_reset(ctx.author.id,ctx)
        
        if piece not in data.pieces:
            not_piece_embed = discord.Embed(
                title="Cette pièce n'existe pas.",
                description=f"La pièce {piece.lower()} n'existe pas.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=not_piece_embed)
        
        inventory = await Cf.get_inv(ctx.author.id)

        if inventory == {}:
            started_embed = discord.Embed(
                title = "Vous n'avez pas commencé l'évènement",
                description = "Faites /start pour commencer l'énèvement.",
                color = discord.Color.red()
            )
            return await ctx.send(embed=started_embed)

        if piece == inventory["room"]:
            already_in_piece_embed = discord.Embed(
                title="Vous êtes déja dans cette pièce.",
                description=f"Vous êtes déjà dans le/la {piece.lower()}.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=already_in_piece_embed)

        if inventory["energie"] < 10:
            no_energie_embed = discord.Embed(
                title="Vous n'avez plus suffisament d'énergie.",
                description=f"Vous avez {inventory["energie"]} d'énergie, et il en faut 10.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=no_energie_embed)

        inventory["room"] = piece
        inventory["energie"] -= 10
        await Cf.save_inv(inventory,ctx.author.id)
        succes_embed = discord.Embed(
            title="Vous avez changé de pièce.",
            description=f"Vous êtes désormais dans le/la {piece.lower()}.\nIl vous reste {inventory["energie"]} énergies.",
            color=discord.Color.green()
        )
        succes_embed.set_image(url=data.images_piece[piece])
        return await ctx.send(embed=succes_embed)
    

    @commands.hybrid_command(name="energie")
    async def energie(self, ctx:commands.Context):
        """
        Une commande vous permettant de voir votre jauge d'énergie
        """
        await Cf.energie_reset(ctx.author.id,ctx)
        inventory = await Cf.get_inv(ctx.author.id)
        energi = inventory["energie"]
        energie_embed = discord.Embed(
            title = f"Vous avez {energi} d'énergie.",
            description = "Revenez demain pour être à 100 d'énergie.",
            color = discord.Color.green()
        )
        return await ctx.send(embed=energie_embed)
    

    @commands.hybrid_command(name="objet")
    @app_commands.autocomplete(objet=object_autcomplete)
    async def objet(self,ctx:commands.Context,objet:str):
        await Cf.energie_reset(ctx.author.id,ctx)
        inventory = await Cf.get_inv(ctx.author.id)
        if inventory["energie"] < 5:
            no_energie_embed = discord.Embed(
                title="Vous n'avez plus suffisament d'énergie.",
                description=f"Vous avez {inventory["energie"]} d'énergie, et il en faut 5.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=no_energie_embed)
        
        if objet not in data.piece_property[inventory["room"]]:
            not_object_in_room_embed = discord.Embed(
                title="L'objet demandé n'est pas dans cette pièce/il n'existe pas.",
                description=f"Liste des objets dans le/la{inventory["room"]}:",
                color=discord.Color.red()
            )
            for objett in data.piece_property[inventory["room"]]:
                not_object_in_room_embed.add_field(name=objett,value="")
            return await ctx.send(embed=not_object_in_room_embed)
        return




async def setup(bot) -> None:
    await bot.add_cog(Commands(bot))