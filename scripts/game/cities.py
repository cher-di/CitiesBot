from typing import Iterable
from random import sample, choice
from typing import Generator
import re


NOT_FOUND = 1
AVAILABLE = 2
NOT_AVAILABLE = 3
WRONG_VALUE = 4
WRONG_FIRST_LETTER = 5

ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
RESTRICTED_LAST_LETTERS = ("й", "ы", "ъ", "ь")
RESTRICTED_FIRST_LETTERS = ("й", "ы")
CITY_PATTERN = re.compile(r"[а-я][а-я\t\-]*")


class GameLogicError(Exception):
    pass


class FirstCityNotChosen(GameLogicError):
    pass


class NoCitiesProvided(GameLogicError):
    pass


class GameIsAlreadyOver(GameLogicError):
    pass


class Game:
    def __init__(self, cities: Iterable):
        # Отфильтруем города
        # 1. Уберём дубликаты
        # 2. Уберём города, название которых не подходят под паттерн
        # 3. Уберём города, которые начинаются на запрещённые буквы
        # 4. Уберём пустые названия
        cities = set(city.lower() for city in cities if self.check_city(city))
        if not cities:
            raise NoCitiesProvided

        self._available_cities = {letter: set() for letter in set(ALPHABET) - set(RESTRICTED_LAST_LETTERS)}
        self._non_available_cities = set()

        for city in cities:
            first_letter = city[0]
            self._available_cities[first_letter].add(city)

        self._last_city = None

    def give_city(self, city: str) -> int:
        if not self.check_city(city):
            return WRONG_VALUE

        city = city.lower()
        first_letter = city[0]

        if self._last_city is None or (self._last_city is not None and city.startswith(self.last_letter_of_last_city)):
            if city in self._available_cities[first_letter]:
                self._available_cities[first_letter].remove(city)
                self._non_available_cities.add(city)
                self._last_city = city
                return AVAILABLE
            elif city in self._non_available_cities:
                return NOT_AVAILABLE
            else:
                return NOT_FOUND
        else:
            return WRONG_FIRST_LETTER

    def get_next_random_city(self):
        if self.game_over:
            raise GameIsAlreadyOver

        if self._last_city is None:
            letter = choice(tuple(self.get_available_letters()))
        else:
            letter = self.last_letter_of_last_city

        return sample(self._available_cities[letter], 1)[0].capitalize()

    def get_available_letters(self) -> Generator:
        for letter, cities in self._available_cities.items():
            if cities:
                yield letter

    @property
    def last_city(self) -> str:
        if self._last_city is None:
            raise FirstCityNotChosen
        return self._last_city

    @property
    def last_letter_of_last_city(self) -> str:
        for letter in self.last_city[::-1]:
            if letter not in RESTRICTED_LAST_LETTERS:
                return letter

    @classmethod
    def check_city(cls, city: str) -> bool:
        city = city.lower()
        return not (re.fullmatch(CITY_PATTERN, city) is None or
                    city.startswith(RESTRICTED_FIRST_LETTERS) or
                    len(city) < 3)

    @property
    def game_over(self) -> bool:
        try:
            return self.last_letter_of_last_city not in self.get_available_letters()
        except FirstCityNotChosen:
            return False
