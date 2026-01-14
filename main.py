#!/usr/bin/env python3
"""
Quiz Generator - Command Line Interface
Converts Markdown quiz files to various output formats.

Usage:
    python main.py input.md -o output.html
    python main.py input.md -o output.html -c config.yaml
    python main.py input.md -f html -o ./output/
    
For GUI integration, import and use the generators directly.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config_loader import ConfigLoader
from core.logger import QuizLogger
from core.parser import MarkdownParser
from generators.html_generator import HTMLGenerator


# Available generators (add more as they're created)
GENERATORS = {
    'html': HTMLGenerator,
    # 'moodle-xml': MoodleXMLGenerator,  # Future
    # 'moodle-gift': MoodleGIFTGenerator,  # Future
    # 'google-forms': GoogleFormsGenerator,  # Future
    # 'h5p': H5PGenerator,  # Future
}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Quiz Generator - Convert Markdown to Quiz Formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s quiz.md -o quiz.html
  %(prog)s quiz.md -o quiz.html -c custom_config.yaml
  %(prog)s quiz.md -f html -o ./output/
  %(prog)s --list-formats

Available formats:
  html          Interactive HTML Quiz (default)
  moodle-xml    Moodle XML Import (coming soon)
  moodle-gift   Moodle GIFT Format (coming soon)
  google-forms  Google Forms (coming soon)
  h5p           H5P Package (coming soon)
'''
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input Markdown file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file or directory'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=list(GENERATORS.keys()),
        default='html',
        help='Output format (default: html)'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='External YAML configuration file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file path (default: quiz_generator.log)'
    )
    
    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='List available output formats'
    )
    
    parser.add_argument(
        '--no-console-log',
        action='store_true',
        help='Disable console output'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Quiz Generator v4.1'
    )
    
    args = parser.parse_args()
    
    # List formats
    if args.list_formats:
        print("Available output formats:")
        for fmt, gen_class in GENERATORS.items():
            status = "✓" if gen_class else "○ (coming soon)"
            desc = gen_class.description if gen_class else ""
            print(f"  {fmt:15} {status} {desc}")
        return 0
    
    # Validate input
    if not args.input:
        parser.print_help()
        return 1
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
        if output_path.is_dir():
            output_path = output_path / f"{input_path.stem}.html"
    else:
        output_path = input_path.with_suffix('.html')
    
    # Log file path
    log_file = args.log_file or str(output_path.with_suffix('.log'))
    
    # Create logger
    logger = QuizLogger(
        log_file=log_file,
        level=args.log_level,
        console_output=not args.no_console_log
    )
    
    try:
        # Get generator class
        generator_class = GENERATORS.get(args.format)
        if not generator_class:
            print(f"Error: Format '{args.format}' is not yet available.", file=sys.stderr)
            return 1
        
        # Create generator and process
        generator = generator_class(logger=logger)
        
        output = generator.process(
            markdown_path=str(input_path),
            config_path=args.config,
            output_path=str(output_path)
        )
        
        # Print summary
        summary = logger.get_summary()
        print(f"\n{'='*50}")
        print(f"✓ Generation complete!")
        print(f"  Output: {output_path}")
        print(f"  Log: {log_file}")
        print(f"  Errors: {summary['errors']}, Warnings: {summary['warnings']}")
        print(f"{'='*50}\n")
        
        return 0 if summary['errors'] == 0 else 1
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


# === Programmatic API for GUI Integration ===

def generate_quiz(
    markdown_content: str,
    output_format: str = 'html',
    config: Optional[dict] = None,
    config_path: Optional[str] = None,
    output_path: Optional[str] = None,
    log_level: str = 'INFO'
) -> tuple:
    """
    Generate quiz output programmatically.
    
    Args:
        markdown_content: Raw markdown content
        output_format: Output format ('html', 'moodle-xml', etc.)
        config: Optional config dictionary (overrides)
        config_path: Optional external config file
        output_path: Optional output file path
        log_level: Logging level
        
    Returns:
        Tuple of (output_string, logger)
        
    Usage in GUI:
        output, logger = generate_quiz(markdown_text, 'html', {'quiz': {'title': 'My Quiz'}})
        if logger.error_count == 0:
            # Success!
        else:
            # Show errors
            for error in logger.get_errors():
                show_error(error.message)
    """
    logger = QuizLogger(level=log_level, console_output=False)
    
    generator_class = GENERATORS.get(output_format)
    if not generator_class:
        raise ValueError(f"Unknown format: {output_format}")
    
    generator = generator_class(logger=logger)
    
    output = generator.process(
        markdown_content=markdown_content,
        config_path=config_path,
        output_path=output_path,
        gui_overrides=config
    )
    
    return output, logger


def get_available_formats() -> dict:
    """
    Get dictionary of available output formats.
    
    Returns:
        Dict with format_name -> generator_info
        
    Usage in GUI:
        formats = get_available_formats()
        for name, info in formats.items():
            add_format_option(name, info['description'])
    """
    return {
        name: {
            'name': gen.name if gen else name,
            'description': gen.description if gen else 'Coming soon',
            'extension': gen.output_extension if gen else '',
            'available': gen is not None
        }
        for name, gen in GENERATORS.items()
    }


if __name__ == '__main__':
    sys.exit(main())
