import discord
from discord import app_commands
from discord.ext import commands
import bot_package.Custom_Func as Cf
import bot_package.data as data
import random


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
        Commencer l'évènement
        """
        if ctx.guild.id != None and ctx.channel.id in data.configuration["commands_channel_id"]:
            not_command_salon_message = "Merci de ne pas éxécuter cette commande dans le #commande!"
            return await ctx.send(not_command_salon_message,ephemeral=True)
        
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
                title = "Vous avez commencé l’aventure..!",
                description = "Bienvenue au manoir. L’endroit le plus hanté de la région : et vous, pour une raison ou pour une autre, vous avez décidé de vous y rendre.\n*Vous voilà enfermés. Pendant toute une semaine. Trouverez-vous la clé de sortie ?*\n*Quoi qu’il en soit, prenez vos aises. Car vous allez rester là un moment. On dit que le manoir regorge de secrets, et qu’il serait même habité de petites créatures… Peut-être devriez-vous jeter un œil à tout ça ?*\n\nBienvenue au manoir ! Prêts à explorer tout ça ?\n\n- Vous êtes enfermés dans le manoir pendant une semaine. Vous avez donc du 26 octobre au 1er novembre pour explorer autant que vous le souhaitez.\n- Cependant vos capacités ne sont pas illimitées, vous devez aussi vous reposer ! Vous aurez chaque jour 100 points d’énergie à dépenser. Faites-en bon usage !\n- Le manoir comporte 7 pièces. Faites /piece pour vous rendre dans l’une d’elle. Mais attention : cette action vous coûtera 10 énergie !\n- Chaque pièce du manoir a ses propres secrets, et ses propres objets à fouiller. Faites /objet pour fouiller l’un d’entre eux, autant de fois que vous le souhaitez. Cette action vous coûtera 5 énergie.\n- Vous aurez l’occasion de découvrir bien d’autres choses en explorant le manoir… Mais maintenant que vous avez les bases, vous découvrirez le reste par vous-même.\n\nBonne exploration !",
                color = discord.Color.green()
            )
            started_embed.set_footer(text="Faites /pièce pour commencer.")
            #started_embed.set_image(url=data.images_piece["Manoir"])
            return await ctx.send(embed=started_embed)
        else:
            already_started_embed = discord.Embed(
                title = "Vous avez déjà commencé l'évènement.",
                description = "Vous avez déjà commencé l'évènement.\nEssayez /pièce pour vous déplacer !",
                color = discord.Color.red()
            )
            return await ctx.send(embed=already_started_embed)



    @commands.hybrid_command(name="pièce")
    @app_commands.autocomplete(piece=piece_autcomplete)
    async def piece(self, ctx:commands.Context, piece:str):
        """
        Changer de pièce
        """
        if ctx.guild.id != None and ctx.channel.id in data.configuration["commands_channel_id"]:
            not_command_salon_message = "Merci de ne pas éxécuter cette commande dans le #commande!"
            return await ctx.send(not_command_salon_message,ephemeral=True)
        if not await Cf.have_started(ctx):
            return
        await Cf.energie_reset(ctx.author.id,ctx)
        if await Cf.aggressif_check(ctx.author.id,ctx):
            return
        
        if piece not in data.pieces:
            not_piece_embed = discord.Embed(
                title="Pièce inconnue.",
                description=f"La pièce {piece.lower()} n'existe pas.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=not_piece_embed)
        
        inventory = await Cf.get_inv(ctx.author.id)

        if not await Cf.have_started(ctx):
            return

        if piece == inventory["room"]:
            already_in_piece_embed = discord.Embed(
                title=f"Vous vous trouvez déjà dans {await Cf.determinant(piece.lower())}!",
                description=f"Essayez de fouiller avec /objet.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=already_in_piece_embed)

        if inventory["energie"] < 10:
            no_energie_embed = discord.Embed(
                title="Vous n'avez pas assez d'énergie.",
                description=f"Il vous reste {inventory["energie"]} énergie, et il vous en faut 10. Réessayez quand vous aurez plus d'énergie !",
                color=discord.Color.red()
            )
            return await ctx.send(embed=no_energie_embed)


        inventory["room"] = piece
        inventory["energie"] -= 10
        await Cf.save_inv(inventory,ctx.author.id)
        succes_embed = discord.Embed(
            title=f"Vous vous rendez dans {await Cf.determinant(piece.lower())}.",
            description=f"{data.room_description[piece]}",
            color=discord.Color.green()
        )
        succes_embed.set_footer(text="- 10 énergie")
        #succes_embed.set_image(url=data.images_piece[piece])
        return await ctx.send(embed=succes_embed)
    


    @commands.hybrid_command(name="energie")
    async def energie(self, ctx:commands.Context):
        """
        Consulter votre taux d'énergie
        """
        if not await Cf.have_started(ctx):
            return
        await Cf.energie_reset(ctx.author.id,ctx)
        inventory = await Cf.get_inv(ctx.author.id)
        energi = inventory["energie"]
        energie_embed = discord.Embed(
            title = f"Il vous reste {energi} énergie.",
            description = "L'énergie se réinitialise à 100 tous les jours !",
            color = discord.Color.green()
        )
        return await ctx.send(embed=energie_embed)

    

    @commands.hybrid_command(name="objet")
    @app_commands.autocomplete(objet=object_autcomplete)
    async def objet(self,ctx:commands.Context,objet:str):
        """
        Fouiller un objet.
        """
        if ctx.guild.id != None and ctx.channel.id in data.configuration["commands_channel_id"]:
            not_command_salon_message = "Merci de ne pas éxécuter cette commande dans le #commande!"
            return await ctx.send(not_command_salon_message,ephemeral=True)
        if not await Cf.have_started(ctx):
            return
        await Cf.energie_reset(ctx.author.id,ctx)
        if await Cf.aggressif_check(ctx.author.id,ctx):
            return
        inventory = await Cf.get_inv(ctx.author.id)
        if inventory["energie"] < 5:
            no_energie_embed = discord.Embed(
                title="Vous n'avez pas assez d'énergie.",
                description=f"Il vous reste {inventory["energie"]} énergie, et il vous en faut 5. Réessayez quand vous aurez plus d'énergie !",
                color=discord.Color.red()
            )
            return await ctx.send(embed=no_energie_embed)
        
        if objet not in data.piece_property[inventory["room"]]:
            not_object_in_room_embed = discord.Embed(
                title="Objet inconnu.",
                description=f"Essayez de fouiller un objet présent dans la pièce.",
                color=discord.Color.red()
            )
            for objett in data.piece_property[inventory["room"]]:
                not_object_in_room_embed.add_field(name=objett,value="")
            return await ctx.send(embed=not_object_in_room_embed)

        inventory["energie"] -= 5

        to_gain = []
        gain_proba = []
        for gain in data.piece_property[inventory["room"]][objet]:
            to_gain.append(gain)
            gain_proba.append(data.piece_property[inventory["room"]][objet][gain]["proba"])

        gain = random.choices(to_gain,gain_proba)[0]
        gain_property = data.piece_property[inventory["room"]][objet][gain]
        print(gain_property)
        if gain_property["effect"] == "energie":
            inventory["energie"] += gain_property["value"]
            if gain_property["value"] > 0:
                energie_embed = discord.Embed(
                    title = f"Vous fouillez {await Cf.determinant(objet.lower())}.",
                    description = gain_property["description"],
                    color = discord.Color.green()
                )
            else:
                energie_embed = discord.Embed(
                    title = f"Vous fouillez {await Cf.determinant(objet.lower())}.",
                    description = gain_property["description"],
                    color = discord.Color.red()
                )
                if inventory["energie"] < 0:
                    inventory["energie"] = 0
                    print(4)
            energie_embed.set_footer(text="- 5 énergie.")
            await Cf.save_inv(inventory,ctx.author.id)
            return await ctx.send(embed=energie_embed)
        
        elif gain_property["effect"] == "points":
            nb_points = random.randint(5,20)
            inventory["points"] += nb_points
            points_embed = discord.Embed(
                title = f"Vous fouillez {await Cf.determinant(objet.lower())}.",
                description = gain_property["description"].format(nb_points),
                color = discord.Color.green()
            )
            points_embed.set_footer(text="- 5 énergie")
            await Cf.save_inv(inventory,ctx.author.id)
            return await ctx.send(embed=points_embed)

        elif gain_property["effect"] == "piece":
            coin = random.choices(data.coin_list.copy(),data.coin_proba.copy())[0]
            inventory = await Cf.give(coin,"coin",inventory)
            coin_embed = discord.Embed(
                title = f"Vous fouillez {await Cf.determinant(objet.lower())}.",
                description = gain_property["description"].format(coin),
                color = discord.Color.green()
            )
            coin_embed.set_footer(text="- 5 énergie.")
            await Cf.save_inv(inventory,ctx.author.id)
            return await ctx.send(embed=coin_embed)

        else:
            yokai = random.choice(data.yokai_room[inventory["room"]])
            if gain_property["effect"] == "yokai passif":
                inventory = await Cf.give(yokai,"yokai",inventory)
                yokai_embed = discord.Embed(
                    title = f"Vous fouillez {await Cf.determinant(objet.lower())}.",
                    description = gain_property["description"].format(yokai),
                    color = discord.Color.green()
                )
                yokai_embed.set_footer(text="- 5 énergie")
                await Cf.save_inv(inventory,ctx.author.id)
                return await ctx.send(embed=yokai_embed)
            else:
                yokai_embed = discord.Embed(
                    title = f"Vous fouillez {await Cf.determinant(objet.lower())}.",
                    description = gain_property["description"].format(yokai),
                    color = discord.Color.yellow()
                )
                inventory["yokai aggressif"] = {"Activated": True,"Yokai": yokai}
                yokai_embed.set_footer(text="- 5 énergie")
                await Cf.save_inv(inventory,ctx.author.id)
                return await ctx.send(embed=yokai_embed)


    @commands.hybrid_command(name="fuir")
    async def fuite(self,ctx:commands.Context):
        """
        Fuir un yokai aggressif.
        """
        if ctx.guild.id != None and ctx.channel.id in data.configuration["commands_channel_id"]:
            not_command_salon_message = "Merci de ne pas éxécuter cette commande dans le #commande!"
            return await ctx.send(not_command_salon_message,ephemeral=True)
        if not await Cf.have_started(ctx):
            return
        await Cf.energie_reset(ctx.author.id,ctx)
        if not await Cf.aggressif_check(ctx.author.id,ctx,True):
            return
        inventory = await Cf.get_inv(ctx.author.id)
        last_room = inventory["room"]

        new_room = random.choice(data.pieces.copy())
        while new_room == inventory["room"]:
            new_room = random.choice(data.pieces.copy())
        inventory["room"] = new_room
        inventory["yokai aggressif"] = {"Activated":False,"Yokai":None}
        fuite_embed = discord.Embed(
            title="Vous avez pris la fuite.",
            description=f"Vous avez fuit dans la direction {await Cf.determinant(new_room.lower(),"de")} !",
            color=discord.Color.dark_gold()
        )
        await Cf.save_inv(inventory,ctx.author.id)
        return await ctx.send(embed=fuite_embed)


    @commands.hybrid_command(name="amadouer")
    async def amadouer(self,ctx:commands.context,energie:int):
        """
        Amadouer un yokai agressif
        """
        if ctx.guild.id != None and ctx.channel.id in data.configuration["commands_channel_id"]:
            not_command_salon_message = "Merci de ne pas éxécuter cette commande dans le #commande!"
            return await ctx.send(not_command_salon_message,ephemeral=True)
        if not await Cf.have_started(ctx):
            return
        await Cf.energie_reset(ctx.author.id,ctx)
        if not await Cf.aggressif_check(ctx.author.id,ctx,True,True):
            return

        if energie <= 0:
            more_embed=discord.Embed(
                title="Le montant saisi n'est pas valide.",
                description="Veuillez saisir un montant supérieur à 0.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=more_embed)
        
        inventory = await Cf.get_inv(ctx.author.id)

        if energie > 25:
            too_many_embed = discord.Embed(
                title="Le montant saisi n'est pas valide.",
                description=f"Veuillez saisir un montant inférieur à 25. Vous voulez amadouer le yokai, pas le droguer !",
                color=discord.Color.red()
            )
            return await ctx.send(embed=too_many_embed)

        if inventory["energie"] < energie:
            not_enough_embed = discord.Embed(
                title="Vous n'avez pas suffisament d'énergie.",
                description=f"Il vous reste {inventory["energie"]}.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=not_enough_embed)

        proba = (energie*4 - energie/3)/100
        antiProba = 1 - proba
        if random.choices([True,False],[proba,antiProba])[0]:
            inventory["energie"] -= energie
            inventory = await Cf.give(inventory["yokai aggressif"]["Yokai"],"yokai",inventory,1)
            succes_embed = discord.Embed(
                title="Vous avez réussi à amadouer le yokai !",
                description=f"Félicitations ! Le yokai {inventory["yokai aggressif"]["Yokai"]} vient de devenir ami avec vous.",
                color=discord.Color.green()
            )
            inventory["yokai aggressif"] = {"Activated":False,"Yokai":None}
            await Cf.save_inv(inventory,ctx.author.id)
            return await ctx.send(embed=succes_embed)
        else:          
            new_room = random.choice(data.pieces.copy())
            while new_room == inventory["room"]:
                new_room = random.choice(data.pieces.copy())
            inventory["room"] = new_room
            inventory["energie"] -= energie
            fail_embed = discord.Embed(
                title="Vous n'avez pas réussi à amadouer le yokai !",
                description=f"Vous n'avez pas réussi à devenir ami avec {inventory["yokai aggressif"]["Yokai"]}.\nVous avez été repoussé vers {await Cf.determinant(new_room.lower(),)}.",
                color=discord.Color.red()
            )
            inventory["yokai aggressif"] = {"Activated":False,"Yokai":None}
            await Cf.save_inv(inventory,ctx.author.id)
            return await ctx.send(embed=fail_embed)


    @commands.hybrid_command(name="points")
    async def points(self, ctx:commands.Context,user:discord.User=None):
        """
        Consulter votre solde de points
        """
        if user == None:
            user == ctx.author
        inventory = await Cf.get_inv(user.id)
        if user.id == ctx.author.id:
            if not await Cf.have_started(ctx):
                return
        elif inventory == {}:
            not_started_embed = discord.Embed(
            title=f"{user.name} n'a pas encore commencé l'évènement !",
            color=discord.Color.red()
            )
            return await ctx.send(embed=not_started_embed)
        if user.id == ctx.author.id:
            await Cf.energie_reset(ctx.author.id,ctx)
            points_embed = discord.Embed(
                title = f"Vous avez {inventory["points"]} points.",
                description = "Vous pouvez les dépenser à la roue ou les transformer en énergie !",
                color = discord.Color.green()
            )
            return await ctx.send(embed=points_embed)
        else:
            points_embed = discord.Embed(
                title = f"{user.name} a {inventory["points"]} points.",
                color = discord.Color.green()
            )
            return await ctx.send(embed=points_embed)


    
    @commands.hybrid_command(name="localisation")
    async def localisation(self, ctx:commands.Context):
        """
        Consulter votre position
        """
        if not await Cf.have_started(ctx):
            return
        await Cf.energie_reset(ctx.author.id,ctx)
        inventory = await Cf.get_inv(ctx.author.id)
        localisation_embed = discord.Embed(
            title = f"Vous vous trouvez dans {await Cf.determinant(inventory["room"].lower())}.",
            description = "Faites /piece pour changer de pièce!",
            color = discord.Color.green()
        )
        #localisation_embed.set_image(url=data.images_piece[inventory["room"]])
        return await ctx.send(embed=localisation_embed)



    @commands.hybrid_command(name="inventaire")
    async def inventaire(self, ctx:commands.Context, user :discord.User = None):
        """
        Permet de consulter un inventaire
        """
        if user == None:
            user = ctx.author

        inv = await Cf.get_inv(user.id)
        if inv == {}:
            if user.id == ctx.author.id:
                not_started_embed = discord.Embed(
                    title = "Vous n'avez pas encore commencé l'évènement !",
                    description = "Faites /start pour commencer l'évènement.",
                    color = discord.Color.red()
                )
                return await ctx.send(embed=not_started_embed)
            else:
                not_started_embed = discord.Embed(
                    title=f"{user.name} n'a pas encore commencé l'évènement !",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=not_started_embed)

        await Cf.energie_reset(ctx.author.id,ctx)

        if user.id == ctx.author.id:
            inv_embed = discord.Embed(
                title="Votre inventaire :",
                color=discord.Color.blurple()
            )
        else:
            inv_embed = discord.Embed(
                title=f"Inventaire de {user.name} :",
                color=discord.Color.blurple()
            )

        field = ""
        if inv["yokai"] != {}:
            for yokai in inv["yokai"]:
                field += f"{yokai} `X{inv["yokai"][yokai]}`\n"
        inv_embed.add_field(name="**Yokai :**", value=field)

        field = ""
        if inv["coin"] != {}:
            for coin in inv["coin"]:
                field += f"{coin} `X{inv["coin"][coin]}`\n"
        inv_embed.add_field(name="**Pièces :**", value=field)

        field = ""
        if inv["objet"] != {}:
            for objet in inv["objet"]:
                field += f"{objet} `X{inv["objet"][objet]}`\n"
        inv_embed.add_field(name="**Objets :**", value=field)

        return await ctx.send(embed=inv_embed)


    @commands.hybrid_command(name="transformer")
    async def transformer(self,ctx:commands.Context,points:int):
        """
        Transformer vos points en énergie
        """
        if points <= 0:
            more_embed=discord.Embed(
                title="Ce montant n'est pas valide.",
                description=f"Veuillez saisir un montant supérieur à 0.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=more_embed)
        if not await Cf.have_started(ctx):
            return
        await Cf.energie_reset(ctx.author.id,ctx)

        inventory = await Cf.get_inv(ctx.author.id)

        if inventory["points"] < points:
            not_enough_embed = discord.Embed(
                title="Vous n'avez pas assez de points.",
                description="Obtenez des points en fouillant les objets du manoir !",
                color=discord.Color.red()
            )
            return await ctx.send(embed=not_enough_embed)

        inventory["energie"] += points
        inventory["points"] -= points

        success_embed = discord.Embed(
            title="Bravo !",
            description=f"Vous avez converti vos points avec succès.\nVous possédez désormais {inventory["energie"]} énergie.",
            color=discord.Color.green()
        )
        await Cf.save_inv(inventory,ctx.author.id)
        return await ctx.send(embed=success_embed)

    

    @commands.hybrid_command(name="salon")
    async def salon(self, ctx = commands.Context):
        """
        Se rendre au salon.
        """
        await self.piece(ctx,"Salon")

    @commands.hybrid_command(name="cuisine")
    async def cuisine(self, ctx = commands.Context):
        """
        Se rendre à la cuisine.
        """
        await self.piece(ctx,"Cuisine")

    @commands.hybrid_command(name="salle-de-bain")
    async def salleDeBain(self, ctx = commands.Context):
        """
        Se rendre à la salle de bain.
        """
        await self.piece(ctx,"Salle de bain")

    @commands.hybrid_command(name="bibliothèque")
    async def bibliotheque(self, ctx = commands.Context):
        """
        Se rendre à la bibliothèque.
        """
        await self.piece(ctx,"Bibliothèque")

    @commands.hybrid_command(name="chambre")
    async def chambre(self, ctx = commands.Context):
        """
        Se rendre à la chambre.
        """
        await self.piece(ctx,"Chambre")

    @commands.hybrid_command(name="galerie")
    async def galerie(self, ctx = commands.Context):
        """
        Se rendre à la galerie.
        """
        await self.piece(ctx,"Galerie")

    @commands.hybrid_command(name="grenier")
    async def grenier(self, ctx = commands.Context):
        """
        Se rendre au grenier.
        """
        await self.piece(ctx,"Grenier")


async def setup(bot) -> None:
    await bot.add_cog(Commands(bot))