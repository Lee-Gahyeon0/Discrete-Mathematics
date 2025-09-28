# Stage 1 - Knowledge Base Basics

This stage builds a minimal propositional knowledge base that works with atomic literals and their negations.

- `kb.py` models literals as plain atoms or ("NOT", atom) tuples and includes helpers such as `negate`, `is_atom`, and `is_not`.
- `KB.add_fact()` adds new facts, ignores duplicates, and raises `ValueError` when both P and ("NOT", "P") are present.
- The knowledge base keeps its fact store consistent for later stages.

`tests/test_stage1_kb.py` exercises fact insertion, duplicate handling, contradiction detection, and the literal helpers.
