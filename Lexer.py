from .Regex import parse_regex
from .NFA import NFA
class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        # prepare the setup for the nfa
        S = set()
        K = set()
        q0 = 0
        d = {}
        F = set()
        q0s = set()
        self.tokens = {}
        # create the nfa
        for regex in spec:
            nfa = parse_regex(regex[1]).thompson()
            q0s.add(nfa.q0)
            S.update(nfa.S)
            K.update(nfa.K)
            K.add(nfa.q0)
            d.update(nfa.d)
            F.update(nfa.F)
            self.tokens[frozenset(nfa.F)] = regex[0]
        # put a new initial state that has alternatives to each old initial states
        d[(q0, '')] = q0s
            
        self.nfa = NFA(S, K, q0, d, F)
        # create the dfa
        self.dfa = self.nfa.subset_construction()

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)
        # if an error occurs and the lexing fails, you should return none # todo: maybe add error messages as a task
        final_res = []
        accepted = ''
        good_token = ('', '')
        current_state = self.dfa.q0
        index = 0
        found = False
        consumed = ''
        which_tokens = []
        new_line = 0
        lines = 0
        # consume the word
        while index < len(word):
            symbol = word[index]
            # check if the symbol is in dfa
            if not symbol in self.dfa.S:
                final_res.clear()
                final_res.append(('', f'No viable alternative at character {index - new_line}, line {lines}'))
                break
            # check if current state and symbol does not go to a SINK STATE
            if (current_state, symbol) in self.dfa.d and self.dfa.d[(current_state, symbol)] != frozenset():
                # consume
                next_state = self.dfa.d[(current_state, symbol)]
                current_state = next_state
                # update the accepted characters so far
                accepted += symbol                                                                                                                                                                                                                                                                                                                                      
                # find the current token that matches the accepted
                for token in self.tokens:
                    for elem in token:
                        if elem in current_state:
                            good_token = (self.tokens[token], accepted)
                            which_tokens.append(good_token)
                            found = True
                            break
                    if found:
                        found = False
                        break               
                index += 1
                # update on which line the cursor is
                if symbol == '\n':
                    new_line = index
                    lines += 1
                # check if the whole word has matches
                # if not the whole word is not accepted
                if index == len(word):
                    if not which_tokens:
                        final_res.clear()
                        final_res.append(('', f'No viable alternative at character EOF, line {lines}'))
                        break
                    final_res.append(good_token) 
            else:
                # if we reach a bad state we find the longest prefix that accepts it and try again
                # if there are no tokens then the word is not accepted
                if not which_tokens:
                    final_res.clear()
                    final_res.append(('', f'No viable alternative at character {index - new_line}, line {lines}'))
                    break
                # if there are, we put the best token in the result
                final_res.append(good_token)
                # reset and start a new consumption
                current_state = self.dfa.q0
                consumed += good_token[1]
                accepted = ''
                index = len(consumed)
                which_tokens.clear()
        return final_res