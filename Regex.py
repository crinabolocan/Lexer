from .NFA import NFA


class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')


# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex

class Character(Regex):
    def __init__(self, character: str):
        # iau caracterul
        self.character = character

    def thompson(self) -> NFA[int]:
        # construiesc un NFA care accepta un singur caracter
        nfa = NFA({self.character}, {0, 1}, 0, {(0, self.character): {1}}, {1})
        return nfa


class Concatenation(Regex):
    def __init__(self, first: Regex, second: Regex):
        self.first = first
        self.second = second

    def thompson(self) -> NFA[int]:
        first_nfa = self.first.thompson()
        second_nfa = self.second.thompson()

        # Ajustează stările pentru a evita suprapunerea
        offset = max(first_nfa.K) + 1  # offset-ul este maximul dintre starile primului NFA
        second_states = {state + offset for state in
                         second_nfa.K}  # stările celui de-al doilea NFA sunt deplasate cu offset-ul
        second_transitions = {((state + offset if state in second_nfa.K else state), char):
                                  {s + offset for s in states} for (state, char), states in second_nfa.d.items()}
        # tranzitiile celui de-al doilea NFA sunt deplasate cu offset-ul

        # Combina stările și tranzitiile pentru a crea un NFA concatenat
        states = first_nfa.K.union(second_states)  # stările sunt stările primului NFA și stările celui de-al doilea NFA
        transitions = first_nfa.d.copy()  # tranzitiile sunt tranzitiile primului NFA
        transitions.update(second_transitions)  # adaugam tranzitiile celui de-al doilea NFA

        # Adaugă tranzitii epsilon de la primul NFA la al doilea NFA
        for final_state in first_nfa.F:
            transitions.setdefault((final_state, ''), set()).add(second_nfa.q0 + offset)

        # Stările finale ale NFA-ului combinat sunt stările finale ale celui de-al doilea NFA
        final_states = {state + offset for state in second_nfa.F}
        return NFA(first_nfa.S.union(second_nfa.S), states, first_nfa.q0, transitions, final_states)


class Union(Regex):
    def __init__(self, first: Regex, second: Regex):
        self.first = first
        self.second = second

    def thompson(self) -> NFA[int]:
        first_nfa = self.first.thompson()
        second_nfa = self.second.thompson()

        # Crează o nouă stare de start
        new_start_state = max(first_nfa.K.union(second_nfa.K)) + 1

        # Ajustează stările din ambele NFA-uri pentru a evita suprapunerea
        offset_first = new_start_state + 1
        offset_second = offset_first + max(first_nfa.K) + 1

        first_states = {state + offset_first for state in first_nfa.K}  # stările primului NFA sunt deplasate cu
        # offset-ul
        second_states = {state + offset_second for state in second_nfa.K}  # stările celui de-al doilea NFA sunt
        # deplasate cu offset-ul

        # Construiește tranzițiile ajustate pentru ambele NFA-uri
        first_transitions = {((state + offset_first), char): {s + offset_first for s in states}
                             for (state, char), states in first_nfa.d.items()}
        # tranzitiile primului NFA sunt deplasate cu offset-ul
        second_transitions = {((state + offset_second), char): {s + offset_second for s in states}
                              for (state, char), states in second_nfa.d.items()}
        # tranzitiile celui de-al doilea NFA sunt deplasate cu offset-ul

        # Tranzitii epsilon de la noua stare de start la starile de start ale celor doua NFA-uri
        transitions = {**first_transitions, **second_transitions,
                       (new_start_state, ''): {first_nfa.q0 + offset_first, second_nfa.q0 + offset_second}}

        # Combina stările și seturile de stări finale
        states = first_states.union(second_states).union({new_start_state})
        final_states = {state + offset_first for state in first_nfa.F}.union(
            {state + offset_second for state in second_nfa.F})

        # Alfabetul combinat
        alphabet = first_nfa.S.union(second_nfa.S)

        return NFA(alphabet, states, new_start_state, transitions, final_states)


