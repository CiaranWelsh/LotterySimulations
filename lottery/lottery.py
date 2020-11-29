from __future__ import annotations

import numpy as np
import typing
from numbers import Number


class Lottery:

    def __init__(self, bankroll, num_balls: int, num_balls_drawn: int = 5,
                 reward_scheme=None):
        """

        :param num_balls: maximum number in the lotto draw
        :param num_balls_drawn: number of balls to draw
        """
        if reward_scheme is None:
            reward_scheme = [0, 0, 3.5, 200, 80000]
        self._num_balls = num_balls
        self._numbers = np.arange(1, self._num_balls + 1)
        self._draws = num_balls_drawn
        self.bankroll = bankroll
        self.reward_scheme = reward_scheme
        if len(self.reward_scheme) != num_balls_drawn + 1:
            raise ValueError("Configuration error: length of reward scheme "
                             "array should equal the num_balls_draws plus 1 "
                             "(for the 0 balls matched case)")

        self.drawn_numbers_ = None  # need to draw() before we get result
        self.sim_results_ = None # need to check() before we can value here

    def draw(self):
        self.drawn_numbers_ = np.sort(np.random.choice(self._numbers, size=self._draws, replace=False))
        return self.drawn_numbers_

    def check(self, numbers: typing.Union[np.ndarray, LuckyDip]):
        if self.drawn_numbers_ is None:
            raise ValueError("No lotto drawn yet")

        if isinstance(numbers, LuckyDip):
            # converge to np.array
            numbers = numbers.numbers

        res = np.zeros(numbers.shape[0])
        for i in range(numbers.shape[0]):
            diff = np.intersect1d(numbers[i], self.drawn_numbers_)
            res[i] = len(diff)
        self.sim_results_ = res.astype(np.int64)
        return self.sim_results_

    def payout(self, numbers_matched=None, print_out_winners=False):
        """
        array of integers indicating how many numbers matched.
        If None, default to output of check()
        :param numbers_matched:
        :return:
        """
        if numbers_matched is None:
            numbers_matched = self.sim_results_

        for i in numbers_matched:
            if print_out_winners:
                if i >= 3:
                    print(f"Matched {i} numbers, you win {self.reward_scheme[i]} pounds.")
            self.bankroll += self.reward_scheme[i]
        return self.bankroll

    def __str__(self):
        return f"Lottery({str(self.drawn_numbers_)})"


class LuckyDip:
    """
    A single lotto lucky dip
    """

    def __init__(self, bankroll, cost, num_draws=None,  num_balls=5, max_num=42, numbers=None):
        self.bankroll = bankroll
        self._num_draws = num_draws
        self._num_balls = num_balls
        self._cost = cost
        self._max_num = max_num
        self._numbers = numbers

        if numbers is None:
            if self._num_draws is None:
                raise ValueError("Need to give argument to either num_draws or numbers")
            if self._num_draws is not None and self._numbers is not None:
                raise ValueError("Need to give argument to either num_draws or numbers (not both)")

            self._numbers = np.zeros((num_draws, num_balls))
            for i in np.arange(num_draws):
                self._numbers[i] = np.sort(np.random.choice(self._max_num, size=self._num_balls, replace=False))
                self.bankroll -= self._cost
        else:
            if isinstance(numbers, LuckyDip):
                self._numbers = numbers.numbers
            elif isinstance(numbers, np.ndarray):
                self._numbers = numbers
            elif isinstance(numbers, list):
                self._numbers = np.array(numbers)
            else:
                raise ValueError(f"unexpected type: {type(numbers)}")
            self._num_draws = self._numbers.shape[0]
            self.bankroll -= (self._cost * self._num_draws)

        self._numbers = self._numbers.astype(np.int32)

    @property
    def numbers(self):
        return self._numbers

    def __str__(self):
        return str(self.numbers)

    def __repr__(self):
        return self.__str__()


class Bankroll:

    def __init__(self, amount):
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    def __isub__(self, other):
        if other > self._amount:
            raise ValueError(f"Not enough money. You have {self._amount} left "
                             f"but are trying to remove {other}")
        self._amount -= other
        return self

    def __iadd__(self, other):
        self._amount += other
        return self

    def __eq__(self, other):
        if isinstance(other, Number):
            return self._amount == other
        elif isinstance(other, Bankroll):
            return self._amount == other._amount
        else:
            raise ValueError("don't know how to compare "
                             f"Bankroll with objects of type {other} ")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Number):
            return self._amount < other
        elif isinstance(other, Bankroll):
            return self._amount < other._amount
        else:
            raise ValueError("don't know how to compare "
                             f"Bankroll with objects of type {other} ")

    def __gt__(self, other):
        if isinstance(other, Number):
            return self._amount > other
        elif isinstance(other, Bankroll):
            return self._amount > other._amount
        else:
            raise ValueError("don't know how to compare "
                             f"Bankroll with objects of type {other} ")

    def __le__(self, other):
        if isinstance(other, Number):
            return self._amount <= other
        elif isinstance(other, Bankroll):
            return self._amount <= other._amount
        else:
            raise ValueError("don't know how to compare "
                             f"Bankroll with objects of type {other} ")

    def __ge__(self, other):
        if isinstance(other, Number):
            return self._amount >= other
        elif isinstance(other, Bankroll):
            return self._amount >= other._amount
        else:
            raise ValueError("don't know how to compare "
                             f"Bankroll with objects of type {other} ")

    def __str__(self):
        return f"Bankroll(amount={self._amount})"

    def __repr__(self):
        return self.__str__()


class Simulations:
    """deprecated simulations"""

    @staticmethod
    def sim1():
        """
        effect of number of luck dips on try's until jackpot reached
        :return:
        """
        bankroll = Bankroll(20)
        lotto = Lottery(bankroll, 42, num_balls_drawn=5, reward_scheme=[0, 0, 0, 3.5, 200, 80000])
        my_numbers = LuckyDip(num_draws=12, bankroll=bankroll, cost=0.35, num_balls=5, max_num=42)
        done = False
        count = 0
        while not done:
            count += 1
            lotto.draw()
            res = lotto.check(my_numbers.numbers)
            if 5 in res:
                done = True
        print(count)

    @staticmethod
    def sim2():
        """
        How many days do I need to buy x tickets to win in 1 year?

        Then there's the money side of things: implement the reward
        :return:
        """
        my_numbers = [[2, 9, 15, 36, 41],
                      [3, 8, 19, 24, 29],
                      [15, 18, 27, 29, 31],
                      [0, 1, 9, 21, 40],
                      [9, 26, 27, 31, 38],
                      [5, 33, 36, 39, 40],
                      [3, 5, 7, 30, 36],
                      [5, 11, 22, 29, 35],
                      [0, 1, 31, 35, 40],
                      [4, 5, 8, 25, 41],
                      [3, 13, 37, 38, 41],
                      [0, 18, 20, 25, 36]]
        my_numbers = np.array(my_numbers)
        bankroll = Bankroll(70)

        days = 30  # *0.35*num_draws = cost for month
        for day in np.arange(days):
            my_numbers = LuckyDip(num_draws=24, numbers=my_numbers, bankroll=bankroll, cost=0.35, num_balls=5,
                                  max_num=42)
            lotto = Lottery(bankroll, 42, num_balls_drawn=5, reward_scheme=[0, 0, 0, 3.5, 200, 80000])
            lotto.draw()
            results = lotto.check(my_numbers.numbers)
            lotto.payout(results)
            print(f"Day {day}: bankroll: {bankroll}")


if __name__ == "__main__":
    # reinforcement learning???

    Simulations.sim2()
