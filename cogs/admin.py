import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
import os
import bot_package.Custom_Func as Cf
import bot_package.Check as Check
import bot_package.data as data

from typing import Literal
import time
import io




#Bot admin commands
class Admin_command(commands.Cog):
    """
    Commande d'administration. Utilisable seulement par l'équipe de développement.

    """
    
    
    
    
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.last_top = 0
        self.all_top={
            "Complétion":[],
            "Points":[]
        }

    
    
    
 
    @commands.hybrid_command(name="reset")
    @Check.is_in_dev_team()
    async def reset(self, ctx : commands.Context, input_id : discord.User):
        """
        Reset le Médallium et la sacoche de l'utilisateur donné.
        """
        #keep only the id
        input_id = input_id.id

        #is the input id fine ?
        try:
            int(input_id)
        except :
            error_embed = discord.Embed(
                title="Merci de fournir un identifiant corect !",
                color= discord.Color.red()
            )
            return await ctx.send(embed=error_embed)
        
        brute_inventory = await Cf.get_inv(input_id)
        
        
        #empt the inv and send the message
        brute_inventory = {}
        await Cf.save_inv(brute_inventory, input_id)
        sucess_embed = discord.Embed(
            title="Le Médallium et la sacoche de cet utilisateur a été vidé !",
            color= discord.Color.green()
        )
        #Log
        return await ctx.send(embed=sucess_embed)
            
                    
            
    # @commands.hybrid_command(name="dailyclear")
    # @Check.is_in_dev_team()
    # async def dailyclear(self, ctx: commands.Context, target: str):
    #     """
    #     Efface les récompenses quotidiennes pour tous les utilisateurs.
    #     """
    #     if target == "me":
    #         if ctx.author.id in data.daily_people["people"]:
    #             index = data.daily_people["people"].index(ctx.author.id)
    #             del data.daily_people["people"][index]
    #             return await ctx.send("tu a bien été oubliez de la liste")
    #         else:
    #             return await ctx.send("Vous n'êtes pas dans la liste")
    #     elif target == "all":
    #         data.daily_people["people"].clear()
    #         return await ctx.send(" tout les personnes qui on effectuer le daily on été oublié")
    #     else:
    #         try:
    #             target_id = int(target)
    #         except:
    #             return await ctx.send(f"Merci de fournir un identifiant corect !\n(me, all ou un id)")
    #         if target_id not in data.daily_people["people"]:
    #             return await ctx.send(f"L'id {target_id} n'est pas dans la liste")
    #         index = data.daily_people["people"].index(target_id)
    #         del data.daily_people["people"][index]
    #         return await ctx.send(f"l'id {target_id} a bien été oubliez de la liste")

            
    @commands.hybrid_command(name="statistique")
    @Check.is_in_dev_team()
    async def statistique(self, ctx : commands.Context, advanced:str = None):
        """
        Donne des info sur les Medalliums/sacoches et autre informations sur les utilisateurs du bot
        """
        
        total_user_md = 0
        total_size_md = 0
        
        total_user_bag = 0
        total_size_bag = 0
        
        #Medallium part
        for dirpath, _, filenames in os.walk("./files/inventory"):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp) and f.endswith(".json"):
                    total_user_md += 1
                    total_size_md += os.path.getsize(fp)
                    
        #Bag part
        for dirpath, _, filenames in os.walk("./files/bag"):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp) and f.endswith(".json"):
                    total_user_bag += 1
                    total_size_bag += os.path.getsize(fp)
        
        
        #mk the embed
        stats_embed = discord.Embed(color=discord.Color.green(), title="Voici les stats de l'inventaire :")
        stats_embed.add_field(name="Le nombre d'utilisateurs qui ont un inventaire :", value=f"`{total_user_md}` utilisateurs", inline=False)
        stats_embed.add_field(name="Taille du dossier `inventory`", value=f"`{total_size_md}` octets", inline=False)
        stats_embed.add_field(name="--------------------",value="")
        stats_embed.add_field(name="Le nombre d'utilisateurs qui ont une sacoche :", value=f"`{total_user_bag}` utilisateurs", inline=False)
        stats_embed.add_field(name="Taille du dossier `bag`", value=f"`{total_size_bag}` octets", inline=False)
        if advanced == None:
            return await ctx.send(embed=stats_embed)
        else:
            stats_embed.set_footer(text="partie 1/2")
            await ctx.send(embed=stats_embed)
        
        # Calculate total yokai
        total_yokai = 0
        ranks = ["E", "D", "C", "B", "A", "S", "LegendaryS", "treasureS", "SpecialS", "DivinityS", "Boss", "Shiny"]
        for dirpath, _, filenames in os.walk("./files/inventory"):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp) and f.endswith(".json"):
                    f = f.removesuffix(".json")
                    medallium = await Cf.get_inv(f)
                    for rank in ranks:
                        if rank in medallium:
                            total_yokai += medallium[rank]

        total_money=0
        for user in data.MONEY_DATA:
            total_money += data.MONEY_DATA[user]

        statis_embed = discord.Embed(color=discord.Color.green(), title="Voici les stats avancées")
        statis_embed.add_field(name="Totals de yo-kai en circulation", value=f"`{total_yokai}` yo-kai")
        statis_embed.add_field(name="Totals d'orbes en circulation", value=f"{total_money} orbes")
        activation_count = int(data.terrheure.get("stats", {}).get("activation_time", 0))
        statis_embed.add_field(name="nombre d'activation de la terrheure", value=f"{activation_count} Terrheure ont déjà été activé")
        statis_embed.set_footer(text="partie 2/2")
        return await ctx.send(embed=statis_embed)



      
    # @commands.hybrid_command(name="give")
    # @Check.is_in_dev_team()
    # @app_commands.autocomplete(rang=class_autcomplete)
    # async def give(self, ctx : commands.Context, input_id : str, yokai : str, rang : str, where:Literal["bag","medallium"], rank_orbe: bool = False, number : str = '1'):
    #     """
    #     Give un Yo-kai/Pièce/Trésor/Objet à un utilisateur donné.
    #     `.give <id de l'utilisateur> <nom> <rang> <bag/medallium> <orbe:True/False> <quantité>`
        
    #     Dans le cas où le rang est "json-mod":
    #     `.give <id de l'utilisateur> <Valeur> json-mod <bag/medallium> <valeur de la clée>`
    #     ⚠️ ** N'utilisez ce mode qui si vous savez ce que vous faites !**
    #     """
    #     if input_id.startswith("m"):
    #         input_id = input_id[1:]
    #         try:
    #             message = await ctx.channel.fetch_message(input_id)
    #         except discord.NotFound:
    #             return await ctx.send("Message introuvable dans ce salon.", ephemeral=True)
    #         except discord.Forbidden:
    #             return await ctx.send("Je n'ai pas la permission de lire ce message.", ephemeral=True)
    #         except discord.HTTPException:
    #             return await ctx.send("Erreur lors de la récupération du message.", ephemeral=True)

    #         mentions = message.mentions
    #         for user in mentions:
    #             input_id = ",".join(str(user.id))
            
    #     input_id_c = input_id.split(", ")
    #     del input_id
    #     input_ids = []
        
    #     try:
    #         for id in input_id_c:
    #             input_ids.append(int(id))
    #     except :
    #         error_embed = discord.Embed(
    #             title="Merci de verifier que vous utilisez le bon format :",
    #             description="`input_id: id1, id2, id3` ou `input_id: id1`",
    #             color= discord.Color.red()
    #         )
    #         return await ctx.send(embed=error_embed)
        
    #     sucess_embed = discord.Embed(title=f"Votre action de give a été exécutée, voici le bilan:",
    #                                         color=discord.Color.green(),
    #                                         description=""
    #                                         )
        
    #     # loop through the ids
    #     for input_id in input_ids:
    #         #get the inv or the bag:
    #         if where == "bag":
    #             inv = await Cf.get_bag(input_id)
    #             default_inv = data.default_bag.copy()
    #             async def save_inv(data, id):
    #                 await Cf.save_bag(data=data, id=id)
                
    #         elif where == "medallium":
    #             inv = await Cf.get_inv(input_id)
    #             default_inv = data.default_medallium.copy()
    #             async def save_inv(data, id):
    #                 await Cf.save_inv(data=data, id=id)
                
    #         else:
    #             error_embed = discord.Embed(
    #                 title="Merci de fournir une localisation (where) correcte!",
    #                 description="Soit `bag` soit `medallium`.",
    #                 color= discord.Color.red()
    #             )
    #             return await ctx.send(embed=error_embed)
            
    #         #format the number :
    #         try :
    #             number = int(number)
    #         except :
    #             pass
            
            
    #         #First, verify if the command is used to mod the inv .json directly
    #         if rang == "json-mod" :
    #             #verify if the inv is empty :
    #             if inv == {}:
    #                 inv = default_inv
    #             #now, mod the json as asked
    #             inv[yokai] = number
    #             await save_inv(inv, input_id)
    #             sucess_embed.add_field(name=f"La valeur `{yokai}` a été modifié sur `{number}` dans le {where} de `<@{input_id}>`",
    #                                    value="--------------") 
    #             self.bot.logger.warning(msg=f"{ctx.author.name} a utilisé le /give sur l'id {input_id}, en mode json-mod, dans le {where}")
    #             continue

                        
            
    #         if rang == "claim":
    #             #In case they are trying to give claims
                
    #             inv = await Cf.get_inv(input_id)
                
    #             if inv == {}:
    #                 inv = data.default_medallium.copy()

    #             inv["claim"] = number
    #             await save_inv(inv, input_id)
    #             sucess_embed.add_field(name=f"`<@{input_id}>` a reçu {number} claims",
    #                                    value="--------------")
    #             self.bot.logger.warning(msg=f"{ctx.author.name} a utilisé le /give sur l'id {input_id}, il a donné {number} claims")
    #             continue

            
            
            
    #         #so, now that we know that the command is used to give a yokai, we have to: 
    #         # format the input:
    #         try :
    #             number = int(number)
            
    #         except :
    #             error_embed = discord.Embed(
    #                     title="La quantité fournie n'est pas valide.",
    #                     description="Merci de verifier si la commande est utilisée de manière valide (`/help Admin_command`)",
    #                     color= discord.Color.red()
    #                 )
    #             return await ctx.send(embed=error_embed)
            
            
            
            
            
            
    #         #Verify if the class (rang) is fine :
    #         class_name = rang
    #         class_id = await Cf.classid_to_class(class_name, True)
    #         if class_id == "" :
    #             #if the class does not exist, it return "" and we can catch it
    #             error_embed = discord.Embed(
    #                 title="Le rang fourni n'est pas valide.",
    #                 description="Merci de verifier si la commande est utilisée de manière valide (`/help Admin_command`)",
    #                 color= discord.Color.red()
    #             )
    #             return await ctx.send(embed=error_embed)
            
    #         if class_id in ["coin", "obj", "treasure"] and where == "medallium":
    #             #Check if the class is valid for the place choosen (medallium)
    #             error_embed = discord.Embed(
    #                 title="Le rang fourni n'est pas valide.",
    #                 description="Il ne fait pas partie des rang suportés dans le médallium",
    #                 color= discord.Color.red()
    #             )
    #             return await ctx.send(embed=error_embed)
            
    #         if not class_id in ["coin", "obj", "treasure"] and where == "bag":
    #             #Check if the class is valid for the place choosen (bag)
    #             error_embed = discord.Embed(
    #                 title="Le rang fourni n'est pas valide.",
    #                 description="Il ne fait pas partie des rang suportés dans le bag",
    #                 color= discord.Color.red()
    #             )
                
    #             return await ctx.send(embed=error_embed)
            

            
            
            
    #         #Verify if the input id has an inventory file :
    #         if inv == {}:
    #             #set the inv to the default
    #             inv = default_inv
                
    #             inv[yokai] = [class_id]
                
    #             inv[class_id] = 1
    #             if not number == 1 :
    #                 inv[yokai].append(int(number))
    #             await save_inv(data=inv, id=input_id)
                
    #         else :
    #             #we have to verify :
    #             # 1. If the yokai is already in the inv
    #             # 2. If yes, if there is already many oh this yokai
    #             # and we do it in range(number) to give several yokai
    #             for i in range(number) :
    #                 try:
    #                     inv[yokai]
    #                     try:
    #                         #stack the yokai
    #                         inv[yokai][1] += 1
    #                         # give orb if the argument is true
    #                         if rank_orbe:
    #                             eco.add_rank_orbe(input_id,rang)
    #                     except :
    #                         #return an exception if the yokai was not stacked
    #                         #so we know there is only one and we can add the mention of two yokai ( .append(2) )
    #                         inv[yokai].append(2)
    #                 except KeyError:
    #                     #return an exception if the yokai was not in the inv
    #                     #add it
    #                     inv[yokai] = [class_id]
    #                     #add one more to the yokai count of the coresponding class
    #                     try:
    #                         inv[class_id] += 1
    #                     except:
    #                         inv[class_id] = 1
                            
    #                 #save the inv
    #                 await save_inv(data=inv, id=input_id)
                
    #         sucess_embed.add_field(name=f"Yo-Kai ajouté(s) {"au Médallium" if where=="medallium" else "à la sacoche"} de {input_id}",
    #                                 value=f"**{yokai}** de rang **{rang}**\n> quantité : {number}\n----------------")
    #         self.bot.logger.warning(msg=f"{ctx.author.name} a utilisé le /give sur l'id {input_id} // yokai : {yokai} // rang : {rang} // x{number}")

    #     return await ctx.send(embed=sucess_embed)
                
                
    
    
    
 
    # @commands.hybrid_command(name="remove")
    # @Check.is_in_dev_team()
    # @app_commands.autocomplete(rang=class_autcomplete)
    # async def remove(self, ctx : commands.Context, input_id : str, yokai : str, rang : str, where:Literal["bag","medallium"], number : int = 1): 
    #     """
    #     Remove un Yo-kai à un utilisateur donné.
    #     `.remove <id de l'utilisateur> <nom> <rang> <bag/medallium> <quantité>`
    #     """
        
        
    #     #first of all, format the input:
    #     #is the input id fine ?
    #     try:
    #         input_id = int(input_id)
    #     except :
    #         error_embed = discord.Embed(
    #             title="Merci de fournir un identifiant corect !",
    #             color= discord.Color.red()
    #         )
    #         return await ctx.send(embed=error_embed)
        
        
        
    #      #get the inv or the bag:
    #     if where == "bag":
    #         inv = await Cf.get_bag(input_id)
    #         default_inv = data.default_bag.copy()
    #         async def save_inv(data, id):
    #             await Cf.save_bag(data=data, id=id)
            
    #     elif where == "medallium":
    #         inv = await Cf.get_inv(input_id)
    #         default_inv = data.default_medallium.copy()
    #         async def save_inv(data, id):
    #             await Cf.save_inv(data=data, id=id)
            
    #     else:
    #         error_embed = discord.Embed(
    #             title="Merci de fournir une localisation (where) correcte!",
    #             description="Soit `bag` soit `medallium`.",
    #             color= discord.Color.red()
    #         )
    #         return await ctx.send(embed=error_embed)
        
        
        
        
    #     #Verify if the class (rang) is fine :
    #     class_name = rang
    #     class_id = await Cf.classid_to_class(class_name, True)
        
    #     if class_id in ["coin", "obj", "treasure"] and where == "medallium":
    #         #Check if the class is valid for the place choosen (medallium)
    #         error_embed = discord.Embed(
    #             title="Le rang fourni n'est pas valide.",
    #             description="Il ne fait pas partie des rang suportés dans le médallium",
    #             color= discord.Color.red()
    #         )
    #         return await ctx.send(embed=error_embed)
        
    #     if not class_id in ["coin", "obj", "treasure"] and where == "bag":
    #         #Check if the class is valid for the place choosen (bag)
    #         error_embed = discord.Embed(
    #             title="Le rang fourni n'est pas valide.",
    #             description="Il ne fait pas partie des rang suportés dans le bag",
    #             color= discord.Color.red()
    #         )
            
    #         return await ctx.send(embed=error_embed)
        
        
    #     #Verify if the input id has an inventory file :
    #     if inv == {}:
    #         error_embed = discord.Embed(
    #             title=f"Ce Yo-kai n'est pas dans le Médallium de {input_id}",
    #             description="Merci de vérifier si la commande est utilisée de manière valide (`/help Admin_command`)",
    #             color= discord.Color.red()
    #         )
    #         return await ctx.send(embed=error_embed)
            
    #     else :
    #         #we have to verify :
    #         # 1. If the yokai is already in the inv
    #         # 2. If yes, if there is already many oh this yokai
    #         # and we do it in range(number) to delete several yokai
            
    #         for i in range(number) :
    #             try :
    #                 one_more_author = inv[yokai][1] > 1
                
                
    #             except KeyError:
    #                 error_embed = discord.Embed(
    #                     title=f"Cet élément n'est pas dans le {where} de {input_id}",
    #                     description="Merci de vérifier si la commande est utilisée de manière valide (`/help Admin_command`)",
    #                     color= discord.Color.red()
    #                 )
    #                 return await ctx.send(embed=error_embed)
                
                
    #             except IndexError :
    #                 if number - i > 1 :
    #                     error_embed = discord.Embed(
    #                         title=f"Vous avez demandé plus de Yo-kai que il n'y en a dans ce {where}.",
    #                         description=f"Le nombre actuel dans le {where} est : `1`",
    #                         color= discord.Color.red()
    #                     )
    #                     return await ctx.send(embed=error_embed)
    #                 one_more_author = False
                    
    #             if one_more_author == True :
    #                 if number - i > inv[yokai][1] :
    #                     #return an error if the user want to remove more yokai than there is in the corespondign Medallium
    #                     error_embed = discord.Embed(
    #                         title=f"Vous avez demandé plus de Yo-kai que il n'y en a dans ce Médallium.",
    #                         description=f"Le nombre actuel dans le Médallium est : `{inv[yokai][1]}`",
    #                         color= discord.Color.red()
    #                     )
    #                     return await ctx.send(embed=error_embed)
                        
                        
    #                 #just remove the mention of several yokai if there are juste two
    #                 if inv[yokai][1] == 2:
    #                     inv[yokai].remove(inv[yokai][1])
    #                 else:
    #                     inv[yokai][1] -= 1
                            
    #             else :
    #                 inv.pop(yokai)
    #                 inv[class_id] -= 1
    #             await save_inv(data=inv, id=input_id)
            
    #     sucess_embed = discord.Embed(title=f"Le(s) Yo-Kai a été retiré {"du Médallium" if where=="medallium" else "de la sacoche"} de {input_id}",
    #                                     color=discord.Color.green(),
    #                                     description=f"**{yokai}** de rang **{rang}** \n> quantité : {number} "
    #                                     )
    #     self.bot.logger.warning(msg=f"{ctx.author.name} a utilisé le /remove sur l'id {input_id}, le yokai {yokai}, la quantité {number}")
    #     return await ctx.send(embed=sucess_embed)
    
    @commands.hybrid_command(name="export")
    @Check.is_in_dev_team()
    async def export(self, ctx : commands.Context, input_id : str,where:Literal["inventory"]): 
        """
        Export le json brute de l'entrée demandée.
        """
        #make the file path
        if where != "inventory":
            return await ctx.send("Merci d'utiliser un \"where\" valide!", ephemeral=True)
        
        path = "./files/inventory/"
        path += input_id+".json" 
        
        try:
            await ctx.send("Voici le fichier !", file=discord.File(path))
        except Exception as e:
            await ctx.send(f"Error: {e}", ephemeral=True)
            
    
    @commands.hybrid_command(name="import")
    @Check.is_in_dev_team()
    async def import_func(self, ctx : commands.Context, input_id : str, file: discord.Attachment,where:Literal["inventory"]): 
        """
        Import le json brute de l'entrée demandée.
        """
        #make the file path
        if where != "inventory":
            return await ctx.send("Merci d'utiliser un \"where\" valide!", ephemeral=True)
        
        path = "./files/inventory/"
        path += input_id + ".json"
        
        try:
            # Download the file from Discord
            file_content = await file.read()
            
            # Save the file to the specified path
            with open(path, 'wb') as f:
                f.write(file_content)
            
            sucess_embed = discord.Embed(
                title=f"Fichier importé avec succès !",
                description=f"Le fichier a été sauvegardé dans `{path}`",
                color=discord.Color.green()
            )
            self.bot.logger.warning(msg=f"{ctx.author.name} a utilisé le /import sur l'id {input_id} dans le {where}")
            await ctx.send(embed=sucess_embed)
        except Exception as e:
            await ctx.send(f"Erreur: {e}", ephemeral=True)
                
    @commands.hybrid_command(name="log")
    @Check.is_in_dev_team()
    async def log(self, ctx : commands.Context, contenu1:str, contenu2:str = None):
        """
        Log un message dans le fichier de log du bot.
        """
        logfile = "./discord.log"
        results = []
        try:
            with data.open_json("./discord.log") as f:
                for line in f:
                    l = line.rstrip("\n")
                    if contenu2:
                        if contenu1 in l and contenu2 in l:
                            results.append(l)
                    else:
                        if contenu1 in l:
                            results.append(l)
        except FileNotFoundError:
            await ctx.send(f"Fichier de log introuvable: {logfile}")
            return
        except Exception as e:
            await ctx.send(f"Erreur lors de la lecture du fichier de log: {e}")
            return

        if not results:
            await ctx.send("Aucun résultat trouvé.")
            return

        content = "\n".join(results)
        # Discord message length limit ~2000, send as file if too long
        if len(content) > 1900:
            bio = io.BytesIO(content.encode("utf-8"))
            bio.seek(0)
            await ctx.send(file=discord.File(fp=bio, filename="results.txt"))
        else:
            await ctx.send(f"{content}")


async def setup(bot : commands.Bot ) -> None:
    await bot.add_cog(Admin_command(bot))