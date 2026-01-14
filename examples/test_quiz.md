---
# ===== QUIZ CONFIGURATION =====
title: "Εισαγωγή στην Python"
subject: "Πληροφορική Β' Λυκείου"
chapter: "Κεφάλαια 1-3"
class: "Β1"
author: "Καθηγητής Πληροφορικής"
date: auto
time_limit: 25

# Συμπεριφορά
shuffle_questions: false
shuffle_answers: true
passing_score: 50
show_explanations: after_submit

# Κουμπιά αποτελεσμάτων
buttons:
  review: true
  print: true
  pdf: true
  markdown: true
  email: true
  drive: true
  docs: true
  restart: true

# Εξωτερικές υπηρεσίες
ide_url: "https://www.online-python.com/"
email: "teacher@school.gr"
share_folder: "https://drive.google.com/drive/folders/1ABC123example"
google_docs: "https://docs.google.com/document/d/1XYZ789example/edit"

# Βιβλίο
book_pdf: "./books/pliroforiki_b_lykeiou.pdf"

# Λίστες μαθητών
students:
  - Αντωνίου Μαρία
  - Γεωργίου Νίκος
  - Δημητρίου Ελένη
  - Παπαδοπούλου Άννα

classes:
  - Β1
  - Β2
  - Β3

# Syntax highlighting
default_language: python
highlight_theme: atom-one-dark
---

# Ενότητα 1: Βασικές Έννοιες

## Ερώτηση
points: 1

Ποια είναι η σωστή σύνταξη για εκτύπωση στην Python;

- [ ] `echo "Hello"`
- [x] `print("Hello")`
- [ ] `console.log("Hello")`
- [ ] `System.out.println("Hello")`

::: theory
Κάθε γλώσσα προγραμματισμού έχει τη δική της συνάρτηση εξόδου:
- **Python:** `print()`
- **JavaScript:** `console.log()`
- **PHP:** `echo`
- **Java:** `System.out.println()`
:::

::: hint
Η Python χρησιμοποιεί μια απλή, ευανάγνωστη συνάρτηση. Σκέψου τη λέξη "εκτύπωση" στα αγγλικά!
:::

::: book
title: Πληροφορική Β' Λυκείου
chapter: Κεφάλαιο 2 - Εισαγωγή στην Python
section: Ενότητα 2.3 - Συναρτήσεις Εισόδου/Εξόδου
pages: 45-48
:::

