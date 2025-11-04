import unittest
from unittest.mock import patch

from game_logic import DiceGame, SlotsGame, PistolRouletteGame, GameResult, IGame

class TestGameLogic(unittest.TestCase):

    def setUp(self):
        """ця функція викликається перед кожним тестом."""
        self.dice_game = DiceGame()
        self.slots_game = SlotsGame()
        self.pistol_game = PistolRouletteGame()

    # --- Тести для DiceGame ---

    def test_dice_game_name(self):
        """тестуємо, що 'Кості' повертають правильну назву"""
        self.assertEqual(self.dice_game.get_game_name(), "Гра в Кості")

    def test_dice_game_play_once_types(self):
        """тестуємо, що 'Кості' повертають коректні ТИПИ даних"""
        result = self.dice_game.play_once()
        self.assertIsInstance(result, GameResult)
        self.assertIsInstance(result.primary_value, int)
        self.assertIsInstance(result.money_delta, float)
        self.assertIsInstance(result.is_win, bool)

    # --- Тести для SlotsGame ---

    def test_slots_game_name(self):
        """тестуємо, що 'Слоти' повертають правильну назву"""
        self.assertEqual(self.slots_game.get_game_name(), "Слот-машина")

    def test_slots_game_play_once_types(self):
        """тестуємо, що 'Слоти' повертають коректні ТИПИ даних"""
        result = self.slots_game.play_once()
        self.assertIsInstance(result, GameResult)
        self.assertIsInstance(result.primary_value, str)
        self.assertIsInstance(result.money_delta, float)
        self.assertIsInstance(result.is_win, bool)

    # --- Тести для PistolRouletteGame ---

    def test_pistol_game_name(self):
        """тестуємо, що 'Рулетка' повертає правильну назву"""
        self.assertEqual(self.pistol_game.get_game_name(), "Рулетка з пістолетом")

    def test_pistol_game_play_once_types(self):
        """тестуємо, що 'Рулетка' повертають коректні ТИПИ даних"""
        result = self.pistol_game.play_once()
        self.assertIsInstance(result, GameResult)
        self.assertIsInstance(result.primary_value, int)
        self.assertIsInstance(result.money_delta, float)
        self.assertIsInstance(result.is_win, bool)

    @patch('game_logic.random.randint')
    def test_dice_game_logic_win(self, mock_randint):
        """тестуємо логіку виграшу в Костях (дубль)"""
        mock_randint.side_effect = [3, 3]
        result = self.dice_game.play_once()
        self.assertTrue(result.is_win)
        self.assertEqual(result.money_delta, 4.0)

    @patch('game_logic.random.randint')
    def test_dice_game_logic_lose(self, mock_randint):
        """тестуємо логіку програшу в Костях (не дубль)"""
        mock_randint.side_effect = [1, 2]
        result = self.dice_game.play_once()
        self.assertFalse(result.is_win)
        self.assertEqual(result.money_delta, -1.0)

    @patch('game_logic.random.choices')
    def test_slots_game_logic_jackpot(self, mock_choices):
        """тестуємо логіку джекпоту в Слотах (7️⃣-7️⃣-7️⃣)в"""
        mock_choices.return_value = ["7️⃣", "7️⃣", "7️⃣"]

        result = self.slots_game.play_once()

        self.assertTrue(result.is_win)
        self.assertEqual(result.money_delta, 100.0)

    @patch('game_logic.random.choices')
    def test_slots_game_logic_lose(self, mock_choices):
        """тестуємо логіку програшу в Слотах"""
        mock_choices.return_value = ["🍒", "BAR", "🍋"]

        result = self.slots_game.play_once()

        self.assertFalse(result.is_win)
        self.assertEqual(result.money_delta, -1.0)

    @patch('game_logic.random.randint')
    def test_pistol_game_logic_lose(self, mock_randint):
        """тестуємо логіку програшу в Рулетці (подія сталася)"""
        mock_randint.return_value = 1
        result = self.pistol_game.play_once()
        self.assertFalse(result.is_win)
        self.assertEqual(result.money_delta, -5.0)

    @patch('game_logic.random.randint')
    def test_pistol_game_logic_win(self, mock_randint):
        """тестуємо логіку виграшу в Рулетці (подія не сталася)"""
        mock_randint.return_value = 4
        result = self.pistol_game.play_once()
        self.assertTrue(result.is_win)
        self.assertEqual(result.money_delta, 1.0)


if __name__ == '__main__':
    unittest.main()