#!/usr/bin/env python3

from abc import ABC, abstractmethod
from copy import deepcopy
from random import randint

from telebot import TeleBot, formatting
from telebot.custom_filters import TextFilter
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import TOKEN

CHOOSE_EASY = 'choose_easy'
CHOOSE_HARD = 'choose_hard'
CHOOSE_X = 'choose_x'
CHOOSE_O = 'choose_o'
CHOOSE_LEVEL = 'choose_level'
OCCUPIED = 'occupied'

unique_dict = dict()

bot = TeleBot(TOKEN)


class TicTacToe(ABC):

    ROWS = 3
    COLS = 3

    def __init__(self):
        self._human_player = 'X'
        self._computer_player = 'O'
        self._board = [[(r * TicTacToe.ROWS + c + 1)
                       for c in range(0, TicTacToe.COLS)] for r in range(0, TicTacToe.ROWS)]

    @property
    def human_player(self):
        return self._human_player

    @human_player.setter
    def human_player(self, value):
        self._human_player = value

    @property
    def computer_player(self):
        return self._computer_player

    @computer_player.setter
    def computer_player(self, value):
        self._computer_player = value

    @abstractmethod
    def calc_move(self):
        pass

    def print_board(self):
        markup = []

        for r in self._board:
            cols = []

            for c in r:
                if c in range(1, TicTacToe.ROWS * TicTacToe.COLS + 1):
                    button = InlineKeyboardButton(
                        str(c), callback_data=f'CHOOSE_{c}')
                else:
                    button = InlineKeyboardButton(
                        c, callback_data=OCCUPIED)
                cols.append(button)
            markup.append(cols)

        return InlineKeyboardMarkup(markup, row_width=TicTacToe.COLS)

    def has_game_over(self):
        return TicTacToe._has_game_over(self._board)

    def do_move(self, move, player):
        TicTacToe._do_move(self._board, move, player)

    @staticmethod
    def _has_game_over(board):
        if TicTacToe._has_won(board, 'X'):
            return [True, 'X']
        elif TicTacToe._has_won(board, 'O'):
            return [True, 'O']
        elif not TicTacToe._moves_available(board):
            return [True, '-']
        else:
            return [False, '']

    @staticmethod
    def _do_move(board, move, player):
        if move not in range(1, TicTacToe.ROWS * TicTacToe.COLS + 1):
            return False

        r, c = TicTacToe._move_to_row_col(move)

        if board[r][c] != 'X' and board[r][c] != 'O':
            board[r][c] = player
            return True

        return False

    @staticmethod
    def _move_to_row_col(move):
        r = (move - 1) // TicTacToe.ROWS
        c = (move - 1) % TicTacToe.COLS

        return (r, c)

    @staticmethod
    def _moves_available(board):
        availables = []

        for r in board:
            for c in r:
                if c != 'X' and c != 'O':
                    availables.append(c)

        return availables

    @staticmethod
    def _has_won(board, player):
        for r in board:
            if r.count(player) == TicTacToe.COLS:
                return True

        for c in range(TicTacToe.COLS):
            column_complete = True

            for r in range(TicTacToe.ROWS):
                if board[r][c] != player:
                    column_complete = False
                    break

            if column_complete:
                return True

        for x in range(TicTacToe.ROWS):
            if board[x][x] != player:
                break
        else:
            return True

        for x in range(TicTacToe.ROWS):
            if board[x][TicTacToe.ROWS - x - 1] != player:
                break
        else:
            return True

        return False


class EasyTicTacToe(TicTacToe):

    def calc_move(self):
        availables = self._moves_available(self._board)
        return availables[randint(0, len(availables) - 1)]


class HardTicTacToe(TicTacToe):

    def calc_move(self):
        if len(TicTacToe._moves_available(self._board)) == TicTacToe.ROWS * TicTacToe.COLS:
            return TicTacToe.ROWS // 2 * TicTacToe.ROWS + TicTacToe.COLS // 2 + 1

        return HardTicTacToe._minimax(self._board, self.computer_player == 'X')[1]

    @staticmethod
    def _check_board(board):
        if TicTacToe._has_won(board, 'X'):
            return 1
        elif TicTacToe._has_won(board, '0'):
            return -1
        else:
            return 0

    @staticmethod
    def _minimax(board, is_next_move_X):
        check = TicTacToe._has_game_over(board)
        if check[0]:
            return [HardTicTacToe._check_board(board), 0]

        computed_move = 0

        if is_next_move_X:
            computed_value = -float('Inf')
            player = 'X'
        else:
            computed_value = float('Inf')
            player = 'O'

        for move in TicTacToe._moves_available(board):
            board_cloned = deepcopy(board)
            TicTacToe._do_move(board_cloned, move, player)
            new_value = HardTicTacToe._minimax(
                board_cloned, not is_next_move_X)[0]

            if is_next_move_X and new_value > computed_value:
                computed_value = new_value
                computed_move = move
            elif not is_next_move_X and new_value < computed_value:
                computed_value = new_value
                computed_move = move

        return [computed_value, computed_move]


