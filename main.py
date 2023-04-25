import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import os
from dotenv.main import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater,run_async
from telegram import ParseMode 
import re
from subprocess import PIPE
import urllib.parse
from yt_dlp import YoutubeDL

load_dotenv()

Token = os.environ['TOKEN']

BOT_Username = os.environ['BOT_USERNAME']

#Commands


@run_async
def start_command(update: Update,context):
    update.message.reply_text('Hello! I`m Nai, i can display links and download from youtube. Enter name of Service that you want! or enter help to know what are the available services.'
                                    '\n'
                                    '\n'
                                    'This is a list of all the command that You need to know, you can enter it with or without ( / ): \n'
                                    '1. start \n'
                                    '2. links\n'
                                    '3. download ex. download https://youtu.be/.......\n'
                                    '4. help\n')
@run_async
def Links(update: Update,context):

     update.message.reply_text("""Links list : \n
	<a href='https://github.com/NaifAskul/Nai_TeleBot'>My Github</a>
	\n """,ParseMode.HTML)

@run_async
def youtube_url_validation(url,update : Update):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url,re.IGNORECASE)

    # Use the regex pattern to check if the link is a valid YouTube video link
    if youtube_regex_match is not None:

        return True

    else:
        update.message.reply_text("Not a valid YouTube video link. Enter download to know more.")

        return False

@run_async
def Youtube_download(update: Update,context):

    update.message.reply_text('download ex. download https://youtu.be/.......')

@run_async
def help(update: Update,context):
     update.message.reply_text(' This is a list of all the command that You need to know, you can enter it with or without ( / ): \n'
                                    '1. start \n'
                                    '2. links\n'
                                    '3. download ex. download https://youtu.be/.......\n'
                                    '4. help\n')
# Responses
@run_async
def handle_Response (text : str,update: Update , context) -> str:


    if len(text) > 8 and text[0:8].lower() == 'download' and youtube_url_validation(text[8:].strip(),update) is not None :

        url = text[8:].strip()
        try:
            with YoutubeDL() as ydl:
                info_dict = ydl.extract_info(url, download=False)
                Title = info_dict.get('title',None)


            command = ['yt-dlp','-f ""best[height<=720]""','-g',url]
            update.message.reply_text('Downloading....')
            result =  subprocess.run(command,stdout=PIPE,universal_newlines=True)
            title = urllib.parse.quote_plus(Title)
            linktoSend : str = result.stdout + "&title="+title

            keyboard = [[InlineKeyboardButton(" Download ", url=linktoSend)],]

            reply_markup : InlineKeyboardMarkup = InlineKeyboardMarkup(keyboard)


            update.message.reply_text('Click Download to download '+url,reply_markup = reply_markup)


        except Exception as e:

            print("Error: " + str(e))
    else:
        update.message.reply_text('Sorry, i do not understand what you wrote. Please Enter help to know what are the available services.')
    return ''

@run_async
def handle_message(update: Update , context):
    message_type: str = update.message.chat.type

    text: str = update.message.text

    print(f'User : ({update.message.chat.id}) in {message_type} : {text}')



    if message_type == 'group':
        if  BOT_Username in text:
            new_text: str = text.replace(BOT_Username,'').strip()
            response: str = handle_Response(new_text,update,context)
        else:
            return
    else:
        response: str = handle_Response(text,update,context)

    print('Bot: ', response)

    update.message.reply_text(response)

@run_async
def error(update: Update , context):
    print(f'Update {update} caused error {context.error}')

def main() -> None :
    print('Starting bot...')

    updater = Updater(Token, use_context=True, workers=4)


    app = updater.dispatcher

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('links', Links))
    app.add_handler(CommandHandler('download', Youtube_download))
    app.add_handler(CommandHandler('help', help))

    app.add_handler(MessageHandler(Filters.text(['start']), start_command))
    app.add_handler(MessageHandler(Filters.text(['links']), Links))
    app.add_handler(MessageHandler(Filters.text(['download']), Youtube_download))
    app.add_handler(MessageHandler(Filters.text(['help']), help))

    # Messages
    app.add_handler(MessageHandler(Filters.text, handle_message))

    # Errors
    app.add_error_handler(error)

    print('Polling...')

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
     main()


