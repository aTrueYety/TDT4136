import math

State = tuple[int, int]  # Tuple of player ( whose turn it is),
# and the number to be decreased
Action = str  # Decrement ( number <- number -1) or halve ( number <- number / 2)


class Game:

    def __init__(self, N: int):
        self.N = N

    def initial_state(self) -> State:
        return 0, self.N

    def to_move(self, state: State) -> int:
        player, _ = state
        return player

    def actions(self, state: State) -> list[Action]:
        return ['--', '/2 ']

    def result(self, state: State, action: Action) -> State:
        _, number = state
        if action == '--':
            return (self.to_move(state) + 1) % 2, number - 1
        else:
            return (self.to_move(state) +
                    1) % 2, number // 2  # Floored division

    def is_terminal(self, state: State) -> bool:
        _, number = state
        return number == 0

    def utility(self, state: State, player: int) -> float:
        assert self.is_terminal(state)
        return 1 if self.to_move(state) == player else -1

    def print(self, state: State):
        _, number = state
        print(f'The number is { number } and ', end='')
        if self.is_terminal(state):
            if self.utility(state, 0) > 0:
                print(f'P1 won ')
            else:
                print(f'P2 won ')
        else:
            print(f'it is P{ self.to_move( state )+1}\' s turn ')


def minimax_search(game: Game, state: State) -> Action | None:
    player = game.to_move(state)  # the player to move is MAX

    def max_value(game: Game, state: State) -> tuple[float, Action | None]:
      if game.is_terminal(state):
          return game.utility(state, player), None
      v, best_action = -math.inf, None
      for action in game.actions(state):
          v2, _ = min_value(game, game.result(state, action))
          if v2 > v:
              v, best_action = v2, action
      return v, best_action
    
    def min_value(game: Game, state: State) -> tuple[float, Action | None]:
      if game.is_terminal(state):
          return game.utility(state, player), None
      v, best_action = math.inf, None
      for action in game.actions(state):
          v2, _ = max_value(game, game.result(state, action))
          if v2 < v:
              v, best_action = v2, action
      return v, best_action

    _, action = max_value(game, state)
    return action


game = Game(5)
state = game.initial_state()
game.print(state)
while not game.is_terminal(state):
    player = game.to_move(state)
    action = minimax_search(game, state)  # The player whose turn it is
    # is the MAX player
    print(f'P{ player +1}\'s action : { action }')
    assert action is not None
    state = game.result(state, action)
    game.print(state)

# Expected output :
# The number is 5 and it is P1 ’s turn
# P1 ’s action : --
# The number is 4 and it is P2 ’s turn
# P2 ’s action : --
# The number is 3 and it is P1 ’s turn
# P1 ’s action : /2
# The number is 1 and it is P2 ’s turn
# P2 ’s action : --
# The number is 0 and P1 won
