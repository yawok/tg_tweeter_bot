from telegram.ext import (CallbackContext, Updater, MessageHandler, CommandHandler, ConversationHandler, Filters)
from telegram import Update, ReplyKeyboardMarkup as rkm, ReplyKeyboardRemove as rkr
import twi_tions as t
import config


COLLECT, TWEET = range(2)
def start(update: Update, context: CallbackContext) -> int:
    """Bot introduction and conversation initialisation"""
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text("Hello, welcome to Twitter By yaw.o.k."
            "Do you want to tweet?", reply_markup=rkm(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return COLLECT


def collect_tweet(update: Update, context: CallbackContext) -> int:
    """Initialise conversation"""
    update.message.reply_text("Enter the tweet")

    return TWEET


def tweet(update: Update, context: CallbackContext) -> int:
    """Send tweet."""
    user_in = update.message.text
    
    if t.send_tweet(user_in):
        update.message.reply_text("Tweet successfully sent.")

    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text("Do you want to tweet?",
            reply_markup=rkm(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return COLLECT


def help(update: Update, context: CallbackContext) -> None:
    """Bot guide"""
    update.message.reply_text("""
            Welcome to Twitter for yaw.o.k.
            Just follow the bot's requests to send tweet.
            """)


def main() -> None:
    """Run the bot"""
    updater = Updater(config.TOKEN)
    disp = updater.dispatcher
    
    conv = ConversationHandler(entry_points = [CommandHandler("start", start)],
            states ={
                COLLECT: [
                    MessageHandler(Filters.regex('^(Yes)$'), collect_tweet), 
                    MessageHandler(Filters.regex('^(No)$'), start)
                    ],
                TWEET: [MessageHandler(Filters.text, tweet)]
                },
            fallbacks = [CommandHandler("help", help)]
            )

    disp.add_handler(conv)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