@bot.message_handler(commands=['start'])
def start_command(message):
    hello_msg = "Привет, {}!\n" \
        "\n" \
        "Я крестиконоликовый бот!\n"

    if message.from_user.last_name:
        name = '{} {}'.format(message.from_user.first_name,
                              message.from_user.last_name)
    else:
        name = '{}'.format(message.from_user.first_name)

    name = formatting.mbold(name)

    bot.send_message(message.chat.id, hello_msg.format(
        name), parse_mode='MARKDOWN')

    msg, markup = new_game()
    bot.send_message(message.chat.id, msg, reply_markup=markup)


def new_game():
    msg = "Если хочешь сыграть в \"Крестики-нолики\"\n" \
          "то жми на кнопку \"Новая игра\"!"

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(
        'Новая игра', callback_data=CHOOSE_LEVEL))

    return (msg, markup)


def choose_level():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Тупой', callback_data=CHOOSE_EASY),
               InlineKeyboardButton('Умный', callback_data=CHOOSE_HARD))
    return ('Хочешь играть когда я тупой или умный?', markup)


def choose_player():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Крестиками', callback_data=CHOOSE_X),
               InlineKeyboardButton('Ноликами', callback_data=CHOOSE_O))
    return ('Хочешь играть крестиками или ноликами?', markup)


def show_board(game, showMsg=True):
    msg = "Выбирай на какое поле\n" \
          "ты поставишь свой {}".format(game.human_player)

    if showMsg:
        return (msg, game.print_board())
    else:
        return ('', game.print_board())


def show_winner(call, game, winner):
    if winner == game.human_player:
        bot.send_message(call.message.chat.id, 'Чёрт! Ты выиграл!')
    elif winner == game.computer_player:
        bot.send_message(call.message.chat.id,
                         'Я выиграл!\nНо я и подозревал что я умнее тебя!')
    else:
        bot.send_message(call.message.chat.id,
                         'Однако победила дружба - НИЧЬЯ!')


@bot.callback_query_handler(func=None)
def callback_reply(call: CallbackQuery):
    game: TicTacToe = unique_dict.get(call.message.chat.id)

    if call.data == CHOOSE_LEVEL:
        msg, markup = choose_level()
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
        return

    elif call.data == CHOOSE_EASY:
        unique_dict[call.message.chat.id] = EasyTicTacToe()
        msg, markup = choose_player()
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
        return

    elif call.data == CHOOSE_HARD:
        unique_dict[call.message.chat.id] = HardTicTacToe()
        msg, markup = choose_player()
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
        return

    elif call.data == CHOOSE_X:
        game.human_player = 'X'
        game.computer_player = 'O'
        bot.send_message(call.message.chat.id, 'Тогда ты начинаешь!')
        msg, markup = show_board(game)
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
        return

    elif call.data == CHOOSE_O:
        game.human_player = 'O'
        game.computer_player = 'X'
        bot.send_message(call.message.chat.id, 'Тогда я начинаю!')

        move = game.calc_move()
        game.do_move(move, 'X')
        msg, markup = show_board(game)
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
        return

    elif call.data == OCCUPIED:
        bot.send_message(call.message.chat.id,
                         'На эту клетку уже ходили, переходи!')
        msg, markup = show_board(game, False)
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)
        return

    elif call.data.startswith('CHOOSE_'):
        move = int(call.data[7:])
        game.do_move(move, game.human_player)
        msg, markup = show_board(game)
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)

        status, winner = game.has_game_over()
        if status:
            show_winner(call, game, winner)

            msg, markup = new_game()
            bot.send_message(call.message.chat.id, msg, reply_markup=markup)
            return

        move = game.calc_move()
        game.do_move(move, game.computer_player)
        msg, markup = show_board(game, False)
        bot.send_message(call.message.chat.id, 'А я отвечу вот так!', reply_markup=markup)

        status, winner = game.has_game_over()
        if status:
            show_winner(call, game, winner)

            msg, markup = new_game()
            bot.send_message(call.message.chat.id, msg, reply_markup=markup)
            return

        bot.send_message(call.message.chat.id, 'Твой ход!')
        return

    else:
        return

bot.infinity_polling()
