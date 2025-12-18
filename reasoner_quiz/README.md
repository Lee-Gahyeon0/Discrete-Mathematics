# Stepwise Reasoner Course

A progressive set of reasoning exercises that grow from propositional knowledge bases to a Streamlit-powered predicate playground.

## Stage Guide
- **Stage 1 - Knowledge Base Basics:** Atomic literals with consistency checks.
- **Stage 2 - Forward Chaining (Modus Ponens):** Single-rule inference loops.
- **Stage 3 - Full Rule Set:** Nine classical propositional rules with feedback chaining.
- **Stage 4 - Predicate Logic Foundations:** Variables, unification, and quantifiers.
- **Stage 5 - Natural Language Templates:** Template-driven NL-to-logic conversions feeding the predicate reasoner.
- **Stage 6 - Streamlit KB UI:** Interactive editor to run the predicate reasoner and inspect results.

## How to Run
```
pip install -r requirements.txt
cd stage1_kb && pytest -q
cd ../stage2_fc_mp && pytest -q
cd ../stage3_all9 && pytest -q
cd ../stage4_predicate && pytest -q
cd ../stage5_nl_demo && pytest -q
# Streamlit app (manual run)
cd ../stage6_streamlit_ui && streamlit run app.py
```

