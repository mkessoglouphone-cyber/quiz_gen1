"""
Configuration Loader
Handles loading configuration from:
1. Default config file
2. External YAML file
3. Markdown frontmatter (highest priority)
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class ConfigLoader:
    """
    Loads and merges configuration from multiple sources.
    Priority: Frontmatter > External YAML > Default Config
    """
    
    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "default_config.yaml"
    
    def __init__(self, default_config_path: Optional[str] = None):
        """
        Initialize ConfigLoader.
        
        Args:
            default_config_path: Optional path to default config file
        """
        self.default_config_path = Path(default_config_path) if default_config_path else self.DEFAULT_CONFIG_PATH
        self._default_config = None
    
    @property
    def default_config(self) -> Dict[str, Any]:
        """Lazy load default configuration."""
        if self._default_config is None:
            self._default_config = self._load_yaml_file(self.default_config_path)
        return self._default_config
    
    def _load_yaml_file(self, path: Path) -> Dict[str, Any]:
        """
        Load a YAML file.
        
        Args:
            path: Path to YAML file
            
        Returns:
            Dictionary with configuration
        """
        if not path.exists():
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                return content if content else {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {path}: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading {path}: {e}")
    
    def _extract_frontmatter(self, markdown_content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract YAML frontmatter from markdown content.
        
        Frontmatter is delimited by --- at the start of the file.
        
        Args:
            markdown_content: Raw markdown string
            
        Returns:
            Tuple of (frontmatter_dict, remaining_content)
        """
        # Pattern for frontmatter: starts with ---, ends with ---
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, markdown_content, re.DOTALL)
        
        if not match:
            return {}, markdown_content
        
        frontmatter_text = match.group(1)
        remaining_content = markdown_content[match.end():]
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            return (frontmatter if frontmatter else {}), remaining_content
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML frontmatter: {e}")
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries.
        Override values take precedence.
        
        Args:
            base: Base dictionary
            override: Dictionary with override values
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _normalize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize configuration to standard format.
        Handles shorthand notations and legacy keys.
        
        Args:
            config: Raw configuration dictionary
            
        Returns:
            Normalized configuration
        """
        normalized = config.copy()
        
        # Handle top-level shortcuts
        shortcuts = {
            'title': ('quiz', 'title'),
            'subject': ('quiz', 'subject'),
            'chapter': ('quiz', 'chapter'),
            'class': ('quiz', 'class'),
            'author': ('quiz', 'author'),
            'date': ('quiz', 'date'),
            'time_limit': ('quiz', 'time_limit'),
            'shuffle_questions': ('behavior', 'shuffle_questions'),
            'shuffle_answers': ('behavior', 'shuffle_answers'),
            'passing_score': ('behavior', 'passing_score'),
            'show_explanations': ('behavior', 'show_explanations'),
            'ide_url': ('services', 'ide_url'),
            'email': ('services', 'email'),
            'share_folder': ('services', 'share_folder'),
            'google_docs': ('services', 'google_docs'),
            'book_pdf': ('book', 'pdf_path'),
            'default_language': ('code', 'default_language'),
            'highlight_theme': ('code', 'highlight_theme'),
        }
        
        for shortcut, (section, key) in shortcuts.items():
            if shortcut in normalized and shortcut not in ['quiz', 'behavior', 'services', 'book', 'code']:
                if section not in normalized:
                    normalized[section] = {}
                if isinstance(normalized[section], dict):
                    normalized[section][key] = normalized.pop(shortcut)
        
        # Auto-fill date if "auto"
        if normalized.get('quiz', {}).get('date') == 'auto':
            normalized['quiz']['date'] = datetime.now().strftime('%Y-%m-%d')
        
        return normalized
    
    def load(self, 
             markdown_content: Optional[str] = None,
             external_config_path: Optional[str] = None,
             gui_overrides: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
        """
        Load and merge configuration from all sources.
        
        Priority (highest to lowest):
        1. GUI overrides (for future GUI integration)
        2. Markdown frontmatter
        3. External YAML config file
        4. Default configuration
        
        Args:
            markdown_content: Optional markdown content with frontmatter
            external_config_path: Optional path to external YAML config
            gui_overrides: Optional dict with GUI-provided settings
            
        Returns:
            Tuple of (merged_config, markdown_without_frontmatter)
        """
        # Start with default config
        config = self.default_config.copy()
        
        # Merge external config if provided
        if external_config_path:
            external_config = self._load_yaml_file(Path(external_config_path))
            external_config = self._normalize_config(external_config)
            config = self._deep_merge(config, external_config)
        
        # Extract and merge frontmatter
        remaining_markdown = markdown_content or ""
        if markdown_content:
            frontmatter, remaining_markdown = self._extract_frontmatter(markdown_content)
            frontmatter = self._normalize_config(frontmatter)
            config = self._deep_merge(config, frontmatter)
        
        # Apply GUI overrides (highest priority)
        if gui_overrides:
            gui_overrides = self._normalize_config(gui_overrides)
            config = self._deep_merge(config, gui_overrides)
        
        return config, remaining_markdown
    
    def get_value(self, config: Dict, *keys, default=None):
        """
        Safely get a nested value from config.
        
        Args:
            config: Configuration dictionary
            *keys: Path of keys to traverse
            default: Default value if not found
            
        Returns:
            Value at path or default
        """
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass
