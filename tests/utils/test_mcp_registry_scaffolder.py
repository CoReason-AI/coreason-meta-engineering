import json
from coreason_meta_engineering.utils.mcp_registry_scaffolder import generate_server_json

def test_generate_server_json_dict():
    schema = {
        "urn": "urn:coreason:actionspace:solver:test_solver:v1",
        "description": "Test description",
        "epistemic_status": "PUBLISHED",
        "economics": {
            "license_class": "OPEN_SOURCE",
            "billing_tier": "TIER_0_FREE"
        },
        "validation": {}
    }
    result = generate_server_json(schema)
    data = json.loads(result)
    assert data["name"] == "test_solver"
    assert data["registry_metadata"]["epistemic_status"] == "PUBLISHED"

def test_generate_server_json_list():
    schema = [{
        "urn": "urn:coreason:actionspace:solver:test_list_solver:v1"
    }]
    result = generate_server_json(schema)
    data = json.loads(result)
    assert data["name"] == "test_list_solver"

def test_generate_server_json_empty_list():
    schema = []
    result = generate_server_json(schema)
    data = json.loads(result)
    assert data["name"] == "unknown_capability"

def test_generate_server_json_invalid_urn():
    schema = {
        "urn": "invalid_urn"
    }
    result = generate_server_json(schema)
    data = json.loads(result)
    assert data["name"] == "unknown_capability"
