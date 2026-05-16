# Copyright (c) 2026 CoReason, Inc
#
# This software is proprietary and dual-licensed
# Licensed under the Prosperity Public License 3.0 (the "License")

import json

import forge_service


# Note: In a real componentization flow, this class would implement
# the interface defined in the generated bindings from world.wit
class ForgeTool:
    def list_tools(self):
        return [
            {
                "name": "scaffold_manifest_state",
                "description": "Scaffolds a new model by orchestrating LLM agents bounded by the JSON schema.",
                "input-schema": json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "state_name": {"type": "string"},
                            "geometric_schema": {"type": "object"},
                            "target_file_path": {"type": "string"},
                            "action_space_id": {"type": "string"},
                            "base_class": {"type": "string", "default": "CoreasonBaseState"},
                        },
                        "required": ["state_name", "geometric_schema", "target_file_path", "action_space_id"],
                    }
                ),
            },
            {
                "name": "reconcile_manifest_state",
                "description": "Reconciles an existing model by orchestrating LLM agents bounded by the JSON schema.",
                "input-schema": json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "state_name": {"type": "string"},
                            "geometric_schema": {"type": "object"},
                            "target_file_path": {"type": "string"},
                            "action_space_id": {"type": "string"},
                            "base_class": {"type": "string", "default": "CoreasonBaseState"},
                        },
                        "required": ["state_name", "geometric_schema", "target_file_path", "action_space_id"],
                    }
                ),
            },
            {
                "name": "scaffold_logic_actuator",
                "description": "Scaffolds a new logic actuator function by orchestrating LLM agents bounded by the JSON schema.",
                "input-schema": json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "actuator_name": {"type": "string"},
                            "geometric_schema": {"type": "object"},
                            "target_file_path": {"type": "string"},
                            "action_space_id": {"type": "string"},
                            "agent_instruction": {"type": "string"},
                            "causal_affordance": {"type": "string"},
                            "epistemic_bounds": {"type": "string"},
                            "return_type": {"type": "string", "default": "None"},
                            "required_imports": {"type": "array", "items": {"type": "string"}},
                            "logic_body": {"type": "string"},
                        },
                        "required": [
                            "actuator_name",
                            "geometric_schema",
                            "target_file_path",
                            "action_space_id",
                            "agent_instruction",
                            "causal_affordance",
                            "epistemic_bounds",
                        ],
                    }
                ),
            },
            {
                "name": "scaffold_epistemic_node",
                "description": "Scaffolds a new Swarm Agent structure by orchestrating LLM agents.",
                "input-schema": json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "node_name": {"type": "string"},
                            "cognitive_boundary_directive": {"type": "string"},
                            "target_file_path": {"type": "string"},
                            "action_space_id": {"type": "string"},
                            "base_class": {"type": "string", "default": "CoreasonBaseAgent"},
                        },
                        "required": [
                            "node_name",
                            "cognitive_boundary_directive",
                            "target_file_path",
                            "action_space_id",
                        ],
                    }
                ),
            },
            {
                "name": "verify_solver_diff",
                "description": "Verify a high-entropy solver diff through the PVV pipeline.",
                "input-schema": json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "deliberation_trace": {"type": "string"},
                            "payload": {"type": "string"},
                            "solver_urn": {"type": "string"},
                            "tokens_burned": {"type": "integer"},
                        },
                        "required": ["deliberation_trace", "payload", "solver_urn", "tokens_burned"],
                    }
                ),
            },
            {
                "name": "scaffold_manifest_yaml",
                "description": "Scaffolds a new manifest.yaml for a given URN.",
                "input-schema": json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "target_dir": {"type": "string"},
                            "urn": {"type": "string"},
                            "author_id": {"type": "string"},
                        },
                        "required": ["target_dir", "urn", "author_id"],
                    }
                ),
            },
        ]

    def call_tool(self, name, arguments):
        args = json.loads(arguments)
        try:
            if name == "scaffold_manifest_state":
                result = forge_service.scaffold_manifest_state(**args)
            elif name == "reconcile_manifest_state":
                result = forge_service.reconcile_manifest_state(**args)
            elif name == "scaffold_logic_actuator":
                result = forge_service.scaffold_logic_actuator(**args)
            elif name == "scaffold_epistemic_node":
                result = forge_service.scaffold_epistemic_node(**args)
            elif name == "verify_solver_diff":
                result = forge_service.verify_solver_diff(**args)
                return {"content": [{"text": json.dumps(result)}], "is-error": False}
            elif name == "scaffold_manifest_yaml":
                result = forge_service.scaffold_manifest_yaml(**args)
            else:
                return {"content": [{"text": f"Unknown tool: {name}"}], "is-error": True}

            return {"content": [{"text": str(result)}], "is-error": False}
        except Exception as e:
            return {"content": [{"text": str(e)}], "is-error": True}
