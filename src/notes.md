### NOTES
---

- **A.** Compute which nonterminals are nullable.
- **B.** Initialize **Read** to **DR**: one set (bit vector of length the number of terminals) for each
nonterminal transition, by inspection of the transition's successor state.
- **C.** Compute reads: one list of nonterminal transitions per nonterminal transition, by
inspection of the successor state of the latter transition.
- **D.** Apply algorithm **Digraph** to **reads** to compute **Read**; if a cycle is detected, announce
that the grammar is not LR(k) for any k.
- **E.** Compute **includes** and **lookback**: one list of nonterminal transitions per nonterminal
transition and reduction, respectively, by inspection of each nonterminal transition and
associated production right parts, and by considering nullable nonterminals appropri-
ately.
- **F.** Apply algorithm **Digraph** to **includes** to compute **Follow**: use the same sets as
initialized in part **B** and completed in part **D**, both as initial values and as workspace.
If a cycle is detected in which a **Read** set is nonempty, announce that (as we conjecture)
the grammar is not LR(k) for any k.
- **G.** Union the **Follow** sets to form the **LA** sets according to the **l o o k b a c k** links computed
in part F.
- **H.** Check for conflicts; if none, announce that the grammar is LALR(1)--we have a parser.
