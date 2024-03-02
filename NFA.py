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

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        closure = set()  # setul cu closure
        stack = [state]  # stiva cu stari
        while stack:  # cat timp stiva nu e goala
            current_state = stack.pop()  # scoatem o stare din stiva
            closure.add(current_state)  # adaugam starea in closure
            epsiolon_transitions = self.d.get((current_state, EPSILON),
                                              set())  # luam toate starile in care putem ajunge cu epsilon din starea
            # curenta
            for next_state in epsiolon_transitions:  # pentru fiecare stare in care putem ajunge cu epsilon din
                # starea curenta
                if next_state not in closure:  # daca nu e in closure
                    stack.append(next_state)  # adaugam starea in stiva
                    closure.add(next_state)  # adaugam starea in closure

        return closure  # returnam closure-ul

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # compute the DFA obtained by applying the subset construction to this NFA
        # you will need the epsilon_closure function defined above for this
        # see the comments in the DFA class for more details
        dfa_states = set()  # setul cu starile DFA-ului
        dfa_transition = dict()  # dictionarul cu tranzitiile DFA-ului
        dfa_final_states = set()  # setul cu starile finale ale DFA-ului
        dfa_start_state = frozenset(self.epsilon_closure(self.q0))  # starea de start a DFA-ului
        stack = [dfa_start_state]  # stiva cu starile DFA-ului

        dfa_states.add(dfa_start_state)  # adaugam starea de start in setul de stari

        while stack:  # cat timp stiva nu e goala
            current_state = stack.pop()  # scoatem o stare din stiva

            # pentru fiecare litera din alfabet
            for letter in self.S:
                next_state = set()  # luam o noua stare

                # pentru fiecare stare din starea curenta
                for state in current_state:
                    if (state, letter) in self.d:  # daca exista o tranzitie din starea curenta cu litera curenta
                        epsilon = self.d[
                            (state, letter)]  # luam starile in care putem ajunge cu litera curenta din starea curenta
                        for i in epsilon:  # pentru fiecare stare in care putem ajunge cu litera curenta din starea
                            # curenta
                            next_state = next_state.union(self.epsilon_closure(
                                i))  # adaugam in next_state closure-ul starii, adica facem epsilon-closure-ul starii

                if next_state not in dfa_states:  # daca next_state nu e in setul de stari
                    dfa_states.add(frozenset(next_state))  # il adaugam
                    stack.append(frozenset(next_state))  # il adaugam in stiva

                dfa_transition[(current_state, letter)] = next_state  # adaugam tranzitia in dictionar

        for state in dfa_states:  # pentru fiecare stare din setul de stari
            for final_state in self.F:  # pentru fiecare stare finala din setul de stari finale
                if final_state in state:  # daca starea finala e in starea curenta
                    dfa_final_states.add(state)  # adaugam starea in setul de stari finale

        return DFA(self.S, dfa_states, dfa_start_state, dfa_transition, dfa_final_states)  # returnam DFA-ul

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        pass
