import discord
import parse
import random
import os

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
    """
    
    inputs = parse.parse("/w {:d}", command)
    if(inputs):
        return inputs[0], 6, False, 0
    
    inputs = parse.parse("/w {:d}!", command)
    if(inputs):
        return inputs[0], 6, True, 0

    inputs = parse.parse("/w {:d}b{:d}", command)
    if(inputs):
        return inputs[0], inputs[1], False, 0

    inputs = parse.parse("/w {:d}!b{:d}", command)
    if(inputs):
        return inputs[0], inputs[1], True, 0

    # Fighting

    inputs = parse.parse("/w {:d}d{:d}b{:d}", command)
    if(inputs):
        return inputs[0], inputs[2], True, inputs[1]

    inputs = parse.parse("/w {:d}d{:d}b{:d}", command)
    if(inputs):
        return inputs[0], inputs[2], False, inputs[1]

    inputs = parse.parse("/w {:d}d{:d}b{:d}", command)
    if(inputs):
        return inputs[0], inputs[2], False, inputs[1]

    inputs = parse.parse("/w {:d}d{:d}b{:d}", command)
    if(inputs):
        return inputs[0], inputs[2], False, inputs[1]

            

    return 0, 0, False, 0

def roll(dice, difficulty, explosive):
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
    noSucc = True
    rolls = []
    successes = 0      
    msg = "Rolling %d dice at diff %d: (" % (dice, difficulty)
    x = 0

    while x < dice:
        d = random.randint(1,10)
        rolls.append(d)
        if(d >= difficulty):
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
            #await message.channel.send('Roll oWoD dice with XbY; X is number of dice, Y is the difficulty. \nOptionally use with "X!bY" to explode tens')
            await message.channel.send('Roll Old World of Darkness style dice.\nFor basic rolls use "XbYtZ" where X is the number of dice Y is the dificulty and Z is the threshold.\nMake dice explode with"X!bYtZ".\nDefault to threshold 0 with "XbY".\nDefault to difficulty 6 with just "X".')
            await message.channel.send('To roll an attack as one command use "XdWbYtZ" where X is the number of dice to hit and W is the number of dice for damage (Y and Z optionally as above).  Difficulty and threshold only apply to the to hit roll.\nYou can also make either damage or to hit dice explode with "X!dWbYtZ" or "XdW!bYtZ" (or both with "X!dW!bYtZ" if you really want to be excessive).')
            return
        elif command.startswith('/w example'):
            await message.channel.send("Let's say Ragnar the Purebreed wants to roll to attack with his claws in Crinos form.\nRagnar has a base of 4 Dexterity, with +1 for Cirnos form, and he has 5 brawling so he has a total of 10 dice to hit.\nRagnar has a base of 4 strength, with a +4 strength for Crinos form and +2 (? correct this) from Werwolf claws, for a total of 11 dice for damage.\nSince Ragnar has specializations in both Ripping and Tearing, both damage and to hit can explode.\nLet's assume that ragnar has been enchanted by the avatar of War, so he has +2 difficulty and +2 threshold for a total of difficulty 8 threshold 2.\n\nThis makes the final command '/w 10!d11!b8t2'")
            return
       
        dice, difficulty, explosive, damage = get_inputs(command)

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

        msg, hits = roll(dice, difficulty, explosive)
        if(damage != 0):
            if(hits > 0):
                msg += "\nThat's a hit! Let's do some damage.\n"
                msg2, _ = roll(damage + hits, difficulty, explosive)
                msg += msg2
            else:
                msg += "\nMission failed, we'll get em next time."
            

        await message.channel.send(msg)

token = os.environ.get('TOKEN')
# Be sure to run 
# $env:TOKEN = 'your bot token'
# in your environment before testing
client.run(token)


    