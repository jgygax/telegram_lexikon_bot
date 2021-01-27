import logging
from telegram.error import NetworkError, Unauthorized
from things import token, id_julia
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
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
        self.written = dict()
        self.scores = dict()

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
        dp.add_handler(CommandHandler('submit', self.submit))
        dp.add_handler(CommandHandler('leave', self.leave_game))
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
        if (user_id, user_name) not in self.players:
            self.players.append((user_id, user_name))
            bot.sendMessage(chat_id=self.chat_id,
                            text=user_name + " has joined the game.")

    def leave_game(self, bot, update):
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        bot.sendMessage(
            chat_id=user_id, text="Please write 'I really want to leave the game' followed by the reason, why you want to leave to leave the game.")
        answer = update.message.text
        bot.sendMessage(chat_id=self.chat_id,
                        text=user_name + " has left the game.")
        self.players.remove((user_id, user_name))
        self.player_ids.remove(user_id)

    def start_game(self, bot, update):
        self.game_state = dict()
        self.guessings = dict()
        for uid, name in self.players:
            self.game_state[uid] = LexikonBot.IDLE
            self.guessings[uid] = -1
            self.scores[uid] = 0
        bot.sendMessage(chat_id=self.chat_id,
                        text="Game starts with: ")
        self.list_players(bot, update)
        self.get_definition(bot, update)

    def list_players(self, bot, update):
        playerlist = ""
        self.player_ids = []
        for uid, name in self.players:
            playerlist += name+"\n"
            self.player_ids += [uid]
        bot.send_message(chat_id=self.chat_id, text="<b>Players:</b>\n"+playerlist, parse_mode=ParseMode.HTML)

    def print_scores(self, bot, update):
        playerlist = ""
        self.player_ids = []
        for (uid, name), (uid2, score) in zip(self.players, self.scores.items()):
            playerlist += name+":\t" + str(score) + "\n"
        bot.send_message(chat_id=self.chat_id, text="<b>Scores:</b>\n"+playerlist, parse_mode=ParseMode.HTML)

    def set_current(self):
        self.current_word, self.answers[0] = self.L.get_definition()

    def get_definition(self, bot, update):
        self.set_current()
        for uid, name in self.players:
            self.game_state[uid] = LexikonBot.WRITING
        bot.sendMessage(chat_id=self.chat_id, text=self.current_word)
        for uid, name in self.players:
            bot.sendMessage(chat_id=uid, text=self.current_word)

    def write_answer(self, bot, update):
        user_id = update.message.from_user.id
        answer = update.message.text
        if self.game_state[user_id] == LexikonBot.WRITING:
            self.answers[user_id] = answer
            bot.sendMessage(
                chat_id=user_id, text="<b>Saved this answer:</b>\n" + self.answers[user_id] + "\n\nWrite '/submit' to submit your answer.", parse_mode=ParseMode.HTML)

        if self.game_state[user_id] == LexikonBot.GUESSING:
            self.guessings[user_id] = int(answer)-1
            try:
                bot.sendMessage(chat_id=user_id,
                                text="<b>You guessed:</b>\n" + self.ans[self.guessings[user_id]][1], parse_mode=ParseMode.HTML)
            except:
                bot.sendMessage(chat_id=user_id,
                                text="This is not a valid guess!")
            self.game_state[user_id] = LexikonBot.RESULTS
            self.results(bot, update)
        else:
            print("Please wait for the others.")

    def submit(self, bot, update):
        user_id = update.message.from_user.id
        self.game_state[user_id] = LexikonBot.READYFORGUESSING
        self.print_answers(bot, update)

    def print_answers(self, bot, update):
        check = True
        for uid, name in self.players:
            if self.game_state[uid] != LexikonBot.READYFORGUESSING:
                check = False
        if check:
            for uid, name in self.players:
                self.game_state[uid] = LexikonBot.GUESSING
            self.ans = [(k, v)
                        for k, v in self.answers.items() if k in self.player_ids or k == 0]
            random.shuffle(self.ans)
            for i, (k, v) in enumerate(self.ans):
                self.answers[k] = str(i+1) + ":\n" + v
                self.written[k] = i
                bot.sendMessage(chat_id=self.chat_id,
                                text=str(i+1) + ":\n" + v)
                for uid, name in self.players:
                    bot.sendMessage(chat_id=uid, text=str(i+1) + ":\n" + v)

    def results(self, bot, update):
        check = True
        for uid, name in self.players:
            if self.game_state[uid] != LexikonBot.RESULTS:
                check = False
        if check:
            bot.sendMessage(chat_id=self.chat_id,
                            text="<b>Correct Definition:</b>\n"+self.answers[0], parse_mode=ParseMode.HTML)
            for uid, name in self.players:
                bot.sendMessage(chat_id=self.chat_id,
                                text=name + " guessed " + str(self.guessings[uid]+1) + " and wrote:\n" + self.answers[uid])

            for uid, name in self.players:
                if self.guessings[uid] == self.written[0]:
                    self.scores[uid] += 1
                for k, w in self.written.items():
                    if self.guessings[uid] == w and k != uid:
                        if k != 0:
                            self.scores[k] += 1
            self.print_scores(bot, update)

    def hello(self, bot, update):
        user_id = update.message.chat_id
        user_name = update.message.from_user.first_name

        bot.sendMessage(chat_id=user_id, text="Hi, " +
                        user_name + ", nice to meet you!")

    def help_bot(self, bot, update):
        user_name = update.message.from_user.first_name
        print("HELP")
        bot.sendMessage(chat_id=self.chat_id, text="De " +
                        user_name + " bruucht dringend Hilf!!!")

    def new_game(self, bot, update):
        self.players = []
        self.chat_id = update.message.chat_id
        bot.sendMessage(chat_id=self.chat_id, text="new game started")

    def start(self, bot, update):
        self.players = []
        self.chat_id = update.message.chat_id
        self.hello(bot, update)
        kb = [
            [telegram.KeyboardButton(
                '/hello'), telegram.KeyboardButton('/start')],
            [telegram.KeyboardButton('/new_game'),
             telegram.KeyboardButton('/join')],
            [telegram.KeyboardButton('/start_game'),
             telegram.KeyboardButton('/leave')],
            [telegram.KeyboardButton('/submit'),
             telegram.KeyboardButton('/new')],
            [telegram.KeyboardButton('/players'),
             telegram.KeyboardButton('/help')]
        ]
        kb_markup = telegram.ReplyKeyboardMarkup(
            keyboard=kb, resize_keyboard=True)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Let's play Lexikon",
                         reply_markup=kb_markup)
