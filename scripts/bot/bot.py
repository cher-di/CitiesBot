import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
from typing import Iterable

import scripts.game.cities as cities

LEFT_TIME = [60, 30, 20, 10, 0]
INTERVALS = [30, 10, 10, 10, 0]
FIRST_INTERVAL = 60


class Bot:
    def __init__(self, token: str, cities: Iterable, logs_path: str):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO,
                            filename=logs_path,
                            filemode="w")

        self._cities = tuple(cities)

        self._updater = Updater(token=token, use_context=True)
        self._dispatcher = self._updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        self._dispatcher.add_handler(start_handler)

        stop_handler = CommandHandler('stop', self.stop)
        self._dispatcher.add_handler(stop_handler)

        message_handler = MessageHandler(Filters.text, self.player_make_step)
        self._dispatcher.add_handler(message_handler)

        self._games = dict()
        self._reminders = dict()
        self._timeout_jobs = dict()

    def get_current_players(self) -> Iterable:
        return (player for player in self._games.keys())

    def check_is_playing(self, chat_id: int):
        return chat_id in self.get_current_players()

    def run(self):
        self._updater.start_polling()

    def start(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        name = update.effective_user.first_name
        context.bot.send_message(chat_id, f"Привет, {name}!")

        if chat_id in self._games.keys():
            context.bot.send_message(chat_id, f"Мы с тобой уже играем!")
        else:
            self._games[chat_id] = cities.Game(self._cities)
            context.bot.send_message(chat_id, "Сыграем в города?\n"
                                              "Правила игры стандартные, но ты должен назвать город не более чем за 2 минуты\n"
                                              "В противном случае, ты проиграл..."
                                              "Я хожу первым!")
            context.job_queue.run_once(self.bot_make_step, 0, context=chat_id)

    def bot_make_step(self, context: CallbackContext):
        chat_id = context.job.context
        game = self._games[chat_id]
        if game.game_over:
            context.bot.send_message(chat_id, "Я не знаю, какой город назвать... Ты выиграл!")
            self.game_over(chat_id)
        else:
            city = game.get_next_random_city()
            game.give_city(city)

            context.bot.send_message(chat_id, f"{city}, тебе на {game.last_letter_of_last_city}")
            job = context.job_queue.run_repeating(callback=self.remind_about_left_time,
                                                  interval=FIRST_INTERVAL,
                                                  first=FIRST_INTERVAL,
                                                  context=(chat_id, iter(INTERVALS), iter(LEFT_TIME)))
            self._reminders[chat_id] = job

            if game.game_over:
                context.bot.send_message(chat_id, f"Больше нет городов на букву {game.last_letter_of_last_city}"
                                                  f"\nТы проиграл!")
                self.game_over(chat_id)

    def player_make_step(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id

        if chat_id not in self._games.keys():
            context.bot.send_message(chat_id, "Если хочешь поиграть со мной, набери '/start'")
        else:
            game = self._games[chat_id]
            city = update.effective_message.text

            status = game.give_city(city)
            if status == cities.AVAILABLE:
                context.job_queue.run_once(self.bot_make_step, 0, context=chat_id)
                self._reminders[chat_id].schedule_removal()
            elif status == cities.WRONG_FIRST_LETTER:
                context.bot.send_message(chat_id, f"Тебе на {game.last_letter_of_last_city}")
            elif status == cities.WRONG_VALUE:
                context.bot.send_message(chat_id, "Проверь правильность написания названия города"
                                                  "\nЯ знаю только русские города")
            elif status == cities.NOT_FOUND:
                context.bot.send_message(chat_id, "Я не знаю такого города")
            elif status == cities.NOT_AVAILABLE:
                context.bot.send_message(chat_id, "Этот город уже был")
            else:
                context.bot.send_message(chat_id, "Ой, что-то пошло не так...")

    def stop(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        if chat_id not in self._games.keys():
            context.bot.send_message(chat_id, "Если хочешь поиграть со мной, набери /start")
        else:
            context.bot.send_message(chat_id, "Игра окончена!")
            self.game_over(chat_id)

    def remind_about_left_time(self, context: CallbackContext):
        job = context.job
        chat_id, intervals_iter, left_time_iter = job.context

        left_time = next(left_time_iter)
        next_interval = next(intervals_iter)

        if left_time == 0:
            context.bot.send_message(chat_id, "Время кончилось!\n"
                                              "Вы проиграли!")
            self.game_over(chat_id)
        else:
            context.bot.send_message(chat_id, f"У вас осталось {left_time} секунд")
            job.interval = next_interval

    def game_over(self, chat_id: int):
        self._reminders[chat_id].schedule_removal()
        self._reminders.pop(chat_id)
        self._games.pop(chat_id)


if __name__ == '__main__':
    print("This is the main file, which execute app")
