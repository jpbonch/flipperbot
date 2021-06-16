import discord
import random
import asyncio
import json
import atexit
from datetime import datetime

intents = discord.Intents().all()
client = discord.Client(intents=intents)

# user commands:
# Flip
# bal
# rank
# pay
# shop

# admin commands:
# give
# take
# event
# stop

async def load_data():
    with open('data.json') as json_file:
        try:
            raw_data = json.load(json_file)
        except json.decoder.JSONDecodeError:
            raw_data = {}
        data = {await client.fetch_user(int(k)): v for k, v in raw_data.items()}
        return data


def update_file():
    with open('data.json', 'w+') as f:
        data_copy = {k.id: v for k, v in data.items()}
        json.dump(data_copy, f)
atexit.register(update_file)


def check_user(user):
    if not user.bot:
        if user not in data.keys():
            data[user] = {"bal": 0, "badge": '👤', "name": user.name, "badges": [], "cfwins": 0, "income":5, "mascot":"none", "sound":"none"}


async def ten_second_save():
    while True:
        update_file()
        await asyncio.sleep(10)


async def income():
    while True:
        for user in data.keys():
            data[user]['bal'] += data[user]['income']
        await asyncio.sleep(3600)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="$flip <amount>"))

    global data
    data = await load_data()
    print("Data loaded.")

    for guild in client.guilds:
        for member in guild.members:
            check_user(member)

    await asyncio.gather(ten_second_save(), income())


@client.event
async def on_member_join(member):
    check_user(member)


async def crate_shop(message):
    catalog = """\U0001F4E6Common Crate - $100
\U0001F381Rare Crate - $1000
\U00002618Epic Crate - $5000
\U0001F4B0Legendary Crate - $10000"""

    embed = discord.Embed(color=0xFFFF00)
    # embed.set_image(url="attachment://image.png")
    embed.add_field(name="CRATE SHOP", value="Luck-based lootboxes", inline=False)
    embed.add_field(name="‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾", value=catalog, inline=False)
    embed.set_footer(text="Click a crate below to buy it")
    mes = await message.channel.send(embed=embed)
    for emoji in ['\U0001F4E6', '\U0001F381', '\U00002618', '\U0001F4B0']:
        await mes.add_reaction(emoji)


    check = lambda reaction, user, mes=mes: client.user != user and reaction.message == mes
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)
        except asyncio.TimeoutError:
            await mes.delete()
            break
        await mes.remove_reaction(reaction.emoji, user)
        cost = {'\U0001F4E6':100, '\U0001F381':1000, '\U00002618':5000, '\U0001F4B0':10000}
        if data[user]['bal'] < cost[reaction.emoji]:
            embed = discord.Embed(color=0xFFFF00, description='Not enough money for that crate ' + data[user]['badge'] + user.mention)
            await message.channel.send(embed=embed)
            continue
        data[user]['bal'] -= cost[reaction.emoji]
        l = random.random()
        if reaction.emoji == '\U0001F4E6':
            if l < 0.1:
                winnings = 500
            elif l < 0.4:
                winnings = 150
            elif l < 0.8:
                winnings = 50
            elif l < 1:
                winnings = 1
        elif reaction.emoji == '\U0001F381':
            if l < 0.1:
                winnings = 5000
            elif l < 0.4:
                winnings = 1500
            elif l < 0.8:
                winnings = 500
            elif l < 1:
                winnings = 10
        elif reaction.emoji == '\U00002618':
            if l < 0.1:
                winnings = 20000
            elif l < 0.4:
                winnings = 7500
            elif l < 0.8:
                winnings = 2500
            elif l < 1:
                winnings = 50
        elif reaction.emoji == '\U0001F4B0':
            if l < 0.1:
                winnings = 30000
            elif l < 0.4:
                winnings = 15000
            elif l < 0.8:
                winnings = 5000
            elif l < 1:
                winnings = 100
        data[user]['bal'] += winnings
        desc = data[user]['badge'] + user.mention +' Bought crate -$'+str(cost[reaction.emoji]) + '\n' + (
               data[user]['badge']+user.mention+' The crate dropped +$'+ str(winnings))
        col = 0xFF0000 if cost[reaction.emoji] > winnings else 0x00FF00
        embed = discord.Embed(color=col, description=desc)
        await message.channel.send(embed=embed)


