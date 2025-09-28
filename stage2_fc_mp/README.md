# Stage 2 - Forward Chaining with Modus Ponens

This stage extends the knowledge base with rule-driven inference while only allowing Modus Ponens.

- `reasoner.py` fires Modus Ponens to derive Q whenever P and ("IMPLIES", P, Q) are present in the knowledge base.
- `KB.forward_chain()` repeats Modus Ponens until a fixpoint is reached and no new facts can be derived.
- The streamlined setup keeps the focus on mastering one rule before expanding to the full calculus.

`tests/test_stage2_mp.py` confirms that P, (P -> Q), and (Q -> R) lead to Q and R after forward chaining.
