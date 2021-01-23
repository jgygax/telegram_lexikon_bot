import logging
from telegram.error import NetworkError, Unauthorized
from things import token, id_julia
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, InlineQueryHandler
from lexikon import Lexikon
import random


class LexikonBot:

    IDLE = 0
    WRITING = 1
    READYFORGUESSING = 2
    GUESSING = 3
    RESULTS = 4
    FINISHED = -1

    def __init__(self):
        self.L = Lexikon()
        self.answers = dict()
        self.players = []
        self.game_state = dict()
        self.guessings = dict()

        print('started')
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

        # configuration of telegram bot, dispatcher
        updater = Updater(token=token)
        dp = updater.dispatcher

        # specified telegram commands
        dp.add_handler(CommandHandler('start', self.start))
        dp.add_handler(CommandHandler('start_game', self.start_game))
        dp.add_handler(CommandHandler('new_game', self.new_game))
        dp.add_handler(CommandHandler('join', self.join_game))
        dp.add_handler(CommandHandler('hello', self.hello))
        dp.add_handler(CommandHandler('guess', self.guess))
        dp.add_handler(CommandHandler('results', self.results))
        dp.add_handler(CommandHandler('help', self.help_bot))
        dp.add_handler(CommandHandler('new', self.get_definition))
        dp.add_handler(CommandHandler('print', self.print_answers))
        dp.add_handler(CommandHandler('players', self.list_players))
        dp.add_handler(MessageHandler(Filters.all, self.write_answer))
        updater.start_polling()
        updater.idle()

    def join_game(self, bot, update):
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        if user_id not in self.players:
            self.players.append((user_id, user_name))
            bot.sendMessage(chat_id=self.chat_id,
                            text=user_name + " has joined the game.")

    def start_game(self, bot, update):
        for uid, name in self.players:
            self.game_state[uid] = LexikonBot.IDLE
            self.guessings[uid] = -1
        bot.sendMessage(chat_id=self.chat_id,
                        text="Game starts with: ")
        self.list_players(bot, update)
        self.get_definition(bot, update)

    def list_players(self, bot, update):
        playerlist = ""
        for uid, name in self.players:
            playerlist += name+"\n"
        bot.send_message(chat_id=self.chat_id, text="Players:\n"+playerlist)

    def set_current(self):
        self.current_word, self.answers[0] = self.L.get_definition()

    def get_definition(self, bot, update):
        self.set_current()
        for uid, name in self.players:
            self.game_state[uid] = LexikonBot.WRITING
        bot.sendMessage(chat_id=self.chat_id, text=self.current_word)

    def write_answer(self, bot, update):
        user_id = update.message.from_user.id
        answer = update.message.text
        if self.game_state[user_id] == LexikonBot.WRITING:
            self.answers[user_id] = answer
            bot.sendMessage(
                chat_id=user_id, text="saved this answer:\n" + self.answers[user_id])

        if self.game_state[user_id] == LexikonBot.GUESSING:
            self.guessings[user_id] = int(answer)-1
            print(answer)
            try:
                bot.sendMessage(chat_id=user_id,
                                text="You guessed:\n" + self.ans[self.guessings[user_id]][1])
            except:
                bot.sendMessage(chat_id=user_id,
                                text="This is not a valid guess!")
            self.game_state[user_id] = LexikonBot.RESULTS
        else:
            print("Please wait for the others.")

    def guess(self, bot, update):
        user_id = update.message.from_user.id
        self.game_state[user_id] = LexikonBot.READYFORGUESSING

    def print_answers(self, bot, update):
        check = True
        for uid, name in self.players:
            if self.game_state[uid] != LexikonBot.READYFORGUESSING:
                check = False
        if check:
            for uid, name in self.players:
                self.game_state[uid] = LexikonBot.GUESSING
            self.ans = list(self.answers.items())
            random.shuffle(self.ans)
            for i,(k, v) in enumerate(self.ans):
                bot.sendMessage(chat_id=self.chat_id, text=v)
                for uid, name in self.players:
                    bot.sendMessage(chat_id=uid, text=str(i+1) + ":\n" + v)


        else:
            bot.sendMessage(chat_id=self.chat_id,
                            text="There is not yet everyone ready.")

    def results(self, bot, update):
        check = True
        for uid, name in self.players:
            if self.game_state[uid] != LexikonBot.RESULTS:
                check = False
        if check:
            for uid, name in self.players:
                bot.sendMessage(chat_id=self.chat_id,
                                text=name + " guessed " + str(self.guessings[uid]+1) + " and wrote:\n" + self.answers[uid])
        else:
            bot.sendMessage(chat_id=self.chat_id,
                            text="There is not yet everyone ready.")

    def hello(self, bot, update):
        user_id = update.message.chat_id
        user_name = update.message.from_user.first_name

        bot.sendMessage(chat_id=user_id, text="Hi, " +
                        user_name + ", nice to meet you!")

    def help_bot(self, bot, update):
        pass

    def new_game(self, bot, update):
        self.players = []
        self.chat_id = update.message.chat_id
        bot.sendMessage(chat_id=self.chat_id, text="new game started")

    def start(self, bot, update):
        self.players = []
        self.chat_id = update.message.chat_id
        self.hello(bot, update)
        kb = [
            [telegram.KeyboardButton('/hello')],
            [telegram.KeyboardButton('/help')]
        ]
        kb_markup = telegram.ReplyKeyboardMarkup(
            keyboard=kb, resize_keyboard=True)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Let's play Lexikon",
                         reply_markup=kb_markup)
