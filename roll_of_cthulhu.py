import discord
import random
import os
import re

def cmp(a, b):
    return (a > b) - (a < b) 

def get_inputs(command):
    """
    Args:
    command (string): user's command

    Returns:
    target (int): # target number for skill
    original_target (int): target before difficulty (returned for cosmetic purposes)
    bonus (int): bonus / penalty status: -2, -1, 0, 1, or 2
    development (bool): is this a roll to improve a skill during development phase?
    """
    target = 0
    original_target = 0
    bonus = 0
    devel = False
    
    match = re.findall(r"\/c\s*(\d+)*(bb|b(?:onus)*|pp|p(?:enalty)*|\+\+|\+|\-\-|\-|h(?:ard)*|e(?:xtreme)*|d(?:ev)*(?:elopment)*)?", command)
    if(match[0][0] != ''):
        target = int(match[0][0])
    original_target = target
    mod    = str(match[0][1])

    if(mod == 'b' or mod == 'bonus' or mod == '+'):
        bonus = 1
    elif(mod == 'bb' or mod == '++'):
        bonus = 2
    elif(mod == 'p' or mod == 'penalty' or mod == '-'):
        bonus = -1
    elif(mod == 'pp' or mod == '--'):
        bonus = -2
    elif(mod == 'h' or mod == 'hard'):
        target = target / 2
    elif(mod == 'e' or mod == 'extreme'):
        target = target / 5
    elif(mod == 'd' or mod == 'dev' or mod == 'development'):
        devel = True

    return target, original_target, bonus, devel

def roll(target, orig_target, bonus):
    """
    Args:
    target (int): # target number for skill
    original_target (int): target before difficulty (returned for cosmetic purposes)
    bonus (int): bonus / penalty status: -2, -1, 0, 1, or 2

    Returns:
    message (str): message to send to the user
    """

    if(target == 0):
        msg = "Rolling `1d100`: "
    elif(orig_target == target):
        msg = "Rolling `1d100` against %d: " % target
    else:
        msg = "Rolling `1d100` against ~~%d~~ %d: " % (orig_target, target)

    if(bonus == 0):
        d100 = random.randint(1, 100)
        dtext = str_roll(target, d100)
        msg += '( %s )' % dtext
    else:
        d10 = random.randint(0, 9)
        dtens1 = random.randint(0, 9) * 10
        dtens2 = random.randint(0, 9) * 10
        dtens3 = random.randint(0, 9) * 10
        roll1 = d10 + dtens1
        if(roll1 == 0):
            roll1 = 100
        roll2 = d10 + dtens2
        if(roll2 == 0):
            roll2 = 100
        roll3 = d10 + dtens3
        if(roll3 == 0):
            roll3 = 100
        dtext1 = str_roll(target, roll1)
        dtext2 = str_roll(target, roll2)
        dtext3 = str_roll(target, roll3)
        if(bonus == 1 or bonus == -1):
            if(cmp(roll1, roll2) * bonus <= 0):
                # 1 is smallest if b roll, 1 is largest if p roll
                msg += '( %s, ~~%s~~ )' % (dtext1, dtext2)
                d100 = roll1
            else:
                msg += '( ~~%s~~, %s )' % (dtext1, dtext2)
                d100 = roll2
        else:
            if(cmp(roll1, roll2) * bonus <= 0):
                # 1 is 'more favorable' than 2
                if(cmp(roll1, roll3) * bonus <= 0):
                    msg += '( %s, ~~%s~~, ~~%s~~ )' % (dtext1, dtext2, dtext3)
                    d100 = roll1
                else:
                    msg += '( ~~%s~~, ~~%s~~, %s )' % (dtext1, dtext2, dtext3)
                    d100 = roll3
            else:
                if(cmp(roll2, roll3) * bonus <= 0):
                    msg += '(~~%s~~, %s, ~~%s~~)' % (dtext1, dtext2, dtext3)
                    d100 = roll2
                else:
                    msg += '(~~%s~~, ~~%s~~, %s)' % (dtext1, dtext2, dtext3)
                    d100 = roll3
    if(target == 0):
        return msg
        
    if(d100 == 1):
        msg += "; that's a critical success!"
    elif( (target < 50 and d100 >= 96) or d100 == 100):
        msg += "; that's a fumble!"
    elif(d100 <= target):
        msg += "; you succeed."
    else:
        msg += "; you fail."
        
    return msg

