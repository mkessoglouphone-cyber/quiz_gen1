"""
HTML Quiz Generator
Generates interactive HTML quiz from parsed markdown.
"""

import re
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Handle both relative and absolute imports
try:
    from ..core.base_generator import BaseGenerator
    from ..core.parser import (
        ParsedQuiz, Question, QuestionType, Section,
        Answer, MatchingPair, OrderingItem, HelperPanel
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.base_generator import BaseGenerator
    from core.parser import (
        ParsedQuiz, Question, QuestionType, Section,
        Answer, MatchingPair, OrderingItem, HelperPanel
    )


class HTMLGenerator(BaseGenerator):
    """
    Generates interactive HTML quiz files.
    """
    
    name = "html"
    description = "Interactive HTML Quiz Generator"
    output_extension = ".html"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._template = None
    
    def generate(self, quiz: ParsedQuiz) -> str:
        """
        Generate HTML quiz from parsed quiz data.
        
        Args:
            quiz: Parsed quiz object
            
        Returns:
            Complete HTML document
        """
        self.logger.info(f"Generating HTML for {len(quiz.questions)} questions")
        
        # Build HTML parts
        html_parts = {
            'head': self._generate_head(),
            'body_attrs': self._generate_body_attrs(),
            'top_controls': self._generate_top_controls(),
            'student_info': self._generate_student_info(),
            'quiz_header': self._generate_quiz_header(quiz),
            'progress': self._generate_progress(quiz),
            'content': self._generate_content(quiz),
            'navigation': self._generate_navigation(),
            'results': self._generate_results(),
            'scripts': self._generate_scripts(),
        }
        
        # Assemble final HTML
        return self._assemble_html(html_parts)
    
    # === Head Section ===
    
    def _generate_head(self) -> str:
        """Generate HTML head section."""
        title = self.get_config('quiz', 'title', default='Quiz')
        css_file = self.get_config('output', 'css_file', default='quiz-interactive.css')
        highlight_theme = self.get_config('code', 'highlight_theme', default='atom-one-dark')
        
        return f'''<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self._escape(title)}</title>
  
  <!-- KaTeX for Math -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  
  <!-- Highlight.js for Code -->
  <link id="hljs-dark" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/atom-one-dark.min.css">
  <link id="hljs-light" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/atom-one-light.min.css" disabled>
  
  <!-- Quiz CSS -->
  <link rel="stylesheet" href="{css_file}">
</head>'''
    
    # === Body Attributes ===
    
    def _generate_body_attrs(self) -> str:
        """Generate body tag attributes."""
        attrs = []
        
        # Data attributes for services
        services = {
            'data-ide-url': self.get_config('services', 'ide_url', default=''),
            'data-email': self.get_config('services', 'email', default=''),
            'data-share-folder': self.get_config('services', 'share_folder', default=''),
            'data-google-docs': self.get_config('services', 'google_docs', default=''),
            'data-book-pdf': self.get_config('book', 'pdf_path', default=''),
            'data-default-date': self.get_config('quiz', 'date', default=''),
        }
        
        for key, value in services.items():
            if value:
                attrs.append(f'{key}="{self._escape(str(value))}"')
        
        return ' '.join(attrs)
    
    # === Top Controls ===
    
    def _generate_top_controls(self) -> str:
        """Generate top control bar (view toggle, timer, theme)."""
        time_limit = self.get_config('quiz', 'time_limit', default=20)
        minutes = str(time_limit).zfill(2)
        
        return f'''<div class="top-controls">
      <div class="view-toggle">
        <button class="view-toggle-btn active" data-view="all" onclick="setViewMode('all')">📋 Όλες</button>
        <button class="view-toggle-btn" data-view="single" onclick="setViewMode('single')">1️⃣ Μία-μία</button>
      </div>
      
      <div class="timer" id="timerContainer">
        <span>⏱️</span>
        <span id="timer-display">{minutes}:00</span>
      </div>
      
      <button class="theme-toggle" onclick="toggleTheme()">🌙</button>
    </div>'''
    
    # === Student Info ===
    
    def _generate_student_info(self) -> str:
        """Generate student info form."""
        students = self.get_config('students', default=[])
        classes = self.get_config('classes', default=[])
        
        # Student options
        student_options = '<option value="">-- Επιλέξτε --</option>\n'
        for student in students:
            student_options += f'            <option value="{self._escape(student)}">{self._escape(student)}</option>\n'
        student_options += '            <option value="__custom__">Άλλο...</option>'
        
        # Class options
        class_options = '<option value="">-- Επιλέξτε --</option>\n'
        for cls in classes:
            class_options += f'            <option value="{self._escape(cls)}">{self._escape(cls)}</option>\n'
        class_options += '            <option value="__custom__">Άλλο...</option>'
        
        return f'''<div class="student-info" id="studentInfo">
      <div class="student-info-title">👤 Στοιχεία Μαθητή</div>
      <div class="student-info-grid">
        <div class="student-field">
          <label class="student-field-label">Ονοματεπώνυμο</label>
          <select id="studentName" onchange="handleCustomSelect(this, 'studentNameCustom')">
            {student_options}
          </select>
          <div class="custom-input-wrapper" id="studentNameCustomWrapper">
            <input type="text" id="studentNameCustom" placeholder="Γράψτε το όνομά σας">
          </div>
        </div>
        
        <div class="student-field">
          <label class="student-field-label">Τμήμα</label>
          <select id="studentClass" onchange="handleCustomSelect(this, 'studentClassCustom')">
            {class_options}
          </select>
          <div class="custom-input-wrapper" id="studentClassCustomWrapper">
            <input type="text" id="studentClassCustom" placeholder="Γράψτε το τμήμα">
          </div>
        </div>
        
        <div class="student-field">
          <label class="student-field-label">Ημερομηνία</label>
          <select id="dateSelect" onchange="handleDateSelect()">
            <option value="current">Τρέχουσα</option>
            <option value="custom">Επιλογή...</option>
          </select>
          <div class="custom-input-wrapper" id="dateCustomWrapper">
            <input type="datetime-local" id="dateCustom">
          </div>
        </div>
        
        <div class="student-field">
          <label class="student-field-label">Κλίμακα Βαθμού</label>
          <select id="gradeScale">
            <option value="10">0-10</option>
            <option value="20" selected>0-20</option>
            <option value="100">0-100</option>
          </select>
        </div>
      </div>
    </div>'''
    
    # === Quiz Header ===
    
    def _generate_quiz_header(self, quiz: ParsedQuiz) -> str:
        """Generate quiz header with title and metadata."""
        title = self.get_config('quiz', 'title', default='Quiz')
        subject = self.get_config('quiz', 'subject', default='')
        
        return f'''<div class="quiz-header">
      <h1 class="quiz-title">📝 {self._escape(title)}</h1>
      <div class="quiz-meta">
        <span class="subject">📚 {self._escape(subject)}</span>
        <span class="questions">📝 <span id="totalQ">{len(quiz.questions)}</span> ερωτήσεις</span>
        <span class="points">⭐ <span id="totalPoints">{quiz.total_points}</span> βαθμοί</span>
      </div>
    </div>'''
    
    # === Progress Bar ===
    
    def _generate_progress(self, quiz: ParsedQuiz) -> str:
        """Generate progress bar."""
        return f'''<div class="progress-container">
      <div class="progress-info">
        <span>Ερώτηση <span id="currentQ">1</span>/<span id="totalQNav">{len(quiz.questions)}</span></span>
        <span id="answeredCount">0 απαντημένες</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
      </div>
    </div>'''
    
    # === Main Content (Sections & Questions) ===
    
    def _generate_content(self, quiz: ParsedQuiz) -> str:
        """Generate main quiz content."""
        content = []
        
        if quiz.sections:
            # Generate with sections
            for section in quiz.sections:
                content.append(self._generate_section_header(section))
                for question in section.questions:
                    content.append(self._generate_question(question))
        else:
            # Generate without sections
            for question in quiz.questions:
                content.append(self._generate_question(question))
        
        return '\n\n'.join(content)
    
    def _generate_section_header(self, section: Section) -> str:
        """Generate section header."""
        return f'''<div class="section-header" id="{section.id}">
      <h2 class="section-title">📖 {self._escape(section.title)}</h2>
    </div>'''
    
    # === Question Generation ===
    
    def _generate_question(self, q: Question) -> str:
        """Generate a single question card."""
        # Question type label
        type_labels = {
            QuestionType.SINGLE: 'Μίας επιλογής',
            QuestionType.MULTIPLE: 'Πολλαπλής επιλογής',
            QuestionType.TRUEFALSE: 'Σωστό/Λάθος',
            QuestionType.MATCHING: 'Αντιστοίχιση',
            QuestionType.ORDERING: 'Ταξινόμηση',
            QuestionType.FILLBLANK: 'Συμπλήρωση',
            QuestionType.SHORTANSWER: 'Ανοικτή',
        }
        type_label = type_labels.get(q.question_type, 'Ερώτηση')
        
        # Data attributes
        data_attrs = [
            f'data-type="{q.question_type.value}"',
            f'data-points="{q.points}"',
        ]
        
        # Add correct answer data
        if q.question_type in [QuestionType.SINGLE, QuestionType.TRUEFALSE]:
            data_attrs.append(f'data-correct="{q.correct_answer}"')
        elif q.question_type == QuestionType.MULTIPLE:
            data_attrs.append(f'data-correct="{q.correct_answer}"')
        elif q.question_type == QuestionType.MATCHING:
            matches = {f"item{i+1}": mp.match_value for i, mp in enumerate(q.matching_pairs)}
            data_attrs.append(f"data-correct='{json.dumps(matches)}'")
        elif q.question_type == QuestionType.ORDERING:
            data_attrs.append(f'data-correct="{",".join(q.correct_order)}"')
        elif q.question_type == QuestionType.FILLBLANK:
            blanks = {fb.blank_id: '|'.join(fb.correct_answers) for fb in q.fill_blanks}
            data_attrs.append(f"data-correct='{json.dumps(blanks)}'")
        
        # Add feedback data
        if q.feedback_positive:
            data_attrs.append(f'data-feedback-positive="{self._escape(q.feedback_positive)}"')
        if q.feedback_negative:
            data_attrs.append(f'data-feedback-negative="{self._escape(q.feedback_negative)}"')
        if q.sample_answer:
            escaped_sample = self._escape(q.sample_answer).replace('\n', '&#10;')
            data_attrs.append(f'data-sample-answer="{escaped_sample}"')
        
        # Extract feedback from panels
        for panel in q.panels:
            if panel.panel_type == 'feedback_positive' and not q.feedback_positive:
                text = panel.content.get('text', '')
                data_attrs.append(f'data-feedback-positive="{self._escape(text)}"')
            elif panel.panel_type == 'feedback_negative' and not q.feedback_negative:
                text = panel.content.get('text', '')
                data_attrs.append(f'data-feedback-negative="{self._escape(text)}"')
        
        data_attrs_str = ' '.join(data_attrs)
        
        # Generate content based on type
        answers_html = self._generate_answers(q)
        
        # Generate helper buttons and panels
        helper_html = self._generate_helper_panels(q)
        
        # Generate media (images, videos, embeds in question text area)
        media_html = self._generate_media(q)
        
        # Generate code blocks
        code_html = self._generate_code_blocks(q)
        
        # Process question text (convert markdown)
        question_text = self._process_question_text(q.text)
        
        return f'''<div class="question-card" id="{q.id}" {data_attrs_str}>
      <div class="question-header">
        <span class="question-number">{q.number}</span>
        <span class="question-type">{type_label}</span>
        <span class="question-points">{q.points} {"βαθμός" if q.points == 1 else "βαθμοί"}</span>
      </div>
      <div class="question-text">{question_text}</div>
      {media_html}
      {code_html}
      {answers_html}
      {helper_html}
    </div>'''
    
    def _generate_answers(self, q: Question) -> str:
        """Generate answer section based on question type."""
        if q.question_type in [QuestionType.SINGLE, QuestionType.TRUEFALSE]:
            return self._generate_choice_answers(q, 'radio')
        elif q.question_type == QuestionType.MULTIPLE:
            return self._generate_choice_answers(q, 'checkbox')
        elif q.question_type == QuestionType.MATCHING:
            return self._generate_matching_answers(q)
        elif q.question_type == QuestionType.ORDERING:
            return self._generate_ordering_answers(q)
        elif q.question_type == QuestionType.FILLBLANK:
            return self._generate_fillblank_answers(q)
        elif q.question_type == QuestionType.SHORTANSWER:
            return self._generate_shortanswer(q)
        
        return ''
    
    def _generate_choice_answers(self, q: Question, input_type: str) -> str:
        """Generate radio/checkbox answer options."""
        options = []
        data_type = 'multiple' if input_type == 'checkbox' else 'single'
        
        for answer in q.answers:
            options.append(f'''<li class="answer-option" data-type="{data_type}">
          <input type="{input_type}" name="{q.id}" id="{q.id}{answer.id.lower()}" value="{answer.id}">
          <label class="answer-label" for="{q.id}{answer.id.lower()}">
            <span class="answer-marker"></span>
            <span class="answer-text">{self._process_inline_markdown(answer.text)}</span>
          </label>
        </li>''')
        
        return f'''<ul class="answers-list">
        {chr(10).join(options)}
      </ul>'''
    
    def _generate_matching_answers(self, q: Question) -> str:
        """Generate matching question interface."""
        rows = []
        all_values = [mp.match_value for mp in q.matching_pairs]
        
        # Create options HTML (same for all dropdowns)
        options_html = '<option value="">-- Επιλέξτε --</option>\n'
        for val in all_values:
            options_html += f'            <option class="matching-option" value="{self._escape(val)}">{self._escape(val)}</option>\n'
        
        for i, mp in enumerate(q.matching_pairs):
            rows.append(f'''<div class="matching-row" data-item="{mp.item_id}">
          <div class="matching-item"><code>{self._escape(mp.item_text)}</code></div>
          <div class="matching-arrow">→</div>
          <select class="matching-select" data-item="{mp.item_id}">
            {options_html}
          </select>
          <span class="match-feedback"></span>
        </div>''')
        
        return f'''<div class="matching-container">
        {chr(10).join(rows)}
      </div>'''
    
    def _generate_ordering_answers(self, q: Question) -> str:
        """Generate ordering question interface."""
        items = []
        
        # Shuffle items for display (but keep track of correct order)
        import random
        display_items = q.ordering_items.copy()
        random.shuffle(display_items)
        
        for item in display_items:
            items.append(f'''<div class="ordering-item" data-id="{item.id}">
          <span class="ordering-handle">☰</span>
          <span class="ordering-text">{self._escape(item.text)}</span>
          <div class="order-buttons">
            <button class="order-up">▲</button>
            <button class="order-down">▼</button>
          </div>
          <span class="order-feedback"></span>
        </div>''')
        
        return f'''<div class="ordering-list">
        {chr(10).join(items)}
      </div>'''
    
    def _generate_fillblank_answers(self, q: Question) -> str:
        """Generate fill-in-the-blank interface."""
        # Use fillblank_text or reconstruct from code blocks
        text = q.fillblank_text or q.text
        
        # Replace [___N___] with input fields
        def replace_blank(match):
            blank_num = match.group(1)
            return f'<input type="text" class="fillblank-input" data-blank="blank{blank_num}" style="width: 80px;">'
        
        processed_text = re.sub(r'\[___(\d+)___\]', replace_blank, text)
        
        # If there's code, wrap in pre
        if q.code_blocks:
            code = q.code_blocks[0]
            lang = code.get('language', 'text')
            code_text = code.get('code', '')
            # Process blanks in code
            code_text = re.sub(r'\[___(\d+)___\]', replace_blank, code_text)
            return f'''<div class="fillblank-container">
        <pre style="background: var(--code-bg); padding: 1.5em; border-radius: 12px; line-height: 2;">
<code class="language-{lang}">{code_text}</code></pre>
      </div>'''
        
        return f'''<div class="fillblank-container">
        {processed_text}
      </div>'''
    
    def _generate_shortanswer(self, q: Question) -> str:
        """Generate short answer textarea."""
        return f'''<div class="shortanswer-container">
        <textarea class="shortanswer-textarea" placeholder="Γράψτε την απάντησή σας..."></textarea>
      </div>'''
    
    # === Helper Panels ===
    
    def _generate_helper_panels(self, q: Question) -> str:
        """Generate helper buttons and panels."""
        buttons = []
        panels = []
        
        panel_configs = {
            'theory': ('📚 Θεωρία', 'panel-theory'),
            'hint': ('💡 Υπόδειξη', 'panel-hint'),
            'image': ('🖼️ Εικόνα', 'panel-image'),
            'explore': ('🔗 Explore', 'panel-explore'),
            'book': ('📖 Βιβλίο', 'panel-book'),
        }
        
        for panel in q.panels:
            ptype = panel.panel_type
            if ptype in panel_configs:
                btn_text, panel_class = panel_configs[ptype]
                panel_id = f"{q.id}-{ptype}"
                
                buttons.append(
                    f'<button class="helper-btn" onclick="togglePanel(\'{panel_id}\')">{btn_text}</button>'
                )
                
                panel_content = self._generate_panel_content(panel, q.id)
                panels.append(f'''<div class="panel {panel_class}" id="{panel_id}" style="display:none">
        <div class="panel-content">
          {panel_content}
        </div>
      </div>''')
        
        # Add explanation panel (shown after submit)
        if q.explanation:
            panels.append(f'''<div class="panel panel-explanation" id="{q.id}-explanation" style="display:none">
        <div class="panel-content">
          <h4>📝 Επεξήγηση</h4>
          {self._process_inline_markdown(q.explanation)}
        </div>
      </div>''')
        
        if not buttons:
            return ''
        
        return f'''
      <div class="helper-buttons">
        {chr(10).join(buttons)}
      </div>
      {chr(10).join(panels)}'''
    
    def _generate_panel_content(self, panel: HelperPanel, question_id: str) -> str:
        """Generate content for a specific panel type."""
        ptype = panel.panel_type
        content = panel.content
        
        if ptype == 'theory':
            return f"<h4>📚 Θεωρία</h4>\n{self._process_inline_markdown(content.get('text', ''))}"
        
        elif ptype == 'hint':
            return f"💡 <strong>Υπόδειξη:</strong> {self._process_inline_markdown(content.get('text', ''))}"
        
        elif ptype == 'image':
            url = content.get('url', '')
            alt = content.get('alt', '')
            caption = content.get('caption', '')
            width = content.get('width', '')
            style = f'max-width: {width}px;' if width else ''
            caption_html = f'<figcaption style="color: var(--text-secondary); margin-top: 8px;">{self._escape(caption)}</figcaption>' if caption else ''
            return f'''<figure style="text-align: center;">
            <img src="{self._escape(url)}" alt="{self._escape(alt)}" style="{style} border-radius: 8px;">
            {caption_html}
          </figure>'''
        
        elif ptype == 'explore':
            links = content.get('links', [])
            links_html = '\n'.join([
                f'<li><a href="{self._escape(link["url"])}" target="_blank">{self._escape(link["text"])}</a></li>'
                for link in links
            ])
            return f'''<h4>🔗 Εξερεύνησε περισσότερα</h4>
          <ul>
            {links_html}
          </ul>'''
        
        elif ptype == 'book':
            title = content.get('title', '')
            chapter = content.get('chapter', '')
            section = content.get('section', '')
            pages = content.get('pages', '')
            start_page = content.get('start_page', 0)
            
            # Get book PDF path from config
            book_pdf = self.get_config('book', 'pdf_path', default='')
            
            book_html = f'<h4>📖 Αναφορά Βιβλίου</h4>\n'
            if title:
                book_html += f'<p><strong>{self._escape(title)}</strong></p>\n'
            if chapter:
                book_html += f'<p>{self._escape(chapter)}</p>\n'
            if section:
                book_html += f'<p>{self._escape(section)}</p>\n'
            
            # Generate PDF link with page number
            if pages and book_pdf:
                pdf_link = f'{book_pdf}#page={start_page}'
                book_html += f'''<p class="book-pages">
            <a href="{self._escape(pdf_link)}" target="_blank" class="book-link">
              📄 Σελίδες {self._escape(pages)} → Άνοιγμα PDF
            </a>
          </p>'''
            elif pages:
                book_html += f'<p>Σελίδες: {self._escape(pages)}</p>'
            
            return book_html
        
        elif ptype == 'raw':
            # Unknown tag - render as plain HTML
            original_tag = content.get('original_tag', 'unknown')
            html_content = content.get('html', '')
            self.logger.warning(f"Rendering unknown tag '{original_tag}' as plain HTML", source=question_id)
            return f'<div class="raw-content" data-original-tag="{original_tag}">{html_content}</div>'
        
        return str(content)
    
    # === Media Generation ===
    
    def _generate_media(self, q: Question) -> str:
        """Generate media elements (images, videos, embeds in main question area)."""
        media_parts = []
        
        # Images
        for img in q.images:
            url = img.get('url', '')
            alt = img.get('alt', '')
            caption = img.get('caption', '')
            width = img.get('width', '')
            style = f'max-width: {width}px;' if width else ''
            
            media_parts.append(f'''<figure class="question-image">
        <img src="{self._escape(url)}" alt="{self._escape(alt)}" style="{style}">
        {f'<figcaption>{self._escape(caption)}</figcaption>' if caption else ''}
      </figure>''')
        
        # Videos
        for vid in q.videos:
            url = vid.get('url', '')
            title = vid.get('title', '')
            
            media_parts.append(f'''<div class="question-video">
        <div class="video-wrapper">
          <iframe src="{self._escape(url)}" title="{self._escape(title)}" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen></iframe>
        </div>
        {f'<div class="video-title">📹 {self._escape(title)}</div>' if title else ''}
      </div>''')
        
        # Embeds
        for emb in q.embeds:
            url = emb.get('url', '')
            title = emb.get('title', '')
            height = emb.get('height', '400')
            
            media_parts.append(f'''<div class="question-embed">
        <div class="embed-header">
          🔗 <a href="{self._escape(url)}" target="_blank">{self._escape(url)}</a>
        </div>
        <div class="embed-wrapper">
          <iframe src="{self._escape(url)}" title="{self._escape(title)}" style="height: {height}px;"></iframe>
        </div>
      </div>''')
        
        return '\n'.join(media_parts)
    
    # === Code Blocks ===
    
    def _generate_code_blocks(self, q: Question) -> str:
        """Generate syntax-highlighted code blocks."""
        if not q.code_blocks:
            return ''
        
        # Skip if already used for fillblank
        if q.question_type == QuestionType.FILLBLANK:
            return ''
        
        blocks = []
        for code in q.code_blocks:
            lang = code.get('language', 'text')
            code_text = self._escape(code.get('code', ''))
            
            blocks.append(f'''<pre><code class="language-{lang}">{code_text}</code></pre>''')
        
        return '\n'.join(blocks)
    
    # === Navigation ===
    
    def _generate_navigation(self) -> str:
        """Generate navigation buttons."""
        return '''<div class="navigation">
      <button class="nav-btn" id="btnPrev" onclick="navigateQuestion(-1)" style="display:none">
        ← Προηγούμενη
      </button>
      <button class="nav-btn btn-submit" id="btnSubmit" onclick="submitQuiz()">
        ✓ Υποβολή Quiz
      </button>
      <button class="nav-btn" id="btnNext" onclick="navigateQuestion(1)" style="display:none">
        Επόμενη →
      </button>
    </div>'''
    
    # === Results Section ===
    
    def _generate_results(self) -> str:
        """Generate results container."""
        # Get button configuration
        buttons_config = self.get_config('buttons', default={})
        
        # Generate button HTML with visibility classes
        button_defs = [
            ('review', '🔍 Επισκόπηση', 'btn-review', 'reviewAnswers()'),
            ('print', '🖨️ Εκτύπωση', 'btn-print', 'printResults()'),
            ('pdf', '📄 PDF', 'btn-pdf', 'exportPDF()'),
            ('markdown', '📝 Markdown', 'btn-markdown', 'exportMarkdown()'),
            ('email', '📧 Email', 'btn-email', 'sendEmail()'),
            ('drive', '☁️ Drive', 'btn-drive', 'shareToCloud()'),
            ('docs', '📑 G.Docs', 'btn-docs', 'exportToGoogleDocs()'),
            ('restart', '🔄 Ξανά', 'btn-restart', 'restartQuiz()'),
        ]
        
        buttons_html = []
        for key, label, css_class, onclick in button_defs:
            # Button is shown by default unless explicitly set to false
            show = buttons_config.get(key, True)
            style = '' if show else 'display:none'
            buttons_html.append(
                f'<button class="nav-btn {css_class}" onclick="{onclick}" style="{style}">{label}</button>'
            )
        
        return f'''<div class="results-container hidden" id="resultsContainer">
      <h2>📊 Αποτελέσματα</h2>
      
      <div class="results-circle">
        <svg viewBox="0 0 180 180">
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#667eea"/>
              <stop offset="100%" stop-color="#764ba2"/>
            </linearGradient>
          </defs>
          <circle class="circle-bg" cx="90" cy="90" r="80"/>
          <circle class="circle-progress" id="progressCircle" cx="90" cy="90" r="80"/>
        </svg>
        <div class="results-percentage" id="resultsPercentage">0%</div>
      </div>
      
      <div class="results-score" id="resultsScore">0/0 βαθμοί</div>
      
      <div class="results-stats">
        <div class="stat-card">
          <div class="stat-value" style="color: var(--success);" id="statCorrect">0</div>
          <div class="stat-label">✓ Σωστές</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: var(--warning);" id="statPartial">0</div>
          <div class="stat-label">◐ Μερικές</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: var(--error);" id="statWrong">0</div>
          <div class="stat-label">✗ Λάθος</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: var(--text-muted);" id="statUnanswered">0</div>
          <div class="stat-label">○ Κενές</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: var(--accent);" id="statPoints">0/0</div>
          <div class="stat-label">⭐ Βαθμοί</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color: var(--primary-start);" id="statGrade">0/20</div>
          <div class="stat-label">📊 Βαθμός</div>
        </div>
      </div>
      
      <div class="results-actions">
        {chr(10).join(buttons_html)}
      </div>
    </div>'''
    
    # === Scripts ===
    
    def _generate_scripts(self) -> str:
        """Generate script tags."""
        js_file = self.get_config('output', 'js_file', default='quiz-core.js')
        time_limit = self.get_config('quiz', 'time_limit', default=20)
        
        # Build config object
        buttons_config = self.get_config('buttons', default={})
        config_json = json.dumps({
            'timeLimit': time_limit,
            'shuffleQuestions': self.get_config('behavior', 'shuffle_questions', default=False),
            'shuffleAnswers': self.get_config('behavior', 'shuffle_answers', default=False),
            'showExplanations': self.get_config('behavior', 'show_explanations', default='after_submit'),
            'buttons': buttons_config
        }, ensure_ascii=False)
        
        return f'''<!-- Loading Overlay -->
  <div class="loading-overlay hidden" id="loadingOverlay">
    <div class="spinner"></div>
  </div>
  
  <!-- External Scripts -->
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/highlight.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/languages/python.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/languages/javascript.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/languages/sql.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/languages/xml.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/languages/css.min.js"></script>
  
  <!-- Quiz Core JS -->
  <script src="{js_file}"></script>
  
  <!-- Quiz Configuration & Initialization -->
  <script>
    const quizConfig = {config_json};
    
    document.addEventListener('DOMContentLoaded', function() {{
      loadTheme();
      initQuiz(quizConfig);
      document.getElementById('totalQNav').textContent = quizState.totalQuestions;
    }});
  </script>'''
    
    # === Assembly ===
    
    def _assemble_html(self, parts: Dict[str, str]) -> str:
        """Assemble all parts into final HTML document."""
        theme = self.get_config('theme', 'default', default='dark')
        
        return f'''<!DOCTYPE html>
<html lang="el" data-theme="{theme}">
{parts['head']}
<body {parts['body_attrs']}>

  <div class="quiz-container" id="quizContainer">
    
    {parts['top_controls']}
    
    {parts['student_info']}
    
    {parts['quiz_header']}
    
    {parts['progress']}
    
    {parts['content']}
    
    {parts['navigation']}
    
    {parts['results']}
    
  </div>
  
  {parts['scripts']}

</body>
</html>'''
    
    # === Utility Methods ===
    
    def _escape(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ''
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
    
    def _process_question_text(self, text: str) -> str:
        """Process question text with markdown conversion."""
        if not text:
            return ''
        return self._process_inline_markdown(text)
    
    def _process_inline_markdown(self, text: str) -> str:
        """Convert inline markdown to HTML."""
        if not text:
            return ''
        
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
        
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
        
        # Line breaks (preserve paragraphs)
        text = re.sub(r'\n\n', '</p><p>', text)
        if '</p><p>' in text:
            text = f'<p>{text}</p>'
        
        return text
