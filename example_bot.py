import discord
from parse import *
import random
import os

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
            await message.channel.send('Roll oWoD dice with XbY; X is number of dice, Y is the difficulty. Optionally end with "!" to explode tens')
       
        inputs = parse("/w {:d}b{:d}{}", command + "*")

        try:
            if (inputs[0] <= 0 or inputs[1] <= 1):
                await message.channel.send('Those numbers aren\'t quit right')
                return
            elif(inputs[0] >= 100):
                await message.channel.send('More than 100 dice! That\'s too much, man!')
                return
        except:
            await message.channel.send('There seems to be a problem...')
            return  

        explosive = (command.find('!') != -1)
        exploded = False

        noSucc = True
        rolls = []
        successes = 0      
        dice = inputs[0]
        difficulty = inputs[1]
        msg = "%d dice at diff %d: (" % (dice, difficulty)

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

        await message.channel.send(msg)

token = os.environ.get('TOKEN')
# Be sure to run 
# $env:TOKEN = 'your bot token'
# in your environment before testing
client.run(token)