async def badge_shop(message):
    badges = {'\U0001F4A2':250, '\U00002744':250, '\U0001F4AA':250, '\U0001F340':250, '\U0001F4A6':250, '\U0001F608':5000, '\U0001F47D':5000,'\U000026A1':5000, '\U0001F4AF':5000, '\U0001F911':5000, '\U0001F525':25000, '\U0001F4A9':25000, '\U0001F3AE':25000, '\U0001F3C6':25000, '\U0001F52A':25000, '\U0001F43A':50000, '\U0001F300':50000, '\U0001F441':50000, '\U0001F0CF':50000, '\U0001F3B2':50000}
    fields = [[], [], [], []]
    i = 0
    for k, v in badges.items():
        fields[i//5].append(k)
        i += 1
    embed = discord.Embed(color=0xFFFF00)
    embed.add_field(name="BADGE SHOP", value="Cosmetic items displayed next to your name\n‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾", inline=False)
    embed.add_field(name="Common - $250", value=' '.join(fields[0]), inline=False)
    embed.add_field(name="Rare - $5000", value=' '.join(fields[1]), inline=False)
    embed.add_field(name="Epic - $25,000", value=' '.join(fields[2]), inline=False)
    embed.add_field(name="Legendary - $50,000", value=' '.join(fields[3]), inline=False)
    embed.set_footer(text="Click a badge below to buy it")
    mes = await message.channel.send(embed=embed)
    for emoji in badges.keys():
        await mes.add_reaction(emoji)
    check = lambda reaction, user, mes=mes: client.user != user and reaction.message == mes
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)
        except asyncio.TimeoutError:
            await mes.delete()
            break
        await mes.remove_reaction(reaction.emoji, user)
        if data[user]['bal'] < badges[reaction.emoji]:
            embed = discord.Embed(color=0xFFFF00, description='Not enough money for that badge ' + data[user]['badge'] + user.mention)
            await message.channel.send(embed=embed)
            continue
        if data[user]['badge'] == reaction.emoji:
            embed = discord.Embed(color=0xFFFF00, description='That badge is already equipped' + data[user]['badge'] + user.mention)
            await message.channel.send(embed=embed)
            continue
        if reaction.emoji in data[user]['badges']:
            embed = discord.Embed(color=0xFFFF00, description='You already own that badge, go to $profile to equip it.' + data[user]['badge'] + user.mention)
            await message.channel.send(embed=embed)
            continue
        data[user]['bal'] -= badges[reaction.emoji]
        data[user]['badges'].append(reaction.emoji)
        embed = discord.Embed(color=0xFFFF00, description=str(badges[reaction.emoji]) + ' subtracted from your balance. Use $profile to equip your new badge ' + data[user]['badge'] + user.mention)
        await message.channel.send(embed=embed)


