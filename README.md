# TelegramGPT

This is a python code snippet to initialize and run a Telegram bot that acts as ChatGPT and responds to your mentions, replies or direct messages.

Telegram bots are deployed via @BotFather on Telegram, there's extensive help available there.

Login to your portal.azure.com, then go to 

https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI

Here you can find your deployed instances and their names, open one up and find "Endpoint"

You can find your API keys here as well, just use Key 1, Key 2 works as well but is meant as a reserve if you need to invalidate Key 1 and dont want to change environments or code.

For security, I recommend setting your environment variables with the relevant information, but you can add .env file handling if you want. just add the following snippet at the start of the code (last import line + first code lines)

    from dotenv import load_dotenv
    load_dotenv()

If you do ^this, _please_ remember NOT to include your .env file _ever_ if you distribute your code anywhere, it's possible to rack up thousands of dollars of costs very quickly if you lose control of your OpenAI API keys.

Remember to install required modules, you can do this by running:

    pip install -r requirements.txt

Finally, start the bot most simply by running:

    python main.py

Alternatively you can start the script in a docker to keep it running easily.
