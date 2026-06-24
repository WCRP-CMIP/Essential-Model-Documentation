"""
CV Field Mapper

Utilities for mapping controlled vocabulary fields from ui_label to validation_key.
Supports bidirectional lookup and caching for efficient graph traversal.
"""

import json
import os
from typing import Dict, Optional, Tuple


class CVMapper:
    """Maps controlled vocabulary fields between ui_label and validation_key."""
    
    # Define CV field graph locations
    CV_GRAPHS = {
        'grid_type': 'constants:grid_type/_graph.json',
        'grid_mapping': 'constants:grid_mapping/_graph.json',
        'region': 'constants:region/_graph.json',
        'temporal_refinement': 'constants:temporal_refinement/_graph.json',
        'units': 'constants:units/_graph.json',
        'truncation_method': 'constants:truncation_method/_graph.json',
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize mapper with optional cache directory."""
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '.cv_cache')
        self._reverse_maps: Dict[str, Dict[str, str]] = {}
        self._forward_maps: Dict[str, Dict[str, str]] = {}
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def load_graph_data(self, field: str, graph_content: list) -> Tuple[Dict, Dict]:
        """
        Load graph data and create forward and reverse lookup maps.
        
        Args:
            field: Field name (e.g., 'grid_type')
            graph_content: List of graph entries from the JSON graph
            
        Returns:
            Tuple of (reverse_map, forward_map) where:
            - reverse_map: ui_label -> validation_key
            - forward_map: validation_key -> ui_label
        """
        reverse_map = {}
        forward_map = {}
        
        for entry in graph_content:
            validation_key = entry.get('validation_key') or entry.get('@id')
            ui_label = entry.get('ui_label')
            
            if validation_key and ui_label:
                reverse_map[ui_label] = validation_key
                forward_map[validation_key] = ui_label
        
        return reverse_map, forward_map
    
    def ui_label_to_validation_key(self, field: str, ui_label: str) -> Optional[str]:
        """
        Convert ui_label to validation_key for a given field.
        
        Args:
            field: Field name (e.g., 'grid_type')
            ui_label: The ui_label value to convert
            
        Returns:
            The validation_key, or None if not found
        """
        if not ui_label or field not in self.CV_GRAPHS:
            return ui_label
        
        if field not in self._reverse_maps:
            return None
        
        return self._reverse_maps[field].get(ui_label, None)
    
    def validation_key_to_ui_label(self, field: str, validation_key: str) -> Optional[str]:
        """
        Convert validation_key to ui_label for a given field.
        
        Args:
            field: Field name (e.g., 'grid_type')
            validation_key: The validation_key value to convert
            
        Returns:
            The ui_label, or None if not found
        """
        if not validation_key or field not in self.CV_GRAPHS:
            return validation_key
        
        if field not in self._forward_maps:
            return None
        
        return self._forward_maps[field].get(validation_key, None)
    
    def is_already_validation_key(self, field: str, value: str) -> bool:
        """Check if a value is already a validation_key."""
        if not value or field not in self.CV_GRAPHS:
            return False
        
        if field not in self._forward_maps:
            return False
        
        return value in self._forward_maps[field]
    
    def cache_graph(self, field: str, graph_content: list) -> None:
        """Cache a graph and its maps."""
        reverse_map, forward_map = self.load_graph_data(field, graph_content)
        self._reverse_maps[field] = reverse_map
        self._forward_maps[field] = forward_map
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded graphs."""
        return {
            field: {
                'entries': len(self._reverse_maps.get(field, {}))
            }
            for field in self.CV_GRAPHS.keys()
        }