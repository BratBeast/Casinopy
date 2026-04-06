import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import logging
from ttkthemes import ThemedTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from game_logic import DiceGame, SlotsGame, PistolRouletteGame, IGame, SimulationEngine

# Налаштування логування для звіту
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CasinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Casinopy - Рефакторений Симулятор")
        self.root.geometry("600x600")

        self.simulation_result = None
        self.last_run_data = []
        self.setup_ui()

    def setup_ui(self):
        # Панель налаштувань
        self.controls_frame = ttk.LabelFrame(self.root, text=" Налаштування симуляції ")
        self.controls_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(self.controls_frame, text="Виберіть гру:").grid(row=0, column=0, padx=5, pady=5)
        self.game_var = tk.StringVar(value="Кості")
        self.game_combo = ttk.Combobox(self.controls_frame, textvariable=self.game_var,
                                       values=["Кості", "Слоти", "Рулетка"], state="readonly")
        self.game_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.controls_frame, text="Кількість запусків:").grid(row=1, column=0, padx=5, pady=5)
        self.runs_entry = ttk.Entry(self.controls_frame)
        self.runs_entry.insert(0, "1000")
        self.runs_entry.grid(row=1, column=1, padx=5, pady=5)

        self.start_button = ttk.Button(self.controls_frame, text="ЗАПУСТИТИ РЕФАКТОРЕНИЙ ДВИГУН",
                                       command=self.start_simulation)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Поле виводу результатів
        self.log_browser = scrolledtext.ScrolledText(self.root, height=10, font=("Consolas", 10))
        self.log_browser.pack(pady=10, padx=10, fill="both", expand=True)

        self.show_chart_button = ttk.Button(self.root, text="Показати графік", command=self.show_chart,
                                            state=tk.DISABLED)
        self.show_chart_button.pack(pady=5)

    def start_simulation(self):
        try:
            num_runs = int(self.runs_entry.get())
            game_name = self.game_var.get()

            game_map = {
                "Кості": DiceGame(),
                "Слоти": SlotsGame(),
                "Рулетка": PistolRouletteGame()
            }
            game = game_map[game_name]

            self.start_button.config(state=tk.DISABLED)
            self.log_browser.delete("1.0", tk.END)
            self.log_browser.insert(tk.END, "Симуляція запущена...\n")

            # Запуск рефактореної логіки у фоновому потоці
            thread = threading.Thread(target=self.run_logic_thread, args=(game, num_runs))
            thread.daemon = True
            thread.start()

            self.check_for_result()
        except ValueError:
            self.log_browser.insert(tk.END, "ПОМИЛКА: Введіть коректне число запусків!")

    def run_logic_thread(self, game: IGame, num_runs: int):
        # Виклик нового SimulationEngine (Крок рефакторингу)
        engine = SimulationEngine(game)
        report, raw_data, duration = engine.run(num_runs)
        self.simulation_result = (report, raw_data)

    def check_for_result(self):
        if self.simulation_result:
            report, data = self.simulation_result
            self.log_browser.delete("1.0", tk.END)
            self.log_browser.insert(tk.END, report)
            self.last_run_data = data
            self.simulation_result = None
            self.start_button.config(state=tk.NORMAL)
            self.show_chart_button.config(state=tk.NORMAL)
        else:
            self.root.after(100, self.check_for_result)

    def show_chart(self):
        if not self.last_run_data:
            return

        # ОЧИЩЕННЯ: Закриваємо попередні вікна, щоб графіки не накладалися [cite: 29, 31]
        plt.close('all')

        plt.figure("Результати симуляції", figsize=(8, 5))

        processed_data = []
        for item in self.last_run_data:
            if isinstance(item, tuple):
                processed_data.append(sum(item))
            else:
                processed_data.append(item)

        if isinstance(processed_data[0], str):
            from collections import Counter
            counts = Counter(processed_data)
            # Сортуємо для кращого вигляду [cite: 8, 31]
            labels, values = zip(*sorted(counts.items(), key=lambda x: x[1], reverse=True))
            plt.bar(labels, values, color='skyblue', edgecolor='black')
            plt.xticks(rotation=45, ha='right')  # Нахиляємо текст, щоб не зливався [cite: 8]
        else:
            plt.hist(processed_data, bins=20, color='skyblue', edgecolor='black')

        plt.title(f"Розподіл результатів: {self.game_var.get()}")
        plt.ylabel("Кількість випадінь")
        plt.tight_layout()  # Автоматично підганяє розміри, щоб написи влізли [cite: 31, 34]
        plt.show()

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = CasinoApp(root)
    root.mainloop()