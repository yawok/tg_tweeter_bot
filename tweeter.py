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

reply_id = ""
images = []
URL_COLLECTION, URL_TT, COLLECT_CAP, NO_OF_IMGS, COLLECT_IMG, CONFIRM, TWEET_PHOTO, TWEET, INTERACT = range(9)

def start(update: Update, context: CallbackContext) -> int:
    """Bot introduction and conversation initialisation"""
    #Storing chat id to send messages wihtout user input later
    global chat_id
    chat_id = update.message.chat_id
    reply_keyboard = [['Tweet'], ['Reply to a tweet']]
    update.message.reply_text(" Do you want to post a tweet or reply to a tweet?",
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return URL_COLLECTION


def url_collect(update: Update, context: CallbackContext) -> int:
    """Collecting url to reply to tweet"""
    update.message.reply_text("Send the link to the tweet you want to reply to.")

    return URL_TT


def url(update: Update, context: CallbackContext) -> int:
    """Collecting url to reply to tweet"""
    global reply_id
    user_in = update.message.text
    reply_id = user_in.split("/")[-1].split("?")[0]
    tweet_txt = t.get_tweet_txt(reply_id)
    print(tweet_txt)

    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text(f"""
            Do you want to reply to the following tweet: 
            
            {tweet_txt}
            """,
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )

    return URL_COLLECTION


def tweet_type(update: Update, context: CallbackContext) -> int:
    """Bot introduction and conversation initialisation"""
    #Storing chat id to send messages wihtout user input later
    global chat_id
    chat_id = update.message.chat_id
    reply_keyboard = [['Caption only'], ['Caption with media']]
    update.message.reply_text("Hello, welcome to Twitter By yaw.o.k."
            " What type of tweet do you want to send?", reply_markup=RKM(
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
    print(reply_id)
    sent = t.send_tweet(user_in, reply_id)
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

    reply_keyboard = [['1', '2'], ['3', '4'], ['video']]
    update.message.reply_text("How many images do you want to attach to the tweet?")
    update.message.reply_text("""
    How many images do you want to attach to the tweet?

    Choose video if you want to attach a video instead.
            """,
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="1"
                )
            )
    
    return COLLECT_IMG


def collect_img(update: Update, context: CallbackContext) -> int:
    """Collect images."""
    global no_imgs, images
    images.clear()
    if update.message.text == "video":
        update.message.reply_text(f"Send video to attach to tweet.")
    else:
        no_imgs = int(update.message.text)
        update.message.reply_text(f"Send {no_imgs} image(s) to attach to tweet.")
    
    return CONFIRM


def confirm(update: Update, context: CallbackContext) -> int:
    """Ask for confirmation to tweet."""
    global images
    if update.message.photo:
        photo = update.message.photo[-1]
        img = photo.get_file().download(f"images/img{len(images)}.jpg")
        images.append(img)
        print(len(images))
        
        if no_imgs - len(images) != 0:
            return CONFIRM
    elif update.message.video:
        vid = update.message.video.get_file().download(f"images/vid.mp4")
        images.append(vid)
    else :
        gif = update.message.animation.get_file().download(f"images/gif.mp4")
        images.append(gif)


    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text("Do you want to send tweet with media",
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return TWEET_PHOTO

def tweet_img(update: Update, context: CallbackContext) -> int:
    """Send tweet."""
    user_in = update.message.text
    
    global sent
    sent = t.send_tweet(caption, reply_id, imgs=images)
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
        reply_keyboard = [['Tweet'], ['Reply to a tweet']]

        
        query.edit_message_text(text="Successfully interacted with most recent tweet")

        context.bot.send_message(
            chat_id=chat_id, text=" Do you want to post a tweet or reply to a tweet?",
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True,
                input_field_placeholder="yes or no?"
                )
            )
        
    return URL_COLLECTION


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
                URL_COLLECTION: [
                    MessageHandler(Filters.regex('^(Yes)$') | Filters.regex('^(Tweet)$'), tweet_type),
                    MessageHandler(Filters.regex('^(No)$'), start), 
                    MessageHandler(Filters.regex('^(Reply to a tweet)$'), url_collect)
                    ], 
                URL_TT: [MessageHandler(Filters.text, url)],
                COLLECT_CAP: [
                    MessageHandler(Filters.regex('^(Caption only)$'), collect_tweet), 
                    MessageHandler(Filters.regex('^(Caption with media)$'), collect_cap)
                    ],
                NO_OF_IMGS: [MessageHandler(Filters.text, no_of_imgs)],
                COLLECT_IMG: [MessageHandler(Filters.text, collect_img)],
                CONFIRM: [MessageHandler(Filters.photo | Filters.video | Filters.document.gif, confirm)],
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
