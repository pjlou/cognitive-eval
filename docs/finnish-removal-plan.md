## The new design

Replace **Tier × Language** with **Tier × Lexical Condition** (Natural vs. Novel), all English:

|              | Natural vocabulary (existing) | Novel/novel-word vocabulary (new) |
|---|---|---|
| **Tier 1: Local Morphosyntax** | Subject–verb agreement attraction (`RULE_EN_AGR_HEAD`) | Same rule, novel-word nouns with regular inflection |
| **Tier 2: Clausal Semantics** | Negation scope (`RULE_EN_NEG_SCOPE` / `RULE_EN_NEG_UNIVERSAL_QUANT`) | Same rules, novel-word content words, real function words/quantifiers |

This is the wug-test paradigm (Berko 1958) plus the "colorless green ideas" logic: keep closed-class morphology and function words real, swap open-class content words for invented ones. It tests almost exactly what your README says the language axis was for — "genuinely structural or merely a surface artifact of training data" — but isolates *lexical memorization* specifically, which arguably targets that claim more directly than cross-linguistic transfer does, and it's a well-precedented paradigm you can cite (Berko 1958; Warstadt et al. 2020's BLiMP already leans on a related logic).

Example items (same JSON shape you already use, same `rule_node_id`, same `correct_choice` field — verifier code doesn't change at all):

```json
{
  "id": "en-agr-nov-001a",
  "module": "novel",
  "tier": "tier_1_morphological",
  "phenomenon": "agreement_attraction",
  "language": "en",
  "prompt": "Complete the sentence 'The wug of the blorptors ___ nearby.' (a) is or (b) are. Respond with only the letter, no explanation.",
  "gold_structure": {"syntactic_head": "wug", "head_number": "singular", "attractor": "blorptors", "attractor_number": "plural", "correct_choice": "a"},
  "rule_node_id": "RULE_EN_AGR_HEAD",
  "verification_method": "forced_choice_truth_conditional",
  "source": "Bock & Miller 1991 (novel-word-lexical adaptation)",
  "minimal_pair_of": "en-agr-nov-001b",
  "notes": "novel-word-noun replication of en-agr-001a. Real determiners/prepositions/copula, invented nouns with regular -s plural, to isolate structural agreement from lexical familiarity."
}
```

```json
{
  "id": "en-neg-nov-001a",
  "module": "novel",
  "tier": "tier_2_clausal",
  "phenomenon": "negation_scope",
  "language": "en",
  "prompt": "Read the sentence: 'Not all the glorbs vorped.' Does this mean: (a) no glorb vorped, (b) at least one glorb vorped, or (c) all glorbs vorped? Respond with only the letter, no explanation.",
  "gold_structure": {"negation_governor": "vorped", "scope_subtree": "all the glorbs ... vorped", "correct_choice": "b"},
  "rule_node_id": "RULE_EN_NEG_SCOPE",
  "verification_method": "forced_choice_truth_conditional",
  "source": "ScoNe 2023 (novel-word-lexical adaptation)",
  "minimal_pair_of": "en-neg-nov-001b",
  "notes": "novel-word-verb/noun replication of en-neg-001a, mirroring the not-all vs none-of minimal pair with invented content words."
}
```

## Migration plan, phased

**Phase 1 — Schema (small, mechanical)**
- `src/schema/test_item.py`: `ModuleType` enum → `{NATURAL = "natural", NOVEL = "novel"}` (drop `ENGLISH`/`FINNISH`). `LanguageCode` → keep only `EN` (drop `FI`); it now always reads `"en"`, which is fine to leave as a schema field for future extensibility.
- Optionally rename the `module` field to `lexical_condition` everywhere it's read/written for clarity — mechanical find/replace, worth doing since "module" no longer means anything once there's only one language.

**Phase 2 — Delete Finnish-specific code**
- Delete `src/verifiers/finnish_verifiers.py`.
- `src/schema/rule_graph.py`: remove the `RULE_FI_*` / `CAT_FI_*` / `FEAT_FI_*` nodes and edges (roughly lines building the Finnish object-case and negation subgraphs). Keep `RULE_EN_AGR_HEAD`, `RULE_EN_NEG_SCOPE`, `RULE_EN_NEG_UNIVERSAL_QUANT` untouched — you reuse them as-is for the novel items.
- `src/eval/scorers.py`: remove the `finnish_verifiers` import and the `language == "finnish"` dispatch branch; dispatch purely on `phenomenon` now since the same verifier serves both natural and novel items.
- `evalcascade/evaluators/rule_graph.py`: remove the `finnish_verifiers` import and the two `("...", "finnish")` dispatch entries; the `("agreement_attraction", "english")` / `("negation_scope", "english")` keys become `("agreement_attraction", "natural")`, `("agreement_attraction", "novel")`, `("negation_scope", "natural")`, `("negation_scope", "novel")` — all four pointing at the same two functions you already have.
- Delete `data/finnish/negation_scope.json` and `data/finnish/object_case_alternation.json`.
- `requirements.txt`: remove `uralicNLP`.

**Phase 3 — Build the novel dataset**
- Add `data/english/agreement_attraction_novel.json` and `data/english/negation_scope_novel.json` (loader globs recursively, so no directory restructuring needed).
- Match your existing pattern: 4 items per phenomenon, minimal pairs, `module: "novel"`. I'd suggest going slightly bigger here than the original Finnish set (6–8 per phenomenon) since this axis is now central to your headline claim and it's essentially free to author — no native speaker needed, just careful novel-word-word construction with regular morphology (avoid irregular plurals/verbs so agreement stays unambiguous).

**Phase 4 — Discovery (Stage 2)**
- `src/discovery/prompts.py`: currently frames "two families, mirroring the two Finnish phenomena" — reframe as natural-vocabulary vs novel-vocabulary free-generation prompts for the same two phenomena.

**Phase 5 — Platform touchpoints**
- `evalcascade/evaluators/statistical.py` line ~299: drop `"fi"`/`"finnish"` from the tag-family exclusion set; add `"natural"`/`"novel"` if you want slice metrics keyed on the new axis (recommended — you'll want a gate/slice comparing natural vs. novel accuracy, since a large gap *is* your headline result).
- `datasets/smoke-v1/manifest.yaml`: swap `fi-case-001a`, `fi-case-001c` for two novel-condition ids, e.g. `en-agr-nov-001a`, `en-neg-nov-001a`, so CI still exercises both axes.
- Check `configs/*.yaml` for any lingering language filters (I didn't find any, but worth a grep before you're done).

**Phase 6 — Docs**
- `cognitive-eval/README.md`: replace the "English/Finnish" 2×2 diagram with "Natural/Novel," update the citation line to add Berko (1958), drop the UralicNLP install step.
- `docs/roadmap.md`: it already anticipated this ("worth returning to once Finnish proficiency... make it relevant again") — good, just add a short note that the novel-vocabulary axis is the interim replacement and cross-linguistic remains a deferred stretch goal, not a cut feature.
- `evalcascade/docs/architecture.md` and `methodology.md`: update the one paragraph each that references Finnish/native-speaker review.
- `dashboard/app.py` (both dashboards): update the one-line description string; check for any language-specific chart/filter logic tied to "finnish".

**Phase 7 — Tests**
- `tests/test_verifiers.py` (cognitive-eval): remove Finnish verifier tests, add equivalent tests asserting the *same* verifier functions handle novel-lexical gold structures correctly (should pass with zero verifier code changes — that's a good thing to assert explicitly).
- Grep `evalcascade/tests/` for any fixture data using old module values (`"english"`/`"finnish"`) and update to `"natural"`/`"novel"`.

**Phase 8 — Verify**
- Run `pytest` in both trees, run the CI smoke command, regenerate the portfolio demo, and refresh `docs/methodology.md`'s honesty section to reflect the new design (this section is your strongest asset — keep it current, not stale).