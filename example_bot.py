import discord
import parse
import random
import os
import re

def get_inputs(command):
    """
    Args:
    command (string): user's command

    Returns:
    dice (int): # dice to roll
    difficulty (int): diff of roll
    explosive (bool): should 10s explode?
    damage (int) # damage dice to roll [non-zero for attacks only]
    explosive_damage (bool): is the damage explosive? [only for attacks]
    threshold (int): threshold of successes needed
    """
    dice = 0
    diff = 6
    expl = False
    dam = 0
    edam = False
    thre = 0

    # Fighting
    inputs = parse.parse("/w {}d{}", command)
    if(inputs):
        match = re.findall(r"\/w (\d+)(!)*d(\d+)(!)*b*(\d+)*t*(\d+)*", command)
        if(match):
            dice = int(match[0][0])
            expl = (match[0][1] == '!')
            dam  = int(match[0][2])
            edam = (match[0][3] == '!')
            if(match[0][4] != ''):
                diff = int(match[0][4])
            if(match[0][5] != ''):
                thre = int(match[0][5])
        return dice, diff, expl, dam, edam, thre

    inputs = parse.parse("/w {}b{}", command)
    if(inputs):
        match = re.findall(r"\/w (\d+)(!)*b(\d+)t*(\d+)*", command)
        if(match):
            dice = int(match[0][0])
            expl = (match[0][1] == '!')
            diff = int(match[0][2])
            if(match[0][3] != ''):
                thre = int(match[0][3])
        return dice, diff, expl, dam, edam, thre  

    inputs = parse.parse("/w {}", command)
    if(inputs):
        match = re.findall(r"\/w (\d+)(!)", command)
        if(match):
            dice = int(match[0][0])
            expl = (match[0][1] == '!')
        return dice, diff, expl, dam, edam, thre

    return dice, diff, expl, dam, edam, thre 

def roll(dice, difficulty, explosive, threshold):
    """
    Args:
    dice (int): # dice to roll
    difficulty (int): diff of roll
    explosive (bool): should 10s explode?

    Returns:
    message (str): message to send to the user
    hits (int): number of successes 
    """

    exploded = False
    noSucc = True # keeping this name for humorous reasons
    rolls = []
    successes = 0      
    if(threshold > 0):
        msg = "Rolling %d dice at difficulty %d, threshold %d: (" % (dice, difficulty, threshold)
    else:
        msg = "Rolling %d dice at difficulty %d: (" % (dice, difficulty)
    x = 0

    while x < dice:
        d = random.randint(1,10)
        rolls.append(d)
        if(d >= difficulty):
            if(threshold > 0):
                threshold -= 1
            else:
                successes += 1
                noSucc = False
            if(exploded):
                msg += " ***%d***" % d
            else:
                msg += " **%d**" % d        
        elif(d == 1):
            successes -= 1
            if(exploded):
                msg += " ~~*%d*~~" % d
            else:
                msg += " ~~%d~~" % d
        else:
            if(exploded):
                msg += " *%d*" % d
            else:
                msg += " %d" % d

        exploded = False
        if(d == 10 and explosive):
            dice += 1
            exploded = True
        x += 1


    msg += ") = %d successes" % successes
    if(noSucc and successes < 0):
        msg += "; that's a botch!" 

    return msg, successes

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    command = message.content

    if command.startswith('/w'):
        if command.startswith('/w help'):
            await message.channel.send('Roll Old World of Darkness style dice.\nFor basic rolls use "XbYtZ" where X is the number of dice Y is the dificulty and Z is the threshold.\nMake dice explode with"X!bYtZ".\nDefault to threshold 0 with "XbY".\nDefault to difficulty 6 with just "X".')
            await message.channel.send('To roll an attack as one command use "XdWbYtZ" where X is the number of dice to hit and W is the number of dice for damage (Y and Z optionally as above).  Difficulty and threshold only apply to the to hit roll.\nYou can also make either damage or to hit dice explode with "X!dWbYtZ" or "XdW!bYtZ" (or both with "X!dW!bYtZ" if you really want to be excessive).')
            return
        elif command.startswith('/w example'):
            await message.channel.send("Let's say Ragnar the Purebreed wants to roll to attack with his claws in Crinos form.\nRagnar has a base of 4 Dexterity, with +1 for Cirnos form, and he has 5 brawling so he has a total of 10 dice to hit.\nRagnar has a base of 5 strength, with a +4 strength for Crinos form and +2 (? correct this) from Werwolf claws, for a total of 11 dice for damage.\nSince Ragnar has specializations in both Ripping and Tearing, both damage and to hit can explode.\nLet's assume that ragnar has been enchanted by the avatar of War, so he has +2 difficulty and +2 threshold for a total of difficulty 8 threshold 2.\n\nThis makes the final command '/w 10!d11!b8t2'")
            return
       
        dice, difficulty, explosive, damage, explosive_damage, threshold = get_inputs(command)

        try:
            if (dice <= 0 or difficulty <= 1):
                await message.channel.send('Those numbers aren\'t quite right')
                return
            elif(dice >= 100):
                await message.channel.send('More than 100 dice! That\'s too much, man!')
                return
        except:
            await message.channel.send('There seems to be a problem...')
            return  

        msg, hits = roll(dice, difficulty, explosive, threshold)
        if(damage != 0):
            if(hits > 0):
                msg += "\nThat's a hit! Let's do some damage.\n"
                msg2, _ = roll(damage + hits - 1, 6, explosive_damage, 0)
                msg += msg2
            else:
                msg += "\nMission failed, we'll get em next time."
            

        await message.channel.send(msg)

token = os.environ.get('TOKEN')
# Be sure to run 
# $env:TOKEN = 'your bot token'
# in your environment before testing
client.run(token)