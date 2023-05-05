import telebot
import openai

# add your telegram bot token here
BOT_TOKEN = <telegram bot token here>
# initialize the bot connection
bot = telebot.TeleBot(BOT_TOKEN)

# Get the bot's username
bot_info = bot.get_me()
bot_username = bot_info.username


# Set up the Azure OpenAI API
openai.api_type = "azure"
openai.api_base = <your azure endpoint URL>
openai.api_version = "2023-03-15-preview" # replace if changed
openai.api_key = <your azure OpenAI API key>


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    response = None
    # Check if the message is a direct message, if the bot's username is in the message text,
    # or if the message is a reply to the bot
    if (message.chat.type == 'private') or f"@{bot_username}" in message.text or (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.username == bot_username
    ):
        print(f'responding to: {message.text}')
        try:
            response = openai.ChatCompletion.create(
                engine="gpt4-32k",
                messages=[{"role": "system",
                           "content": "You are a witty and creative AI assistant named Aino. You do your utmost to help"
                           " everyone find answers to their questions and help them with their creative dilemmas."},
                          {"role": "user", "content": message.text}],
                temperature=0.95,
                max_tokens=1024,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
        except ValueError as e:
            print(f"Error while fetching response from OpenAI API: {e}")
            bot.reply_to(message, "Error: " + str(e))
            return
        except TypeError as e:
            print(f"Error while fetching response from OpenAI API: {e}")
            bot.reply_to(message, "Error: " + str(e))
            return
        except AttributeError as e:
            print(f"Error while fetching response from OpenAI API: {e}")
            bot.reply_to(message, "Error: " + str(e))
            return
        except openai.error.APIError as e:
            if "content_filter" in str(e):
                bot.reply_to(message,
                             "The input text has triggered the content filter. Please modify your message and try "
                             "again.")
                return
            else:
                bot.reply_to(message, f"Error while fetching response from OpenAI API: {e}")
                return
        except Exception as e:
            bot.reply_to(message, f"An unexpected error occurred: {e}")
            return

        if response:
            # print(response)
            airesponse = response['choices'][0]['message']['content'].strip()
            print(f"AI: {airesponse}")
            bot.reply_to(message, airesponse)
        else:
            print("No response received from the API.")
            bot.reply_to(message, "No response received from the API.")
            return
    else:
        print(f"ignoring: {message.text}")


bot.infinity_polling()