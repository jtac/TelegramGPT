# TelegramGPT

This is a python code snippet to initialize and run a Telegram bot that acts as ChatGPT and responds to your mentions, replies or direct messages.

Telegram bots are deployed via @BotFather on Telegram, there's extensive help available there.

Remember to login to your portal.azure.com, then go to https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/OpenAI

Here you can find your deployed instances and their names, open one up and find "Endpoint", this is was you need for  

``
openai.api_base = <your azure endpoint URL>
``

You can find your API keys here as well, just use Key 1, Key 2 works as well but is meant as a reserve if you need to invalidate Key 1 and dont want to change environments or code.
