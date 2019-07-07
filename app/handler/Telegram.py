import datetime
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop

from config import config
from db_models import Memes
from objects import session
from func.essentials import (add_meme, categorise_meme, history, id_to_meme,
                             list_tags, list_users, rate_meme, yield_random_meme)
from func.search import yield_search
from func.static import show_help

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='UpVote', callback_data='UpVote'),
     InlineKeyboardButton(text='DownVote', callback_data='DownVote')],
])


# https://telepot.readthedocs.io/en/latest/
class TelegramAPI():
    def start(self):
        def handle(message):
            # pylint: disable=unused-variable
            content_type, chat_type, chat_id = telepot.glance(message)
            user = message["from"]["username"]
            message = message.get("text")
            if message.startswith('/ran_meme'):
                for ms in yield_random_meme(message):
                    print(ms)
                    bot.sendMessage(chat_id, ms, reply_markup=keyboard)

            if message.startswith('/help'):
                bot.sendMessage(chat_id, show_help(), parse_mode='Markdown')

            if message.startswith('/size'):
                size: int = session.query(Memes).count()
                bot.sendMessage(chat_id, "There are : " + str(size) + " memes in the database")

            if message.startswith('/search'):
                for ms in yield_search(message.split(" ")[1:]):
                    bot.sendMessage(chat_id, ms, reply_markup=keyboard)

            if message.startswith('/tags'):
                bot.sendMessage(chat_id, "```" + list_tags() + "```", parse_mode='Markdown')

            if message.startswith("/posters"):
                bot.sendMessage(chat_id, "```" + list_users() + "```", parse_mode='Markdown')

            if message.startswith("/info"):
                bot.sendMessage(chat_id, history(message.split(" ")[1]), parse_mode='Markdown')

            if message.startswith("/post_meme"):
                add_meme(message.split(" ")[1], message.split(" ")[2], user, 1, datetime.datetime.utcnow())

            if message.startswith("/id2meme"):
                bot.sendMessage(chat_id, id_to_meme(int(message.split(" ")[1])), reply_markup=keyboard)

            if message.startswith("/cate_meme"):
                args: list = message.split(" ")[1:]
                categorise_meme(args[0], args[1], user, 1)

        def query(message):
            # pylint: disable=unused-variable
            query_id, from_id, query_data = telepot.glance(message, flavor='callback_query')

            username = message["from"]["username"]
            rating = query_data
            meme_id: int = int(message["message"]["text"].split(" ")[8])

            if rating == "UpVote":
                rate_meme(int(meme_id), 1, username, 1)
            elif rating == "DownVote":
                rate_meme(int(meme_id), -1, username, 1)

            bot.answerCallbackQuery(query_id, text="thanks for your rating (" + rating + "/" + str(meme_id) + ")")

        bot = telepot.Bot(config["tele_token"])
        MessageLoop(bot, {'chat': handle, 'callback_query': query}).run_as_thread()
