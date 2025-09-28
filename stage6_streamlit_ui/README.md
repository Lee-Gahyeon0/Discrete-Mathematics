# Stage 6 - Streamlit Knowledge-Base UI

This stage wraps the predicate reasoner with a Streamlit front end so users can edit a knowledge base and inspect derived conclusions.

- pp.py parses lightweight fact and rule syntax (e.g., parent(alice,bob) and orall x,y: parent(x,y) -> ancestor(x,y)) and converts them into Stage 4 data structures.
- A form lets you paste or tweak the knowledge base, submit it to the reasoner, and see which facts are given versus newly derived.
- Query patterns (such as ncestor(?who, dana)) run against the current KB and display satisfying substitutions in a table.
- The sidebar includes a one-click ancestor sample that pairs with the natural language templates from Stage 5.

To launch the UI, install requirements and run streamlit run app.py inside the stage6_streamlit_ui directory.
