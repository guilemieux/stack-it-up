import functools
import random
from dataclasses import dataclass
from itertools import permutations
from typing import Callable, Generic, TypeVar


Strategy = TypeVar("Strategy")

@dataclass
class TwoPlayerNormalFormGame(Generic[Strategy]):
    strategy_profiles: tuple[set[Strategy], set[Strategy]]
    payoff: Callable[[Strategy, Strategy], float]


class Agent(Generic[Strategy]):
    def __init__(self, game: TwoPlayerNormalFormGame[Strategy], strategy_profile: set[Strategy]):
        self.game = game
        self.strategy_profile = tuple(strategy_profile)
        self._regret_sum: list[float] = [0.0] * len(strategy_profile)
        self._strategy_sum: list[float] = [0.0] * len(strategy_profile)

    def _get_strategy_prob(self) -> list[float]:
        """Return the probability of playing each strategy in the strategy profile."""
        strategy = [max(0, regret) for regret in self._regret_sum]
        strategy_sum = sum(strategy)
        if strategy_sum > 0:
            strategy = [regret / strategy_sum for regret in strategy]
        else:
            strategy = [1 / len(strategy)] * len(strategy)
        return strategy

    def get_strategy(self) -> Strategy:
        """Return a strategy from the strategy profile."""
        strategy = self._get_strategy_prob()
        return random.choices(self.strategy_profile, weights=strategy)[0]

    def update_regret(self, my_strategy: Strategy, opponent_strategy: Strategy):
        payoff = self.game.payoff(my_strategy, opponent_strategy)
        for i, strategy in enumerate(self.strategy_profile):
            self._regret_sum[i] += self.game.payoff(strategy, opponent_strategy) - payoff
        self._strategy_sum = [x + y for x, y in zip(self._strategy_sum, self._get_strategy_prob())]

    def get_average_strategy(self) -> list[tuple[Strategy, float]]:
        """Return the average strategy."""
        return [
            (s, strategy / sum(self._strategy_sum))
            for s, strategy in zip(self.strategy_profile, self._strategy_sum)
        ]


def train(iterations: int, agent1: Agent, agent2: Agent):
    for _ in range(iterations):
        agent1_strategy = agent1.get_strategy()
        agent2_strategy = agent2.get_strategy()
        agent1.update_regret(agent1_strategy, agent2_strategy)
        agent2.update_regret(agent2_strategy, agent1_strategy)


@dataclass(frozen=True)
class Player:
    name: str
    rating: float

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class Roster:
    players: tuple[Player, ...]


def match_prob(player1: Player, player2: Player) -> float:
    diff = player1.rating - player2.rating
    odds = 10 ** (diff / 400)
    prob = odds / (1 + odds)
    return prob


@functools.cache
def meet_outcome_prob(roster1: Roster, roster2: Roster) -> tuple[float, float, float]:
    if len(roster1.players) != len(roster2.players):
        raise ValueError("Rosters must have the same number of players")
    
    team_size = len(roster1.players)
    total_outcomes = 2 ** team_size

    meet_win_prob = 0.0
    meet_loss_prob = 0.0
    meet_tie_prob = 0.0
    for i in range(total_outcomes):
        wins = bin(i).count("1")

        prob = 1.0
        for j in range(team_size):
            prob_roster1_wins_match_j = match_prob(roster1.players[j], roster2.players[j])
            if (i >> j) & 1:
                prob *= prob_roster1_wins_match_j
            else:
                prob *= (1 - prob_roster1_wins_match_j)
        
        if wins > team_size / 2:
            meet_win_prob += prob
        elif wins < team_size / 2:
            meet_loss_prob += prob
        else:
            meet_tie_prob += prob

    assert abs(meet_win_prob + meet_tie_prob + meet_loss_prob - 1) < 1e-6
    return meet_win_prob, meet_tie_prob, meet_loss_prob


def payoff(team1_roster: Roster, team2_roster: Roster) -> float:
    meet_win_prob, _, meet_loss_prob = meet_outcome_prob(team1_roster, team2_roster)        
    return meet_win_prob - meet_loss_prob


college_tennis = TwoPlayerNormalFormGame[Roster](
    strategy_profiles=(
        {
            Roster(players=player_permutation)
            for player_permutation in permutations((
            # Roster(players=(
                Player(name="A1", rating=2000),
                Player(name="A2", rating=1920),
                Player(name="A3", rating=1800),
                Player(name="A4", rating=1700),
                Player(name="A5", rating=1750),
                Player(name="A6", rating=1500),
            ))
        },
        {
            # Roster(players=player_permutation)
            # for player_permutation in permutations((
            Roster(players=(
                Player(name="B1", rating=2300),
                Player(name="B2", rating=2000),
                Player(name="B3", rating=1825),
                Player(name="B4", rating=1800),
                Player(name="B5", rating=1705),
                Player(name="B6", rating=500),
            ))
            # ])
        },
    ),
    payoff=payoff,
)

mcgill = Agent[Roster](game=college_tennis, strategy_profile=college_tennis.strategy_profiles[0])
udem = Agent[Roster](game=college_tennis, strategy_profile=college_tennis.strategy_profiles[1])

if __name__ == "__main__":
    train(10000, mcgill, udem)
    mcgill_average_strategy = sorted(mcgill.get_average_strategy(), key=lambda x: x[1], reverse=True)
    udem_average_strategy = sorted(udem.get_average_strategy(), key=lambda x: x[1], reverse=True)
    for roster, prob in mcgill_average_strategy:
        if prob > 0.01:
            print(f"{roster} {prob * 100:.2f}%")
            print(meet_outcome_prob(roster, udem_average_strategy[0][0]))

    print()
    for roster, prob in udem_average_strategy:
        if prob > 0.0001:
            print(f"{roster} {prob * 100:.2f}%")
