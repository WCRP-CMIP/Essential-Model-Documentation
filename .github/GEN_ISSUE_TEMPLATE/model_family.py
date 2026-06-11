# Model Family Template Data
from cmipld.utils.ldparse import graph_entry
import time
import requests

def graph_entry_with_retry(url, depth=2, max_retries=3):
    """Wrapper around graph_entry with retry logic for timeout issues"""
    for attempt in range(max_retries):
        try:
            print(f"Fetching {url} (attempt {attempt + 1}/{max_retries})...")
            return graph_entry(url, depth=depth)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  Attempt {attempt + 1} failed: {str(e)[:100]}")
                print(f"  Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"  ❌ All {max_retries} attempts failed")
                raise

DATA = {
    'institution': [i.get('id') for i in requests.get('https://esgvoc.ipsl.fr/api/v1/universe/data_descriptors/organisation/terms').json()],
    'component': graph_entry_with_retry('constants:scientific_domain/_graph.json'),
    'family_type': ['model', 'component'],
    'issue_kind': ['New', 'Modify']
}
