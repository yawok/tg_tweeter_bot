from telegram.ext import (CallbackContext, Updater, MessageHandler, CommandHandler, ConversationHandler, Filters)
from telegram import Update, ReplyKeyboardMarkup as rkm, ReplyKeyboardRemove as rkr

COLLECT, TWEET = range(2)
def start(update: Update, context: CallbackContext) -> int:
    """Bot introduction and conversation initialisation"""
    reply_markup = [['Yes', 'No']]
    update.message.reply_text = ("Hello, welcome to Twitter By yaw.o.k."
            "Do you want to tweet?", rkm(reply_markup, one_time_keyboard=True, input_field_placeholder="yes or no?"))
    return COLLECT


def collect_tweet(update: Update, context: CallbackContext) -> int:
    """Initialise conversation"""
    update.message.reply_text("Enter the tweet")

    return TWEET


def tweet(update: Update, context: CallbackContext) -> int:
    """Send tweet."""
    user_in = update.message.text

    reply_markup = [['Yes', 'No']]
    update.message.reply_text = ("Do you want to tweet?",
            rkm(reply_markup, one_time_keyboard=True, input_field_placeholder="yes or no?"))
    return COLLECT


def help(update: Update, context: CallbackContext) -> None:
    """Bot guide"""



with open('token.txt', 'r') as f:
    TOKEN = f.read()


def main() -> None:
    """Run the bot"""
    updater = Updater(TOKEN)
    disp = updater.dispatcher
    
    conv = ConversationHandler(entry_point = [CommandHandler("start", start)],
            states ={
                COLLECT: [MessageHandler(Filters.regex('^(Yes)$'), collect_tweet), MessageHandler(Filters.regex('^(No)$'), start)],
                TWEET: [MessageHandler(Filters.text, tweet)]
                }


    disp.add_handler()
    updater.start_polling()
    updater.idle()



