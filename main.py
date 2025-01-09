import os
from dotenv import load_dotenv
import telebot
import logging
import csv
from datetime import datetime, timedelta
import tempfile

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Read the required values from environment variables
try:
    BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    EILLAT_CHAT_ID = os.environ["EILLAT_CHAT_ID"]
except KeyError as e:
    logger.error(f"Environment variable {e} not set")
    exit(1)

# Initialize the bot connection
logger.info("Initializing bot...")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logger.info("Received start/help command")
    bot.reply_to(message, "Hi! I'm working!")

@bot.message_handler(commands=['chatinfo'])
def handle_chatinfo_command(message):
    chat_info = f"Chat Information:\nChat ID: {message.chat.id}\nChat Type: {message.chat.type}"
    if message.chat.title:
        chat_info += f"\nChat Title: {message.chat.title}"
    if message.chat.username:
        chat_info += f"\nChat Username: @{message.chat.username}"
    if message.chat.description:
        chat_info += f"\nDescription: {message.chat.description}"
    logger.info(f"Chat info requested in {message.chat.type} chat {message.chat.id}")
    bot.reply_to(message, chat_info)

def process_email_file(file_path):
    """Process a file containing email addresses and generate invite links."""
    results = []
    try:
        with open(file_path, 'r') as f:
            emails = [line.strip() for line in f if line.strip()]
        
        # Generate invite links for each email
        for email in emails:
            try:
                # Create expiring invite link (1 month, 1 use)
                expire_date = int((datetime.now() + timedelta(days=30)).timestamp())
                invite_link = bot.create_chat_invite_link(
                    EILLAT_CHAT_ID,
                    name=f"Invite for {email}",
                    creates_join_request=False,
                    expire_date=expire_date,
                    member_limit=1
                )
                results.append({
                    'email': email,
                    'invite_link': invite_link.invite_link,
                    'expires': datetime.fromtimestamp(expire_date).strftime('%Y-%m-%d %H:%M:%S')
                })
                logger.info(f"Generated invite link for {email}")
            except Exception as e:
                logger.error(f"Error generating invite for {email}: {e}")
                results.append({
                    'email': email,
                    'invite_link': 'ERROR',
                    'expires': 'N/A'
                })
        
        # Create output file
        output_file = tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            prefix='invites_',
            suffix='.csv'
        )
        
        with open(output_file.name, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['email', 'invite_link', 'expires'])
            writer.writeheader()
            writer.writerows(results)
        
        return output_file.name
    except Exception as e:
        logger.error(f"Error processing email file: {e}")
        raise

@bot.message_handler(content_types=['document'])
def handle_document(message):
    logger.debug(f"Received document message: {message}")
    # Check if this is a file with the /invite command in caption
    if message.caption and '/invite' in message.caption:
        handle_invite_request(message)

@bot.message_handler(commands=['invite'])
def handle_invite_command(message):
    logger.debug(f"Received invite command: {message}")
    handle_invite_request(message)

def handle_invite_request(message):
    """Handle invite request from either command or document."""
    logger.debug("Processing invite request")
    try:
        # Get document from the message
        document = getattr(message, 'document', None)
        if not document:
            # No file attached, create a single invite link that never expires
            logger.debug("No document attached, creating single invite link")
            invite_link = bot.create_chat_invite_link(
                EILLAT_CHAT_ID,
                name="Bot Generated Invite",
                creates_join_request=False,
                expire_date=None
            )
            bot.reply_to(message, f"Here's your invite link to join the group:\n{invite_link.invite_link}")
            return

        # Process attached file
        logger.debug(f"Processing document with file_id: {document.file_id}")
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(downloaded_file)
            input_file_path = temp_file.name

        # Process the file and generate invites
        output_file_path = process_email_file(input_file_path)
        
        # Send the results file back
        with open(output_file_path, 'rb') as f:
            bot.send_document(
                message.chat.id,
                f,
                caption="Here are your invite links. Each link expires in 30 days and can be used once.",
                reply_to_message_id=message.message_id
            )
        
        # Cleanup temporary files
        os.unlink(input_file_path)
        os.unlink(output_file_path)
        
    except Exception as e:
        logger.error(f"Error handling invite command: {e}")
        bot.reply_to(message, "Sorry, I couldn't process your request. Please make sure you've attached a file with email addresses (one per line).")

@bot.message_handler(content_types=['text'])
def handle_message(message):
    # Log incoming messages
    logger.info(
        f"Message received in {message.chat.type} chat {message.chat.id} "
        f"from user {message.from_user.id} (@{message.from_user.username}): {message.text[:100]}"
    )

    # Only process messages that mention the bot or are in private chat
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
        logger.info(f"Bot mentioned in {message.chat.type} chat {message.chat.id}")

# Handler for when bot is added to a group
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_chat_members(message):
    for member in message.new_chat_members:
        if member.username == bot_username:
            logger.info(f"Bot added to new chat: {message.chat.id} ({message.chat.type})")
            chat_info = (
                f"Bot added to new chat!\n"
                f"Use /chatinfo to see details about this chat\n"
                f"Use /invite to get an invite link"
            )
            bot.send_message(message.chat.id, chat_info)

if __name__ == "__main__":
    logger.info("Starting bot...")
    try:
        logger.info("Starting polling...")
        bot.polling(none_stop=True, interval=2, timeout=20)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        bot.stop_polling()
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info("Bot stopped")
