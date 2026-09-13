1. Report against baselines, not raw accuracy alone.
Add a majority-class baseline and a random baseline to every report. Right now a report saying "model X: 78% accuracy" is meaningless without knowing chance is ~50% (or ~56% if it just always answers "b" given your current key distribution). This is a metrics.py addition, not a dataset change — cheap.

2. Counterbalance/audit answer-position bias.
Deliberately balance correct_choice across a/b/c so it's close to uniform, and add a unit test asserting the distribution stays balanced within a tolerance as the dataset grows. Also worth having extract_final_choice scoring done on option-order-shuffled variants of a few items, to confirm the model isn't tracking position rather than content.

3. Add confidence intervals via bootstrap-over-items.
With 18–30 items, a point-accuracy number invites the (correct) criticism "that's not statistically distinguishable from noise." Bootstrap resampling over items to get a 95% CI, and report it alongside every accuracy number in the dashboard and JSON report. This is a metrics.py addition — no new data needed, and it forces honest framing of exactly how much your current sample size can support.

4. Add a paired significance test for natural vs. novel.
Since natural/novel items are constructed as matched pairs (same rule, same structure), use McNemar's test per model to ask "is the natural-vs-novel accuracy gap significant for this model," not just "is it different." This turns your headline claim (surface artifact vs. structural competence) into a falsifiable statistical statement instead of an eyeballed gap.

5. Formalize a novel-word construction pipeline.
Right now novel words are hand-invented. Two risks: they might accidentally collide with real words/brands, and there's no documented, reproducible generation method. Either build a small deterministic novel-word generator (phonotactically legal CVC/CVCC forms, checked against an English wordlist to guarantee non-collision) or, at minimum, write a docs/item-construction.md that states the exact rules you followed (regular morphology only, no accidental real-word collisions, matched syllable count/length to the natural-condition minimal pair). This is what makes items extensible by someone else, which is itself a credibility signal.

6. Flag and mitigate contamination risk on natural items.
The Bock & Miller (1991) canonical stimuli ("The key to the cabinet(s)...") are widely cited in psycholinguistics and NLP papers and plausibly appear in pretraining corpora verbatim. That's a real threat to validity for the natural condition specifically — and it's actually a point in your favor if you name it explicitly: frame the novel-lexical condition as your contamination-robust control, since invented words can't have been memorized. Add a line to methodology.md making this argument directly; it preempts the most obvious objection a reviewer would raise.

7. Check robustness to prompt phrasing.
Author one alternate phrasing per item (different framing of the same forced-choice question) and confirm accuracy doesn't swing wildly. If it does, that's evidence the model is pattern-matching your specific template rather than reasoning about the structure — which is itself a legitimate, reportable finding, not just a nuisance to fix.

8. Add three more phenomena that fit the existing design cleanly.
The following support forced-choice scoring, have solid citations, and work with the natural/novel-lexical pairing:

(1) NPI licensing ("any" under negation vs. affirmative contexts) — Ladusaw (1979); cleanly forced-choice, cleanly novel-word-able.
(2) Scalar implicature ("some" pragmatically implicating "not all") — Grice (1975) / Levinson (2000); tests pragmatic reasoning, a different competence than your current syntax/semantics split, which broadens the claim meaningfully.
(3) Quantifier scope ambiguity: Negation-scope items already cite ScoNe (2023), which is specifically about scope resolution. Quantifier-quantifier scope (e.g. "Every student read some book" — surface ∀>∃ vs. inverse ∃>∀) is the direct sibling phenomenon, with its own solid literature (Ioup 1975; Anderson 2004 on how plausibility biases scope preference). Smoke-v1 dataset already has one dormant item (en-comp-judge-001, tagged compositional_logic) that's exactly this kind of task — a scope-under-negation reading routed to the llm_judge evaluator, which the docs say is "specified but not a release gate in this MVP." Adding a real quantifier-scope phenomenon gives a natural, non-contrived reason to actually exercise Stage 3 of the cascade instead of it being one placeholder item. That's a second piece of the architecture becoming load-bearing, which is a meaningfully bigger credibility win than the phenomenon itself.  It fits the novel-lexical axis cleanly, same as negation scope does.

The one real construction hazard: genuine scope ambiguity doesn't have a single "correct" reading in isolation — you need a disambiguating continuation ("...It was the same book for everyone" forces inverse scope) to make each item have one defensible gold answer. That's more construction discipline than your negation-scope items needed, and it's exactly where a human baseline (from the Tier 2 plan) earns its keep — if humans don't converge on your intended reading, the item's context isn't disambiguating enough yet.

9. Report scaling curves, not just per-model tables.
You already have qwen2.5 at 1.5b/3b/7b plus ministral and llama3.1 in your eval logs — that's a scaling comparison sitting unused. Make "does linguistic competence survive parameter reduction" a first-class chart (accuracy vs. param count, natural vs. novel condition as two lines) since that's the actual scientific question your README poses. This is a reporting change, not new data collection.

10. Convergent validity check against an established benchmark.
Where your Tier 1 agreement-attraction phenomenon overlaps with BLiMP's subject_verb_agreement items, check whether your models' relative ranking matches published BLiMP numbers for the same models/sizes. If it does, that's real external validation that your instrument is measuring the same underlying thing as an established benchmark, not something idiosyncratic to your item set.

11. Response-consistency check.
Run each item multiple times at nonzero temperature (n=5, say) instead of relying on single greedy-decoded answers, and report agreement/entropy across repeats. A model that "passes" an item once but is unstable across resampling is a different (weaker) finding than one that reliably reproduces the correct structural judgment — this is a cheap addition to the adapter layer (repeat + majority-vote or report variance) and meaningfully strengthens any claim about "competence" versus "lucky sample."