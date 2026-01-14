"""
Quiz Generator Logger
Handles logging of errors, warnings, and info messages.
Outputs to both console and log file.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class LogEntry:
    """Represents a single log entry."""
    level: LogLevel
    message: str
    source: str = ""           # e.g., "question_5", "config", "parser"
    line_number: int = 0       # Line number in markdown (if applicable)
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_string(self) -> str:
        """Convert to formatted string."""
        parts = [f"[{self.level.value}]"]
        
        if self.source:
            parts.append(f"[{self.source}]")
        
        if self.line_number > 0:
            parts.append(f"(line {self.line_number})")
        
        parts.append(self.message)
        
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "line_number": self.line_number,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class QuizLogger:
    """
    Logger for quiz generation process.
    Collects all messages and can export to file or GUI.
    """
    
    def __init__(self, 
                 log_file: Optional[str] = None,
                 level: str = "INFO",
                 console_output: bool = True):
        """
        Initialize logger.
        
        Args:
            log_file: Optional path to log file
            level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
            console_output: Whether to print to console
        """
        self.log_file = Path(log_file) if log_file else None
        self.level = LogLevel[level.upper()]
        self.console_output = console_output
        
        self.entries: List[LogEntry] = []
        self._setup_python_logger()
    
    def _setup_python_logger(self):
        """Setup Python's logging module."""
        self._logger = logging.getLogger("QuizGenerator")
        self._logger.setLevel(getattr(logging, self.level.value))
        
        # Clear existing handlers
        self._logger.handlers = []
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.level.value))
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on level."""
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        return level_order.index(level) >= level_order.index(self.level)
    
    def _log(self, level: LogLevel, message: str, source: str = "", 
             line_number: int = 0, details: Dict[str, Any] = None):
        """
        Internal logging method.
        
        Args:
            level: Log level
            message: Log message
            source: Source identifier (e.g., "question_5")
            line_number: Line number in markdown
            details: Additional details dictionary
        """
        entry = LogEntry(
            level=level,
            message=message,
            source=source,
            line_number=line_number,
            details=details or {}
        )
        
        self.entries.append(entry)
        
        if self._should_log(level):
            log_msg = entry.to_string()
            if level == LogLevel.DEBUG:
                self._logger.debug(log_msg)
            elif level == LogLevel.INFO:
                self._logger.info(log_msg)
            elif level == LogLevel.WARNING:
                self._logger.warning(log_msg)
            elif level == LogLevel.ERROR:
                self._logger.error(log_msg)
    
    def debug(self, message: str, source: str = "", line_number: int = 0, **details):
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, source, line_number, details)
    
    def info(self, message: str, source: str = "", line_number: int = 0, **details):
        """Log info message."""
        self._log(LogLevel.INFO, message, source, line_number, details)
    
    def warning(self, message: str, source: str = "", line_number: int = 0, **details):
        """Log warning message."""
        self._log(LogLevel.WARNING, message, source, line_number, details)
    
    def error(self, message: str, source: str = "", line_number: int = 0, **details):
        """Log error message."""
        self._log(LogLevel.ERROR, message, source, line_number, details)
    
    def unknown_tag(self, tag: str, line_number: int = 0, content: str = ""):
        """Log unknown/unrecognized tag."""
        self.warning(
            f"Unknown tag '::: {tag}' - rendering as plain HTML",
            source="parser",
            line_number=line_number,
            tag=tag,
            content_preview=content[:100] if content else ""
        )
    
    def parse_error(self, message: str, line_number: int = 0, content: str = ""):
        """Log parsing error."""
        self.error(
            f"Parse error: {message}",
            source="parser",
            line_number=line_number,
            content_preview=content[:100] if content else ""
        )
    
    # === Summary Methods ===
    
    @property
    def error_count(self) -> int:
        """Count of error entries."""
        return sum(1 for e in self.entries if e.level == LogLevel.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Count of warning entries."""
        return sum(1 for e in self.entries if e.level == LogLevel.WARNING)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all log entries."""
        return {
            "total_entries": len(self.entries),
            "errors": self.error_count,
            "warnings": self.warning_count,
            "infos": sum(1 for e in self.entries if e.level == LogLevel.INFO),
            "has_errors": self.error_count > 0
        }
    
    def get_errors(self) -> List[LogEntry]:
        """Get all error entries."""
        return [e for e in self.entries if e.level == LogLevel.ERROR]
    
    def get_warnings(self) -> List[LogEntry]:
        """Get all warning entries."""
        return [e for e in self.entries if e.level == LogLevel.WARNING]
    
    # === Export Methods ===
    
    def save_to_file(self, path: Optional[str] = None):
        """
        Save log to file.
        
        Args:
            path: Optional custom path, uses self.log_file if not provided
        """
        output_path = Path(path) if path else self.log_file
        if not output_path:
            return
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Quiz Generator Log\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"{'=' * 60}\n\n")
            
            summary = self.get_summary()
            f.write(f"Summary: {summary['errors']} errors, {summary['warnings']} warnings\n\n")
            
            if self.entries:
                f.write("Entries:\n")
                f.write("-" * 40 + "\n")
                for entry in self.entries:
                    f.write(f"{entry.timestamp.strftime('%H:%M:%S')} {entry.to_string()}\n")
                    if entry.details:
                        for k, v in entry.details.items():
                            f.write(f"    {k}: {v}\n")
            else:
                f.write("No log entries.\n")
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all entries to list of dicts (for GUI)."""
        return [e.to_dict() for e in self.entries]
    
    def clear(self):
        """Clear all entries."""
        self.entries = []
    
    def __str__(self) -> str:
        """String representation."""
        summary = self.get_summary()
        return f"QuizLogger({summary['errors']} errors, {summary['warnings']} warnings)"
