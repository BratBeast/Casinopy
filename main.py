import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading
from ttkthemes import ThemedTk
import time
from game_logic import DiceGame, SlotsGame, PistolRouletteGame, IGame, GameResult
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter


class CasinoApp:
    def __init__(self, root):
        """Конструктор нашого додатка."""
        self.root = root
        self.root.title("OvvraBet Casino Simulator")
        self.root.geometry("500x480")  # зробив вікно ще вищим

        self.current_theme = tk.StringVar(value="arc")

        # --- МЕНЮ ---
        self.root.option_add('*tearOff', False)
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="Файл", menu=self.file_menu)

        self.file_menu.add_command(
            label="Налаштування...",
            command=self.show_settings_dialog
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Вихід",
            command=self.root.destroy
        )

        self.help_menu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="Допомога", menu=self.help_menu)

        self.help_menu.add_command(
            label="Про програму...",
            command=self.show_about_dialog
        )

        # --- "контейнер" для всіх елементів ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- секція вибору гри (Радіо-кнопки) ---
        game_frame = ttk.LabelFrame(main_frame, text="Виберіть гру")
        game_frame.pack(fill=tk.X, padx=5, pady=5)

        self.selected_game = tk.StringVar(value="dice")

        dice_rb = ttk.Radiobutton(
            game_frame,
            text="Кості",
            variable=self.selected_game,
            value="dice"
        )
        dice_rb.pack(anchor=tk.W, padx=10, pady=2)

        slots_rb = ttk.Radiobutton(
            game_frame,
            text="Слоти",
            variable=self.selected_game,
            value="slots"
        )
        slots_rb.pack(anchor=tk.W, padx=10, pady=2)

        pistol_rb = ttk.Radiobutton(
            game_frame,
            text="Рулетка з пістолетом",
            variable=self.selected_game,
            value="pistol"
        )
        pistol_rb.pack(anchor=tk.W, padx=10, pady=2)

        # --- секція налаштувань (Кількість запусків) ---
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, padx=5, pady=10)

        runs_label = ttk.Label(settings_frame, text="Кількість запусків:")
        runs_label.pack(side=tk.LEFT, padx=5)

        self.runs_spinbox = ttk.Spinbox(settings_frame, from_=1, to=1000000)
        self.runs_spinbox.set(1000)
        self.runs_spinbox.pack(side=tk.LEFT)

        # --- кнопка "Старт" ---
        self.start_button = ttk.Button(
            main_frame,
            text="СТАРТ СИМУЛЯЦІЇ",
            command=self.start_simulation
        )
        self.start_button.pack(fill=tk.X, padx=5, pady=5)

        self.show_chart_button = ttk.Button(
            main_frame,
            text="Показати графік",
            command=self.show_chart_window
        )
        self.show_chart_button.pack(fill=tk.X, padx=5, pady=5)
        self.show_chart_button.config(state=tk.DISABLED)

        #--- поле для результатів (Лог) ---
        self.log_browser = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=10
        )
        self.log_browser.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        #змінна для зберігання результату з потоку
        self.simulation_result = None

        #змінні для графіка
        self.last_run_data = None
        self.last_game_type = None

    def show_about_dialog(self):
        """
        Створює та показує нове вікно "Про програму".
        Це наше ВІКНO №2.
        """
        about_window = tk.Toplevel(self.root)
        about_window.title("Про програму")
        about_window.geometry("300x180")

        about_window.transient(self.root)
        about_window.grab_set()

        frame = ttk.Frame(about_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        about_label = ttk.Label(
            frame,
            text="OvvraBet Casino Simulator\n\n"
                 "Лабораторна робота №2\n"
                 "Виконав: Максим Овраменко",
            justify=tk.CENTER
        )
        about_label.pack(pady=10)

        ok_button = ttk.Button(
            frame,
            text="OK",
            command=about_window.destroy  #команда на закриття
        )
        ok_button.pack(pady=10, padx=20, fill=tk.X)

        self.root.wait_window(about_window)

    def show_settings_dialog(self):
        """
        Створює та показує нове вікно "Налаштування".
        Це наше ВІКНО №3.
        """
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Налаштування")

        settings_window.transient(self.root)
        settings_window.grab_set()

        frame = ttk.Frame(settings_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        theme_frame = ttk.LabelFrame(frame, text="Вибір теми")
        theme_frame.pack(fill=tk.X, padx=5, pady=5)

        selected_theme_var = tk.StringVar(value=self.current_theme.get())

        themes = ["arc", "radiance", "plastik"]
        for theme_name in themes:
            rb = ttk.Radiobutton(
                theme_frame,
                text=theme_name.capitalize(),
                variable=selected_theme_var,
                value=theme_name
            )
            rb.pack(anchor=tk.W, padx=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        save_button = ttk.Button(
            button_frame,
            text="Зберегти",
            command=lambda: self.apply_settings(
                selected_theme_var.get(), settings_window
            )
        )
        save_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = ttk.Button(
            button_frame,
            text="Скасувати",
            command=settings_window.destroy
        )
        cancel_button.pack(side=tk.RIGHT)

        self.root.wait_window(settings_window)

    def apply_settings(self, new_theme, window_to_close):
        """
        Застосовує нову тему і закриває вікно налаштувань.
        """
        self.root.set_theme(new_theme)
        self.current_theme.set(new_theme)
        window_to_close.destroy()

    def show_chart_window(self):
        """
        Створює та показує нове вікно "Графік".
        Це наше ВІКНО №4.
        """
        if self.last_run_data is None:
            tk.messagebox.showerror("Помилка", "Немає даних для графіка. "
                                               "Спочатку запустіть симуляцію.")
            return

        chart_window = tk.Toplevel(self.root)
        chart_window.title(f"Графік: {self.last_game_type.capitalize()}")
        chart_window.geometry("600x400")

        chart_window.transient(self.root)

        frame = ttk.Frame(chart_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        #готуємо дані для графіка
        data_counter = Counter(self.last_run_data)

        #сортуємо дані для гарного вигляду
        if self.last_game_type == "dice":
            #сортуємо за сумою (ключем)
            labels = sorted(data_counter.keys())
        else:
            #сортуємо за частотою (значенням)
            labels = [k for k, v in data_counter.most_common()]

        values = [data_counter[label] for label in labels]

        #створюємо фігуру Matplotlib
        fig = plt.Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(range(len(labels)), values, tick_label=labels)
        ax.set_title(f"Розподіл результатів ({self.last_game_type})")
        ax.set_ylabel("Кількість випадінь")
        fig.tight_layout()

        #вбудовуємо фігуру в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #кнопка "Закрити"
        close_button = ttk.Button(
            frame,
            text="Закрити",
            command=chart_window.destroy
        )
        close_button.pack(side=tk.BOTTOM, pady=10)

    def start_simulation(self):
        """
        Ця функція (ГОЛОВНИЙ ПОТІК) запускає симуляцію
        у фоновому потоці.
        """

        self.start_button.config(state=tk.DISABLED)
        self.show_chart_button.config(state=tk.DISABLED)
        self.log_browser.delete("1.0", tk.END)
        self.log_browser.insert(tk.END, "Запуск симуляції... Будь ласка, зачекайте...\n")
        self.root.update_idletasks()

        self.last_run_data = None  #очищуємо старі дані

        try:
            num_runs = int(self.runs_spinbox.get())
        except ValueError:
            self.log_browser.insert(tk.END, "Помилка: Кількість запусків має бути числом.")
            self.start_button.config(state=tk.NORMAL)
            return

        game_choice = self.selected_game.get()
        self.last_game_type = game_choice  #зберігаємо, яку гру запустили
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

        simulation_thread = threading.Thread(
            target=self.run_simulation_logic,
            args=(game, num_runs)
        )
        simulation_thread.start()

        self.check_for_result()

    def run_simulation_logic(self, game: IGame, num_runs: int):
        """
        Ця функція (ФОНОВИЙ ПОТІК) виконує всю важку роботу.
        Вона НЕ МАЄ права чіпати UI (напр. log_browser).
        """

        total_wins = 0
        total_money_delta = 0.0

        raw_data_list = []  #збираємо дані для графіка

        for _ in range(num_runs):
            result = game.play_once()
            if result.is_win:
                total_wins += 1
            total_money_delta += result.money_delta

            raw_data_list.append(result.primary_value)  #зберегти результат

        if num_runs == 0:
            win_percentage = 0
        else:
            win_percentage = (total_wins / num_runs) * 100.0

        rtp_text = ""
        if isinstance(game, SlotsGame) and num_runs > 0:
            rtp = (total_money_delta + num_runs) / num_runs * 100
            rtp_text = f"RTP (Return To Player): {rtp:.2f}%\n"

        result_text = ""
        result_text += f"--- Запуск гри '{game.get_game_name()}' ({num_runs} разів) ---\n"
        result_text += "\n--- СТАТИСТИКА ЗАВЕРШЕНА ---\n"
        result_text += f"Всього виграшів: {total_wins} ({win_percentage:.2f} %)\n"
        result_text += f"Чистий прибуток/збиток: {total_money_delta} монет\n"
        result_text += rtp_text

        self.simulation_result = (result_text, raw_data_list)

    def check_for_result(self):
        """
        ця функція кожні 100мс перевіряє,
        чи фоновий потік вже закінчив роботу.
        """
        if self.simulation_result is not None:
            text_result, data_result = self.simulation_result

            self.log_browser.delete("1.0", tk.END)
            self.log_browser.insert(tk.END, text_result)

            #зберігаємо дані та вмикаємо кнопку
            self.last_run_data = data_result
            self.start_button.config(state=tk.NORMAL)
            self.show_chart_button.config(state=tk.NORMAL)

            self.simulation_result = None
        else:
            self.root.after(100, self.check_for_result)


# --- Блок запуску програми ---
if __name__ == "__main__":
    #це потрібно для коректної роботи графіків на Windows
    plt.switch_backend('agg')

    root = ThemedTk(theme="arc")
    app = CasinoApp(root)
    app.current_theme.set("arc")
    root.mainloop()