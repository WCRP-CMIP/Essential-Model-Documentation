"""
Handler for Horizontal Grid Cell registration (Stage 1)
"""

import os
import sys
import json
from typing import Any

# Import from cmipld utils
from cmipld.utils.id_generation import generate_id_from_issue
from cmipld.utils.esgvoc import pycmipld, DATA_DESCRIPTOR_CLASS_MAPPING


kind = __file__.split('/')[-1].replace('.py','')

def generate_markdown_report(model_obj: pycmipld, data: dict) -> str:

    md = ""
    
    # 1. Model Field Checks Section
    if model_obj.model_class:
        md += "## 📋 Model Field Validation Rules\n\n"
        
        # Get model fields and their constraints
        if hasattr(model_obj.model_class, 'model_fields'):
            fields = model_obj.model_class.model_fields
            md += "| Field | Type | Required | Description |\n"
            md += "| --- | --- | --- | --- |\n"
            
            for field_name, field_info in fields.items():
                field_type = field_info.annotation if hasattr(field_info, 'annotation') else str(field_info.annotation)
                required = "✅" if field_info.is_required() else "❌"
                description = field_info.description or ""
                md += f"| `{field_name}` | `{field_type.__name__ if hasattr(field_type, '__name__') else str(field_type)}` | {required} | {description} |\n"
        
        md += "\n"
    
    # 2. Validation Errors Section (if any)
    if model_obj.validation_md:
        md += "## ⚠️ Validation Errors\n\n"
        md += "❌ **This submission has validation errors:**\n\n"
        md += model_obj.validation_md
        md += "\n"
    else:
        md += "## ✅ Validation Status\n\n"
        md += "**All validation checks passed!**\n\n"
    
    # 3. JSON Data Section
    md += "## 📄 Submitted Data\n\n"
    md += "```json\n"
    md += json.dumps(data, indent=2, ensure_ascii=False)
    md += "\n```\n\n"
    
    # 4. Non-Empty Fields Checklist for Reviewer
    md += "## ✏️ Fields Submitted (Reviewer Checklist)\n\n"
    md += "Check each field for accuracy:\n\n"
    
    non_empty_fields = {k: v for k, v in data.items() if v and not k.startswith('@') and k != '_validation_report'}
    
    if non_empty_fields:
        for field_name, value in non_empty_fields.items():
            # Truncate long values for display
            display_value = str(value)
            if len(display_value) > 50:
                display_value = display_value[:50] + "..."
            md += f"- [ ] `{field_name}`: `{display_value}`\n"
    else:
        md += "- [ ] *No non-empty fields submitted*\n"
    
    md += "\n"
    
    return md


def run(parsed_issue, issue, dry_run=False):
    """
    Process horizontal grid cell submission.
    Generate @id from author + timestamp if not provided.
    
    Returns dict with:
    - File path as key, data as value: {'path/to/file.json': data}
    - Metadata keys starting with '_': _author, _contributors, _make_pull
    """
    # If no validation_key, generate @id from author + timestamp
    if not parsed_issue.get('validation_key') and issue.get('author') and issue.get('created_at'):
        id_result = generate_id_from_issue(issue.get('author'), issue.get('created_at'))
        
        data = {
            "@context": "_context",
            "@id": f"tempgrid_{id_result['id']}",
            "@type": ["wcrp:horizontal_grid_cell", "esgvoc:HorizontalGridCells"],
            **parsed_issue
        }
        
        # Return as dict with file path and metadata
        file_path = os.path.join('horizontal_grid_cell', f"{data['@id']}.json")
        
        # Parse contributors
        additional_collaborators = parsed_issue.get('additional_collaborators', 
                                                   parsed_issue.get('collaborators', ''))
        contributors = []
        if additional_collaborators:
            contributors = [c.strip() for c in additional_collaborators.split(',') if c.strip()]
        
        return {
            file_path: data,
            '_author': issue.get('author'),
            '_contributors': contributors,
            '_make_pull': True,  # Always make pull request for grid cells
        }
    
    # Otherwise let generic handler build from validation_key
    return None


def update(files_to_write, parsed_issue, issue, dry_run=False):
    """
    Validate all files with esgvoc pydantic model.
    Generates markdown validation report for each file.
    
    Args:
        files_to_write: Dict of {'path/file.json': data, '_author': ..., '_contributors': [...], '_make_pull': ...}
        parsed_issue: Parsed issue body sections
        issue: Full issue metadata
        dry_run: If True, don't perform side effects
    
    Modifies files_to_write in place, adding '_validation_report' to each data dict.
    Metadata keys (starting with '_') are preserved.
    """
    
    for file_path, data in files_to_write.items():
        # Skip metadata keys (starting with '_')
        if file_path.startswith('_'):
            continue
        
        # Validate with esgvoc pydantic model
        model = pycmipld(DATA_DESCRIPTOR_CLASS_MAPPING.get(kind), **data)
        
        # Generate and store validation report
        data['_validation_report'] = generate_markdown_report(model, data)
