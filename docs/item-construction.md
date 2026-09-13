# Item construction

This note is the procedure for adding a Cognitive-Eval item. The scored suite is the JSON under `data/english/`. Alternate phrasings and option-order probes are derived from those items; they are not a second gold standard.

## Crossed design

Every Stage 1 phenomenon has a natural item and a novel-lexical counterpart with the same rule node, the same structural contrast, and real closed-class words. Pair them with `lexical_pair_of` in both directions. `minimal_pair_of` is the within-condition contrast (number flip, quantifier flip, licensed vs unlicensed), not the lexical pair.

Novel items isolate lexical familiarity only when:

- open-class nouns and verbs are invented,
- inflection is regular `-s` or `-ed` only (no irregular stems, no `-es`),
- determiners, prepositions, negation, quantifiers, and `any`/`some` stay real English.

Match syllable count and approximate length to the natural counterpart. A one-syllable novel noun pairs with a one-syllable natural noun.

## Novel words

Generate new stems with `src/lexicon/novel_words.py` (seeded CVC/CVCC, legal onsets and codas). A stem is rejected if the stem, the plural, or the past is in `english_wordlist.txt` or `supplemental_blocklist.txt`. The frequency list misses some real words (`gag`, `yomp`) and brands (`snorg`); the supplemental list is there for those.

Do not reuse a blocked stem. Current replacements: `yomp` → `swuf`, `teck` → `klek`, `snorg` → `snep`.

`wug` is Berko's (1958) nonce and is not in the wordlist, so it stays. Longer grandfathered nonce forms that are not CVC/CVCC but do not collide (`blorptor`, `zanth`, `flimm`, `queeb`, `borgle`) stay on older items. New items use generator-legal stems only. Record those stems on `gold_structure.novel_stems` so the collision check stays mechanical.

## Answer position

Do not let the correct letter sit on one position. Binary items are balanced across `a`/`b`. Ternary items are balanced across `a`/`b`/`c`. Balance is per option-count stratum, not by forcing a third option onto agreement. The invariant is tested: within a stratum, the share of the most common gold letter and the least common differ by at most 0.20.

Rotating letters must move the option text with the letter. The gold meaning does not change.

`probes/shuffled_probe.json` is a few ternary items with cycled option order. It is not loaded by `load_all_test_items`. A content-sensitive responder answers `correct_choice`. A responder that always repeats the original letter fails. That is the position-tracking check.

## Prompt phrasing

Each item stores `alternate_prompt`, produced by `src/schema/prompt_variants.py`: the same sentence and options, a different question frame and response instruction. The default run uses the canonical prompt. `EVAL_PROMPT_VARIANT=both` or `--prompt-variant both` adds copies with ids ending in `-alt`. Those copies drop `lexical_pair_of` and are reported as a phrasing gap, not as McNemar pairs. A large gap is a result (the model tracked the template), not a bug to paper over.

## Contamination

Natural items can appear in pretraining. That threat is sharpest for the canonical Bock & Miller (1991) stimuli `en-agr-002a` and `en-agr-002b` ("The key to the cabinets..."). Their notes flag the risk. The novel-lexical condition is the contamination-robust control: invented stems cannot have been memorized as those sentences. A natural-versus-novel gap is therefore interpretable as lexical familiarity, including memorized canonical examples, and not as a failure of the pairing.

## New phenomena

NPI licensing (Ladusaw 1979): `any` is acceptable under negation and unacceptable in a plain affirmative. `any` and negation stay real.

Scalar implicature (Grice 1975; Levinson 2000): when the question asks what the speaker is communicating, `some` gold is the not-all reading. The paired `all` item is the control that does not implicate not-all.

Quantifier scope (Ioup 1975; Anderson 2004): a sentence like "Every student read some book" has no single gold reading in isolation. Each Stage 1 item includes a continuation that forces one reading ("a different book for each student" → surface ∀>∃; "the same book for everyone" → inverse ∃>∀). If humans would not converge on that reading, the continuation is not disambiguating enough. A human baseline is still out of scope; the notes say so on purpose.

Stage 3 items (`en-comp-judge-001` and its novel twin) ask for a justification of the inverse reading rather than a letter. They have a disclosed `judge_rubric` and no forced-choice verifier, so the cascade leaves them to the judge.

## What not to do

- Do not invent an irregular plural or past on a novel stem.
- Do not score a scope sentence that has no disambiguating continuation.
- Do not treat an accuracy number without the majority baseline, the random baseline, and a bootstrap interval as a result.
- Do not pair natural and novel items that test different rules.
