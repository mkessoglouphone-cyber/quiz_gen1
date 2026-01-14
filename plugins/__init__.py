"""
Quiz Generator Plugins Module
Contains extensible tag handlers for custom ::: blocks.
"""

from ..core.parser import TagHandler

__all__ = ['TagHandler']

# Example of creating a custom tag handler:
#
# class MyCustomTagHandler(TagHandler):
#     tag_name = "myblock"
#     
#     def parse(self, content: str, logger) -> Dict[str, Any]:
#         # Parse content and return dict
#         return {'data': content}
#
# Then register in parser:
# parser.register_handler(MyCustomTagHandler())
