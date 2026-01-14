"""
Markdown Parser for Quiz Generator
Extensible parser with plugin system for custom tags.
"""

import re
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .logger import QuizLogger


class QuestionType(Enum):
    """Supported question types."""
    SINGLE = "single"
    MULTIPLE = "multiple"
    TRUEFALSE = "truefalse"
    MATCHING = "matching"
    ORDERING = "ordering"
    FILLBLANK = "fillblank"
    SHORTANSWER = "shortanswer"


@dataclass
class Answer:
    """Represents an answer option."""
    id: str                     # e.g., "A", "B", "C"
    text: str
    is_correct: bool = False
    feedback: str = ""


@dataclass
class MatchingPair:
    """Represents a matching pair."""
    item_id: str
    item_text: str
    match_value: str


@dataclass
class OrderingItem:
    """Represents an ordering item."""
    id: str
    text: str
    correct_position: int


@dataclass
class FillBlank:
    """Represents a fill-in-the-blank."""
    blank_id: str
    correct_answers: List[str]  # Multiple correct answers (pipe-separated)


@dataclass
class HelperPanel:
    """Represents a helper panel (theory, hint, book, etc.)."""
    panel_type: str             # theory, hint, image, video, embed, explore, book
    content: Dict[str, Any]     # Type-specific content


@dataclass
class Question:
    """Represents a parsed question."""
    id: str
    number: int
    question_type: QuestionType
    text: str
    points: float = 1.0
    
    # Answer options (for single, multiple, truefalse)
    answers: List[Answer] = field(default_factory=list)
    correct_answer: str = ""    # Single correct answer ID(s), comma-separated for multiple
    
    # Matching-specific
    matching_pairs: List[MatchingPair] = field(default_factory=list)
    
    # Ordering-specific
    ordering_items: List[OrderingItem] = field(default_factory=list)
    correct_order: List[str] = field(default_factory=list)
    
    # Fill-blank specific
    fill_blanks: List[FillBlank] = field(default_factory=list)
    fillblank_text: str = ""
    
    # Short answer specific
    sample_answer: str = ""
    
    # Helper panels
    panels: List[HelperPanel] = field(default_factory=list)
    
    # Feedback
    feedback_positive: str = ""
    feedback_negative: str = ""
    explanation: str = ""
    
    # Media
    images: List[Dict] = field(default_factory=list)
    videos: List[Dict] = field(default_factory=list)
    embeds: List[Dict] = field(default_factory=list)
    
    # Code blocks
    code_blocks: List[Dict] = field(default_factory=list)
    
    # Raw/unknown content
    raw_content: str = ""


@dataclass
class Section:
    """Represents a quiz section."""
    id: str
    title: str
    questions: List[Question] = field(default_factory=list)


@dataclass
class ParsedQuiz:
    """Represents a fully parsed quiz."""
    sections: List[Section] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)  # All questions flat
    total_points: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TagHandler:
    """
    Base class for custom tag handlers.
    Extend this to add new ::: tag ::: blocks.
    """
    
    tag_name: str = ""
    
    def can_handle(self, tag: str) -> bool:
        """Check if this handler can process the tag."""
        return tag.lower() == self.tag_name.lower()
    
    def parse(self, content: str, logger: QuizLogger) -> Dict[str, Any]:
        """
        Parse the tag content.
        
        Args:
            content: Raw content inside the tag
            logger: Logger for warnings/errors
            
        Returns:
            Parsed content as dictionary
        """
        raise NotImplementedError


