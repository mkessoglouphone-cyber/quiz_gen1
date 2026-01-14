# Quiz Generator v4.1

Modular Python system for converting Markdown quiz files to various output formats.

## 📁 Project Structure

```
quiz_generators/
├── config/
│   └── default_config.yaml     # Default configuration
├── core/
│   ├── __init__.py
│   ├── base_generator.py       # Abstract base class
│   ├── config_loader.py        # YAML/frontmatter config loader
│   ├── logger.py               # Logging system
│   └── parser.py               # Markdown parser
├── generators/
│   ├── __init__.py
│   └── html_generator.py       # HTML Quiz generator
├── plugins/
│   └── __init__.py             # Custom tag handlers
├── examples/
│   ├── test_quiz.md            # Example quiz
│   ├── test_output.html        # Generated output
│   ├── quiz-interactive.css    # Required CSS
│   └── quiz-core.js            # Required JS
├── output/                     # Generated files directory
└── main.py                     # CLI entry point
```

## 🚀 Quick Start

### Command Line

```bash
# Basic usage
python main.py quiz.md -o quiz.html

# With external config
python main.py quiz.md -o quiz.html -c custom_config.yaml

# Specify output directory
python main.py quiz.md -o ./output/

# Show help
python main.py --help

# List available formats
python main.py --list-formats
```

### Programmatic Usage (for GUI)

```python
from main import generate_quiz, get_available_formats

# Generate quiz
markdown_text = open('quiz.md').read()
output, logger = generate_quiz(
    markdown_content=markdown_text,
    output_format='html',
    config={'quiz': {'title': 'My Quiz'}},  # Optional overrides
    output_path='output/quiz.html'
)

# Check for errors
if logger.error_count == 0:
    print("Success!")
else:
    for error in logger.get_errors():
        print(f"Error: {error.message}")

# Get available formats
formats = get_available_formats()
for name, info in formats.items():
    print(f"{name}: {info['description']}")
```

## 📝 Markdown Format

### Configuration (YAML Frontmatter)

```yaml
---
title: "Εισαγωγή στην Python"
subject: "Πληροφορική"
time_limit: 25
shuffle_questions: false

buttons:
  review: true
  print: true
  pdf: true
  markdown: true
  email: true
  drive: true
  docs: true
  restart: true

email: "teacher@school.gr"
share_folder: "https://drive.google.com/..."
google_docs: "https://docs.google.com/..."
book_pdf: "./books/textbook.pdf"

students:
  - Μαθητής 1
  - Μαθητής 2
classes:
  - Β1
  - Β2
---
```

### Question Types

#### Single Choice
```markdown
## Ερώτηση
points: 1

Ποια είναι η σωστή απάντηση;

- [ ] Λάθος απάντηση
- [x] Σωστή απάντηση
- [ ] Άλλη λάθος
```

#### Multiple Choice
```markdown
## Ερώτηση (πολλαπλής)
points: 2

Ποιες είναι σωστές;

- [x] Σωστή 1
- [x] Σωστή 2
- [ ] Λάθος
```

#### True/False
```markdown
## Ερώτηση
type: truefalse
points: 1

Η Python είναι interpreted.

- [x] Σωστό
- [ ] Λάθος
```

#### Matching
```markdown
## Ερώτηση
type: matching
points: 3

Αντιστοιχίστε:

::: matches
int: 42
float: 3.14
str: "Hello"
:::
```

#### Ordering
```markdown
## Ερώτηση
type: ordering
points: 2

Βάλε στη σωστή σειρά:

::: items
1. Πρώτο βήμα
2. Δεύτερο βήμα
3. Τρίτο βήμα
:::

::: correct_order
1, 2, 3
:::
```

#### Fill in the Blank
```markdown
## Ερώτηση
type: fillblank
points: 2

Συμπλήρωσε:

```python
for i in [___1___](5):
    [___2___](i)
```

::: blanks
1: range
2: print
:::
```

#### Short Answer
```markdown
## Ερώτηση
type: shortanswer
points: 4

Γράψε μια συνάρτηση:

::: sample_answer
def hello():
    print("Hello")
:::
```

### Helper Panels

```markdown
::: theory
Θεωρία με **markdown** formatting.
:::

::: hint
Υπόδειξη για τη λύση.
:::

::: image
url: https://example.com/image.png
alt: Description
caption: Λεζάντα
width: 300
:::

::: video
url: https://www.youtube.com/embed/VIDEO_ID
title: Video Title
:::

::: embed
url: https://docs.python.org/3/
title: Python Docs
height: 400
:::

::: explore
- [Link 1](https://url1.com)
- [Link 2](https://url2.com)
:::

::: book
title: Όνομα Βιβλίου
chapter: Κεφάλαιο 1
pages: 45-48
:::

::: feedback_positive
Μπράβο!
:::

::: feedback_negative
Λάθος. Δοκίμασε ξανά.
:::
```

## 🔧 Configuration Priority

1. **GUI Overrides** (highest) - Passed programmatically
2. **Markdown Frontmatter** - `---` block at start of file
3. **External YAML** - Passed with `-c` flag
4. **Default Config** - `config/default_config.yaml`

## 📊 Logging

The generator creates a log file with:
- Errors (parsing failures, invalid syntax)
- Warnings (unknown tags, deprecated features)
- Info (processing status)

Unknown tags are logged as warnings and rendered as plain HTML.

## 🔌 Extending with Custom Tags

```python
from core.parser import TagHandler

class MyCustomHandler(TagHandler):
    tag_name = "mycustom"
    
    def parse(self, content: str, logger) -> dict:
        # Parse your custom tag content
        return {'data': content}

# Register in parser
parser.register_handler(MyCustomHandler())
```

## 📦 Output Files Required

For the generated HTML to work, you need:
- `quiz-interactive.css` - Styling
- `quiz-core.js` - JavaScript functionality

These should be in the same directory as the HTML output.

## 🗓️ Future Generators

- [ ] Moodle XML Import
- [ ] Moodle GIFT Format
- [ ] Google Forms
- [ ] H5P Package
- [ ] eClass Export

## 📜 License

Educational use.

---

Quiz Generator v4.1 - Created 2025
