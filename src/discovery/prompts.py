# src/discovery/prompts.py
"""
Free-form generation prompts for Cascade Stage 2 (statistical failure discovery).

These are deliberately NOT multiple-choice and NOT scored against a gold
label. They exist to produce open-ended text that can be embedded and
clustered to surface failure patterns we haven't already written a rule
for -- including patterns tied to lexical items and phrasings that don't
appear anywhere in the graded dataset.

Two phenomenon families (agreement completion and negation paraphrase),
each split into natural-vocabulary and novel-vocabulary prompts. That
mirrors the graded natural/novel axis without recycling its nouns or
verbs, so a discovered cluster is a new observation rather than a
rediscovery of a scored item.
"""

from typing import NamedTuple


class DiscoveryPrompt(NamedTuple):
    id: str
    family: str  # "agreement_completion" | "negation_paraphrase"
    lexical_condition: str  # "natural" | "novel"
    prompt: str


FREE_GENERATION_PROMPTS: list[DiscoveryPrompt] = [
    # --- Natural agreement completion (no options given) ---------------
    # Lexical items are not in the graded natural set (list/key/report/cabinet).
    DiscoveryPrompt(
        "disc-agr-nat-001",
        "agreement_completion",
        "natural",
        "Complete the sentence with the form of 'be' that sounds natural: "
        "'The captain of the ships ___ delayed.' Reply with only the completed sentence.",
    ),
    DiscoveryPrompt(
        "disc-agr-nat-002",
        "agreement_completion",
        "natural",
        "Complete the sentence with the form of 'be' that sounds natural: "
        "'The label on the bottles ___ torn.' Reply with only the completed sentence.",
    ),
    DiscoveryPrompt(
        "disc-agr-nat-003",
        "agreement_completion",
        "natural",
        "Complete the sentence with the form of 'be' that sounds natural: "
        "'The handles of the drawer ___ loose.' Reply with only the completed sentence.",
    ),
    DiscoveryPrompt(
        "disc-agr-nat-004",
        "agreement_completion",
        "natural",
        "Complete the sentence with the form of 'be' that sounds natural: "
        "'The cover of the manuals ___ missing.' Reply with only the completed sentence.",
    ),

    # --- Novel agreement completion: real function words, invented nouns
    # Novel-word stems are not in the graded novel set.
    DiscoveryPrompt(
        "disc-agr-nov-001",
        "agreement_completion",
        "novel",
        "Complete the sentence with 'is' or 'are': "
        "'The blick of the daxes ___ lost.' Reply with only the completed sentence.",
    ),
    DiscoveryPrompt(
        "disc-agr-nov-002",
        "agreement_completion",
        "novel",
        "Complete the sentence with 'is' or 'are': "
        "'The toma beside the kazzes ___ broken.' Reply with only the completed sentence.",
    ),
    DiscoveryPrompt(
        "disc-agr-nov-003",
        "agreement_completion",
        "novel",
        "Complete the sentence with 'is' or 'are': "
        "'The gazzes under the nizz ___ visible.' Reply with only the completed sentence.",
    ),
    DiscoveryPrompt(
        "disc-agr-nov-004",
        "agreement_completion",
        "novel",
        "Complete the sentence with 'is' or 'are': "
        "'The blickets of the dax ___ ready.' Reply with only the completed sentence.",
    ),

    # --- Natural negation paraphrase (no options given) ----------------
    # Quantifiers and nouns are not the graded 'not all students' / 'none of the buses' set.
    DiscoveryPrompt(
        "disc-neg-nat-001",
        "negation_paraphrase",
        "natural",
        "Explain in your own words what this sentence means: "
        "'Not every waiter arrived before the dinner.'",
    ),
    DiscoveryPrompt(
        "disc-neg-nat-002",
        "negation_paraphrase",
        "natural",
        "Explain in your own words what this sentence means: "
        "'Not every parcel was opened yesterday.'",
    ),
    DiscoveryPrompt(
        "disc-neg-nat-003",
        "negation_paraphrase",
        "natural",
        "Explain in your own words what this sentence means: "
        "'None of the doctors signed the form.'",
    ),
    DiscoveryPrompt(
        "disc-neg-nat-004",
        "negation_paraphrase",
        "natural",
        "Explain in your own words what this sentence means: "
        "'None of the parcels were opened yesterday.'",
    ),

    # --- Novel negation paraphrase: real function words, invented content
    DiscoveryPrompt(
        "disc-neg-nov-001",
        "negation_paraphrase",
        "novel",
        "Explain in your own words what this sentence means: "
        "'Not all the blicks gazzed.'",
    ),
    DiscoveryPrompt(
        "disc-neg-nov-002",
        "negation_paraphrase",
        "novel",
        "Explain in your own words what this sentence means: "
        "'Not all the tomas nizzed.'",
    ),
    DiscoveryPrompt(
        "disc-neg-nov-003",
        "negation_paraphrase",
        "novel",
        "Explain in your own words what this sentence means: "
        "'None of the blicks gazzed.'",
    ),
    DiscoveryPrompt(
        "disc-neg-nov-004",
        "negation_paraphrase",
        "novel",
        "Explain in your own words what this sentence means: "
        "'None of the tomas nizzed.'",
    ),
]
