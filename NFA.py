from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]
    
    
    def epsilon_closure_aux(self, epsilon_closure: set[STATE], state: STATE) -> set[STATE]:
        # verify if there is an epsilon transition from state
        if (state, '') in self.d:
            # add the state if it has not been added yet
            if state not in epsilon_closure:
                epsilon_closure.add(state)
            # add all epsilon transitions from state
            for next_state in self.d[(state, '')]:
                if next_state in epsilon_closure:
                    continue
                epsilon_closure.add(next_state)
                # update the set[STATE] with other possible epsilon transition from next_state
                epsilon_closure.update(self.epsilon_closure_aux(epsilon_closure, next_state))
        return epsilon_closure
    
    def epsilon_closure(self, state: STATE) -> set[STATE]:
        epsilon_closures = set()
        return self.epsilon_closure_aux(epsilon_closures, state)

    # Convert this NFA to a DFA using the subset construction algorithm
    def subset_construction(self) -> DFA[frozenset[STATE]]:
        
        # creating the initial state of the DFA
        dfa_q0_aux = self.epsilon_closure(self.q0)
        q0_aux = frozenset()
        # if the outcome is not a set of states
        if dfa_q0_aux == set():
            # epsilon closure returned nothing, so initial state from the NFA 
            # is the same in the DFA
            q0_aux = frozenset([self.q0])
        else:
            # create initial state for DFA
            q0_aux = frozenset(dfa_q0_aux)
        
        # initialize the list of the DFA states
        states_list = []
        # initialize the list of the DFA final states
        final_states = []
        # initialize a list of DFA states that have not been treated 
        list_aux = []
        # initialize the dictionary of the DFA 
        new_dict = dict()
        # add the initial state of the DFA
        list_aux.append(q0_aux)

        while list_aux:
            state = list_aux.pop()
            # check if the state has already been treated
            if state in states_list:
                continue
            # add the state to the DFA's list of states
            states_list.append(state)
            # iterate through each symbol of the DFA
            for symbol in self.S:
                new_state = []
                # check if the state that is being treated
                # has final states from the NFA
                # if it does, add the state in the list of the DFA final states
                final_states.extend([frozenset(state)
                                     for s in state
                                     if s in self.F])
                # iterate through each state from the DFA state
                # check the NFA dictionary for new states ready
                # for the DFA  
                for old_state in state:
                    if (old_state, symbol) in self.d:
                        # iterate through each state
                        # that an old state (called old_next_state) has with the certain symbol
                        # create a frozenset of the old_next_state and other states
                        # that come from the epsilon closure applied on the old_next_state
                        # if the old_next_state has no epsilon transitions
                        # just add the old_next_state
                        # extend the new_state
                        new_state.extend([frozenset(self.epsilon_closure(old_next_state))
                                          if frozenset(self.epsilon_closure(old_next_state)) != frozenset()
                                          else frozenset([old_next_state])
                                          for old_next_state in self.d[(old_state, symbol)]])
                # merge all the frozensets from the list into a single frozenset
                # so it creates the new state for the DFA
                created_state = frozenset().union(*new_state)
                # add the created state to be treated next
                list_aux.append(created_state)
                # update the DFA dictionary for the state that has been treated
                # with the transition to created state with the certain symbol
                new_dict[(frozenset(state), symbol)] = created_state
        return DFA(self.S, frozenset(states_list), q0_aux, new_dict, frozenset(final_states))


    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        pass