::: explore
- [Python print() documentation](https://docs.python.org/3/library/functions.html#print)
- [W3Schools - Python print()](https://www.w3schools.com/python/ref_func_print.asp)
:::

::: feedback_positive
Σωστά! Η `print()` είναι η βασική συνάρτηση εξόδου της Python.
:::

::: feedback_negative
Λάθος. Η `echo` είναι για PHP, η `console.log()` για JavaScript.
:::

---

## Ερώτηση (με εικόνα)
points: 2

Παρατήρησε το λογότυπο της Python:

::: image
url: https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/200px-Python-logo-notext.svg.png
alt: Python Logo
caption: Το επίσημο λογότυπο της Python
width: 150
:::

Τι είδους γλώσσα προγραμματισμού είναι η Python;

- [x] Interpreted (Διερμηνευόμενη)
- [ ] Compiled (Μεταγλωττιζόμενη)
- [ ] Assembly
- [ ] Machine Code

::: theory
Οι γλώσσες προγραμματισμού χωρίζονται σε:
- **Διερμηνευόμενες (Interpreted):** Ο κώδικας εκτελείται γραμμή-γραμμή (Python, JavaScript, PHP)
- **Μεταγλωττιζόμενες (Compiled):** Ο κώδικας μετατρέπεται σε εκτελέσιμο πριν την εκτέλεση (C, C++, Java)
:::

::: hint
Η Python δεν χρειάζεται compilation πριν την εκτέλεση.
:::

---

## Ερώτηση (με βίντεο)
points: 2

Παρακολούθησε το εισαγωγικό βίντεο:

::: video
url: https://www.youtube.com/embed/kqtD5dpn9C8
title: Python Tutorial for Beginners
width: 560
height: 315
:::

Ποιο είναι το πρώτο βήμα για να ξεκινήσεις με Python;

- [ ] Να μάθεις C++ πρώτα
- [x] Να εγκαταστήσεις την Python
- [ ] Να αγοράσεις ειδικό hardware
- [ ] Να μάθεις μαθηματικά

---

## Ερώτηση (με embed)
points: 2

Μελέτησε την τεκμηρίωση της tkinter:

::: embed
url: https://docs.python.org/3/library/tkinter.html
title: tkinter Documentation
width: 100%
height: 400
:::

Η tkinter χρησιμοποιείται για:

- [ ] Επεξεργασία εικόνας
- [ ] Machine Learning
- [x] Δημιουργία γραφικών διεπαφών (GUI)
- [ ] Web Development

::: theory
**tkinter** είναι η standard Python βιβλιοθήκη για δημιουργία GUI (Graphical User Interface).
Παρέχει widgets όπως buttons, labels, text boxes, menus κ.α.
:::

---

# Ενότητα 2: Κώδικας Python

## Ερώτηση
points: 2

Τι θα εμφανίσει ο παρακάτω κώδικας;

```python
# Υπολογισμός αθροίσματος
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Το άθροισμα είναι: {total}")
```

- [ ] Το άθροισμα είναι: [1, 2, 3, 4, 5]
- [x] Το άθροισμα είναι: 15
- [ ] Το άθροισμα είναι: 5
- [ ] Error

::: theory
Η συνάρτηση `sum()` υπολογίζει το άθροισμα όλων των στοιχείων ενός iterable.
Το f-string (`f"..."`) επιτρέπει την ενσωμάτωση μεταβλητών μέσα σε strings.
:::

::: hint
Πρόσθεσε τους αριθμούς: 1 + 2 + 3 + 4 + 5 = ?
:::

::: book
title: Πληροφορική Β' Λυκείου
chapter: Κεφάλαιο 4 - Λίστες
pages: 87-92
:::

---

## Ερώτηση (πολλαπλής επιλογής)
points: 2

Ποιοι από τους παρακάτω είναι έγκυροι τύποι δεδομένων στην Python;

- [x] `int`
- [x] `str`
- [x] `float`
- [ ] `char`
- [x] `bool`
- [ ] `double`

::: theory
Η Python έχει τους εξής βασικούς τύπους:
- `int` - Ακέραιοι αριθμοί
- `float` - Δεκαδικοί αριθμοί
- `str` - Συμβολοσειρές
- `bool` - Λογικές τιμές (True/False)
- `list`, `tuple`, `dict`, `set` - Συλλογές

Η Python **δεν** έχει `char` (χρησιμοποιεί str) ούτε `double` (χρησιμοποιεί float).
:::

---

# Ενότητα 3: Προχωρημένα

## Ερώτηση (αντιστοίχιση)
type: matching
points: 3

Αντιστοιχίστε κάθε τύπο δεδομένων με το παράδειγμά του:

::: matches
int: 42
float: 3.14
str: "Hello"
bool: True
:::

::: theory
Παραδείγματα τύπων:
- `int`: 42, -10, 0, 1000
- `float`: 3.14, -0.5, 2.0
- `str`: "Hello", 'Python', ""
- `bool`: True, False
:::

::: hint
- Οι ακέραιοι δεν έχουν υποδιαστολή
- Τα strings έχουν εισαγωγικά
- Οι booleans είναι True ή False
:::

---

## Ερώτηση (ταξινόμηση)
type: ordering
points: 2

Βάλε τα βήματα debugging στη σωστή σειρά:

::: items
1. Εντόπισε το σφάλμα
2. Κατανόησε την αιτία
3. Διόρθωσε τον κώδικα
4. Δοκίμασε ξανά
:::

::: correct_order
1, 2, 3, 4
:::

::: theory
Η διαδικασία debugging ακολουθεί συγκεκριμένα βήματα:
1. **Εντοπισμός:** Βρες πού συμβαίνει το σφάλμα
2. **Κατανόηση:** Καταλάβε γιατί συμβαίνει
3. **Διόρθωση:** Διόρθωσε τον κώδικα
4. **Επαλήθευση:** Δοκίμασε ότι λειτουργεί
:::

---

## Ερώτηση (συμπλήρωση κενών)
type: fillblank
points: 2

Συμπλήρωσε τον κώδικα:

```python
# For loop
for i in [___1___](5):
    [___2___](i)
```

::: blanks
1: range
2: print
:::

::: hint
Η `range()` δημιουργεί ακολουθία αριθμών, η `print()` εμφανίζει τιμές.
:::

---

## Ερώτηση (ανοικτή)
type: shortanswer
points: 4

Γράψε μια συνάρτηση Python που υπολογίζει το παραγοντικό ενός αριθμού:

::: sample_answer
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
:::

::: hint
Μπορείς να χρησιμοποιήσεις αναδρομή: n! = n × (n-1)!
Βάση: 0! = 1! = 1
:::

::: theory
Το παραγοντικό n! ορίζεται ως:
- n! = n × (n-1) × (n-2) × ... × 2 × 1
- 0! = 1 (εξ ορισμού)

Παραδείγματα:
- 5! = 5 × 4 × 3 × 2 × 1 = 120
- 3! = 3 × 2 × 1 = 6
:::

---

## Ερώτηση (Σωστό/Λάθος)
type: truefalse
points: 1

Η Python είναι case-sensitive (διακρίνει πεζά-κεφαλαία).

- [x] Σωστό
- [ ] Λάθος

::: theory
Η Python είναι **case-sensitive**, που σημαίνει ότι:
- `myVar` ≠ `myvar` ≠ `MYVAR`
- `Print()` θα δώσει error (η σωστή είναι `print()`)
:::
