import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading
from ttkthemes import ThemedTk
import time

from game_logic import DiceGame, SlotsGame, PistolRouletteGame, IGame, GameResult


class CasinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OvvraBet Casino Simulator")
        self.root.geometry("500x400")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        game_frame = ttk.LabelFrame(main_frame, text="Виберіть гру")
        game_frame.pack(fill=tk.X, padx=5, pady=5)

        self.selected_game = tk.StringVar(value="dice")

        dice_rb = ttk.Radiobutton(
            game_frame,
            text="Кості",
            variable=self.selected_game,
            value="dice"
        )
        dice_rb.pack(anchor=tk.W, padx=10)

        slots_rb = ttk.Radiobutton(
            game_frame,
            text="Слоти",
            variable=self.selected_game,
            value="slots"
        )
        slots_rb.pack(anchor=tk.W, padx=10)

        pistol_rb = ttk.Radiobutton(
            game_frame,
            text="Рулетка з пістолетом",
            variable=self.selected_game,
            value="pistol"
        )
        pistol_rb.pack(anchor=tk.W, padx=10)

        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, padx=5, pady=10)

        runs_label = ttk.Label(settings_frame, text="Кількість запусків:")
        runs_label.pack(side=tk.LEFT, padx=5)

        self.runs_spinbox = ttk.Spinbox(settings_frame, from_=1, to=1000000)
        self.runs_spinbox.set(1000)
        self.runs_spinbox.pack(side=tk.LEFT)

        self.start_button = ttk.Button(
            main_frame,
            text="СТАРТ СИМУЛЯЦІЇ",
            command=self.start_simulation
        )
        self.start_button.pack(fill=tk.X, padx=5, pady=5)

        self.log_browser = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=10
        )
        self.log_browser.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.simulation_result = None

    def start_simulation(self):
        """Ця функція запускає симуляцію у фоновому потоці."""
        self.start_button.config(state=tk.DISABLED)
        self.log_browser.delete("1.0", tk.END)
        self.log_browser.insert(tk.END, "Запуск симуляції... Будь ласка, зачекайте...\n")
        self.root.update_idletasks()

        try:
            num_runs = int(self.runs_spinbox.get())
        except ValueError:
            self.log_browser.insert(tk.END, "Помилка: Кількість запусків має бути числом.")
            self.start_button.config(state=tk.NORMAL)
            return

        game_choice = self.selected_game.get()
        game: IGame = None

        if game_choice == "dice":
            game = DiceGame()
        elif game_choice == "slots":
            game = SlotsGame()
        elif game_choice == "pistol":
            game = PistolRouletteGame()
        else:
            self.log_browser.insert(tk.END, "Помилка: Ця гра ще не реалізована.")
            self.start_button.config(state=tk.NORMAL)
            return

        #запускаємо потік
        simulation_thread = threading.Thread(
            target=self.run_simulation_logic,
            args=(game, num_runs)
        )
        simulation_thread.start()
        self.check_for_result()

    def run_simulation_logic(self, game: IGame, num_runs: int):
        """Ця функція виконує всю важку роботу у фоновому потоці."""

        #запуск симуляції
        total_wins = 0
        total_money_delta = 0.0
        for _ in range(num_runs):
            result = game.play_once()
            if result.is_win:
                total_wins += 1
            total_money_delta += result.money_delta

        #розрахунок статистики
        win_percentage = (total_wins / num_runs) * 100.0


        #розрахунок RTP (тільки для слотів)
        rtp_text = ""
        if isinstance(game, SlotsGame):
            rtp = (total_money_delta + num_runs) / num_runs * 100
            rtp_text = f"RTP (Return To Player): {rtp:.2f}%\n"

        #формування фінального тексту
        result_text = ""
        result_text += f"--- Запуск гри '{game.get_game_name()}' ({num_runs} разів) ---\n"
        result_text += "\n--- СТАТИСТИКА ЗАВЕРШЕНА ---\n"
        result_text += f"Всього виграшів: {total_wins} ({win_percentage:.2f} %)\n"
        result_text += f"Чистий прибуток/збиток: {total_money_delta} монет\n"
        result_text += rtp_text  #додаємо рядок RTP (буде порожнім для костей)

        #збереження результату для головного потоку
        self.simulation_result = result_text

    def check_for_result(self):
        """Перевіряє, чи фоновий потік закінчив роботу."""
        if self.simulation_result is not None:
            self.log_browser.delete("1.0", tk.END)
            self.log_browser.insert(tk.END, self.simulation_result)
            self.start_button.config(state=tk.NORMAL)
            self.simulation_result = None
        else:
            self.root.after(100, self.check_for_result)


# --- Блок запуску програми ---
if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = CasinoApp(root)
    root.mainloop()