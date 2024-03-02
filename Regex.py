from .NFA import NFA
from dataclasses import dataclass
from .RegToNfaUtils import process_regex, isoperation

class Regex:
    # static variable for naming the states
    name_state = 0
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

def parse_regex(regex: str) -> Regex:
    """
        This function creates a Regex object which calls the Thompson algorithm
    in order to create the final NFA of the regex
    Args:
        regex as string

    Returns:
        a Regex object
    """
    # create a Regex object by parsing the string
    queue = process_regex(regex)
    if not queue:
        return Character('')
    # an intermediate list containing different languages on which
    # an operation will be applied
    nfas = []
    for character in queue:
        if character[0] == '[':
            # syntactic sugar case
            nfas.append(Sugar(character))
        elif character[0] == '\\':
            # special symbols case
            nfas.append(Character(character[1]))
        elif not isoperation(character):
            nfas.append(Character(character))
        elif character == '|':
            second_nfa = nfas.pop()
            first_nfa = nfas.pop()
            nfas.append(Union(first_nfa.thompson(), second_nfa.thompson()))
        elif character == '*':
            nfa = nfas.pop()
            nfas.append(Kleene(nfa.thompson()))
        elif character == '&':
            second_nfa = nfas.pop()
            first_nfa = nfas.pop()
            nfas.append(Concat(first_nfa.thompson(), second_nfa.thompson()))
        elif character == '+':
            # plus sign means at least once
            # this can be seen as a concatenation
            # between the languange itself and
            # kleene star applied on that language
            nfa = nfas.pop()
            nfas.append(Concat(nfa.thompson(), Kleene(nfa.thompson()).thompson()))
        elif character == '?':
            nfa = nfas.pop()
            nfas.append(Optional(nfa.thompson()))
    return nfas.pop()

@dataclass
class Character(Regex):
    character: chr
    def thompson(self) -> NFA[int]:
        """
            Creates the NFA object for a Character object using Thompson
        algorithm
        Returns:
            the NFA
        """
        symbols = set()
        kStates = set()
        q0State = -1
        finalStates = set()
        d = {}
        symbols.add(self.character)
        Regex.name_state += 1
        first_state = Regex.name_state
        kStates.add(first_state)
        Regex.name_state += 1
        second_state = Regex.name_state
        kStates.add(second_state)
        q0State = first_state
        finalStates.add(second_state)
        d[(first_state, self.character)] = set([second_state])
        return NFA(symbols, kStates, q0State, d, finalStates)
    
@dataclass
class Concat(Regex):
    first_concat: NFA[int]
    second_concat: NFA[int]
    
    def thompson(self) -> NFA[int]:
        """
            Creates the NFA object for a Concatenation between two languages 
        using Thompson algorithm
        Returns:
            the NFA
        """
        symbols = set().union(self.first_concat.S, self.second_concat.S)
        kStates = set().union(self.first_concat.K, self.second_concat.K)
        q0State = self.first_concat.q0
        finalStates = set(self.second_concat.F)
        d = {}
        d.update(self.first_concat.d)
        d.update(self.second_concat.d)
        for final in self.first_concat.F:
            d[(final, '')] = set(([self.second_concat.q0]))
        return NFA(symbols, kStates, q0State, d, finalStates)
    
@dataclass
class Union(Regex):
    first_union: NFA[int]
    second_union: NFA[int]
    
    def thompson(self) -> NFA[int]:
        """
            Creates the NFA object for a Union between two languages 
        using Thompson algorithm
        Returns:
            the NFA
        """
        symbols = set().union(self.first_union.S, self.second_union.S)
        kStates = set().union(self.first_union.K, self.second_union.K)
        finalStates = set(self.second_union.F)
        d = {}
        d.update(self.first_union.d)
        d.update(self.second_union.d)
        Regex.name_state += 1
        first_state = Regex.name_state
        kStates.add(first_state)
        Regex.name_state += 1
        second_state = Regex.name_state
        kStates.add(second_state)
        q0State = first_state
        finalStates.add(second_state)
        for final in self.first_union.F:
            d[(final, '')] = set([second_state])
        for final in self.second_union.F:
            d[(final, '')] = set([second_state])
        d[(first_state, '')] = set([self.first_union.q0])
        d[(first_state, '')].add(self.second_union.q0)
        return NFA(symbols, kStates, q0State, d, finalStates)

@dataclass    
class Kleene(Regex):
    nfa: NFA[int]
    
    def thompson(self) -> NFA[int]:
        """
            Creates the NFA object for a language on which is applied Kleene Star 
        using Thompson algorithm
        Returns:
            the NFA
        """
        symbols = set().union(self.nfa.S)
        kStates = set().union(self.nfa.K)
        finalStates = set()
        d = {}
        d.update(self.nfa.d)
        Regex.name_state += 1
        first_state = Regex.name_state
        kStates.add(first_state)
        Regex.name_state += 1
        second_state = Regex.name_state
        kStates.add(second_state)
        q0State = first_state
        finalStates.add(second_state)
        for final in self.nfa.F:
            d[(final, '')] = set([self.nfa.q0])
            d[(final, '')].add(second_state)
        d[(first_state, '')] = set([self.nfa.q0])
        d[(first_state, '')].add(second_state)
        return NFA(symbols, kStates, q0State, d, finalStates)

@dataclass
class Optional(Regex):
    nfa: NFA[int]
    
    def thompson(self) -> NFA[int]:
        """
            Creates the NFA object for a language on which is applied *Optional 
        using Thompson algorithm
        
        *Optional = Once Or Never
        
        Returns:
            the NFA
        """
        symbols = set().union(self.nfa.S)
        kStates = set().union(self.nfa.K)
        finalStates = set(self.nfa.F)
        d = {}
        d.update(self.nfa.d)
        Regex.name_state += 1
        first_state = Regex.name_state
        kStates.add(first_state)
        Regex.name_state += 1
        second_state = Regex.name_state
        kStates.add(second_state)
        q0State = first_state
        finalStates.add(second_state)
        for final in self.nfa.F:
            d[(final, '')] = set([second_state])
        d[(first_state, '')] = set([self.nfa.q0])
        d[(first_state, '')].add(second_state)
        return NFA(symbols, kStates, q0State, d, finalStates)

@dataclass    
class Sugar(Regex):
    sugar: str
    
    def thompson(self) -> NFA[int]:
        """
            Creates the NFA object for a syntactic sugar language
        using Thompson algorithm
        
        Returns:
            the NFA
        """
        symbols = set()
        kStates = set()
        q0State = -1
        finalStates = set()
        d = {}
        Regex.name_state += 1
        first_state = Regex.name_state
        kStates.add(first_state)
        Regex.name_state += 1
        second_state = Regex.name_state
        kStates.add(second_state)
        finalStates.add(second_state)
        q0State = first_state
        start = self.sugar[1]
        end = self.sugar[3]
        character = start
        # create transitions for all characters from the syntactic sugar
        while character <= end:
            symbols.add(character)
            d[(first_state, character)] = set([second_state])
            character = chr(ord(character) + 1)
        return NFA(symbols, kStates, q0State, d, finalStates)