class MarkdownParser:
    """
    Extensible Markdown parser for quiz content.
    Supports custom tag handlers for new ::: blocks.
    """
    
    def __init__(self, logger: Optional[QuizLogger] = None):
        """
        Initialize parser.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or QuizLogger()
        self._tag_handlers: Dict[str, TagHandler] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register built-in tag handlers."""
        # Built-in handlers are implemented inline for simplicity
        # Custom handlers can be registered via register_handler()
        pass
    
    def register_handler(self, handler: TagHandler):
        """
        Register a custom tag handler.
        
        Args:
            handler: TagHandler instance
        """
        self._tag_handlers[handler.tag_name.lower()] = handler
        self.logger.debug(f"Registered tag handler: {handler.tag_name}")
    
    # === Main Parse Methods ===
    
    def parse(self, markdown: str, config: Dict[str, Any] = None) -> ParsedQuiz:
        """
        Parse markdown content into structured quiz data.
        
        Args:
            markdown: Markdown content (without frontmatter)
            config: Configuration dictionary
            
        Returns:
            ParsedQuiz object
        """
        config = config or {}
        
        self.logger.info("Starting markdown parsing")
        
        # Split into sections and questions
        sections, questions = self._split_content(markdown)
        
        # Calculate total points
        total_points = sum(q.points for q in questions)
        
        result = ParsedQuiz(
            sections=sections,
            questions=questions,
            total_points=total_points,
            metadata=config.get('quiz', {})
        )
        
        self.logger.info(
            f"Parsing complete: {len(questions)} questions, {total_points} total points",
            questions=len(questions),
            total_points=total_points
        )
        
        return result
    
    def _split_content(self, markdown: str) -> Tuple[List[Section], List[Question]]:
        """
        Split markdown into sections and questions.
        
        Args:
            markdown: Raw markdown
            
        Returns:
            Tuple of (sections, all_questions)
        """
        sections = []
        all_questions = []
        current_section = None
        question_number = 0
        
        # Split by section headers (# Ενότητα or # Section)
        # and question headers (## Ερώτηση or ## Question)
        
        lines = markdown.split('\n')
        current_block = []
        current_block_type = None  # 'section' or 'question'
        current_line_start = 0
        
        for i, line in enumerate(lines):
            # Check for section header
            if re.match(r'^#\s+(?:Ενότητα|Section|ΕΝΟΤΗΤΑ)', line, re.IGNORECASE):
                # Save previous block
                if current_block and current_block_type == 'question':
                    question_number += 1
                    q = self._parse_question('\n'.join(current_block), question_number, current_line_start)
                    all_questions.append(q)
                    if current_section:
                        current_section.questions.append(q)
                
                # Start new section
                section_title = re.sub(r'^#\s+', '', line).strip()
                current_section = Section(
                    id=f"section_{len(sections) + 1}",
                    title=section_title
                )
                sections.append(current_section)
                current_block = []
                current_block_type = 'section'
                current_line_start = i + 1
                
            # Check for question header
            elif re.match(r'^##\s+(?:Ερώτηση|Question|ΕΡΩΤΗΣΗ)', line, re.IGNORECASE):
                # Save previous question
                if current_block and current_block_type == 'question':
                    question_number += 1
                    q = self._parse_question('\n'.join(current_block), question_number, current_line_start)
                    all_questions.append(q)
                    if current_section:
                        current_section.questions.append(q)
                
                # Start new question
                current_block = [line]
                current_block_type = 'question'
                current_line_start = i + 1
                
            elif current_block_type == 'question':
                current_block.append(line)
        
        # Don't forget last question
        if current_block and current_block_type == 'question':
            question_number += 1
            q = self._parse_question('\n'.join(current_block), question_number, current_line_start)
            all_questions.append(q)
            if current_section:
                current_section.questions.append(q)
        
        return sections, all_questions
    
    def _parse_question(self, block: str, number: int, line_start: int) -> Question:
        """
        Parse a question block.
        
        Args:
            block: Question markdown block
            number: Question number
            line_start: Starting line number in original file
            
        Returns:
            Question object
        """
        question = Question(
            id=f"q{number}",
            number=number,
            question_type=QuestionType.SINGLE,
            text=""
        )
        
        # Extract question header metadata
        header_match = re.match(r'^##\s+(?:Ερώτηση|Question)[^\n]*', block, re.IGNORECASE)
        if header_match:
            header = header_match.group(0)
            
            # Check for type in parentheses
            type_match = re.search(r'\(([^)]+)\)', header)
            if type_match:
                type_hint = type_match.group(1).lower()
                question.question_type = self._detect_type_from_hint(type_hint)
            
            # Remove header from block for further processing
            block = block[header_match.end():].strip()
        
        # Extract points
        points_match = re.search(r'^points:\s*(\d+(?:\.\d+)?)', block, re.MULTILINE | re.IGNORECASE)
        if points_match:
            question.points = float(points_match.group(1))
            block = block[:points_match.start()] + block[points_match.end():]
        
        # Extract type declaration
        type_match = re.search(r'^type:\s*(\w+)', block, re.MULTILINE | re.IGNORECASE)
        if type_match:
            question.question_type = self._detect_type_from_hint(type_match.group(1))
            block = block[:type_match.start()] + block[type_match.end():]
        
        # Parse ::: blocks
        block = self._parse_panels(block, question, line_start)
        
        # Parse code blocks
        block = self._parse_code_blocks(block, question)
        
        # Parse answers/content based on type
        if question.question_type in [QuestionType.SINGLE, QuestionType.MULTIPLE, QuestionType.TRUEFALSE]:
            self._parse_choice_answers(block, question)
        elif question.question_type == QuestionType.MATCHING:
            self._parse_matching(block, question)
        elif question.question_type == QuestionType.ORDERING:
            self._parse_ordering(block, question)
        elif question.question_type == QuestionType.FILLBLANK:
            self._parse_fillblank(block, question)
        elif question.question_type == QuestionType.SHORTANSWER:
            self._parse_shortanswer(block, question)
        
        # Extract question text (everything before answers/special blocks)
        question.text = self._extract_question_text(block, question)
        
        return question
    
    def _detect_type_from_hint(self, hint: str) -> QuestionType:
        """Detect question type from hint string."""
        hint = hint.lower().strip()
        
        type_map = {
            'single': QuestionType.SINGLE,
            'μίας επιλογής': QuestionType.SINGLE,
            'μιας επιλογης': QuestionType.SINGLE,
            'multiple': QuestionType.MULTIPLE,
            'πολλαπλής': QuestionType.MULTIPLE,
            'πολλαπλης': QuestionType.MULTIPLE,
            'truefalse': QuestionType.TRUEFALSE,
            'true/false': QuestionType.TRUEFALSE,
            'σωστό/λάθος': QuestionType.TRUEFALSE,
            'σωστο/λαθος': QuestionType.TRUEFALSE,
            'matching': QuestionType.MATCHING,
            'αντιστοίχιση': QuestionType.MATCHING,
            'αντιστοιχιση': QuestionType.MATCHING,
            'ordering': QuestionType.ORDERING,
            'ταξινόμηση': QuestionType.ORDERING,
            'ταξινομηση': QuestionType.ORDERING,
            'fillblank': QuestionType.FILLBLANK,
            'fill-blank': QuestionType.FILLBLANK,
            'συμπλήρωση': QuestionType.FILLBLANK,
            'συμπληρωση': QuestionType.FILLBLANK,
            'shortanswer': QuestionType.SHORTANSWER,
            'short-answer': QuestionType.SHORTANSWER,
            'σύντομη': QuestionType.SHORTANSWER,
            'συντομη': QuestionType.SHORTANSWER,
            'ανοικτή': QuestionType.SHORTANSWER,
            'ανοικτη': QuestionType.SHORTANSWER,
        }
        
        # Check for keywords
        for key, qtype in type_map.items():
            if key in hint:
                return qtype
        
        return QuestionType.SINGLE
    
    # === Panel Parsing ===
    
    def _parse_panels(self, block: str, question: Question, line_start: int) -> str:
        """
        Parse ::: tag ::: blocks.
        
        Args:
            block: Question block
            question: Question object to update
            line_start: Starting line for error reporting
            
        Returns:
            Block with panels removed
        """
        # Pattern for ::: tag ... :::
        pattern = r':::\s*(\w+)\s*\n(.*?)\n:::'
        
        def replace_panel(match):
            tag = match.group(1).lower()
            content = match.group(2).strip()
            
            panel = self._parse_panel_content(tag, content, line_start)
            if panel:
                question.panels.append(panel)
                
                # Also store in specific lists
                if tag == 'image':
                    question.images.append(panel.content)
                elif tag == 'video':
                    question.videos.append(panel.content)
                elif tag == 'embed':
                    question.embeds.append(panel.content)
            
            return ""  # Remove from block
        
        return re.sub(pattern, replace_panel, block, flags=re.DOTALL)
    
    def _parse_panel_content(self, tag: str, content: str, line_start: int) -> Optional[HelperPanel]:
        """
        Parse content of a ::: tag block.
        
        Args:
            tag: Tag name (theory, hint, image, etc.)
            content: Raw content
            line_start: Line number for error reporting
            
        Returns:
            HelperPanel object or None
        """
        # Check for registered custom handler
        if tag in self._tag_handlers:
            parsed = self._tag_handlers[tag].parse(content, self.logger)
            return HelperPanel(panel_type=tag, content=parsed)
        
        # Built-in handlers
        parsers = {
            'theory': self._parse_text_panel,
            'hint': self._parse_text_panel,
            'explanation': self._parse_text_panel,
            'feedback_positive': self._parse_text_panel,
            'feedback_negative': self._parse_text_panel,
            'image': self._parse_image_panel,
            'video': self._parse_video_panel,
            'embed': self._parse_embed_panel,
            'explore': self._parse_explore_panel,
            'book': self._parse_book_panel,
            'matches': self._parse_matches_panel,
            'items': self._parse_items_panel,
            'blanks': self._parse_blanks_panel,
            'correct_order': self._parse_order_panel,
            'sample_answer': self._parse_text_panel,
        }
        
        if tag in parsers:
            parsed = parsers[tag](content)
            return HelperPanel(panel_type=tag, content=parsed)
        
        # Unknown tag - log warning and return as raw HTML
        self.logger.unknown_tag(tag, line_start, content)
        return HelperPanel(panel_type='raw', content={'html': content, 'original_tag': tag})
    
    def _parse_text_panel(self, content: str) -> Dict[str, Any]:
        """Parse simple text content."""
        return {'text': content.strip()}
    
    def _parse_image_panel(self, content: str) -> Dict[str, Any]:
        """Parse image panel with url, alt, caption, width."""
        result = {'url': '', 'alt': '', 'caption': '', 'width': ''}
        
        for line in content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key in result:
                    result[key] = value
        
        return result
    
    def _parse_video_panel(self, content: str) -> Dict[str, Any]:
        """Parse video panel with url, title, width, height."""
        result = {'url': '', 'title': '', 'width': '560', 'height': '315'}
        
        for line in content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key in result:
                    result[key] = value
        
        return result
    
    def _parse_embed_panel(self, content: str) -> Dict[str, Any]:
        """Parse embed panel with url, title, width, height."""
        result = {'url': '', 'title': '', 'width': '100%', 'height': '400'}
        
        for line in content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key in result:
                    result[key] = value
        
        return result
    
    def _parse_explore_panel(self, content: str) -> Dict[str, Any]:
        """Parse explore panel with list of links."""
        links = []
        
        # Pattern: - [text](url) or - text: url
        for line in content.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue
            
            line = line[1:].strip()
            
            # Markdown link format
            md_match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', line)
            if md_match:
                links.append({'text': md_match.group(1), 'url': md_match.group(2)})
                continue
            
            # Simple format: text: url
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2 and parts[1].strip().startswith('http'):
                    links.append({'text': parts[0].strip(), 'url': parts[1].strip()})
        
        return {'links': links}
    
    def _parse_book_panel(self, content: str) -> Dict[str, Any]:
        """Parse book panel with title, chapter, section, pages."""
        result = {'title': '', 'chapter': '', 'section': '', 'pages': '', 'start_page': 0}
        
        for line in content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key in result:
                    result[key] = value
        
        # Extract start page number
        if result['pages']:
            page_match = re.match(r'(\d+)', result['pages'])
            if page_match:
                result['start_page'] = int(page_match.group(1))
        
        return result
    
    def _parse_matches_panel(self, content: str) -> Dict[str, Any]:
        """Parse matching pairs (item: value)."""
        pairs = []
        
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    pairs.append({
                        'item': parts[0].strip(),
                        'value': parts[1].strip()
                    })
        
        return {'pairs': pairs}
    
    def _parse_items_panel(self, content: str) -> Dict[str, Any]:
        """Parse ordering items."""
        items = []
        
        for line in content.split('\n'):
            line = line.strip()
            # Pattern: 1. text or - text
            match = re.match(r'^(?:(\d+)\.\s*|-\s*)(.+)$', line)
            if match:
                pos = int(match.group(1)) if match.group(1) else len(items) + 1
                items.append({
                    'position': pos,
                    'text': match.group(2).strip()
                })
        
        return {'items': items}
    
    def _parse_blanks_panel(self, content: str) -> Dict[str, Any]:
        """Parse fill-blank answers."""
        blanks = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    blank_id = parts[0].strip()
                    answers = parts[1].strip()
                    blanks[blank_id] = answers  # Can be pipe-separated
        
        return {'blanks': blanks}
    
    def _parse_order_panel(self, content: str) -> Dict[str, Any]:
        """Parse correct order."""
        order = []
        
        # Could be comma-separated or newline-separated
        if ',' in content:
            order = [x.strip() for x in content.split(',')]
        else:
            order = [x.strip() for x in content.split('\n') if x.strip()]
        
        return {'order': order}
    
    # === Answer Parsing ===
    
    def _parse_choice_answers(self, block: str, question: Question):
        """Parse checkbox/radio answer options."""
        # Pattern: - [ ] text (unchecked) or - [x] text (checked)
        pattern = r'-\s*\[([xX ])\]\s*(.+?)(?=\n-\s*\[|\n\n|\n:::|$)'
        
        matches = re.findall(pattern, block, re.DOTALL)
        correct_answers = []
        
        for i, (checked, text) in enumerate(matches):
            answer_id = chr(65 + i)  # A, B, C, ...
            is_correct = checked.lower() == 'x'
            
            answer = Answer(
                id=answer_id,
                text=text.strip(),
                is_correct=is_correct
            )
            question.answers.append(answer)
            
            if is_correct:
                correct_answers.append(answer_id)
        
        question.correct_answer = ','.join(correct_answers)
        
        # Auto-detect multiple choice
        if len(correct_answers) > 1:
            question.question_type = QuestionType.MULTIPLE
    
    def _parse_matching(self, block: str, question: Question):
        """Parse matching question specifics."""
        # Get matches from panel
        for panel in question.panels:
            if panel.panel_type == 'matches':
                pairs = panel.content.get('pairs', [])
                for i, pair in enumerate(pairs):
                    mp = MatchingPair(
                        item_id=f"item{i+1}",
                        item_text=pair['item'],
                        match_value=pair['value']
                    )
                    question.matching_pairs.append(mp)
    
    def _parse_ordering(self, block: str, question: Question):
        """Parse ordering question specifics."""
        # Get items from panel
        for panel in question.panels:
            if panel.panel_type == 'items':
                items = panel.content.get('items', [])
                for item in items:
                    oi = OrderingItem(
                        id=f"step{item['position']}",
                        text=item['text'],
                        correct_position=item['position']
                    )
                    question.ordering_items.append(oi)
            elif panel.panel_type == 'correct_order':
                question.correct_order = panel.content.get('order', [])
        
        # If no explicit order, derive from items
        if not question.correct_order and question.ordering_items:
            question.correct_order = [f"step{i+1}" for i in range(len(question.ordering_items))]
    
    def _parse_fillblank(self, block: str, question: Question):
        """Parse fill-blank question specifics."""
        # Get blanks from panel
        for panel in question.panels:
            if panel.panel_type == 'blanks':
                blanks = panel.content.get('blanks', {})
                for blank_id, answers in blanks.items():
                    fb = FillBlank(
                        blank_id=f"blank{blank_id}",
                        correct_answers=answers.split('|')
                    )
                    question.fill_blanks.append(fb)
        
        # Extract fillblank text (with [___N___] placeholders)
        # Look for code blocks or text with blanks
        fillblank_pattern = r'\[___(\d+)___\]'
        text_with_blanks = block
        
        # Also handle ``` code blocks with blanks
        code_match = re.search(r'```[\w]*\n(.+?)\n```', block, re.DOTALL)
        if code_match:
            question.fillblank_text = code_match.group(1)
    
    def _parse_shortanswer(self, block: str, question: Question):
        """Parse short answer question specifics."""
        for panel in question.panels:
            if panel.panel_type == 'sample_answer':
                question.sample_answer = panel.content.get('text', '')
    
    def _parse_code_blocks(self, block: str, question: Question) -> str:
        """Extract code blocks from content."""
        pattern = r'```(\w*)\n(.*?)\n```'
        
        def extract_code(match):
            language = match.group(1) or 'text'
            code = match.group(2)
            question.code_blocks.append({
                'language': language,
                'code': code
            })
            return f"[[CODE_BLOCK_{len(question.code_blocks) - 1}]]"
        
        return re.sub(pattern, extract_code, block, flags=re.DOTALL)
    
    def _extract_question_text(self, block: str, question: Question) -> str:
        """Extract the main question text."""
        # Remove answer patterns
        text = re.sub(r'-\s*\[[xX ]\].*', '', block)
        
        # Remove already processed markers
        text = re.sub(r'\[\[CODE_BLOCK_\d+\]\]', '', text)
        
        # Remove metadata lines
        text = re.sub(r'^(points|type):\s*\S+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean up
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        # Remove question header if still present
        text = re.sub(r'^##\s+.*\n', '', text)
        
        return text.strip()
