from telegram.ext import (
        CallbackContext,
        Updater,
        MessageHandler, 
        CommandHandler, 
        ConversationHandler, 
        Filters,
        CallbackQueryHandler
        )
from telegram import (
        Update, 
        ReplyKeyboardMarkup as RKM,
        ReplyKeyboardRemove as RKR,
        InlineKeyboardButton as IKB,
        InlineKeyboardMarkup as IKM
        )
import twi_tions as t
import config


COLLECT, TWEET, INTERACT = range(3)
def start(update: Update, context: CallbackContext) -> int:
    """Bot introduction and conversation initialisation"""
    #Storing chat id to send messages wihtout user input later
    global chat_id
    chat_id = update.message.chat_id
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text("Hello, welcome to Twitter By yaw.o.k."
            "Do you want to tweet?", reply_markup=RKM(
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
    
    global sent
    sent = t.send_tweet(user_in)
    if sent:
        update.message.reply_text("Tweet successfully sent.")
    else: 
        update.message.reply_text("Tweet not sent.")
    
    #like or retweet
    keyboard = [
            [
                IKB("Like", callback_data="1"),
                IKB("Retweet", callback_data="2")
                ],
            [IKB("Done", callback_data="0")]
            ]

    reply_markup = IKM(keyboard)

    update.message.reply_text("Would you like to retweet or like?", reply_markup=reply_markup)

    return INTERACT


def button(update: Update, context: CallbackContext) -> int:
    """Retweets or Likes"""

    query = update.callback_query
    query.answer()
    
    if query.data == "1":
        t.like(sent)

        return INTERACT

    elif query.data == "2":
        t.retweet(sent)

        return INTERACT

    elif query.data == "0":
        reply_keyboard = [['Yes', 'No']]
        
        query.edit_message_text(text="Successfully interacted with most recent tweet")

        context.bot.send_message(
            chat_id=chat_id, text="Do you want to tweet?",
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True,
                input_field_placeholder="yes or no?"
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
                TWEET: [MessageHandler(Filters.text, tweet)],
                INTERACT: [CallbackQueryHandler(button)]
                },
            fallbacks = [CommandHandler("help", help)]
            )

    disp.add_handler(conv)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
