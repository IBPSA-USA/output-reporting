"""
doit task/build automation
"""

import os
import sys
from pathlib import Path

from lattice import Lattice

reporting_data_model = Lattice()
web_content_files = [str(p) for p in Path("docs/web").rglob("*") if p.is_file()]


def task_validate_example_files():
    """Validates the example files against the JSON schema (and other validation steps)"""
    return {
        "file_dep": reporting_data_model.examples
        + [schema.schema.file_path for schema in reporting_data_model.schema_info],
        "actions": [(reporting_data_model.validate_example_files, [])],
    }


def task_generate_web_docs():
    """Generates Markdown Documentation"""
    return {
        "file_dep": [schema.schema.file_path for schema in reporting_data_model.schema_info]
        + [template.path for template in reporting_data_model.doc_templates]
        + web_content_files,
        "targets": [os.path.join(reporting_data_model.web_docs_directory_path, "public")],
        "actions": [(reporting_data_model.generate_web_documentation, [])],
    }


def task_test_report():
    """Runs the report tool tests"""
    return {
        "actions": [f'"{sys.executable}" -m pytest report/tests -q'],
        "verbosity": 2,
    }
