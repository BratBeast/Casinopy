import random
from dataclasses import dataclass
from abc import ABC, abstractmethod

#контейнер для результатів
@dataclass
class GameResult:
    """Простий клас для зберігання результату одного раунду."""
    primary_value: any
    is_win: bool
    money_delta: float

#"контракт" IGame
class IGame(ABC):
    """Абстрактний інтерфейс для всіх ігор казино."""

    @abstractmethod
    def play_once(self) -> GameResult:
        """Запускає один раунд гри."""
        pass

    @abstractmethod
    def get_game_name(self) -> str:
        """Повертає назву гри для UI."""
        pass

#гра "Кості"
class DiceGame(IGame):
    """Реалізація гри в Кості. Правило: дубль = перемога."""

    def get_game_name(self) -> str:
        return "Гра в Кості"

    def play_once(self) -> GameResult:
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        is_win = (dice1 == dice2)

        if is_win:
            money_delta = 4.0
        else:
            money_delta = -1.0

        return GameResult(
            primary_value=(dice1 + dice2),
            is_win=is_win,
            money_delta=money_delta
        )

#гра "Слоти" (Визначена нагорі, а не в __main__)
class SlotsGame(IGame):
    """
    Реалізація гри в Слоти.
    Використовує "зважені" ймовірності.
    """
    SYMBOLS = ["🍒", "🍋", "🍊", "BAR", "🔔", "7️⃣"]
    WEIGHTS = [25, 20, 15, 15, 10, 5]  # Разом 90

    def get_game_name(self) -> str:
        return "Слот-машина"

    def play_once(self) -> GameResult:
        reels = random.choices(self.SYMBOLS, self.WEIGHTS, k=3)
        is_win = False
        money_delta = -1.0  # Ставка = -1 монета

        if reels[0] == reels[1] and reels[1] == reels[2]:
            is_win = True
            symbol = reels[0]
            if symbol == "🍒":
                money_delta = 5.0
            elif symbol == "🍋":
                money_delta = 10.0
            elif symbol == "🍊":
                money_delta = 15.0
            elif symbol == "BAR":
                money_delta = 25.0
            elif symbol == "🔔":
                money_delta = 50.0
            elif symbol == "7️⃣":
                money_delta = 100.0

        return GameResult(
            primary_value=" ".join(reels),
            is_win=is_win,
            money_delta=money_delta
        )

class PistolRouletteGame(IGame):
    """
    Реалізація гри "Рулетка з пістолетом".
    Модель: 1 з 6 шансів на подію.
    """

    def get_game_name(self) -> str:
        return "Рулетка з пістолетом"

    def play_once(self) -> GameResult:
        #симулюємо "прокрутку барабана" (1 з 6 шансів)
        trigger_pull = random.randint(1, 6)

        #правила: "Виграш" - якщо подія не сталася (випало не 1)
        #"програш" - якщо подія сталася (випало 1)
        is_win = (trigger_pull != 1)

        #розрахунок грошей
        if is_win:
            money_delta = 1.0  # Виграли 1 монету (5/6 шансів)
        else:
            money_delta = -5.0 # Програли 5 монет (1/6 шансів)

        #повертаємо результат
        return GameResult(
            primary_value=trigger_pull,
            is_win=is_win,
            money_delta=money_delta
        )

# --- Блок для тестування---
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

    print("\n" + "=" * 30 + "\n")
    print("Тестування логіки SlotsGame...")

    slot_game = SlotsGame()
    print(f"Гра: {slot_game.get_game_name()}")

    slot_balance = 0
    slot_runs = 100000  #для слотів треба більше запусків

    for _ in range(slot_runs):
        result = slot_game.play_once()
        slot_balance += result.money_delta

    #розрахунок RTP (Return To Player)
    #скільки % грошей повернулося гравцю
    #ми "поставили" 100000 монет (по -1 за спін)
    rtp = (slot_balance + slot_runs) / slot_runs * 100

    print(f"Зіграно {slot_runs} спінів.")
    print(f"Баланс: {slot_balance}")
    print(f"RTP (Return To Player): {rtp:.2f}%")

    print("\n" + "=" * 30 + "\n")
    print("Тестування логіки PistolRouletteGame...")

    pistol_game = PistolRouletteGame()
    print(f"Гра: {pistol_game.get_game_name()}")

    pistol_balance = 0
    pistol_wins = 0
    pistol_runs = 100000

    for _ in range(pistol_runs):
        result = pistol_game.play_once()
        if result.is_win:
            pistol_wins += 1
        pistol_balance += result.money_delta

    print(f"Зіграно {pistol_runs} раундів.")
    print(f"Виграшів (подія не сталася): {pistol_wins}")
    print(f"Баланс: {pistol_balance}")
    #теоретично, баланс має бути близьким до 0, оскільки
    #(5/6 * 1.0) + (1/6 * -5.0) = 0