async def mascot_shop(message):
    mascots = {'\U0001F9C1':250, '\U0001F468':250, '\U0001F34C':5000, '\U0001F30E':5000, '\U0001F438':25000, '\U0001F431':25000, '\U0001F47D':50000,'\U0001F435':50000}
    filenames = {'\U0001F9C1':"nyan.gif", '\U0001F468':"blink.gif", '\U0001F34C':"banana.gif", '\U0001F30E':"earth.gif", '\U0001F438':"pepe.gif", '\U0001F431':"catjam.gif", '\U0001F47D':"alien.gif",'\U0001F435':"monkey.gif"}

    embed = discord.Embed(color=0xFFFF00)
    embed.add_field(name="MASCOT SHOP", value="Animated collectibles displayed on your profile\n‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾", inline=False)
    file = discord.File("mascotshop.gif")
    embed.set_image(url="attachment://mascotshop.gif")
    embed.set_footer(text="Click the matching icon below to buy a mascot")
    mes = await message.channel.send(embed=embed, file=file)
    for emoji in mascots.keys():
        await mes.add_reaction(emoji)
    check = lambda reaction, user, mes=mes: client.user != user and reaction.message == mes
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)
        except asyncio.TimeoutError:
            await mes.delete()
            break
        await mes.remove_reaction(reaction.emoji, user)
        if data[user]['bal'] < mascots[reaction.emoji]:
            embed = discord.Embed(color=0xFFFF00, description='Not enough money for that mascot ' + data[user]['badge'] + user.mention)
            await message.channel.send(embed=embed)
            continue
        if data[user]['mascot'] == reaction.emoji:
            embed = discord.Embed(color=0xFFFF00, description='That mascot is already equipped' + data[user]['badge'] + user.mention)
            await message.channel.send(embed=embed)
            continue
        data[user]['bal'] -= mascots[reaction.emoji]
        data[user]['mascot'] = filenames[reaction.emoji]
        embed = discord.Embed(color=0xFFFF00, description=str(mascots[reaction.emoji]) + ' subtracted from your balance. Use $profile to see your new mascot ' + data[user]['badge'] + user.mention)
        await message.channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.bot:
        return

    if not message.content.startswith('$'):
        data[message.author]['bal'] += 1

    if message.content.startswith('$help') or message.content.startswith('$commands'):
        embed = discord.Embed(title="Commands", color=0xFFFF00, description="Prefix: $")
        embed.add_field(name="$flip <amount>", value="Start a coinflip which another user can accept: the winner takes the amount.\nAliases: $help, $commands", inline=False)
        embed.add_field(name="$bal", value="Check your current balance.", inline=False)
        embed.add_field(name="$rank", value="List the richest user in the server.\nAliases: $rank, $baltop", inline=False)
        embed.add_field(name="$pay <target> <amount>", value="Pays the target a specified amount out of your balance. The target must be an @ mention.", inline=False)
        embed.add_field(name="$shop", value="Shows the item shops.", inline=False)
        embed.add_field(name="$casino", value="Shows gambling options", inline=False)
        embed.add_field(name="$profile", value="Shows off your balance, mascot, badge, stats and more.", inline=False)
        await message.channel.send(embed=embed)

    if message.content.startswith('$bal'):
        embed = discord.Embed(description=data[message.author]['badge'] + message.author.mention + ' balance: $' + str(data[message.author]['bal']), color=0xFFFF00)
        await message.channel.send(embed=embed)

    if message.content.startswith('$rank') or message.content.startswith('$baltop'):
        data_copy = {k: v['bal'] for k, v in data.items() if k in message.guild.members}
        sorted_members = sorted(data_copy, key=data_copy.get, reverse=True)
        sorted_nicks = []
        for user in sorted_members:
            member = message.guild.get_member(user.id)
            if member.nick is None:
                sorted_nicks.append(member.name)
            else:
                sorted_nicks.append(member.nick)

        ret = ''
        iter = len(sorted_members) if len(sorted_members) < 11 else 10
        for i in range(iter):
            ret += f"{i+1}. {data[sorted_members[i]]['badge']}{sorted_nicks[i]} ${data_copy[sorted_members[i]]}\n"
        if message.author not in sorted_members[:10]:
            authorindex = sorted_members.index(message.author)
            ret += f"{authorindex+1}. {data[message.author]['badge']}{sorted_nicks[authorindex]} ${data_copy[message.author]}\n"
        embed = discord.Embed(title='TOP ' + message.guild.name + ' MEMBERS', description=ret, color=0xFFFF00)
        await message.channel.send(embed=embed)

    if message.content.startswith('$flip'):
        amount = int(message.content.split(' ')[1])
        if amount > data[message.author]['bal']:
            embed = discord.Embed(color=0xFFFF00, description='Not enough balance ' + data[message.author]['badge'] +message.author.mention)
            await message.channel.send(embed=embed)
            return
        if amount < 1:
            embed = discord.Embed(color=0xFFFF00, description='Flip must be at least $1 ' + data[message.author]['badge'] + message.author.mention)
            await message.channel.send(embed=embed)
            return
        await message.add_reaction('✅')
        await asyncio.sleep(0.2)
        check = lambda reaction, user, mes=message: client.user != user and reaction.message == mes
        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", check=check, timeout=300)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break
            if user == message.author:
                embed = discord.Embed(color=0xFFFF00, description='Cant coinflip yourself ' + data[message.author]['badge'] +user.mention)
                await message.channel.send(embed=embed)
                await message.remove_reaction(reaction.emoji, user)
                continue
            if data[user]['bal'] < amount:
                embed = discord.Embed(color=0xFFFF00, description='Not enough balance ' + data[user]['badge'] +user.mention)
                await message.channel.send(embed=embed)
                await message.remove_reaction(reaction.emoji, user)
                continue
            await message.clear_reaction('✅')
            ret = ''
            if random.choice([0, 1]) == 1:
                # if its 1 user wins
                data[user]['cfwins'] += 1
                data[user]['bal'] += amount
                data[message.author]['bal'] -= amount
                ret += data[user]['badge'] +user.mention + " won the coinflip! ➕ $" + str(amount) + '!\n'
                ret += data[message.author]['badge'] + message.author.mention + " lost the coinflip. ➖ $" + str(amount) + "\n"
            else:
                # if its 0 messge.author wins
                data[message.author]['cfwins'] += 1
                data[user]['bal'] -= amount
                data[message.author]['bal'] += amount
                ret += data[message.author]['badge']+message.author.mention + " won the coinflip! + $" + str(amount) + '!\n'
                ret += data[user]['badge'] +user.mention + " lost the coinflip. - $" + str(amount) + "\n"

            ret += '─────────────────────────────────────────────\n'
            ret += data[message.author]['badge']+message.author.mention + " balance: $" + str(data[message.author]['bal']) + '\n'
            ret += data[user]['badge'] +user.mention + " balance: $" + str(data[user]['bal'])
            embed = discord.Embed(color=0xFFFF00, description=ret)
            await message.channel.send(embed=embed)

    if message.content.startswith('$pay'):
        target = message.content.split(' ')[1]
        target = await client.fetch_user(target[3:-1])
        if message.author == target:
            embed = discord.Embed(color=0xFFFF00, description="Can't send money to yourself " + data[target]['badge'] + target.mention)
            await message.channel.send(embed=embed)
            return
        amount = int(message.content.split(' ')[2])
        if data[message.author]['bal'] < amount:
            embed = discord.Embed(color=0xFFFF00, description="Not enough money to pay that " + data[message.author]['badge'] + message.author.mention)
            await message.channel.send(embed=embed)
            return
        if amount < 0:
            embed = discord.Embed(color=0xFFFF00, description="Payment must be at least $1" + data[message.author]['badge'] + message.author.mention)
            await message.channel.send(embed=embed)
            return
        data[target]['bal'] += amount
        data[message.author]['bal'] -= amount
        embed = discord.Embed(color=0xFFFF00, description='$' + str(amount) + ' sent to ' + data[target]['badge'] + target.mention)
        await message.channel.send(embed=embed)

    if message.content.startswith('$shop'):
        await asyncio.gather(badge_shop(message), mascot_shop(message))


    if message.content.startswith('$give'):
        if not message.author.guild_permissions.administrator:
            embed = discord.Embed(color=0xFFFF00, description='Only admins can give money')
            await message.channel.send(embed=embed)
            return
        target = message.content.split(' ')[1]
        target = await client.fetch_user(target[3:-1])
        amount = int(message.content.split(' ')[2])
        data[target]['bal'] += amount
        embed = discord.Embed(color=0xFFFF00, description='$' + str(amount) + ' sent to ' + data[target]['badge'] + target.mention)
        await message.channel.send(embed=embed)

    if message.content.startswith('$take'):
        if not message.author.guild_permissions.administrator:
            embed = discord.Embed(color=0xFFFF00, description='Only admins can take money')
            await message.channel.send(embed=embed)
            return
        target = message.content.split(' ')[1]
        target = await client.fetch_user(target[3:-1])
        amount = int(message.content.split(' ')[2])
        data[target]['bal'] -= amount
        embed = discord.Embed(color=0xFFFF00, description='$' + str(amount) + ' taken from ' + data[target]['badge'] + target.mention)
        await message.channel.send(embed=embed)

    if message.content.startswith('$stop'):
        if message.author.id != 392462177606434828:
            return
        quit()

    if message.content.startswith('$event'):
        if not message.author.guild_permissions.administrator:
            embed = discord.Embed(color=0xFFFF00, description='Only admins can start event')
            await message.channel.send(embed=embed)
            return
        embed = discord.Embed(color=0xFFFF00, description="Person to send the most messages in 15 seconds wins!")
        await message.channel.send(embed=embed)
        score = {}
        time = datetime.utcnow()
        await asyncio.sleep(20)
        async for msg in message.channel.history(after=time):
            score[msg.author] = score.get(msg.author, 0) + 1
        v = list(score.values())
        k = list(score.keys())
        winner = k[v.index(max(v))]
        embed = discord.Embed(color=0xFFFF00, description="Winner: " + data[winner]['badge'] + winner.mention + " won $500")
        await message.channel.send(emebd=embed)
        data[winner]['bal'] += 500

    if message.content.startswith('$casino'):
        await crate_shop(message)

    if message.content.startswith('$profile'):
        if message.author.nick is None:
            name = message.author.name
        else:
            name = message.author.nick
        embed = discord.Embed(title=data[message.author]['badge']+name, color=0xFFFF00)
        embed.set_thumbnail(url=message.author.avatar_url)
        stats = "Balance: $"+ str(data[message.author]['bal']) + '\n' + "Coinflips won: "+str(data[message.author]['cfwins'])
        embed.add_field(name="Stats", value=stats, inline=False)
        embed.add_field(name="Income", value="$"+str(data[message.author]['income'])+"/hr", inline=True)
        if len(data[message.author]['badges']) == 0:
            badges_str = 'No badges yet'
        else:
            badges_str = ''.join(data[message.author]['badges'])
        embed.add_field(name="Badges", value=badges_str, inline=True)
        embed.set_footer(text="Click a badge below to equip it")
        if data[message.author]["mascot"] == "none":
            embed.add_field(name="Mascot", value='No mascot owned, buy one in $shop', inline=False)
            profile = await message.channel.send(embed=embed)
        else:
            embed.add_field(name="Mascot", value="Use $mascot to display it in chat!", inline=False)
            file = discord.File(data[message.author]['mascot'])
            embed.set_image(url="attachment://"+data[message.author]['mascot'])
            profile = await message.channel.send(embed=embed, file=file)

        for badge in data[message.author]['badges']:
            await profile.add_reaction(badge)
        check = lambda reaction, user, mes=profile: client.user != user and reaction.message == mes
        while True:
            cont = False
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=300, check=check)
            except asyncio.TimeoutError:
                await profile.delete()
                break
            for reactor in await reaction.users().flatten():
                if reactor != message.author and reactor != client.user:
                    await profile.remove_reaction(reaction.emoji, reactor)
                    embed = discord.Embed(color=0xFFFF00, description='This is not your profile '+ data[reactor]['badge'] + reactor.mention+ ', use $profile to change your own badge.')
                    await message.channel.send(embed=embed)
                    cont = True
            # breaks out of nested loop
            if cont:
                continue
            await profile.remove_reaction(reaction.emoji, user)
            if data[user]['badge'] == reaction.emoji:
                embed = discord.Embed(color=0xFFFF00, description='That badge is already equipped' + data[user]['badge'] + user.mention)
                await message.channel.send(embed=embed)
                continue
            if reaction.emoji not in data[user]['badges']:
                embed = discord.Embed(color=0xFFFF00, description='You do not own that badge, use $shop to buy it ' + data[user]['badge'] + user.mention)
                await message.channel.send(embed=embed)
                continue
            data[user]['badge'] = reaction.emoji
            embed = discord.Embed(color=0xFFFF00, description=reaction.emoji + ' equipped, ' + data[user]['badge'] + user.mention)
            await message.channel.send(embed=embed)

    if message.content.startswith('$mascot'):
        await message.channel.send(file=discord.File(data[message.author]['mascot']))

with open("bottoken.txt", "r") as f:
    bottoken = f.read().strip("\n")

client.run(bottoken)
