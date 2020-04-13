# Testing this code

If you want to test this code on your own you'll need to make a bot. 

1. Start by going here: https://discordapp.com/developers/applications/
2. Create a `New Application`
3. Make a bot and take note of its token. It'll look like a random string of base64
4. Clone the repo and download the packages in requests.txt
5. Create an environment variable named 'TOKEN' and set it to the token above. Be sure never to push a commit that contains this or anyone in the world can hijack your bot!
6. Add the bot to a server, give it the right permissions (for these you at least need it to read messages and @ anyone), and run the code.
