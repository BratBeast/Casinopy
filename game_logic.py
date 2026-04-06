import random
import time
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 1. Налаштування логування (вимога лаби) [cite: 14, 61]
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class GameResult:
    primary_value: any
    is_win: bool
    money_delta: float


class IGame(ABC):
    @abstractmethod
    def play_once(self) -> GameResult:
        pass

    @abstractmethod
    def get_game_name(self) -> str:
        pass


# --- ОСЬ ВІН, ТВІЙ РЕФАКТОРИНГ ---
class SimulationEngine:
    """
    Окремий клас для розрахунків (Business Logic).
    Відповідає принципу Single Responsibility.
    """

    def __init__(self, game: IGame):
        self.game = game

    def run(self, num_runs: int):
        # Вимірювання продуктивності (Performance measurement) [cite: 13, 51]
        start_time = time.perf_counter()

        total_wins = 0
        total_money_delta = 0.0
        raw_data = []

        for _ in range(num_runs):
            res = self.game.play_once()
            if res.is_win:
                total_wins += 1
            total_money_delta += res.money_delta
            raw_data.append(res.primary_value)

        end_time = time.perf_counter()
        duration = end_time - start_time

        win_pc = (total_wins / num_runs * 100) if num_runs > 0 else 0

        report = (
            f"--- Результати: {self.game.get_game_name()} ---\n"
            f"Запусків: {num_runs}\n"
            f"Виграшів: {total_wins} ({win_pc:.2f}%)\n"
            f"Чистий профіт: {total_money_delta}\n"
            f"Час обробки: {duration:.4f} сек."
        )

        # Логування в консоль [cite: 60]
        logging.info(f"Виконано {num_runs} тестів гри {self.game.get_game_name()}")

        return report, raw_data, duration


# --- Твої ігри (залишаються як були) ---
class DiceGame(IGame):
    def get_game_name(self): return "Гра в Кості"

    def play_once(self):
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        is_win = (d1 == d2)
        return GameResult((d1, d2), is_win, 4.0 if is_win else -1.0)


class SlotsGame(IGame):
    def get_game_name(self): return "Слот-машина"

    def play_once(self):
        res = random.choices(["🍒", "7️⃣"], weights=[80, 20], k=3)
        is_win = (res[0] == res[1] == res[2])
        return GameResult(" ".join(res), is_win, 50.0 if is_win else -1.0)


class PistolRouletteGame(IGame):
    def get_game_name(self): return "Рулетка"

    def play_once(self):
        val = random.randint(1, 6)
        is_win = (val != 1)
        return GameResult(val, is_win, 1.0 if is_win else -5.0)