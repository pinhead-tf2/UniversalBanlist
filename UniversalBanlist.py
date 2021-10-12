import discord
from discord import guild
from discord import user
from discord.ext import commands
from discord.ext.commands import bot, has_permissions, CheckFailure
from discord.app import Option
import os
import sys
import sqlite3
import asyncio
from datetime import datetime, time
import random
from random import randint
from discord.ext.commands.flags import F
from discord.flags import Intents
from dotenv import load_dotenv

botPrefix = 'u.'
bot = commands.Bot(command_prefix=botPrefix, help_command=None)
client = discord.Client()
botStartTime = datetime.now()

statusList = ["Discord latency", "for errors", "uptime"]
guild_ids = [886442801812877402]
authorized_users = [246291288775852033]

@bot.event
async def on_ready():
    db = sqlite3.connect('banlist.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banlist(
        ban_id TEXT,
        user_id TEXT,
        time TEXT,
        type TEXT,
        reason TEXT
        )
    ''')
    # guilds = await client.fetch_guilds(limit=150).flatten()
    # print(guilds)
    print("fuck you <3")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Time to start: ' + str((datetime.now() - botStartTime))))
    await asyncio.sleep(10)
    client.loop.create_task(rotateStatus())

#  __            
# |__)  /\  |\ | 
# |__) /~~\ | \| 

@bot.slash_command(guild_ids=guild_ids)
async def ban(
    ctx,
    userid: Option(str, "Insert the ID of the user you wish to ban here.", required=True),
    bantype: Option(str, "Choose the ban type.", choices=["Bot", "Raider"], required=True),
    reason: Option(str, "Insert a reason for the user's ban.", required=True),
    ):
    if ctx.author.id in authorized_users:
        userCheck = await bot.fetch_user(int(userid))
        if userCheck:
            db = sqlite3.connect('banlist.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT user_id FROM banlist WHERE user_id = {userid}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO banlist(user_id, time, type, reason) VALUES(?, ?, ?, ?)")
                bantime = str(datetime.now())
                val = (userid, bantime, bantype, reason)
                cursor.execute(sql, val)
                rowid = str(cursor.lastrowid)
                db.commit()
                cursor.close()
                db.close()
                # await ctx.guild.ban(userCheck)
                embed = discord.Embed(color = discord.Color.green(), title='Successfully banned user!')
                embed.add_field(name='Ban Info', value='Ban ID: `' + rowid + '`\nUser ID: `' + userid + '`\nBan Time: `' + bantime + '`\nType: `' + bantype + '`\nReason: `' + reason + '`', inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(color = discord.Color.red())
                embed.add_field(name='An error occured while running this command', value='This user is already in the banlist!')
                await ctx.send(embed=embed)

@bot.slash_command(guild_ids=guild_ids)
async def updateban(
    ctx,
    userid: Option(str, "Insert the ID of the banned user.", required=True),
    bantype: Option(str, "Update the ban's type.", choices=["Bot", "Raider"], required=True),
    reason: Option(str, "Update the ban's reason.", required=True),
    ):
    if ctx.author.id in authorized_users:
        db = sqlite3.connect('banlist.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM banlist WHERE user_id = {userid}")
        result = cursor.fetchone()
        if result is None:
            embed = discord.Embed(color = discord.Color.red())
            embed.add_field(name='An error occured while running this command', value='This user is not in the banlist!')
            await ctx.send(embed=embed)
        else:
            cursor2 = db.cursor()
            cursor2.execute(f"SELECT time FROM banlist WHERE user_id = {userid}")
            bantime = str(cursor2.fetchone())
            sql = ("UPDATE banlist SET type = ?, reason = ? WHERE user_id = ?")
            val = (bantype, reason, userid)
            cursor.execute(sql, val)
            rowid = str(cursor.lastrowid)
            db.commit()
            cursor.close()
            cursor2.close()
            db.close()
            embed = discord.Embed(color = discord.Color.green(), title='Successfully updated ban info!')
            embed.add_field(name='Ban Info', value='Ban ID: `' + rowid + '`\nUser ID: `' + userid + '`\nBan Time: `' + bantime + '`', inline=False)
            embed.add_field(name='Updated Values', value='Type: `' + bantype + '`\nReason: `' + reason + '`', inline=False)
            await ctx.send(embed=embed)
        
@bot.command(pass_context=True)
async def embedTest(ctx):
    embed = discord.Embed(color = discord.Color.green(), title='Successfully updated ban info!')
    embed.add_field(name='Ban Info', value='Ban ID: `' + '1' + '`\nUser ID: `' + '764195980106399825' + '`', inline=False)
    embed.add_field(name='Updated Values', value='Type: `' + 'Raider' + '`\nReason: `' + "is a bitch made coward" + '`', inline=False)
    await ctx.send(embed=embed)

# @client.event
# async def on_member_join(ctx, member):
#     joinID = member.id
#     print(joinID)
#     currentGuild = bot.get_guild(ctx.guild)
#     if currentGuild.guild_permissions.ban_members:
#         db = sqlite3.connect('banlist.sqlite')
#         cursor = db.cursor()
#         cursor.execute(f"SELECT user_id FROM banlist WHERE user_id = {joinID}")
#         result = cursor.fetchone()
#         print (result)
#         if result is not None:
#             print(result)
#             await ctx.guild.ban(member)

#            __            
# |  | |\ | |__)  /\  |\ | 
# \__/ | \| |__) /~~\ | \|

@bot.command(pass_context=True, aliases=['removeban', 'deleteban'])
async def unban(ctx, user: discord.User, *messageContent):
    msg = await ctx.fetch_message(ctx.message.id)

#       __  ___          ___ 
# |  | |__)  |  |  |\/| |__  
# \__/ |     |  |  |  | |___ 

@bot.command(pass_context=True, aliases=['runTime', 'runDuration'])
async def uptime(ctx):
    startTime = datetime.now()
    runTime = startTime.replace(microsecond=0) - botStartTime.replace(microsecond=0)
    embed = discord.Embed(color = discord.Color.blue())
    embed.add_field(name='Uptime (hh:mm:ss):', value=runTime)
    await ctx.send(embed=embed)

#  __          __  
# |__) | |\ | / _` 
# |    | | \| \__> 

@bot.command(pass_context=True, aliases=['lag', 'latency'])
async def ping(ctx):
    botLatency = bot.latency*1000
    embed = discord.Embed(color = discord.Color.blue())
    embed.add_field(name='Pong! Delay:', value=botLatency)
    await ctx.send(embed=embed)

#  __            ___  __   __            
# /__` |__| |  |  |  |  \ /  \ |  | |\ | 
# .__/ |  | \__/  |  |__/ \__/ |/\| | \| 

@bot.command(pass_context=True, aliases=['stop', 'kill'])
async def shutdown(ctx):
    if ctx.author.id == 246291288775852033:
        exit()  

#  __   __   ___  __   ___       __   ___     __   __  ___      ___    __       
# |__) |__) |__  /__` |__  |\ | /  ` |__     |__) /  \  |   /\   |  | /  \ |\ | 
# |    |  \ |___ .__/ |___ | \| \__, |___    |  \ \__/  |  /~~\  |  | \__/ | \| 

async def rotateStatus():
    while True:
        random.seed(a=None, version=2)
        randomValue = randint(0, 100)
        if randomValue <= 5 and randomValue >= 2:
            await bot.change_presence(activity=discord.Game(name="Team Fortress 2"))
            await asyncio.sleep(randint(10, 60))
        elif randomValue <= 1:
            await bot.change_presence(activity=discord.Game(name="Titanfall 2"))
            await asyncio.sleep(randint(10, 60))
        else: 
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(statusList)))
            await asyncio.sleep(randint(10, 60))

load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))