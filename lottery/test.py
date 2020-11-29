import unittest
from unittest import mock
import numpy as np

from .lottery import Lottery, LuckyDip, Bankroll


class BankrollTests(unittest.TestCase):

    def test_iadd(self):
        bankroll = Bankroll(20)
        bankroll += 10
        self.assertEqual(30, bankroll)

    def test_isub(self):
        bankroll = Bankroll(20)
        bankroll -= 10
        self.assertEqual(10, bankroll)

    def test_eq(self):
        bankroll1 = Bankroll(20)
        bankroll2 = Bankroll(20)
        self.assertEqual(bankroll1, bankroll2)

    def test_ne(self):
        bankroll1 = Bankroll(20)
        bankroll2 = Bankroll(20)
        self.assertFalse(bankroll1 != bankroll2)

    def test_gl(self):
        bankroll1 = Bankroll(20)
        bankroll2 = Bankroll(40)
        self.assertTrue(bankroll2 > bankroll1)

    def test_lt(self):
        bankroll1 = Bankroll(20)
        bankroll2 = Bankroll(40)
        self.assertTrue(bankroll1 < bankroll2)


class TestLuckyDip(unittest.TestCase):

    def test_generate_new_numbers(self):
        np.random.seed(6)
        mock_bankroll = mock.MagicMock(spec=Bankroll)
        mock_bankroll._amount = 20.0

        lucky_dip = LuckyDip(
            num_draws=10, bankroll=mock_bankroll, cost=0.35,
            num_balls=5, max_num=42
        )
        expected = [
            [6, 21, 23, 32, 41],
            [23, 25, 29, 34, 37],
            [8, 9, 34, 35, 37],
            [1, 2, 4, 6, 37],
            [3, 25, 26, 27, 41],
            [8, 17, 18, 34, 38],
            [16, 19, 25, 37, 39],
            [9, 11, 14, 28, 30],
            [1, 5, 21, 22, 34],
            [5, 21, 25, 27, 40]
        ]
        expected = np.array(expected)
        self.assertTrue(np.array_equal(expected, lucky_dip.numbers))

    def test_use_existing_numbers(self):
        mock_bankroll = mock.MagicMock(spec=Bankroll)
        mock_bankroll._amount = 20.0

        expected = [
            [6, 21, 23, 32, 41],
            [23, 25, 29, 34, 37],
            [8, 9, 34, 30, 37],
            [1, 2, 4, 6, 37],
            [3, 25, 27, 27, 41],
            [8, 17, 18, 32, 38],
            [16, 19, 25, 37, 39],
            [9, 11, 14, 28, 30],
            [1, 5, 21, 22, 34],
            [5, 21, 25, 27, 40]
        ]
        lucky_dip = LuckyDip(
            num_draws=10, bankroll=mock_bankroll, cost=0.35,
            num_balls=5, max_num=42, numbers=expected
        )
        expected = np.array(expected)
        self.assertTrue(np.array_equal(expected, lucky_dip.numbers))

    # note to self: testing that bankroll is decremented properly is an integration test
    #   so we do not include it here in a unit test


