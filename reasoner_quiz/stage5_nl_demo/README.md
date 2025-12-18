# Stage 5 - Natural Language Template Demo

This stage layers a lightweight natural-language-to-logic bridge over the predicate reasoner from Stage 4.

- 	emplate_demo.py defines a TemplateEngine with reusable sentence templates that emit predicate facts, universally quantified rules, and query patterns.
- The demo covers four examples: two ground facts, two universal rules, and a query such as "Who is an ancestor of Carol?", demonstrating template reuse.
- 
un_demo() loads all templates into a shared knowledge base, triggers forward chaining via the Stage 4 reasoner, and validates that Alice is inferred to be Carol's ancestor.
- The module exposes structured results (DemoResult) so the templates can feed CLI, tests, or future UI layers.

	ests/test_template_demo.py verifies template rendering, successful inference from the combined templates, and the query pattern.

