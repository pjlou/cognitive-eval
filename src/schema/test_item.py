# src/schema/test_item.py
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ModuleType(str, Enum):
    NATURAL = "natural"
    NOVEL = "novel"

class LanguageCode(str, Enum):
    EN = "en"

class TierLevel(str, Enum):
    TIER_1_MORPHOLOGICAL = "tier_1_morphological"
    TIER_2_CLAUSAL = "tier_2_clausal"
    TIER_3_EXTENSION = "tier_3_extension"

class VerificationMethod(str, Enum):
    DEPENDENCY_PARSE = "dependency_parse"
    MORPHOLOGICAL_FEATURE = "morphological_feature"
    HYBRID_PARSE_MORPH = "hybrid_parse_morph"
    FORCED_CHOICE_TRUTH_CONDITIONAL = "forced_choice_truth_conditional"
    LEGACY_FORCED_TRUTH_CONDITIONAL = "forced_truth_conditional"
    LLM_JUDGE = "llm_judge"

    @classmethod
    def _missing_(cls, value):
        if value == "forced_truth_conditional":
            return cls.FORCED_CHOICE_TRUTH_CONDITIONAL
        return None

class TestItem(BaseModel):
    id: str = Field(..., description="Unique ID, e.g., 'en-agr-001a' or 'en-agr-nov-001a'")
    lexical_condition: ModuleType
    tier: TierLevel
    phenomenon: str = Field(..., description="Target phenomenon, e.g., 'agreement_attraction', 'negation_scope'")
    language: LanguageCode
    prompt: str = Field(..., description="The prompt sent to the target LLM")
    
    # Gold structural expectation used by verifiers
    gold_structure: Dict[str, Any] = Field(
        ..., 
        description="Structural properties required for a pass (e.g., target head, expected number, condition ID)"
    )
    
    rule_node_id: str = Field(
        ..., 
        description="Grounding rule ID in NetworkX rule graph (e.g., 'RULE_EN_AGR_HEAD' or 'RULE_EN_NEG_SCOPE')"
    )
    
    verification_method: VerificationMethod
    difficulty: str = Field(default="medium")
    source: str = Field(..., description="Citation source, e.g., 'Bock & Miller 1991' or 'ScoNe 2023'")
    minimal_pair_of: Optional[str] = Field(None, description="ID of paired test item isolating this contrast")
    lexical_pair_of: Optional[str] = Field(
        None,
        description="ID of the natural/novel counterpart that holds the rule and structure fixed",
    )
    alternate_prompt: Optional[str] = Field(
        None,
        description="Second framing of the same forced-choice question, used for phrasing-robustness checks",
    )
    judge_rubric: Optional[str] = Field(
        None,
        description="Disclosed Stage 3 rubric. Present only when no deterministic verifier applies.",
    )
    notes: Optional[str] = None

    class Config:
        use_enum_values = True
