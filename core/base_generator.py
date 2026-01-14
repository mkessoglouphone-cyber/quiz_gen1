"""
Base Generator Abstract Class
All output generators (HTML, Moodle, Google Forms, etc.) extend this class.
"""

import re
import sys
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional

# Handle both relative and absolute imports
try:
    from .parser import ParsedQuiz, MarkdownParser
    from .config_loader import ConfigLoader
    from .logger import QuizLogger
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parser import ParsedQuiz, MarkdownParser
    from config_loader import ConfigLoader
    from logger import QuizLogger


class BaseGenerator(ABC):
    """
    Abstract base class for quiz generators.
    Extend this to create new output formats.
    """
    
    # Override in subclass
    name: str = "base"
    description: str = "Base generator"
    output_extension: str = ".txt"
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 logger: Optional[QuizLogger] = None):
        """
        Initialize generator.
        
        Args:
            config: Optional pre-loaded configuration
            logger: Optional logger instance
        """
        self.config = config or {}
        self.logger = logger or QuizLogger()
        self.config_loader = ConfigLoader()
        self.parser = MarkdownParser(self.logger)
    
    @abstractmethod
    def generate(self, quiz: ParsedQuiz) -> str:
        """
        Generate output from parsed quiz.
        
        Args:
            quiz: Parsed quiz object
            
        Returns:
            Generated output as string
        """
        raise NotImplementedError
    
    def process(self,
                markdown_path: Optional[str] = None,
                markdown_content: Optional[str] = None,
                config_path: Optional[str] = None,
                output_path: Optional[str] = None,
                gui_overrides: Optional[Dict[str, Any]] = None) -> str:
        """
        Full processing pipeline: load config, parse markdown, generate output.
        
        Args:
            markdown_path: Path to markdown file
            markdown_content: Raw markdown content (alternative to path)
            config_path: Optional external config file
            output_path: Optional output file path
            gui_overrides: Optional config overrides from GUI
            
        Returns:
            Generated output string
        """
        self.logger.info(f"Starting {self.name} generation")
        
        # Load markdown content
        if markdown_path:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            self.logger.info(f"Loaded markdown from: {markdown_path}")
        
        if not markdown_content:
            raise ValueError("No markdown content provided")
        
        # Load configuration
        self.config, clean_markdown = self.config_loader.load(
            markdown_content=markdown_content,
            external_config_path=config_path,
            gui_overrides=gui_overrides
        )
        self.logger.debug(f"Configuration loaded: {len(self.config)} sections")
        
        # Parse markdown
        quiz = self.parser.parse(clean_markdown, self.config)
        
        # Generate output
        output = self.generate(quiz)
        
        # Save if output path provided
        if output_path:
            self._save_output(output, output_path)
        
        # Save log file
        log_file = self.config.get('logging', {}).get('file')
        if log_file:
            log_path = Path(output_path).parent / log_file if output_path else Path(log_file)
            self.logger.save_to_file(str(log_path))
        
        return output
    
    def _save_output(self, content: str, path: str):
        """
        Save generated content to file.
        
        Args:
            content: Content to save
            path: Output file path
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Output saved to: {path}")
    
    # === Helper Methods for Subclasses ===
    
    def get_config(self, *keys, default=None):
        """
        Get nested config value.
        
        Args:
            *keys: Path of keys
            default: Default value if not found
            
        Returns:
            Config value or default
        """
        return self.config_loader.get_value(self.config, *keys, default=default)
    
    def escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
    
    def markdown_to_html(self, text: str) -> str:
        """
        Convert basic markdown to HTML.
        
        Args:
            text: Markdown text
            
        Returns:
            HTML string
        """
        if not text:
            return ""
        
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        
        # Code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
        
        # Line breaks
        text = text.replace('\n', '<br>\n')
        
        return text


# No additional imports needed - re is imported at top
