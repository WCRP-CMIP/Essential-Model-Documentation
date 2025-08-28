# Per-File Template Generator

**Simple, minimal template generator that processes each CSV/Python pair independently.**

## 🎯 **Ultra-Simple Design**

Each template is just **2 files** with **minimal code**:

```
templates/
├── component_submission.csv    # Field definitions  
├── component_submission.py     # Simple data dictionary
├── top_level_model.csv         # Field definitions
├── top_level_model.py          # Simple data dictionary
└── ...
```

## 📝 **Template Files**

### 1. CSV File (`template_name.csv`)
Standard field definitions (same as before):

```csv
field_order,field_type,field_id,label,description,data_source,required,placeholder,options_type,default_value
1,input,name,Name,Your name,none,true,"e.g., John",,
2,dropdown,type,Type,Select type,contact_types,true,,dict_keys,
```

### 2. Python File (`template_name.py`)
**Super simple** - just configuration and data:

```python
# Template Configuration
TEMPLATE_CONFIG = {
    'name': 'My Template',
    'description': 'Template description',
    'title': '[EMD] My Template',
    'labels': ['emd-submission', 'category']
}

# Data for Jinja2
DATA = {
    'contact_types': {
        'technical': {'id': 'technical'},
        'support': {'id': 'support'}
    },
    'priorities': ['Low', 'High'],
    # For hardcoded options: fieldname_options
    'type_options': ['Option 1', 'Option 2']
}
```

**That's it!** No classes, no complex logic, just data.

## 🚀 **Usage**

```bash
# Process all templates in default directory
python per_file_generator.py

# Specify directories
python per_file_generator.py ./templates ./output
```

## 🔄 **How It Works**

1. **Finds all CSV files** in template directory
2. **For each CSV**, looks for matching Python file
3. **Loads data** from Python file using simple `exec()`
4. **Generates YAML** by feeding data directly to field generation
5. **Processes independently** - each template pair is self-contained

## 📊 **Data Usage**

The generator looks for these variables in Python files:

- **`TEMPLATE_CONFIG`** - Required header information
- **`DATA`** - Dictionary of data for Jinja2 templates

### Data Source Mapping

| CSV `data_source` | Python `DATA` key | Usage |
|-------------------|-------------------|--------|
| `realms` | `DATA['realms']` | Dict for `dict_keys` |
| `priorities` | `DATA['priorities']` | List for `list` |
| `contact_method` | `DATA['contact_method_options']` | List for `hardcoded` |

### Options Types

- **`dict_keys`**: Uses `DATA[data_source].keys()`
- **`list`**: Uses `DATA[data_source]` directly
- **`dict_checkbox`**: Dict keys as checkbox labels
- **`hardcoded`**: Uses `DATA['{field_id}_options']`
- **`tier_hardcoded`**: Built-in `['0', '1', '2', '3']`

## ✅ **Adding New Templates**

1. **Create CSV**: Define your fields
2. **Create Python**: Add config and data
3. **Run generator**: Process automatically

**Example - New Survey Template:**

`survey.csv`:
```csv
field_order,field_type,field_id,label,description,data_source,required,placeholder,options_type,default_value
1,input,name,Name,Your name,none,true,,
2,dropdown,satisfaction,Satisfaction,Rate your satisfaction,satisfaction_levels,true,,list,
```

`survey.py`:
```python
TEMPLATE_CONFIG = {
    'name': 'Survey Form',
    'description': 'Customer satisfaction survey',
    'title': '[Survey] Satisfaction',
    'labels': ['survey']
}

DATA = {
    'satisfaction_levels': ['Poor', 'Fair', 'Good', 'Excellent']
}
```

Done! No complex inheritance or classes needed.

## 🎯 **Benefits**

- ✅ **Ultra-simple**: Python files are just data
- ✅ **Independent**: Each template processes alone
- ✅ **Minimal code**: Generator has minimal logic
- ✅ **Easy to understand**: No complex abstractions
- ✅ **Self-contained**: Templates don't depend on each other
- ✅ **Fast**: Processes only what's needed

## 📋 **Example Output**

```
🔧 Per-File Template Generator
==============================
📁 Template directory: ./templates
📁 Output directory: ../ISSUE_TEMPLATE
🔍 Found 4 CSV files

📝 Processing component_submission...
    ✅ Loaded config: Model Component Submission
    ✅ Loaded data: 2 items
    ✅ Loaded 9 fields from CSV
    ✅ Generated component_submission.yml (3247 chars)

📝 Processing top_level_model...
    ✅ Loaded config: Top Level Model Submission
    ✅ Loaded data: 2 items
    ✅ Loaded 8 fields from CSV
    ✅ Generated top_level_model.yml (2891 chars)

🎯 Results:
  ✅ Success: 4/4
🎉 Templates generated successfully!
```

**Each template is now completely independent with minimal, easy-to-understand Python files!** 🎊
