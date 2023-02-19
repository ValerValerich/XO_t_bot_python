import time
from token_1 import TOKEN_API

import telebot
from telebot import types
import uuid


bot = telebot.TeleBot(TOKEN_API)
storage = {}

# инициализируем классы идент игры, кто сейчас ходит, чат, сообщение, поле
class Game:
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.current = "X"
        self.chat_id = None
        self.message_id = None
        self.map = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' ']
        ]




# команда для начала игры
@bot.message_handler(commands=["start"])
def start(message):
    game = Game()
    storage[game.uuid] = game
    message = bot.send_message(message.chat.id, "Начинаем игру")
    time.sleep(2)
    game.message_id = message.id
    game.chat_id = message.chat.id
    step(game)

# шаг игры (изменения сообщения поочередное)
def step(game, flag=None):
    kk = gen_markup(game)
    # bot.send_message(message.chat.id, f"Ходят: {game.current}", reply_markup=kk)
    if flag == None:
        bot.edit_message_text(f"Ходят: {game.current}", game.chat_id, game.message_id, reply_markup=kk)
    else:
        bot.edit_message_text(f"Тут уже занято. Ходят: {game.current}", game.chat_id, game.message_id, reply_markup=kk)

#генерация клавиатуры в зависимости от поля
def gen_markup(game):
    keyboard = types.InlineKeyboardMarkup()
    for i, row in enumerate(game.map):
        aa = []
        for j, item in enumerate(row):
            aa.append(
                telebot.types.InlineKeyboardButton(f"{item}",
                                                   callback_data=f"touch:{i}:{j}:{game.uuid}:{game.current}"))

        keyboard.row(*aa)

    return keyboard

# функция которая реализовывает ходы
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    action, i, j, uuid, current = call.data.split(":")
    i = int(i)
    j = int(j)

    game = storage[uuid]
    if game.map[i][j] not in ['O', 'X']:
        game.map[i][j] = current
        if current == 'X':
            game.current = 'O'
        else:
            game.current = 'X'
        step(game)
        win = check_map_for_win(game.map)
    else:
        step(game, "error")
        callback_query(call)
    if win:
        bot.answer_callback_query(call.id, f"{win} победили!")
        stop_game(game,win)

def stop_game(game,win):
    bot.edit_message_text(f"Победили: {win}", game.chat_id, game.message_id, reply_markup=None)


#функция проверки комбинаций
def check_map_for_win(game_map):
    combinations = [
        [[0, 0], [0, 1], [0, 2]],
        [[1, 0], [1, 1], [1, 2]],
        [[2, 0], [2, 1], [2, 2]],
        [[0, 0], [1, 0], [2, 0]],
        [[0, 1], [1, 1], [2, 1]],
        [[0, 2], [1, 2], [2, 2]],
        [[0, 0], [1, 1], [2, 2]],
        [[0, 2], [1, 1], [2, 0]],
    ]

    for combination in combinations:
        arr = []
        for point in combination:
            value = game_map[point[0]][point[1]]
            arr.append(value)
        if (arr[0] == "X" or arr[0] == "O") and arr[0] == arr[1] and arr[1] == arr[2]:
            return arr[0]

    return False

bot.infinity_polling()
