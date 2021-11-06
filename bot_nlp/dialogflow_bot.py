import os
import logging
import dialogflow

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bot_config.bot_config import (token_bot,
                                   key_dialogflow_bot,
                                   dialogflow_language_code,
                                   dialogflow_project_id,
                                   sesion_id)


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger()

updater = Updater(token_bot, use_context=True)    # Токен API к Telegram
dispatcher = updater.dispatcher
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_dialogflow_bot    # скачнный JSON


DIALOGFLOW_PROJECT_ID = dialogflow_project_id    # PROJECT ID из DialogFlow 
DIALOGFLOW_LANGUAGE_CODE = dialogflow_language_code    # язык
SESSION_ID = sesion_id    # ID бота из телеграма


def startCommand1(update: Update, context: CallbackContext):
    update.message.reply_text('Добрый день!')

    
def textMessage1(update: Update, context: CallbackContext):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID,
                                          SESSION_ID)
    
    text_input = dialogflow.types.TextInput(text=update.message.text,
                                            language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    
    try:
        response = session_client.detect_intent(session=session,
                                                query_input=query_input)
    except InvalidArgument:
         raise

    text = response.query_result.fulfillment_text
    if text:
        update.message.reply_text(response.query_result.fulfillment_text)
    else:
        update.message.reply_text('Что?')
        

# on different commands - answer in Telegram
dispatcher.add_handler(CommandHandler("start", startCommand1))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, textMessage1))

# Start the Bot
updater.start_polling()
updater.idle()
