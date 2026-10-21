import os
import json
import bot_package.data as data
from difflib import SequenceMatcher
import aiofiles
import time
import random
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands


if os.name == "nt":  # Only execute on Windows
    def fix_encoding(obj):
        #the func that encode well everything; bcs we are french, we use é, à, è
            if isinstance(obj, dict):
                return {fix_encoding(k): fix_encoding(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_encoding(item) for item in obj]
            elif isinstance(obj, str):
                try:
                    return obj.encode('latin-1').decode('utf-8')
                except UnicodeEncodeError:
                    return obj
                except UnicodeDecodeError:
                    return obj
            else:
                return obj

else:
    def fix_encoding(obj):            
        return obj


#Get inv func
async def get_inv(id : int):
    """
    A func to get the inv of a user (with his id)
    """
    if os.path.exists(f"./files/inventory/{str(id)}.json"):
        async with aiofiles.open(f"./files/inventory/{str(id)}.json") as f:
            content = await f.read()
            data = fix_encoding(json.loads(content))
    else :
        # Return nothing if there's nothing to :/
        data = {}
       
    return data



#save inv func
async def save_inv(data : dict, id : int):
    """
    A func to save the inv of a user (with his id)
    """
    async with aiofiles.open(f"./files/inventory/{str(id)}.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))


async def get_midnight():
    """
    A function that return the time at midnight
    """
    # Get current time and convert to midnight timestamp
    current_time = time.time()
    current_day = time.localtime(current_time)
    midnight = time.mktime((current_day.tm_year, current_day.tm_mon, 
                            current_day.tm_mday, 0, 0, 0, 0, 0, 0))
    midnight -= 3600
    return midnight


async def energie_reset(user:int, ctx:commands.context):
    """
    """
    inventory = await get_inv(user)
    midnight = await get_midnight()
    if inventory["last_reset"] < midnight:
        inventory["energie"] = 100
        inventory["last_reset"] = midnight
        await save_inv(inventory,user)
        energie_reset_embed = discord.Embed(
            title = "Énergie réinitialisé",
            description = "Votre énergie quotidienne à été réinitialisé, elle est désormais à 100.",
            color=discord.Color.green()
        )
        return await ctx.send(embed=energie_reset_embed)

async def give(thing:str,where:str,inventory:dict,number:int=1):
    try:
        inventory[where][thing] += number
    except KeyError:
        inventory[where][thing] = number
    return inventory

async def determinant(word:str,det:str="le"):
    if word in data.feminin.copy():
        if det == "le":
            return f"la {word}"
        elif det == "de":
            return f"de la {word}"
        else:
            return f"à la {word}"
    elif word in data.pluriels.copy():
        if det == "le":
            return f"les {word}"
        elif det == "de":
            return f"des {word}"
        else:
            return f"aux {word}"
    elif word in data.nothing.copy():
        word = list(word)
        word[0] = word[0].upper()
        complete_word = ""
        for letter in word:
            complete_word += letter
        return complete_word
    elif word[0] in ["a", "e", "i", "o", "u", "y"] and det == "le":
            return f"l'{word}"
    else:
        if det == "le":
            return f"le {word}"
        elif det == "de":
            return f"du {word}"
        else:
            return f"au {word}"

async def have_started(ctx):
    inventory = await get_inv(ctx.author.id)
    if inventory == {}:
        not_started_embed = discord.Embed(
            title = "Vous n'avez pas commencé l'évènement !",
            description = "Faites /start pour commencer l'évènement.",
            color = discord.Color.red()
        )
        await ctx.send(embed=not_started_embed)
        return False
    else:
        return True

async def aggressif_check(user:int,ctx:commands.context,reverse:bool=False, amadouer:bool=False):
    inventory = await get_inv(user)
    if reverse:
        if not inventory["yokai aggressif"]["Activated"]:
            if not amadouer:
                fail_embed = discord.Embed(
                    title="Il n'y a aucun yokai aggressif à fuire.",
                    color=discord.Color.red()
                )
            else:
                fail_embed = discord.Embed(
                    title="Il n'y a aucun yokai aggressif à amadouer.",
                    color=discord.Color.red()
                )
            await ctx.send(embed=fail_embed)
            return False
        return True
    if inventory["yokai aggressif"]["Activated"]:
        fail_embed = discord.Embed(
            title="Il y a un yokai aggressif qui vous attaque.",
            description="Vous devez faire /fuire ou /amadouer avant de pouvoir éxécuter cette commande!",
            color=discord.Color.red()
        )
        await ctx.send(embed=fail_embed)
        return True
    return False