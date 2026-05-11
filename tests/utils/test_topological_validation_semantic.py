# Copyright (c) 2026 CoReason, Inc.
import pytest
from coreason_meta_engineering.utils.topological_validation import (
    extract_semantic_wells,
    generate_multi_well_embeddings,
    check_semantic_ambiguity,
    SemanticAmbiguityError
)

def test_extract_semantic_wells():
    docstring = """
    AGENT INSTRUCTION: Mathematically prove the absence of kinetic execution bleed before instantiating this class.
    CAUSAL AFFORDANCE: Mutates the graph by injecting a compliance edge.
    EPISTEMIC BOUNDS: Cannot exceed 1.0 probability.
    MCP ROUTING TRIGGERS: compliance, AST, security
    """
    wells = extract_semantic_wells(docstring)
    assert "Mathematically prove" in wells["instruction"]
    assert "Mutates the graph" in wells["affordance"]
    assert "Cannot exceed 1.0" in wells["bounds"]
    assert "compliance, AST" in wells["routing"]

def test_generate_multi_well_embeddings():
    # Will use fallback if sentence_transformers isn't available
    docstring = """
    AGENT INSTRUCTION: Test
    CAUSAL AFFORDANCE: Test
    EPISTEMIC BOUNDS: Test
    MCP ROUTING TRIGGERS: Test
    """
    embeddings = generate_multi_well_embeddings(docstring)
    assert len(embeddings["instruction"]) == 384
    assert len(embeddings["affordance"]) == 384

def test_check_semantic_ambiguity():
    embeddings = {
        "instruction": [1.0, 0.0] + [0.0]*382,
        "affordance": [1.0, 0.0] + [0.0]*382,
        "bounds": [1.0, 0.0] + [0.0]*382,
        "routing": [1.0, 0.0] + [0.0]*382,
    }
    
    local_registry = {
        "urn:coreason:actionspace:oracle:test:v1": {
            "embedding_instruction": [1.0, 0.0] + [0.0]*382, # 1.0 sim (collision!)
        }
    }
    
    with pytest.raises(SemanticAmbiguityError):
        check_semantic_ambiguity(embeddings, local_registry)
        
    local_registry_safe = {
        "urn:coreason:actionspace:oracle:test:v1": {
            "embedding_instruction": [0.0, 1.0] + [0.0]*382, # 0.0 sim (safe)
        }
    }
    assert check_semantic_ambiguity(embeddings, local_registry_safe) is True
