from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]
    
    def accept(self, word: str) -> bool:
    # simulate the dfa on the given word. return True if the dfa accepts the word, False otherwise
        current_state = self.q0
        for symbol in word:
            # check if the transition for the current symbol exists
            if (current_state, symbol) in self.d:
                next_state = self.d[(current_state, symbol)]
                current_state = next_state
            else:
                # if the transition does not exist, the word is not accepted
                return False
        # check if the final state is reached
        return current_state in self.F


    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        pass
