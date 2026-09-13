"""Dataset invariants for the linguistic-rigor pass."""

from collections import Counter

from src.lexicon.novel_words import collides, generate_novel_stems, is_phonotactically_legal, load_wordlist
from src.schema.dataset_loader import load_all_test_items


def test_generator_stems_are_legal_and_unused():
    wordlist = load_wordlist()
    stems = generate_novel_stems(8, seed=4, wordlist=wordlist)
    assert len(set(stems)) == 8
    for stem in stems:
        assert is_phonotactically_legal(stem)
        assert not collides(stem, wordlist)


def test_choice_balance_and_pairs():
    items = load_all_test_items()
    by_id = {item.id: item for item in items}
    groups: dict[int, Counter] = {}
    for item in items:
        assert item.lexical_pair_of in by_id
        assert by_id[item.lexical_pair_of].lexical_pair_of == item.id
        assert item.alternate_prompt and item.alternate_prompt != item.prompt
        gold = item.gold_structure or {}
        if gold.get("correct_choice") and gold.get("n_options"):
            groups.setdefault(int(gold["n_options"]), Counter())[gold["correct_choice"]] += 1
    for n_options, counts in groups.items():
        total = sum(counts.values())
        shares = [counts.get(letter, 0) / total for letter in "abc"[:n_options]]
        assert max(shares) - min(shares) <= 0.20
