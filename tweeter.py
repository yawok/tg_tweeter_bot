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
import logging
import datetime as dt
import twi_tions as t
import config

#logging 
today = dt.datetime.today()
filename = f"logs/{today.month:02d}-{today.day:02d}-{today.year}.log"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TweeterBot")

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)




reply_id = ""
images = []
URL_COLLECTION, URL_TT, COLLECT_CAP, NO_OF_IMGS, COLLECT_IMG, CONFIRM, TWEET_PHOTO, TWEET, INTERACT = range(9)

def start(update: Update, context: CallbackContext) -> int:
    """Bot introduction and conversation initialisation"""
    logger.info("User started bot.")
    #Storing chat id to send messages wihtout user input later
    global chat_id
    chat_id = update.message.chat_id
    reply_keyboard = [['Tweet'], ['Reply to a tweet']]
    update.message.reply_text("""
    Hello, welcome to Twitter By yaw.o.k. 
    Do you want to post a tweet or reply to a tweet?
    """,
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return URL_COLLECTION


def url_collect(update: Update, context: CallbackContext) -> int:
    """Collecting url to reply to tweet"""
    logger.info(f"'{update.message.text}' selected.")
    update.message.reply_text("Send the link to the tweet you want to reply to.")

    return URL_TT


def url(update: Update, context: CallbackContext) -> int:
    """Saving url"""
    global reply_id
    user_in = update.message.text
    reply_id = user_in.split("/")[-1].split("?")[0]
    tweet_txt = t.get_tweet_txt(reply_id)
    logger.info("tweet id {reply_id} extracted from collected url.")

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
    """Select tweet type."""
    #Storing chat id to send messages wihtout user input later
    global chat_id
    chat_id = update.message.chat_id
    reply_keyboard = [['Caption only'], ['Caption with media']]
    update.message.reply_text("What type of tweet do you want to send?",
            reply_markup=RKM(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="yes or no?"
                )
            )
    
    return COLLECT_CAP



def collect_tweet(update: Update, context: CallbackContext) -> int:
    """Tweet caption collection for tweet without attachments"""
    logger.info("'{update.message.text}' tweet type selected")
    update.message.reply_text("Enter the tweet")

    return TWEET


def tweet(update: Update, context: CallbackContext) -> int:
    """Send tweet."""
    user_in = update.message.text
    
    global sent
    sent = t.send_tweet(user_in, reply_id)
    if type(sent) == int:
        update.message.reply_text("Tweet successfully sent.")
        logger.info("Tweet with caption only sucessfully sent.")
    else: 
        update.message.reply_text("Tweet not sent.")
        logger.error("Tweet not sent(tweet too long maybe)")
    
    #like or retweet
    keyboard = [
            [
                IKB("Like", callback_data="1"),
                IKB("Retweet", callback_data="2")
                ],
            [IKB("Done", callback_data="0")]
            ]

    reply_markup = IKM(keyboard)

    update.message.reply_text(
    """
    Would you like to retweet or like?
    Press Done to continue when done with interaction
    """,
    reply_markup=reply_markup
    )

    return INTERACT


def collect_cap(update: Update, context: CallbackContext) -> int:
    """Collect caption for images"""
    logger.info("{update.message.text} selected.")
    update.message.reply_text("Enter the caption for the tweet.")

    return NO_OF_IMGS

 
def no_of_imgs(update: Update, context: CallbackContext) -> int:
    """Collect number of images or media type."""
    logger.info("Caption collected for Tweet with media.")
    global caption 
    caption = update.message.text

    reply_keyboard = [['1', '2'], ['3', '4'], ['video/gif']]
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
    if update.message.text == "video/gif":
        logger.info(f"1 {update.message.text} selected as media to attach to caption.")
        update.message.reply_text(f"Send a video/gif to attach to tweet.")
    else:
        logger.info("{update.message.text} images(s) selected as media to attach to caption.")
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
        logger.info("Video collected.")
    
    else :
        gif = update.message.animation.get_file().download(f"images/gif.mp4")
        images.append(gif)
        logger.info("Gif collected.")
    
    logger.info("{no_imgs} images collected.")
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text("Do you want to send tweet with attached media?",
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
        logger.info("Tweet with media attachments sent.")
    else: 
        update.message.reply_text("Tweet not sent.")
        logger.error("Tweet with media attachments not sent.")
    
    #like or retweet
    keyboard = [
            [
                IKB("Like", callback_data="1"),
                IKB("Retweet", callback_data="2")
                ],
            [IKB("Done", callback_data="0")]
            ]

    reply_markup = IKM(keyboard)

    update.message.reply_text(
    """
    Would you like to retweet or like?
    Press Done to continue when done with interaction
    """,
    reply_markup=reply_markup
    )

    return INTERACT


def button(update: Update, context: CallbackContext) -> int:
    """Retweets or Likes"""

    query = update.callback_query
    query.answer()
    
    if query.data == "1":
        t.like(sent)
        logger.info("Recent tweet liked.")

        return INTERACT

    elif query.data == "2":
        logger.info("Recent tweet retweeted.")
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
    logger.info("Bot help viewed.")
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
