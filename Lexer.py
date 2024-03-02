from src.NFA import NFA
from src.Regex import parse_regex


class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        self.dfa = self.build_dfa(spec)  # am apeleat metoda build_dfa care imi creeaza un dfa pe baza specificatiei

    @staticmethod
    def build_dfa(spec):
        # initializari
        combined_nfa_states = {0}
        combined_nfa_transitions = {}
        combined_nfa_start_state = 0
        combined_nfa_final_states = {}
        alfabet = set()
        offset = 1

        for token, regex in spec:
            # pentru fiecare token si regex din specificatie
            regex_object = parse_regex(regex)
            nfa = regex_object.thompson()
            # am creat un nfa pe baza regex-ului
            alfabet.update(nfa.S)
            adjusted_states = {state + offset for state in nfa.K}  # am ajustat starile cu un offset pentru a nu avea
            # conflicte
            combined_nfa_states.update(adjusted_states)

            for (state, char), next_states in nfa.d.items():
                combined_nfa_transitions[(state + offset, char)] = {s + offset for s in next_states}
            # am adaugat tranzitiile in combined_nfa_transitions

            combined_nfa_transitions.setdefault((combined_nfa_start_state, ''), set()).add(nfa.q0 + offset)

            for final_state in nfa.F:
                combined_nfa_final_states[final_state + offset] = token
            # am adaugat starile finale in combined_nfa_final_states

            offset += max(nfa.K) + 1

        combined_nfa = NFA(alfabet, combined_nfa_states, combined_nfa_start_state, combined_nfa_transitions,
                           set(combined_nfa_final_states.keys()))
        dfa = combined_nfa.subset_construction()
        # am apeleat metoda subset_construction pentru a obtine un dfa pe baza nfa-ului combinat

        dfa_final_states = {}
        for dfa_state in dfa.F:
            # Identifică toate tokenurile corespunzătoare stărilor NFA din starea DFA
            corresponding_tokens = [combined_nfa_final_states[nfa_state] for nfa_state in dfa_state if
                                    nfa_state in combined_nfa_final_states]

            # Alege tokenul care apare primul în specificație
            if corresponding_tokens:
                first_appearance = min(corresponding_tokens,
                                       key=lambda token: [idx for idx, (t, _) in enumerate(spec) if t == token][0])
                dfa_final_states[dfa_state] = first_appearance

        # Setează stările finale ale DFA-ului
        dfa.F = dfa_final_states

        return dfa


    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)

        # if an error occurs and the lexing fails, you should return none # todo: maybe add error messages as a task

        position = 0
        tokens = []
        line_position = 0
        line_number = 0
        ok = False

        while position < len(word):
            longest_match = None
            longest_match_length = 0
            current_state = self.dfa.q0
            char_match = False
            if word[position] == '\n':
                ok = True
                line_position = 0
                line_number += 1
            else:
                line_position += 1
            # am initializat current_state cu starea de start a dfa-ului
            for i in range(position, len(word)):
                # pentru fiecare caracter din cuvant
                char = word[i]

                current_state_frozenset = frozenset({current_state}) if isinstance(current_state,
                                                                                   set) else current_state
                transition_key = (current_state_frozenset, char)
                # am creat o cheie pentru a accesa tranzitia din dfa
                if transition_key in self.dfa.d:
                    next_state = self.dfa.d[transition_key]

                    if isinstance(next_state, set):
                        current_state = frozenset(next_state)
                    else:
                        current_state = frozenset([next_state])
                    # am actualizat current_state cu urmatoarea stare in functie de felul in care e reprezentata
                    if current_state in self.dfa.F:
                        longest_match = (self.dfa.F[current_state], word[position:i + 1])
                        longest_match_length = i - position + 1
                        char_match = True
                else:
                    if not char_match:
                        return [("", f"No viable alternative at character " + str(position) + ", line " + str(
                            word.count('\n', 0, line_number)))]

            if longest_match:
                # daca am gasit un match
                tokens.append(longest_match)
                position += longest_match_length
            else:
                if (position + 1) == len(word):
                    return [("", f"No viable alternative at character EOF, line {line_number}")]
                line_position += 1
                if ok == True:
                    return [("", f"No viable alternative at character " + str(line_position-1) + ", line " + str(
                        word.count('\n', 0, line_number) + 1))]
                else:
                    return [("", f"No viable alternative at character " + str(position + 1) + ", line " + str(
                        word.count('\n', 0, line_number)))]

        return tokens