class TestLottery(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_bankroll = mock.MagicMock(spec=Bankroll)
        self.mock_bankroll._amount = 20.0

        numbers = np.array([
            [0, 2, 9, 14, 27],
            [0, 2, 9, 14, 26],
            [0, 2, 9, 13, 26],
            [0, 2, 8, 13, 26],
            [0, 1, 8, 13, 26],
            [23, 25, 29, 34, 37],
        ])

        self.mock_lucky_dip = mock.MagicMock(spec=LuckyDip)
        self.mock_lucky_dip.numbers = numbers

    def test_draw(self):
        np.random.seed(2)
        lotto = Lottery(self.mock_bankroll, num_balls=42, num_balls_drawn=5, reward_scheme=[0, 0, 0, 3.5, 200, 80000])
        lotto.draw()
        expected = np.array([0, 2, 9, 14, 27])
        self.assertTrue(np.array_equal(expected, lotto.drawn_numbers_))

    def test_check(self):
        np.random.seed(2)
        lotto = Lottery(self.mock_bankroll, num_balls=42, num_balls_drawn=5, reward_scheme=[0, 0, 0, 3.5, 200, 80000])
        lotto.draw()  # [ 0,  2,  9, 14, 27]
        expected = [5, 4, 3, 2, 1, 0]
        actual = lotto.check(self.mock_lucky_dip)
        self.assertTrue(np.array_equal(expected, actual))

    def payout(self, numbers, assert_called_with_argument):
        mock_bankroll = mock.MagicMock(spec=Bankroll)
        mock_bankroll.amount.return_value = 20

        mock_lucky_dip = mock.MagicMock(spec=LuckyDip)
        mock_lucky_dip.numbers = np.array(numbers)

        lotto = Lottery(mock_bankroll, num_balls=42, num_balls_drawn=5, reward_scheme=[0, 0, 0, 3.5, 200, 80000])
        lotto.draw()
        print("lotto numbers:", lotto.drawn_numbers_)
        lotto.check(mock_lucky_dip)
        lotto.payout()
        # note: we don't care about the value of backroll, only that the appropriate
        #   methods have been called with the appropriate arguments.
        #   It is the responsibility of unit tests for Bankroll object to ensure
        #   the math is done correctly
        mock_bankroll.__iadd__.assert_called_once()
        mock_bankroll.__iadd__.assert_called_with(assert_called_with_argument)

    def test_payout_5_matched(self):
        np.random.seed(2)  # [ 0,  2,  9, 14, 27]
        self.payout([0, 2, 9, 14, 27], 80000)

    def test_payout_4_matched(self):
        np.random.seed(2)  # [ 0,  2,  9, 14, 27]
        self.payout([[0, 2, 9, 14, 32]], 200)

    def test_payout_3_matched(self):
        np.random.seed(2)  # [ 0,  2,  9, 14, 27]
        self.payout([[0, 2, 9, 17, 31]], 3.5)

    def test_payout_2_matched(self):
        np.random.seed(2)  # [ 0,  2,  9, 14, 27]
        self.payout([[0, 2, 11, 16, 30]], 0)

    def test_payout_1_matched(self):
        np.random.seed(2)  # [ 0,  2,  9, 14, 27]
        self.payout([[0, 3, 10, 15, 29]], 0)

    def test_payout_0_matched(self):
        np.random.seed(2)  # [ 0,  2,  9, 14, 27]
        self.payout([[1, 3, 10, 15, 29]], 0)


class IntegrationTests(unittest.TestCase):

    def test_1_game(self):
        np.random.seed(7)  # drawn numbers: [15 17 18 31 34]
        bankroll = Bankroll(20)
        my_numbers = LuckyDip(numbers=[[15, 17, 18, 31, 34]], bankroll=bankroll, cost=0.35, num_balls=5, max_num=42)
        lotto = Lottery(bankroll=bankroll, num_balls=42, num_balls_drawn=5, reward_scheme=[0, 0, 0, 3.5, 200, 80000])
        lotto.draw()
        lotto.check(my_numbers)
        lotto.payout()
        self.assertEqual(bankroll, 80019.65)

    def test_10_lines_in_one_game(self):
        np.random.seed(5)  # drawn numbers: [ 3 23 24 25 28]
        numbers = [
            [3, 23, 24, 25, 28], # + 80000
            [3, 23, 24, 25, 27], # + 200
            [3, 23, 24, 26, 27], # + 3.5
            [3, 23, 23, 26, 27], # + 0
            [3, 22, 23, 26, 27], # + 0
            [2, 22, 23, 26, 27], # + 0

            [15, 17, 18, 31, 34],
            [6, 14, 20, 30, 40],
            [19, 27, 31, 36, 37],
            [16, 22, 25, 37, 39],
        ]
        bankroll = Bankroll(20)
        my_numbers = LuckyDip(numbers=numbers, bankroll=bankroll, cost=0.35, num_balls=5, max_num=42)
        lotto = Lottery(bankroll=bankroll, num_balls=42, num_balls_drawn=5, reward_scheme=[0, 0, 0, 3.5, 200, 80000])

        lotto.draw()
        lotto.check(my_numbers)
        lotto.payout()
        expected_amount = 20 - (0.35*10) + 80000 + 200 + 3.5
        self.assertEqual(bankroll, expected_amount)