def str_roll(target, roll):
    """
    Creates a string representing a given roll

    Args:
    target (int): the target to beat
    roll (int): the roll to make a string of

    Return:
    text (str): the roll as a string
    """
    if(roll == 1):
        return "**" + str(roll) + "**"
    elif( (target < 50 and roll >= 96) or roll == 100):
        return "*"  + str(roll) + "*"
    else:
        return str(roll)

def roll_3d6():
    """
    Roll 3d6
    """
    dsix1 = random.randint(1, 6)
    dsix2 = random.randint(1, 6)
    dsix3 = random.randint(1, 6)
    return dsix1, dsix2, dsix3

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    command = message.content

    if command.startswith('/c'):
        if command.startswith('/c help'):
            dm = message.author.dm_channel
            if(dm == None):
                await message.author.create_dm()
            dm = message.author.dm_channel
            await dm.send("Hi, I'm Roll Of Cthulhu! I roll dice for you following the Call of Cthulhu rules.")
            await dm.send("For starters, roll a d100 (or d%) with `/c`.")
            await dm.send("To make a skill roll, type `/c X`, where X is your rating in that skill.")
            await dm.send("You can add bonus or penalty by adding b / + for bonus or p / - for penalty (and bb / ++ / pp / -- for double): `/c 45++`")
            await dm.send("Add h to make a hard roll, or e to make an extreme roll: `/c 60e`")
            await dm.send("To roll stats for a new character, type `/c chargen`")
            await dm.send("Finally, during development phase add d after the target to see if a ticked skill improves: `/c 15d`")
            return
        elif command.startswith('/c example'):
            dm = message.author.dm_channel
            if(dm == None):
                await message.author.create_dm()
            dm = message.author.dm_channel
            await dm.send("Let's say you need to shoot someone who is stabbing one of your friends behind a car. You'll take a penalty for shooting through cover, and for shooting into melee. Your shooting skill is a high 70, but you will take 2 penalties. Roll `/c 70pp` or `/c 70--`")
            await dm.send("Let's say you managed to shoot someone, at some point, during an arc. At the end you have a chance to improve it: just roll `/c 70d`; that's it! Easy bot.")
            return
        elif command.startswith('/c chargen'):
            stats3 = ["STR", "CON", "DEX", "APP", "POW"]
            stats2 = ["SIZ", "INT", "EDU"]
            msg = "";
            await message.channel.send(message.author.mention + ': Rolling stats (before aging)')
            for stat in stats3:
                d1, d2, d3 = roll_3d6()
                msg += "`" + stat + " = ( %d + %d + %d ) * 5 = %d `\n" % (d1, d2, d3, (d1+d2+d3)*5)
            for stat in stats2:
                d1, d2, d3 = roll_3d6()
                msg += "`" + stat + " = ( %d + %d + 6 ) * 5 = %d `\n" % (d1, d2, (d1+d2+6)*5)
            await message.channel.send(msg)
            return
       
        target, orig_target, bonus, development = get_inputs(command)

        try:
            if (target < 0):
                await message.channel.send(message.author.mention + ': Those numbers aren\'t quite right')
                return
        except:
            await message.channel.send(message.author.mention + ': There seems to be a problem...')
            return  
   
        if(development):
            d100 = random.randint(1, 100)
            msg = 'Rolling `1d100` to improve %d: ( %d )' % (target, d100)
            if(d100 > target or d100 > 95):
                d10 = random.randint(1, 10)
                msg += '; congratulations! Your skill improves by `1d10` ( %d ) to **%d**!' % (d10, target + d10)
                await message.channel.send(message.author.mention + ': ' + msg)
                if(target + d10 < 90):
                    return
                else:
                    dsix1 = random.randint(1, 6)
                    dsix2 = random.randint(1, 6)
                    msg = "Your skill improved past 90! Gain `2d6` ( %d + %d ) = %d sanity." % (dsix1, dsix2, dsix1 + dsix2)
                    await message.channel.send(message.author.mention + ': ' + msg)
                    return
            else:
                msg += "; unfortunately the skill does not improve."
                await message.channel.send(message.author.mention + ': ' + msg)
                return
        msg = roll(target, orig_target, bonus)
        await message.channel.send(message.author.mention + ': ' + msg)
        return

token = os.environ.get('TOKEN')
# Be sure to run 
# $env:TOKEN = 'your bot token'
# in your environment before testing
client.run(token)
