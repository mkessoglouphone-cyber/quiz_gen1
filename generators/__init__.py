"""
Quiz Generators Module
Contains all output format generators.
"""

from .html_generator import HTMLGenerator

# Future generators:
# from .moodle_generator import MoodleXMLGenerator, MoodleGIFTGenerator
# from .google_forms_generator import GoogleFormsGenerator
# from .h5p_generator import H5PGenerator

__all__ = ['HTMLGenerator']