class KleeneStar(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        inner_nfa = self.regex.thompson()

        # Crează noi stări pentru NFA-ul Kleene Star
        start_state = max(inner_nfa.K) + 1  # starea de start este maximul dintre starile NFA-ului
        final_state = start_state + 1  # starea finala este starea de start + 1

        # Stările pentru NFA-ul Kleene Star
        states = inner_nfa.K.union({start_state, final_state})

        # Tranzițiile pentru NFA-ul Kleene Star
        transitions = inner_nfa.d.copy()

        # Adaugă tranziții epsilon pentru a permite repetiții și pentru a permite 'zero' instanțe
        transitions[(start_state, '')] = {inner_nfa.q0, final_state}
        for final_state_inner in inner_nfa.F:
            transitions.setdefault((final_state_inner, ''), set()).add(inner_nfa.q0)
            transitions.setdefault((final_state_inner, ''), set()).add(final_state)

        # Setul de stări finale conține doar noua stare finală
        final_states = {final_state}

        return NFA(inner_nfa.S, states, start_state, transitions, final_states)


class Optional(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        inner_nfa = self.regex.thompson()

        # Crează noi stări pentru NFA-ul Optional
        start_state = max(inner_nfa.K) + 1  # starea de start este maximul dintre starile NFA-ului
        final_state = start_state + 1  # starea finala este starea de start + 1

        # Stările pentru NFA-ul Optional
        states = inner_nfa.K.union({start_state, final_state})

        # Tranzițiile pentru NFA-ul Optional
        transitions = inner_nfa.d.copy()  # tranzitiile sunt tranzitiile NFA-ului

        # Adaugă tranziții epsilon pentru a permite 'zero' sau 'una' instanță
        transitions[(start_state, '')] = {inner_nfa.q0, final_state}
        for final_state_inner in inner_nfa.F:
            transitions.setdefault((final_state_inner, ''), set()).add(final_state)

        # Setul de stări finale conține doar noua stare finală
        final_states = {final_state}

        return NFA(inner_nfa.S, states, start_state, transitions, final_states)


class Plus(Regex):
    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        # Crează NFA-ul original
        original_nfa = self.regex.thompson()

        # Crează NFA-ul cu Kleene Star aplicat pe expresia regulată
        kleene_star_nfa = KleeneStar(self.regex).thompson()

        # Offset pentru stările din kleene_star_nfa pentru a evita suprapunerea
        offset = max(original_nfa.K) + 1
        adjusted_states = {state + offset for state in kleene_star_nfa.K}
        adjusted_transitions = {}
        for (state, symbol), next_states in kleene_star_nfa.d.items():
            adjusted_next_states = {s + offset if s in kleene_star_nfa.K else s for s in next_states}
            adjusted_transitions[
                (state + offset if state in kleene_star_nfa.K else state, symbol)] = adjusted_next_states

        # Combina stările și tranzitiile NFA-urilor
        states = original_nfa.K.union(adjusted_states)
        transitions = original_nfa.d.copy()
        transitions.update(adjusted_transitions)

        # Adaugă tranziții epsilon de la stările finale ale original_nfa la starea de start a kleene_star_nfa
        for final_state in original_nfa.F:
            transitions.setdefault((final_state, ''), set()).add(kleene_star_nfa.q0 + offset)

        # Stările finale ale NFA-ului combinat sunt stările finale ale kleene_star_nfa
        final_states = {state + offset for state in kleene_star_nfa.F}

        return NFA(original_nfa.S.union(kleene_star_nfa.S), states, original_nfa.q0, transitions, final_states)


class Literal(Regex):
    def __init__(self, literal: str):
        self.literal = literal

    def thompson(self) -> NFA[int]:
        start_state = 0  # starea de start este 0
        final_state = len(self.literal)  # starea finala este lungimea literalului

        states = set(range(final_state + 1))  # starile sunt de la 0 la lungimea literalului
        transitions = {}  # tranzitiile

        current_state = start_state  # starea curenta este starea de start
        for char in self.literal:  # pentru fiecare caracter din literal
            next_state = current_state + 1  # starea urmatoare este starea curenta + 1
            transitions[(current_state, char)] = {next_state}  # adaugam tranzitia
            current_state = next_state  # starea curenta devine starea urmatoare

        return NFA(set(self.literal), states, start_state, transitions, {final_state})


class CharacterSet(Regex):
    def __init__(self, start_char: str, end_char: str):
        self.start_char = start_char
        self.end_char = end_char

    def thompson(self) -> NFA[int]:
        start_state = 0  # starea de start este 0
        final_state = 1  # starea finala este 1
        transitions = {}  # tranzitiile

        for char in range(ord(self.start_char), ord(self.end_char) + 1):
            transitions[(start_state, chr(char))] = {final_state}  # adaugam tranzitia

        return NFA(set(chr(c) for c in range(ord(self.start_char), ord(self.end_char) + 1)),
                   {start_state, final_state}, start_state, transitions, {final_state})


class Reject(Regex):
    def __init__(self):
        pass

    def thompson(self) -> NFA[int]:
        # NFA care nu acceptă nicio intrare
        return NFA(set(), {0}, 0, {}, set())


def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string

    # you can define additional classes and functions to help with the parsing process

    # the checker will call this function, then the thompson method of the generated object. the resulting NFA's
    # behaviour will be checked using your implementation form stage 1
    if not regex:
        return Reject()
    stack = []  # stiva
    i = 0

    while i < len(regex):
        char = regex[i]  # luam caracterul curent

        if char == ' ':  # daca e spatiu
            i += 1
            continue

        if char == '\n':  # daca e newline
            stack.append(Literal('\n'))
            i += 1
            continue

        if char == '|':  # daca e |
            i += 1
            first = parse_regex(regex[:i - 1])
            second = parse_regex(regex[i:])
            return Union(first, second)

        elif char == '(':  # daca e (
            count = 1
            j = i + 1
            while j < len(regex) and count > 0:
                if regex[j] == '(':
                    count += 1
                elif regex[j] == ')':
                    count -= 1
                j += 1

            inner_expr = parse_regex(regex[i + 1:j - 1])  # parsam expresia dintre paranteze

            if j < len(regex) and regex[j] == '*':  # daca e *
                inner_expr = KleeneStar(inner_expr)
                j += 1

            elif j < len(regex) and regex[j] == '?':  # daca e ?
                inner_expr = Optional(inner_expr)
                j += 1

            elif j < len(regex) and regex[j] == '+':  # daca e +
                inner_expr = Plus(inner_expr)
                j += 1

            stack.append(inner_expr)
            i = j
            continue

        elif char == '[':  # daca e [
            j = i + 1
            while j < len(regex) and regex[j] != ']':
                j += 1
            if j < len(regex) and regex[j] == ']':
                char_range = regex[i + 1:j].split('-')
                if len(char_range) == 2:
                    char_set = CharacterSet(char_range[0], char_range[1])
                    i = j + 1

                    if i < len(regex) and regex[i] == '*':
                        char_set = KleeneStar(char_set)
                        i += 1

                    if i < len(regex) and regex[i] == '?':
                        char_set = Optional(char_set)
                        i += 1

                    if i < len(regex) and regex[i] == '+':
                        char_set = Plus(char_set)
                        i += 1

                    stack.append(char_set)

        elif char == '\\':  # daca e \
            i += 1
            if i < len(regex):
                next_char = regex[i]
                if next_char in ' |*+?()[]':
                    stack.append(Character(next_char))
                elif next_char == ' ':
                    stack.append(Character(' '))
                elif next_char == '\n':
                    stack.append(Character('\n'))
                elif next_char in '+-':
                    stack.append(Literal(next_char))
                else:
                    stack.append(Character(next_char))
                i += 1
                continue

        elif i + 1 < len(regex) and regex[i + 1] in '*?+':  # daca e * sau ? sau +
            op = regex[i + 1]
            if op == '*':
                stack.append(KleeneStar(Character(char)))
            elif op == '?':
                stack.append(Optional(Character(char)))
            elif op == '+':
                stack.append(Plus(Character(char)))
            i += 1

        elif char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789':  # daca e litera
            stack.append(Character(char))
            i += 1

        elif char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789:.@':
            start = i
            while i < len(regex) and regex[i] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789:.@':
                i += 1
            literal = regex[start:i]
            stack.append(Literal(literal))
            continue

        elif char in '-._':  # daca e -._
            stack.append(Literal(char))
            i += 1
            continue

        else:
            i += 1

    while len(stack) > 1:
        second = stack.pop()
        first = stack.pop()
        stack.append(Concatenation(first, second))  # concatenam tot ce a ramas in stiva

    return stack.pop() if stack else None
