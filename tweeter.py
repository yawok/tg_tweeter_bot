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


images = []
COLLECT_CAP, NO_OF_IMGS, COLLECT_IMG, CONFIRM, TWEET_PHOTO, TWEET, INTERACT = range(7)
def start(update: Update, context: CallbackContext) -> int:
    """Bot introduction and conversation initialisation"""
    #Storing chat id to send messages wihtout user input later
    global chat_id
    chat_id = update.message.chat_id
    reply_keyboard = [['Caption only', 'Caption with images']]
    update.message.reply_text("Hello, welcome to Twitter By yaw.o.k."
            "Do you want to tweet?", reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return COLLECT_CAP


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


def collect_cap(update: Update, context: CallbackContext) -> int:
    """Collect caption for images"""
    update.message.reply_text("Enter the caption for the tweet.")

    return NO_OF_IMGS

 
def no_of_imgs(update: Update, context: CallbackContext) -> int:
    """Collect images."""
    global caption 
    caption = update.message.text

    reply_keyboard = [['1', '2'], ['3', '4']]
    update.message.reply_text("How many images do you want to attach to the tweet?",
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="1"
                )
            )
    
    return COLLECT_IMG


def collect_img(update: Update, context: CallbackContext) -> int:
    """Collect images."""
    global no_imgs 
    no_imgs = int(update.message.text)

    update.message.reply_text(f"Send {no_imgs} image(s) to attach to tweet.")
    
    return CONFIRM


def confirm(update: Update, context: CallbackContext) -> int:
    """Ask for confirmation to tweet."""
    global images
    photo = update.message.photo[-1]
    if update.message.photo:
        img = photo.get_file().download(f"images/img{len(images)}.jpg")
        images.append(img)
        print(len(images))
        
        if no_imgs - len(images) != 0:
            return CONFIRM

    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text("Do you want to send tweet with images",
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return TWEET_PHOTO

def tweet_img(update: Update, context: CallbackContext) -> int:
    """Send tweet."""
    user_in = update.message.text
    
    global sent
    sent = t.send_tweet(caption, imgs=images)
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
        
    return COLLECT_CAP


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
                COLLECT_CAP: [
                    MessageHandler(Filters.regex('^(Caption only)$'), collect_tweet), 
                    MessageHandler(Filters.regex('^(Caption with images)$'), collect_cap)
                    ],
                NO_OF_IMGS: [MessageHandler(Filters.text, no_of_imgs)],
                COLLECT_IMG: [MessageHandler(Filters.text, collect_img)],
                CONFIRM: [MessageHandler(Filters.photo, confirm)],
                TWEET_PHOTO:[
                    MessageHandler(Filters.regex('^(Yes)$'), tweet_img),
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
