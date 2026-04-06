import unittest
from unittest.mock import patch, MagicMock
from game_logic import DiceGame, SimulationEngine, GameResult


class TestSimulationEngine(unittest.TestCase):
    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.get_game_name.return_value = "Test Game"
        self.engine = SimulationEngine(self.mock_game)

    def test_simulation_runs_correct_number_of_times(self):
        """Перевірка, що двигун викликає гру рівно N разів."""
        num_runs = 50
        self.mock_game.play_once.return_value = GameResult(primary_value=1, is_win=True, money_delta=1.0)

        report, data, duration = self.engine.run(num_runs)

        self.assertEqual(self.mock_game.play_once.call_count, num_runs)
        self.assertEqual(len(data), num_runs)
        self.assertGreater(duration, 0)

    def test_performance_measurement(self):
        """Перевірка, що час виконання вимірюється."""
        self.mock_game.play_once.return_value = GameResult(1, True, 1.0)
        _, _, duration = self.engine.run(10)
        self.assertIsInstance(duration, float)


class TestDiceGameRefactored(unittest.TestCase):
    @patch('game_logic.random.randint')
    def test_dice_win_logic(self, mock_randint):
        """Перевірка логіки дубля (перемоги) в костях."""
        mock_randint.side_effect = [6, 6]  # Дубль
        game = DiceGame()
        result = game.play_once()
        self.assertTrue(result.is_win)
        self.assertEqual(result.money_delta, 4.0)


if __name__ == '__main__':
    unittest.main()