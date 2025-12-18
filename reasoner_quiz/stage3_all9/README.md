# Stage 3 - Full Rule Set

This stage activates the complete collection of rules while keeping the forward chaining loop from earlier stages.

- `reasoner.py` implements nine classical rules: Modus Ponens, Modus Tollens, Simplification, Conjunction, Addition, Disjunctive Syllogism, Hypothetical Syllogism, Constructive Dilemma, and Destructive Dilemma.
- Forward chaining applies every rule in turn, adding newly inferred facts and rules until no further updates are possible.
- Derived rules are fed back into the rule set so longer reasoning chains emerge automatically.

`tests/test_all_rules.py` assembles facts and implications that trigger each rule and verifies the combined forward chaining behavior.
