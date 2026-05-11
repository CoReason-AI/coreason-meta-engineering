# Copyright (c) 2026 CoReason, Inc.
import os
from coreason_meta_engineering.utils.ast_extraction import extract_kinetic_skeleton

def test_extract_kinetic_skeleton(tmp_path):
    code = """
\"\"\"Module docstring.\"\"\"
import os
from math import sqrt
def my_func(a, b: int) -> int:
    \"\"\"Function docstring.\"\"\"
    return a + b

class MyClass:
    \"\"\"Class docstring.\"\"\"
    pass
"""
    p = tmp_path / "test_extract.py"
    p.write_text(code, encoding="utf-8")
    
    skeleton = extract_kinetic_skeleton(str(p))
    
    assert skeleton["docstring"] == "Module docstring."
    assert "os" in skeleton["imports"]
    assert "math" in skeleton["imports"]
    assert "def my_func(a, b) -> int:" in skeleton["signatures"]

def test_extract_kinetic_skeleton_no_docstring(tmp_path):
    code = "import sys\ndef foo(): pass"
    p = tmp_path / "test_no_doc.py"
    p.write_text(code, encoding="utf-8")
    skeleton = extract_kinetic_skeleton(str(p))
    assert skeleton["docstring"] == ""
    assert "sys" in skeleton["imports"]

def test_extract_kinetic_skeleton_deep_fallback(tmp_path):
    code = """
def func_with_doc():
    \"\"\"Found func doc\"\"\"
    pass

class ClassWithDoc:
    \"\"\"Found class doc\"\"\"
    pass
"""
    p = tmp_path / "test_deep.py"
    p.write_text(code, encoding="utf-8")
    
    # Hits line 34 (func doc)
    skeleton = extract_kinetic_skeleton(str(p))
    assert skeleton["docstring"] == "Found func doc"
    
    code_class = """
class ClassWithDoc:
    \"\"\"Found class doc\"\"\"
    pass
"""
    p2 = tmp_path / "test_deep_class.py"
    p2.write_text(code_class, encoding="utf-8")
    
    # Hits line 38 (class doc)
    skeleton2 = extract_kinetic_skeleton(str(p2))
    assert skeleton2["docstring"] == "Found class doc"
