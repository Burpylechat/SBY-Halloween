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

    
    @commands.hybrid_command(name="give")
    @Check.is_in_dev_team()
    async def give(self, ctx : commands.Context, input_id : discord.User,where:Literal["coin","yokai","energie","points","objet"],thing:str="",number:int=1):
        inventory = await Cf.get_inv(input_id.id)
        if inventory == {}:
            fail = discord.Embed(
                title = f"{input_id.name} n'as pas commencé l'event"
            )
            return await ctx.send(embed=fail)
        if where == "coin" or where == "yokai" or where == "objet":
            if thing == "":
                fail_embed = discord.Embed(
                    title = "Veillez préciser un yokai/pièce/objet!",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=fail_embed)
            try:
                inventory[where][thing] += number
            except KeyError:
                inventory[where][thing] = number
            embed = discord.Embed(
                title = f"Vous avez donné un {number}X{thing} à {input_id.name}"
            )
        else:
            inventory[where] += number
            embed = discord.Embed(
                title = f"Vous avez donné {number} {where} à {input_id.name}.\nIl en a désormais {inventory[where]}."
            )
        await Cf.save_inv(inventory,input_id.id)
        return await ctx.send(embed=embed)

    @commands.hybrid_command(name="remove")
    @Check.is_in_dev_team()
    async def remove(self, ctx : commands.Context, input_id : discord.User,where:Literal["coin","yokai","energie","points","objet"],thing:str="",number:int=1):
        inventory = await Cf.get_inv(input_id.id)
        if inventory == {}:
            fail = discord.Embed(
                title = f"{input_id.name} n'as pas commencé l'event"
            )
            return await ctx.send(embed=fail)
        if where == "coin" or where == "yokai" or where == "objet":
            if thing == "":
                fail_embed = discord.Embed(
                    title = "Veillez préciser un yokai/pièce!",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=fail_embed)
            try:
                inventory[where][thing] -= number
                if inventory[where][thing] <= 0:
                    del inventory[where][thing]
                    print(inventory)
            except KeyError:
                fail = discord.Embed(
                    title=f"{input_id.name} n'as pas de {thing} de type {where}"
                )
                return await ctx.send(embed=fail)
            embed = discord.Embed(
                title = f"Vous avez retiré un {number}X{thing} à {input_id.name}"
            )
        else:
            inventory[where] -= number
            embed = discord.Embed(
                title = f"Vous avez retiré {number} {where} à {input_id.name}.\nIl lui en reste {inventory[where]}."
            )
        await Cf.save_inv(inventory,input_id.id)
        return await ctx.send(embed=embed)
        

    
 
    @commands.hybrid_command(name="reset")
    @Check.is_in_dev_team()
    async def reset(self, ctx : commands.Context, input_id : discord.User):
        """
        Reset l'inventaire de l'utilisateur donné.
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