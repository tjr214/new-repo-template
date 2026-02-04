#!/usr/bin/env python3
"""
Validate a task implementation plan YAML file against the schema.

Usage:
    python validate_template.py task-template.yaml
    python validate_template.py task-template-example.yaml
"""

import sys
import json
import yaml
from jsonschema import validate, ValidationError, SchemaError
from pathlib import Path


def load_yaml(filepath: str) -> dict:
    """Load YAML file and return as dict."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def load_json_schema(filepath: str) -> dict:
    """Load JSON schema file."""
    with open(filepath, "r") as f:
        return json.load(f)


def validate_template(template_path: str, schema_path: str) -> bool:
    """
    Validate template against schema.

    Returns:
        True if valid, False otherwise
    """
    try:
        print(f"📄 Loading template: {template_path}")
        template = load_yaml(template_path)

        print(f"📋 Loading schema: {schema_path}")
        schema = load_json_schema(schema_path)

        print("🔍 Validating...")
        validate(instance=template, schema=schema)

        print("✅ Template is VALID!")
        print(f"\n📊 Template Summary:")
        print(f"   Task: {template['task']['name']}")
        print(f"   Status: {template['task']['status']}")
        print(f"   Phases: {len(template['task']['phases'])}")

        # Count steps and instructions
        total_steps = 0
        total_instructions = 0

        def count_phase_items(phase):
            nonlocal total_steps, total_instructions
            if "steps" in phase:
                total_steps += len(phase["steps"])
                for step in phase["steps"]:
                    total_instructions += len(step["instructions"])
            if "sub_phases" in phase:
                for sub_phase in phase["sub_phases"]:
                    count_phase_items(sub_phase)

        for phase in template["task"]["phases"]:
            count_phase_items(phase)

        print(f"   Steps: {total_steps}")
        print(f"   Instructions: {total_instructions}")

        return True

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return False

    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return False

    except SchemaError as e:
        print(f"❌ Schema error: {e}")
        return False

    except ValidationError as e:
        print(f"❌ Validation error:")
        print(f"   Path: {' -> '.join(str(p) for p in e.path)}")
        print(f"   Message: {e.message}")
        if e.context:
            print(f"   Context:")
            for ctx in e.context:
                print(f"     - {ctx.message}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python validate_template.py <task-template.yaml> [schema.json]")
        sys.exit(1)

    template_path = sys.argv[1]
    schema_path = sys.argv[2] if len(
        sys.argv) > 2 else ".template_scripts/task-template-schema.json"

    if not Path(template_path).exists():
        print(f"❌ Template file not found: {template_path}")
        sys.exit(1)

    if not Path(schema_path).exists():
        print(f"❌ Schema file not found: {schema_path}")
        sys.exit(1)

    is_valid = validate_template(template_path, schema_path)
    sys.exit(0 if is_valid else 1)
