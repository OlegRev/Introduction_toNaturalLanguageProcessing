# -- coding: utf-8 -
import string
import nltk
import annoy
import pickle
import numpy as np
import tensorflow as tf
import logging
# import dialogflow
# import tqdm

# from tqdm import tqdm_notebook
from pymorphy2 import MorphAnalyzer
from stop_words import get_stop_words
from transformers import TFAutoModel, AutoTokenizer
from bot_config.bot_config import token_bot
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)


morpher = MorphAnalyzer()
sw = set(get_stop_words("ru") + nltk.corpus.stopwords.words("russian"))
exclude = set(string.punctuation)

bert = TFAutoModel.from_pretrained("./data/bert/")
tokenizer = AutoTokenizer.from_pretrained("./data/tokenizer/")

bert_index = annoy.AnnoyIndex(768, "angular")
bert_index.load("./data/bert/bert_index")
with open("./data/pickle_files/index_map.pkl", "rb") as read_file:
    index_map = pickle.load(read_file)

    
updater = Updater(token_bot, use_context=True)
dispatcher = updater.dispatcher


def startCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Добрый день!')

    
def preprocess_txt(line):
    spls = "".join(i for i in line.strip() if i not in exclude).split()
    spls = [morpher.parse(i.lower())[0].normal_form for i in spls]
    spls = [i for i in spls if i not in sw and i != ""]
    return " ".join(spls)

def get_answer(
    question,
    index,
    index_map,
    probability_of_choice=[
        0.2,
        0.175,
        0.15,
        0.125,
        0.1,
        0.075,
        0.05,
        0.05,
        0.05,
        0.025,
    ],
    size=3,
):
    question = preprocess_txt(question)
    tok = tokenizer(question, return_token_type_ids=False, return_tensors="tf")
    vector = bert(**tok)[1].numpy()[0]
    answers = index.get_nns_by_vector(vector, 10)
    # return [index_map[i] for i in answers]
    result = np.random.choice(
        [index_map[i] for i in answers],
        size=size,
        replace=False,
        p=probability_of_choice,
    ).tolist()
    
    return result


def textMessage(update: Update, context: CallbackContext):
    message = update.message
    question = message.text 
    # print(question)
    result = get_answer(question, bert_index, index_map, size=1)
    # print(result)
    for item in result:
        update.message.reply_text(item)
    # bot.send_message(chat_id=update.message.chat_id, text="question: {} answer: {}".format(question, answer))
    return 


# on different commands - answer in Telegram
dispatcher.add_handler(CommandHandler("start", startCommand))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, textMessage))

# Start the Bot
updater.start_polling()
updater.idle()