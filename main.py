import os
import telebot
import openai
import tiktoken
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read the required values from environment variables
try:
    BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    openai.api_type = "azure"
    openai.api_base = os.environ["AZURE_ENDPOINT_URL"]
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.environ["AZURE_OPENAI_API_KEY"]
except KeyError as e:
    logger.error(f"Environment variable {e} not set")
    exit(1)

# Initialize the bot connection
bot = telebot.TeleBot(BOT_TOKEN)

# Get the bot's username
bot_info = bot.get_me()
bot_username = bot_info.username

# tiktoken to count tokens and keep track of usage:
encoding = tiktoken.get_encoding("cl100k_base")
maxtokens = 1000

# Initialize the bot's messages
messages = []
def init_messages():
    global messages
    messages = [{"role": "system",
                 "content": "You are a technically savvy, witty and creative AI named Aino. When users ask you a "
                            "question, work the answer out in a step by step way to be sure you have the right "
                            "answer."}]
init_messages()

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    init_messages()
    bot.reply_to(message, "Bot messages have been reset.")
def limit_token_count():
    global messages, maxtokens, encoding
    message_strings = [message["content"] for message in messages]
    text = " ".join(message_strings)
    tokens_integer = encoding.encode(text)
    while len(tokens_integer) > maxtokens:
        messages.pop(1)
        message_strings = [message["content"] for message in messages]
        text = " ".join(message_strings)
        tokens_integer = encoding.encode(text)

def append_message(message):
    global messages
    messages.append(message)
    limit_token_count()


@bot.message_handler(content_types=['text'])
def handle_message(message):
    should_respond = (
        message.chat.type == 'private'
        or f"@{bot_username}" in message.text
        or (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.username == bot_username
        )
    )

    if should_respond:
        response = get_ai_response(message.text)
        bot.reply_to(message, response)
        append_message({"role": "assistant", "content": response})


def get_ai_response(prompt):
    append_message({"role": "user", "content": prompt})
    logger.info(f"Query: {prompt}")
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        logger.info(f"Bot: {response['choices'][0]['message']['content']}")
        return response['choices'][0]['message']['content']
    except openai.Error as e:
        logger.error(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process your request at the moment. Please try again later."

# Start the bot's polling loop
if __name__ == "__main__":
    logger.info("Starting bot...")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")
