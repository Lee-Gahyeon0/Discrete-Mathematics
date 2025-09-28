# Stage 4 - Predicate Logic Foundations

This stage upgrades the reasoner to handle a fragment of first-order logic with variables, unification, and quantifiers.

- easoner.py defines pattern-matching utilities such as is_variable, unify, and substitute, and stores facts and rules in the KB class.
- Universally quantified rules use the form ('FORALL', vars, ('IMPLIES', premises, conclusion)); premises are matched against ground facts via unification to derive new instances.
- Existential conclusions are Skolemised on demand so rules like orall x. parent(x) -> exists y. loves(x, y) introduce fresh witnesses automatically.
- KB.query() supports template-based queries by unifying patterns with derived facts.

	ests/test_predicate_reasoner.py covers transitive reasoning with variables, existential instantiation, unification edge-cases, and query substitution results.
