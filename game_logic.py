import random
from dataclasses import dataclass
from abc import ABC, abstractmethod

#контейнер для результатів (аналог struct з C++)
#@dataclass автоматично створює конструктор (__init__)
@dataclass
class GameResult:
    """Простий клас для зберігання результату одного раунду."""
    primary_value: any
    is_win: bool
    money_delta: float


#2. "Контракт" IGame (Абстрактний базовий клас)
#усі наші ігри МУСЯТЬ реалізувати ці методи.
class IGame(ABC):
    """абстрактний інтерфейс для всіх ігор казино."""

    @abstractmethod
    def play_once(self) -> GameResult:
        """
        Запускає один раунд гри.
        :return: Об'єкт GameResult з результатом.
        """
        pass

    @abstractmethod
    def get_game_name(self) -> str:
        """
        :return: Назва гри для відображення в UI.
        """
        pass

class DiceGame(IGame):
    """реалізація гри в кості. дубль = перемога."""

    def get_game_name(self) -> str:
        return "Гра в Кості"

    def play_once(self) -> GameResult:
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)

        is_win = (dice1 == dice2)

        if is_win:
            money_delta = 4.0  #виграш (ставка 1, виграли 4)
        else:
            money_delta = -1.0  #програш (втратили ставку 1)

        #повертаємо результат
        return GameResult(
            primary_value=(dice1 + dice2),  #збережемо суму
            is_win=is_win,
            money_delta=money_delta
        )


# --- Блок для тестування ---
if __name__ == "__main__":
    print("Тестування логіки DiceGame...")

    game = DiceGame()
    print(f"Гра: {game.get_game_name()}")

    wins = 0
    balance = 0
    runs = 1000

    for _ in range(runs):
        result = game.play_once()
        if result.is_win:
            wins += 1
        balance += result.money_delta

    print(f"Зіграно {runs} ігор.")
    print(f"Виграшів: {wins} ({(wins / runs) * 100:.2f}%)")
    print(f"Баланс: {balance}")