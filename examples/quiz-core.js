/**
 * Quiz Generator - Core JavaScript
 * Version: 4.1 - Configurable Buttons, Google Docs, Media Support
 */

// ===== Quiz State =====
const quizState = {
  currentQuestion: 0,
  totalQuestions: 0,
  viewMode: 'all',
  submitted: false,
  answers: {},
  results: {
    correct: 0,
    wrong: 0,
    unanswered: 0,
    partial: 0,
    selfGraded: 0,
    totalPoints: 0,
    earnedPoints: 0
  },
  timeLeft: 0,
  timerInterval: null,
  questionPoints: {},
  config: {}
};

// ===== Sound Effects =====
const sounds = { correct: null, incorrect: null, complete: null };

function initSounds() {
  sounds.correct = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(523.25, ctx.currentTime);
      osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.1);
      osc.frequency.setValueAtTime(783.99, ctx.currentTime + 0.2);
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
      osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.5);
    } catch(e) {}
  };
  
  sounds.incorrect = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(150, ctx.currentTime);
      osc.frequency.setValueAtTime(100, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
      osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.3);
    } catch(e) {}
  };
  
  sounds.complete = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.15);
        gain.gain.setValueAtTime(0.2, ctx.currentTime + i * 0.15);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.15 + 0.4);
        osc.start(ctx.currentTime + i * 0.15);
        osc.stop(ctx.currentTime + i * 0.15 + 0.4);
      });
    } catch(e) {}
  };
}

function playSound(type) {
  try { if (sounds[type]) sounds[type](); } catch (e) {}
}

// ===== Initialization =====
function initQuiz(config = {}) {
  quizState.config = config;
  
  const questions = document.querySelectorAll('.question-card');
  quizState.totalQuestions = questions.length;
  quizState.timeLeft = (config.timeLimit || 20) * 60;
  
  // Calculate total points
  let totalPoints = 0;
  questions.forEach(q => {
    const points = parseFloat(q.dataset.points) || 1;
    quizState.questionPoints[q.id] = points;
    totalPoints += points;
  });
  quizState.results.totalPoints = totalPoints;
  
  document.getElementById('totalQ').textContent = quizState.totalQuestions;
  const totalPointsEl = document.getElementById('totalPoints');
  if (totalPointsEl) totalPointsEl.textContent = totalPoints;
  
  initSounds();
  setupAnswerListeners();
  setupMatchingQuestions();
  setupOrderingQuestions();
  setupFillBlankQuestions();
  setupShortAnswerListeners();
  setupCodeBlocks();
  setupResultButtons(config.buttons);
  startTimer();
  updateProgress();
  updateNavigation();
  
  // Syntax highlighting
  if (typeof hljs !== 'undefined') {
    document.querySelectorAll('pre code').forEach(block => {
      hljs.highlightElement(block);
    });
  }
  
  // Math rendering
  if (typeof renderMathInElement !== 'undefined') {
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ]
    });
  }
  
  console.log('Quiz v4.1 initialized:', quizState.totalQuestions, 'questions,', totalPoints, 'total points');
}

// ===== Setup Result Buttons Based on Config =====
function setupResultButtons(buttonsConfig = {}) {
  const defaults = {
    review: true,
    print: true,
    pdf: true,
    markdown: true,
    email: true,
    drive: true,
    docs: true,
    restart: true
  };
  
  const buttons = { ...defaults, ...buttonsConfig };
  
  // Store in state for later use
  quizState.config.buttons = buttons;
  
  // Will apply visibility after submission in showResults()
}

function applyButtonVisibility() {
  const buttons = quizState.config.buttons || {};
  
  const buttonMap = {
    review: '.btn-review',
    print: '.btn-print',
    pdf: '.btn-pdf',
    markdown: '.btn-markdown',
    email: '.btn-email',
    drive: '.btn-drive',
    docs: '.btn-docs',
    restart: '.btn-restart'
  };
  
  Object.entries(buttonMap).forEach(([key, selector]) => {
    const btn = document.querySelector(selector);
    if (btn) {
      btn.style.display = buttons[key] !== false ? '' : 'none';
    }
  });
  
  // Check if services are configured
  const email = document.body.dataset.email;
  const driveFolder = document.body.dataset.shareFolder;
  const googleDocs = document.body.dataset.googleDocs;
  
  // Hide buttons if service not configured
  const emailBtn = document.querySelector('.btn-email');
  const driveBtn = document.querySelector('.btn-drive');
  const docsBtn = document.querySelector('.btn-docs');
  
  if (emailBtn && !email) emailBtn.style.display = 'none';
  if (driveBtn && !driveFolder) driveBtn.style.display = 'none';
  if (docsBtn && !googleDocs) docsBtn.style.display = 'none';
}

// ===== Theme Toggle =====
function toggleTheme() {
  const html = document.documentElement;
  const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  
  const btn = document.querySelector('.theme-toggle');
  if (btn) btn.textContent = newTheme === 'dark' ? '🌙' : '☀️';
  
  localStorage.setItem('quiz-theme', newTheme);
  
  // Update highlight.js theme
  const hljsDark = document.getElementById('hljs-dark');
  const hljsLight = document.getElementById('hljs-light');
  if (hljsDark) hljsDark.disabled = newTheme === 'light';
  if (hljsLight) hljsLight.disabled = newTheme === 'dark';
}

function loadTheme() {
  const saved = localStorage.getItem('quiz-theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
    const btn = document.querySelector('.theme-toggle');
    if (btn) btn.textContent = saved === 'dark' ? '🌙' : '☀️';
    
    const hljsDark = document.getElementById('hljs-dark');
    const hljsLight = document.getElementById('hljs-light');
    if (hljsDark) hljsDark.disabled = saved === 'light';
    if (hljsLight) hljsLight.disabled = saved === 'dark';
  }
}

// ===== View Mode Toggle =====
function setViewMode(mode) {
  quizState.viewMode = mode;
  
  document.querySelectorAll('.view-toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === mode);
  });
  
  const container = document.getElementById('quizContainer');
  const studentInfo = document.getElementById('studentInfo');
  const quizHeader = document.querySelector('.quiz-header');
  const sectionsHeaders = document.querySelectorAll('.section-header');
  
  if (mode === 'single') {
    if (container) container.classList.add('single-mode');
    if (studentInfo) studentInfo.style.display = 'none';
    if (quizHeader) quizHeader.style.display = 'none';
    sectionsHeaders.forEach(h => h.style.display = 'none');
    showQuestion(quizState.currentQuestion);
  } else {
    if (container) container.classList.remove('single-mode');
    if (studentInfo) studentInfo.style.display = '';
    if (quizHeader) quizHeader.style.display = '';
    sectionsHeaders.forEach(h => h.style.display = '');
    document.querySelectorAll('.question-card').forEach(q => q.style.display = '');
  }
  
  updateNavigation();
}

function showQuestion(index) {
  if (quizState.viewMode !== 'single') return;
  
  document.querySelectorAll('.question-card').forEach((q, i) => {
    q.style.display = i === index ? 'block' : 'none';
    q.classList.toggle('active', i === index);
  });
  
  quizState.currentQuestion = index;
  document.getElementById('currentQ').textContent = index + 1;
  
  updateNavigation();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function navigateQuestion(direction) {
  const newIndex = quizState.currentQuestion + direction;
  if (newIndex >= 0 && newIndex < quizState.totalQuestions) {
    showQuestion(newIndex);
  }
}

function updateNavigation() {
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  
  if (!btnPrev || !btnNext) return;
  
  if (quizState.viewMode === 'single') {
    btnPrev.style.display = '';
    btnNext.style.display = '';
    btnPrev.disabled = quizState.currentQuestion === 0;
    btnNext.disabled = quizState.currentQuestion === quizState.totalQuestions - 1;
  } else {
    btnPrev.style.display = 'none';
    btnNext.style.display = 'none';
  }
}

// ===== Timer =====
function startTimer() {
  updateTimerDisplay();
  
  quizState.timerInterval = setInterval(() => {
    quizState.timeLeft--;
    updateTimerDisplay();
    
    if (quizState.timeLeft <= 0) {
      clearInterval(quizState.timerInterval);
      alert('Ο χρόνος τελείωσε! Το quiz θα υποβληθεί αυτόματα.');
      submitQuiz();
    }
  }, 1000);
}

function updateTimerDisplay() {
  const minutes = Math.floor(quizState.timeLeft / 60);
  const seconds = quizState.timeLeft % 60;
  const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  
  const timerDisplay = document.getElementById('timer-display');
  if (timerDisplay) timerDisplay.textContent = display;
  
  const timerEl = document.getElementById('timerContainer');
  if (timerEl) {
    timerEl.classList.remove('warning', 'danger');
    if (quizState.timeLeft <= 60) timerEl.classList.add('danger');
    else if (quizState.timeLeft <= 300) timerEl.classList.add('warning');
  }
}

function stopTimer() {
  if (quizState.timerInterval) {
    clearInterval(quizState.timerInterval);
    quizState.timerInterval = null;
  }
}

// ===== Answer Tracking =====
function setupAnswerListeners() {
  document.querySelectorAll('.question-card input[type="radio"], .question-card input[type="checkbox"]').forEach(input => {
    input.addEventListener('change', function() {
      if (quizState.submitted) return;
      
      const card = this.closest('.question-card');
      const questionId = card.id;
      
      if (this.type === 'radio') {
        quizState.answers[questionId] = this.value;
      } else {
        if (!quizState.answers[questionId]) quizState.answers[questionId] = [];
        if (this.checked) {
          if (!quizState.answers[questionId].includes(this.value)) {
            quizState.answers[questionId].push(this.value);
          }
        } else {
          quizState.answers[questionId] = quizState.answers[questionId].filter(v => v !== this.value);
        }
      }
      
      updateProgress();
    });
  });
}

function setupMatchingQuestions() {
  document.querySelectorAll('.question-card[data-type="matching"]').forEach(card => {
    const selects = card.querySelectorAll('.matching-select');
    
    selects.forEach(select => {
      select.addEventListener('change', function() {
        if (quizState.submitted) return;
        
        const questionId = card.id;
        if (!quizState.answers[questionId]) quizState.answers[questionId] = {};
        
        quizState.answers[questionId][this.dataset.item] = this.value;
        updateProgress();
      });
    });
  });
}

function setupOrderingQuestions() {
  document.querySelectorAll('.question-card[data-type="ordering"]').forEach(card => {
    const list = card.querySelector('.ordering-list');
    if (!list) return;
    
    const items = list.querySelectorAll('.ordering-item');
    
    items.forEach(item => {
      item.draggable = true;
      
      item.addEventListener('dragstart', function(e) {
        if (quizState.submitted) return;
        e.dataTransfer.setData('text/plain', this.dataset.id);
        this.classList.add('dragging');
      });
      
      item.addEventListener('dragend', function() {
        this.classList.remove('dragging');
        saveOrderingAnswer(card);
      });
      
      item.addEventListener('dragover', function(e) {
        e.preventDefault();
        if (quizState.submitted) return;
        
        const dragging = list.querySelector('.dragging');
        if (dragging && dragging !== this) {
          const rect = this.getBoundingClientRect();
          const midY = rect.top + rect.height / 2;
          if (e.clientY < midY) {
            list.insertBefore(dragging, this);
          } else {
            list.insertBefore(dragging, this.nextSibling);
          }
        }
      });
      
      const upBtn = item.querySelector('.order-up');
      const downBtn = item.querySelector('.order-down');
      
      if (upBtn) {
        upBtn.addEventListener('click', () => {
          if (quizState.submitted) return;
          const prev = item.previousElementSibling;
          if (prev) {
            list.insertBefore(item, prev);
            saveOrderingAnswer(card);
          }
        });
      }
      
      if (downBtn) {
        downBtn.addEventListener('click', () => {
          if (quizState.submitted) return;
          const next = item.nextElementSibling;
          if (next) {
            list.insertBefore(next, item);
            saveOrderingAnswer(card);
          }
        });
      }
    });
  });
}

function saveOrderingAnswer(card) {
  const list = card.querySelector('.ordering-list');
  const items = list.querySelectorAll('.ordering-item');
  const order = Array.from(items).map(item => item.dataset.id);
  quizState.answers[card.id] = order;
  updateProgress();
}

function setupFillBlankQuestions() {
  document.querySelectorAll('.question-card[data-type="fillblank"]').forEach(card => {
    const inputs = card.querySelectorAll('.fillblank-input');
    
    inputs.forEach(input => {
      input.addEventListener('input', function() {
        if (quizState.submitted) return;
        
        const questionId = card.id;
        if (!quizState.answers[questionId]) quizState.answers[questionId] = {};
        
        quizState.answers[questionId][this.dataset.blank] = this.value.trim();
        updateProgress();
      });
    });
  });
}

function setupShortAnswerListeners() {
  document.querySelectorAll('.question-card[data-type="shortanswer"] textarea').forEach(textarea => {
    textarea.addEventListener('input', function() {
      if (quizState.submitted) return;
      
      const card = this.closest('.question-card');
      quizState.answers[card.id] = this.value.trim();
      updateProgress();
    });
  });
}

// ===== Progress Update =====
function updateProgress() {
  let answered = 0;
  
  document.querySelectorAll('.question-card').forEach(card => {
    const type = card.dataset.type || 'single';
    const answer = quizState.answers[card.id];
    
    let hasAnswer = false;
    
    if (type === 'single' || type === 'truefalse') {
      hasAnswer = !!answer;
    } else if (type === 'multiple') {
      hasAnswer = Array.isArray(answer) && answer.length > 0;
    } else if (type === 'matching' || type === 'fillblank') {
      hasAnswer = answer && Object.keys(answer).length > 0;
    } else if (type === 'ordering') {
      hasAnswer = Array.isArray(answer) && answer.length > 0;
    } else if (type === 'shortanswer') {
      hasAnswer = answer && answer.length > 0;
    }
    
    if (hasAnswer) answered++;
  });
  
  const percentage = quizState.totalQuestions > 0 ? (answered / quizState.totalQuestions) * 100 : 0;
  
  const progressFill = document.getElementById('progressFill');
  if (progressFill) progressFill.style.width = percentage + '%';
  
  const answeredCount = document.getElementById('answeredCount');
  if (answeredCount) answeredCount.textContent = answered + ' απαντημένες';
}

// ===== Quiz Submission =====
function submitQuiz() {
  if (quizState.submitted) return;
  
  const selfGradedQuestions = document.querySelectorAll('.question-card[data-type="shortanswer"]');
  
  if (selfGradedQuestions.length > 0) {
    if (!confirm('Το quiz περιέχει ερωτήσεις ανοικτού τύπου που θα βαθμολογήσετε εσείς. Συνέχεια;')) {
      return;
    }
  } else {
    if (!confirm('Υποβολή quiz;')) {
      return;
    }
  }
  
  stopTimer();
  quizState.submitted = true;
  
  let correctCount = 0, wrongCount = 0, unansweredCount = 0, partialCount = 0, selfGradedCount = 0;
  let earnedPoints = 0;
  
  document.querySelectorAll('.question-card').forEach(card => {
    const questionId = card.id;
    const type = card.dataset.type || 'single';
    const points = quizState.questionPoints[questionId] || 1;
    
    card.classList.add('submitted');
    card.querySelectorAll('input, select, textarea').forEach(el => el.disabled = true);
    
    const result = gradeQuestion(card, type, points);
    
    if (result.status === 'correct') {
      correctCount++;
      earnedPoints += result.earnedPoints;
      playSound('correct');
    } else if (result.status === 'incorrect') {
      wrongCount++;
      playSound('incorrect');
    } else if (result.status === 'partial') {
      partialCount++;
      earnedPoints += result.earnedPoints;
    } else if (result.status === 'unanswered') {
      unansweredCount++;
    } else if (result.status === 'selfgraded') {
      selfGradedCount++;
    }
  });
  
  quizState.results = {
    correct: correctCount,
    wrong: wrongCount,
    unanswered: unansweredCount,
    partial: partialCount,
    selfGraded: selfGradedCount,
    totalPoints: quizState.results.totalPoints,
    earnedPoints: earnedPoints
  };
  
  setTimeout(() => playSound('complete'), 500);
  showResults();
}

function gradeQuestion(card, type, points) {
  const questionId = card.id;
  const userAnswer = quizState.answers[questionId];
  const feedbackPositive = card.dataset.feedbackPositive || 'Σωστά! Μπράβο!';
  const feedbackNegative = card.dataset.feedbackNegative || 'Λάθος.';
  
  if (type === 'shortanswer') {
    return gradeSelfGradedQuestion(card, points);
  }
  
  let hasAnswer = false;
  if (type === 'single' || type === 'truefalse') {
    hasAnswer = !!userAnswer;
  } else if (type === 'multiple') {
    hasAnswer = Array.isArray(userAnswer) && userAnswer.length > 0;
  } else if (type === 'matching') {
    hasAnswer = userAnswer && Object.keys(userAnswer).length > 0;
  } else if (type === 'ordering') {
    hasAnswer = Array.isArray(userAnswer) && userAnswer.length > 0;
  } else if (type === 'fillblank') {
    hasAnswer = userAnswer && Object.values(userAnswer).some(v => v.length > 0);
  }
  
  if (!hasAnswer) {
    showCorrectAnswer(card, type);
    showExplanation(card, false, feedbackNegative);
    return { status: 'unanswered', earnedPoints: 0 };
  }
  
  let result;
  
  switch (type) {
    case 'single':
    case 'truefalse':
      result = gradeSingleChoice(card, points);
      break;
    case 'multiple':
      result = gradeMultipleChoice(card, points);
      break;
    case 'matching':
      result = gradeMatching(card, points);
      break;
    case 'ordering':
      result = gradeOrdering(card, points);
      break;
    case 'fillblank':
      result = gradeFillBlank(card, points);
      break;
    default:
      result = { status: 'unanswered', earnedPoints: 0 };
  }
  
  if (result.status === 'correct') {
    card.classList.add('result-correct');
    showExplanation(card, true, feedbackPositive);
  } else if (result.status === 'incorrect') {
    card.classList.add('result-incorrect');
    showExplanation(card, false, feedbackNegative);
  } else if (result.status === 'partial') {
    card.classList.add('result-partial');
    showExplanation(card, false, `Μερικώς σωστό (${result.earnedPoints.toFixed(1)}/${points} βαθμοί)`);
  }
  
  return result;
}

function gradeSingleChoice(card, points) {
  const correctAnswer = card.dataset.correct;
  const userAnswer = quizState.answers[card.id];
  const isCorrect = userAnswer === correctAnswer;
  
  card.querySelectorAll('.answer-option').forEach(opt => {
    const input = opt.querySelector('input');
    if (input.value === correctAnswer) opt.classList.add('correct');
    if (input.value === userAnswer && userAnswer !== correctAnswer) opt.classList.add('incorrect');
  });
  
  return { status: isCorrect ? 'correct' : 'incorrect', earnedPoints: isCorrect ? points : 0 };
}

function gradeMultipleChoice(card, points) {
  const correctAnswer = card.dataset.correct.split(',').map(s => s.trim());
  const userAnswer = quizState.answers[card.id] || [];
  
  const correctSet = new Set(correctAnswer);
  const userSet = new Set(userAnswer);
  
  let correctCount = 0, wrongCount = 0;
  
  card.querySelectorAll('.answer-option').forEach(opt => {
    const input = opt.querySelector('input');
    const value = input.value;
    const isCorrectAnswer = correctSet.has(value);
    const isUserAnswer = userSet.has(value);
    
    if (isCorrectAnswer) {
      opt.classList.add('correct');
      if (isUserAnswer) correctCount++;
    }
    if (isUserAnswer && !isCorrectAnswer) {
      opt.classList.add('incorrect');
      wrongCount++;
    }
  });
  
  const totalCorrect = correctAnswer.length;
  const earnedPoints = Math.max(0, (correctCount - wrongCount) / totalCorrect * points);
  
  if (correctCount === totalCorrect && wrongCount === 0) {
    return { status: 'correct', earnedPoints: points };
  } else if (earnedPoints > 0) {
    return { status: 'partial', earnedPoints };
  } else {
    return { status: 'incorrect', earnedPoints: 0 };
  }
}

function gradeMatching(card, points) {
  const correctMatches = JSON.parse(card.dataset.correct);
  const userMatches = quizState.answers[card.id] || {};
  
  let correctCount = 0;
  const totalItems = Object.keys(correctMatches).length;
  
  card.querySelectorAll('.matching-row').forEach(row => {
    const itemId = row.dataset.item;
    const correctValue = correctMatches[itemId];
    const userValue = userMatches[itemId];
    
    if (userValue === correctValue) {
      correctCount++;
      row.classList.add('match-correct');
    } else {
      row.classList.add('match-incorrect');
      const feedback = row.querySelector('.match-feedback');
      if (feedback) {
        const correctOption = card.querySelector(`.matching-option[value="${correctValue}"]`);
        feedback.textContent = `→ ${correctOption?.textContent || correctValue}`;
      }
    }
  });
  
  const earnedPoints = (correctCount / totalItems) * points;
  
  if (correctCount === totalItems) return { status: 'correct', earnedPoints: points };
  else if (correctCount > 0) return { status: 'partial', earnedPoints };
  else return { status: 'incorrect', earnedPoints: 0 };
}

function gradeOrdering(card, points) {
  const correctOrder = card.dataset.correct.split(',').map(s => s.trim());
  
  let correctPositions = 0;
  
  card.querySelectorAll('.ordering-item').forEach((item, index) => {
    const correctPosition = correctOrder.indexOf(item.dataset.id);
    
    if (correctPosition === index) {
      correctPositions++;
      item.classList.add('order-correct');
    } else {
      item.classList.add('order-incorrect');
      const feedback = item.querySelector('.order-feedback');
      if (feedback) feedback.textContent = `(σωστή θέση: ${correctPosition + 1})`;
    }
  });
  
  const earnedPoints = (correctPositions / correctOrder.length) * points;
  
  if (correctPositions === correctOrder.length) return { status: 'correct', earnedPoints: points };
  else if (correctPositions > 0) return { status: 'partial', earnedPoints };
  else return { status: 'incorrect', earnedPoints: 0 };
}

function gradeFillBlank(card, points) {
  const correctAnswers = JSON.parse(card.dataset.correct);
  const userAnswers = quizState.answers[card.id] || {};
  
  let correctCount = 0;
  const totalBlanks = Object.keys(correctAnswers).length;
  
  card.querySelectorAll('.fillblank-input').forEach(input => {
    const blankId = input.dataset.blank;
    const correctValue = correctAnswers[blankId].toLowerCase();
    const userValue = (userAnswers[blankId] || '').toLowerCase();
    
    const correctOptions = correctValue.split('|').map(s => s.trim());
    
    if (correctOptions.includes(userValue)) {
      correctCount++;
      input.classList.add('blank-correct');
    } else {
      input.classList.add('blank-incorrect');
      const feedback = document.createElement('span');
      feedback.className = 'blank-feedback';
      feedback.textContent = ` → ${correctAnswers[blankId].split('|')[0]}`;
      input.after(feedback);
    }
  });
  
  const earnedPoints = (correctCount / totalBlanks) * points;
  
  if (correctCount === totalBlanks) return { status: 'correct', earnedPoints: points };
  else if (correctCount > 0) return { status: 'partial', earnedPoints };
  else return { status: 'incorrect', earnedPoints: 0 };
}

function gradeSelfGradedQuestion(card, points) {
  const userAnswer = quizState.answers[card.id] || '';
  
  if (!userAnswer.trim()) {
    card.classList.add('result-unanswered');
    return { status: 'unanswered', earnedPoints: 0 };
  }
  
  const selfGradePanel = document.createElement('div');
  selfGradePanel.className = 'self-grade-panel';
  selfGradePanel.innerHTML = `
    <div class="self-grade-header">
      <span class="icon">📝</span>
      <span>Βαθμολογήστε την απάντησή σας:</span>
    </div>
    ${card.dataset.sampleAnswer ? `<div class="self-grade-hint"><p><strong>Ενδεικτική απάντηση:</strong><pre><code>${card.dataset.sampleAnswer.replace(/&#10;/g, '\n')}</code></pre></p></div>` : ''}
    <div class="self-grade-options">
      <button class="self-grade-btn" data-grade="0" onclick="applySelfGrade('${card.id}', 0, ${points})">
        ✗ Λάθος<br><small>0/${points}</small>
      </button>
      <button class="self-grade-btn" data-grade="0.5" onclick="applySelfGrade('${card.id}', 0.5, ${points})">
        ◐ Μερικώς<br><small>${(points/2).toFixed(1)}/${points}</small>
      </button>
      <button class="self-grade-btn" data-grade="1" onclick="applySelfGrade('${card.id}', 1, ${points})">
        ✓ Σωστά<br><small>${points}/${points}</small>
      </button>
    </div>
  `;
  
  const textarea = card.querySelector('textarea');
  if (textarea) textarea.after(selfGradePanel);
  
  card.classList.add('awaiting-grade');
  
  return { status: 'selfgraded', earnedPoints: 0 };
}

function applySelfGrade(questionId, multiplier, points) {
  const card = document.getElementById(questionId);
  const earnedPoints = points * multiplier;
  
  if (multiplier === 1) {
    quizState.results.correct++;
    quizState.results.selfGraded--;
    card.classList.add('result-correct');
    playSound('correct');
  } else if (multiplier === 0.5) {
    quizState.results.partial++;
    quizState.results.selfGraded--;
    card.classList.add('result-partial');
  } else {
    quizState.results.wrong++;
    quizState.results.selfGraded--;
    card.classList.add('result-incorrect');
    playSound('incorrect');
  }
  
  quizState.results.earnedPoints += earnedPoints;
  card.classList.remove('awaiting-grade');
  
  card.querySelectorAll('.self-grade-btn').forEach(btn => {
    btn.disabled = true;
    if (parseFloat(btn.dataset.grade) === multiplier) btn.classList.add('selected');
  });
  
  const feedbackPositive = card.dataset.feedbackPositive || '';
  const feedbackNegative = card.dataset.feedbackNegative || '';
  showExplanation(card, multiplier >= 0.5, multiplier === 1 ? feedbackPositive : feedbackNegative);
  
  updateResultsDisplay();
}

function showCorrectAnswer(card, type) {
  if (type === 'single' || type === 'truefalse' || type === 'multiple') {
    const correctValues = card.dataset.correct.split(',').map(s => s.trim());
    card.querySelectorAll('.answer-option').forEach(opt => {
      const input = opt.querySelector('input');
      if (correctValues.includes(input.value)) opt.classList.add('correct');
    });
  }
}

function showExplanation(card, isCorrect, feedbackText) {
  const explanationPanel = card.querySelector('.panel-explanation');
  if (explanationPanel) {
    explanationPanel.style.display = 'block';
    if (!isCorrect) explanationPanel.classList.add('wrong');
  }
  
  if (!card.querySelector('.feedback-message') && feedbackText) {
    const feedbackEl = document.createElement('div');
    feedbackEl.className = 'feedback-message ' + (isCorrect ? 'feedback-positive' : 'feedback-negative');
    feedbackEl.innerHTML = `<span class="feedback-icon">${isCorrect ? '✓' : '✗'}</span> ${feedbackText}`;
    
    const container = card.querySelector('.answers-list, .matching-container, .ordering-list, .fillblank-container, .shortanswer-container');
    if (container) container.after(feedbackEl);
  }
}

// ===== Results Display =====
function showResults() {
  const { correct, wrong, unanswered, partial, selfGraded, totalPoints, earnedPoints } = quizState.results;
  const percentage = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
  
  const gradeScaleEl = document.getElementById('gradeScale');
  const gradeScale = gradeScaleEl ? parseInt(gradeScaleEl.value) : 20;
  const grade = ((earnedPoints / totalPoints) * gradeScale).toFixed(1);
  
  document.getElementById('statCorrect').textContent = correct;
  document.getElementById('statWrong').textContent = wrong;
  document.getElementById('statUnanswered').textContent = unanswered;
  
  const statPartial = document.getElementById('statPartial');
  if (statPartial) statPartial.textContent = partial;
  
  document.getElementById('statGrade').textContent = grade + '/' + gradeScale;
  
  const statPoints = document.getElementById('statPoints');
  if (statPoints) statPoints.textContent = earnedPoints.toFixed(1) + '/' + totalPoints;
  
  const scoreEl = document.getElementById('resultsScore');
  if (scoreEl) {
    scoreEl.textContent = `${earnedPoints.toFixed(1)}/${totalPoints} βαθμοί`;
    scoreEl.className = 'results-score';
    if (percentage >= 80) scoreEl.classList.add('excellent');
    else if (percentage >= 50) scoreEl.classList.add('good');
    else scoreEl.classList.add('needs-work');
  }
  
  document.getElementById('resultsPercentage').textContent = percentage + '%';
  
  const circle = document.getElementById('progressCircle');
  if (circle) {
    const circumference = 2 * Math.PI * 80;
    const offset = circumference - (percentage / 100) * circumference;
    setTimeout(() => circle.style.strokeDashoffset = offset, 100);
  }
  
  if (selfGraded > 0) {
    const notice = document.createElement('div');
    notice.className = 'self-grade-notice';
    notice.innerHTML = `⚠️ ${selfGraded} ερωτήσεις περιμένουν βαθμολόγηση.`;
    document.getElementById('resultsContainer').prepend(notice);
  }
  
  document.getElementById('resultsContainer').classList.remove('hidden');
  document.getElementById('btnSubmit').disabled = true;
  document.getElementById('btnSubmit').textContent = '✓ Υποβλήθηκε';
  
  // Apply button visibility based on config
  applyButtonVisibility();
  
  setViewMode('all');
  
  setTimeout(() => {
    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
  }, 300);
}

function updateResultsDisplay() {
  const { correct, wrong, partial, totalPoints, earnedPoints, selfGraded } = quizState.results;
  const percentage = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
  
  const gradeScaleEl = document.getElementById('gradeScale');
  const gradeScale = gradeScaleEl ? parseInt(gradeScaleEl.value) : 20;
  const grade = ((earnedPoints / totalPoints) * gradeScale).toFixed(1);
  
  document.getElementById('statCorrect').textContent = correct;
  document.getElementById('statWrong').textContent = wrong;
  
  const statPartial = document.getElementById('statPartial');
  if (statPartial) statPartial.textContent = partial;
  
  document.getElementById('statGrade').textContent = grade + '/' + gradeScale;
  
  const statPoints = document.getElementById('statPoints');
  if (statPoints) statPoints.textContent = earnedPoints.toFixed(1) + '/' + totalPoints;
  
  document.getElementById('resultsPercentage').textContent = percentage + '%';
  
  const scoreEl = document.getElementById('resultsScore');
  if (scoreEl) {
    scoreEl.textContent = `${earnedPoints.toFixed(1)}/${totalPoints} βαθμοί`;
    scoreEl.className = 'results-score';
    if (percentage >= 80) scoreEl.classList.add('excellent');
    else if (percentage >= 50) scoreEl.classList.add('good');
    else scoreEl.classList.add('needs-work');
  }
  
  const circle = document.getElementById('progressCircle');
  if (circle) {
    const circumference = 2 * Math.PI * 80;
    const offset = circumference - (percentage / 100) * circumference;
    circle.style.strokeDashoffset = offset;
  }
  
  if (selfGraded === 0) {
    const notice = document.querySelector('.self-grade-notice');
    if (notice) notice.remove();
  }
}

function reviewAnswers() {
  setViewMode('all');
  document.querySelector('.question-card')?.scrollIntoView({ behavior: 'smooth' });
}

function restartQuiz() {
  if (confirm('Ξεκινήσετε από την αρχή;')) location.reload();
}

// ===== Helper Functions =====
function handleCustomSelect(selectEl, customInputId) {
  const wrapper = document.getElementById(customInputId + 'Wrapper');
  if (selectEl.value === '__custom__') {
    wrapper.classList.add('show');
    document.getElementById(customInputId)?.focus();
  } else {
    wrapper.classList.remove('show');
  }
}

function handleDateSelect() {
  const select = document.getElementById('dateSelect');
  const wrapper = document.getElementById('dateCustomWrapper');
  
  if (select?.value === 'custom') {
    wrapper.classList.add('show');
    const dateInput = document.getElementById('dateCustom');
    if (dateInput) {
      const now = new Date();
      now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
      dateInput.value = now.toISOString().slice(0, 16);
    }
  } else {
    wrapper.classList.remove('show');
  }
}

function getStudentInfo() {
  const nameSelect = document.getElementById('studentName');
  const nameCustom = document.getElementById('studentNameCustom');
  const name = nameSelect?.value === '__custom__' ? nameCustom?.value : nameSelect?.value || '';
  
  const classSelect = document.getElementById('studentClass');
  const classCustom = document.getElementById('studentClassCustom');
  const studentClass = classSelect?.value === '__custom__' ? classCustom?.value : classSelect?.value || '';
  
  const dateSelect = document.getElementById('dateSelect');
  const defaultDate = document.body.dataset.defaultDate || new Date().toLocaleDateString('el-GR');
  let date;
  
  if (dateSelect?.value === 'default') date = defaultDate;
  else if (dateSelect?.value === 'current') date = new Date().toLocaleString('el-GR');
  else {
    const customDate = document.getElementById('dateCustom')?.value;
    date = customDate ? new Date(customDate).toLocaleString('el-GR') : new Date().toLocaleString('el-GR');
  }
  
  const gradeScale = document.getElementById('gradeScale')?.value || '20';
  const grade = document.getElementById('statGrade')?.textContent || '0';
  
  return { name, studentClass, date, grade, gradeScale };
}

function togglePanel(panelId) {
  const panel = document.getElementById(panelId);
  if (!panel) return;
  
  const isVisible = panel.style.display !== 'none';
  const questionCard = panel.closest('.question-card');
  
  if (questionCard) {
    questionCard.querySelectorAll('.panel:not(.panel-explanation)').forEach(p => p.style.display = 'none');
    questionCard.querySelectorAll('.helper-btn').forEach(btn => btn.classList.remove('active'));
  }
  
  if (!isVisible) {
    panel.style.display = 'block';
    event?.target?.closest('.helper-btn')?.classList.add('active');
  }
}

// ===== Code Block Setup with Syntax Highlighting =====
function setupCodeBlocks() {
  document.querySelectorAll('pre code').forEach((codeBlock) => {
    const pre = codeBlock.parentElement;
    if (pre.parentElement.classList.contains('code-wrapper')) return;
    
    const wrapper = document.createElement('div');
    wrapper.className = 'code-wrapper';
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);
    
    // Detect language
    const langClass = Array.from(codeBlock.classList).find(c => c.startsWith('language-'));
    const language = langClass ? langClass.replace('language-', '') : 'text';
    
    const actions = document.createElement('div');
    actions.className = 'code-actions';
    
    // Language badge
    const langBadge = document.createElement('span');
    langBadge.className = 'code-language';
    langBadge.textContent = language.toUpperCase();
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'code-action-btn copy-btn';
    copyBtn.innerHTML = '📋 Αντιγραφή';
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(codeBlock.textContent).then(() => {
        copyBtn.innerHTML = '✓ OK!';
        setTimeout(() => copyBtn.innerHTML = '📋 Αντιγραφή', 2000);
      });
    };
    
    const ideUrl = document.body.dataset.ideUrl || 'https://glot.io/new/python';
    const runBtn = document.createElement('button');
    runBtn.className = 'code-action-btn run-btn';
    runBtn.innerHTML = '▶️ IDE';
    runBtn.onclick = () => {
      navigator.clipboard.writeText(codeBlock.textContent);
      showToast('Κώδικας αντιγράφηκε! Ανοίγει το IDE...', 'info');
      window.open(ideUrl, '_blank');
    };
    
    actions.appendChild(langBadge);
    actions.appendChild(copyBtn);
    actions.appendChild(runBtn);
    wrapper.insertBefore(actions, pre);
  });
}

function showToast(message, type = 'info') {
  document.querySelectorAll('.toast').forEach(t => t.remove());
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ===== Print & Export =====
function printResults() { window.print(); }

function generateFilename(extension = 'pdf') {
  const info = getStudentInfo();
  const className = (info.studentClass || 'quiz').replace(/\s+/g, '');
  const name = info.name ? info.name.replace(/\s+/g, '_') : 'student';
  const date = new Date().toISOString().slice(0, 10);
  return `${className}-${name}-${date}.${extension}`;
}

function exportPDF() {
  const studentInfo = getStudentInfo();
  const { correct, wrong, partial, totalPoints, earnedPoints } = quizState.results;
  const percentage = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
  
  const title = document.querySelector('.quiz-title')?.textContent || 'Quiz';
  const subject = document.querySelector('.quiz-meta .subject')?.textContent || '';
  const scoreColor = percentage >= 80 ? '#4caf50' : (percentage >= 50 ? '#667eea' : '#f44336');
  const filename = generateFilename('pdf');
  
  const html = `<!DOCTYPE html><html lang="el"><head><meta charset="UTF-8"><title>${title}</title>
<style>@media print{.no-print{display:none!important}@page{size:A4;margin:1.5cm}}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;padding:30px;color:#333;max-width:800px;margin:0 auto}
.btn{position:fixed;top:20px;right:20px;padding:12px 24px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:8px;cursor:pointer}
.header{text-align:center;padding-bottom:20px;margin-bottom:24px;border-bottom:3px solid #667eea}
.header h1{color:#667eea;font-size:28px}
.info{display:grid;grid-template-columns:1fr 1fr;gap:12px;background:#f8f9fa;padding:20px;border-radius:12px;margin-bottom:24px}
.info strong{color:#667eea}
.score{text-align:center;padding:30px;background:linear-gradient(135deg,rgba(102,126,234,.1),rgba(118,75,162,.1));border-radius:16px;margin-bottom:24px}
.pct{font-size:64px;font-weight:bold;color:${scoreColor}}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:30px}
.stat{text-align:center;padding:16px;background:#f8f9fa;border-radius:12px}
.stat-val{font-size:24px;font-weight:bold}
.stat-lbl{font-size:12px;color:#666}
.tip{background:#e3f2fd;padding:16px;border-radius:8px;margin-bottom:20px;color:#1565c0}
.footer{text-align:center;margin-top:40px;padding-top:20px;border-top:1px solid #e0e0e0;color:#999;font-size:12px}
</style></head><body>
<button class="btn no-print" onclick="window.print()">🖨️ Εκτύπωση / PDF</button>
<div class="tip no-print">💡 Για PDF επιλέξτε "Αποθήκευση ως PDF". Όνομα: <code>${filename}</code></div>
<div class="header"><h1>📝 ${title}</h1><p>${subject}</p></div>
<div class="info">
<div><strong>Όνομα:</strong> ${studentInfo.name || '—'}</div>
<div><strong>Τμήμα:</strong> ${studentInfo.studentClass || '—'}</div>
<div><strong>Ημερομηνία:</strong> ${studentInfo.date || '—'}</div>
<div><strong>Βαθμός:</strong> ${studentInfo.grade}</div>
</div>
<div class="score"><div class="pct">${percentage}%</div>
<div style="color:#666;margin-top:8px">${earnedPoints.toFixed(1)} / ${totalPoints} βαθμοί</div></div>
<div class="stats">
<div class="stat"><div class="stat-val" style="color:#4caf50">${correct}</div><div class="stat-lbl">✓ Σωστές</div></div>
<div class="stat"><div class="stat-val" style="color:#ff9800">${partial}</div><div class="stat-lbl">◐ Μερικές</div></div>
<div class="stat"><div class="stat-val" style="color:#f44336">${wrong}</div><div class="stat-lbl">✗ Λάθος</div></div>
<div class="stat"><div class="stat-val" style="color:#667eea">${studentInfo.grade}</div><div class="stat-lbl">📊 Βαθμός</div></div>
</div>
<div class="footer">Quiz Generator v4.1 • ${new Date().toLocaleString('el-GR')}</div>
</body></html>`;
  
  const w = window.open('', '_blank');
  if (w) {
    w.document.write(html);
    w.document.close();
    setTimeout(() => w.print(), 500);
  }
}

// ===== EMAIL =====
function sendEmail() {
  const info = getStudentInfo();
  const email = document.body.dataset.email || '';
  
  if (!email) {
    showToast('Δεν έχει οριστεί email αποστολής', 'error');
    return;
  }
  
  const title = document.querySelector('.quiz-title')?.textContent || 'Quiz';
  const { totalPoints, earnedPoints, correct, wrong, partial } = quizState.results;
  const pct = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
  
  const subject = encodeURIComponent(`Quiz: ${title} - ${info.name} (${info.studentClass})`);
  const body = encodeURIComponent(`📝 ΑΠΟΤΕΛΕΣΜΑΤΑ QUIZ
═══════════════════════════════

📚 ${title}

👤 ΣΤΟΙΧΕΙΑ ΜΑΘΗΤΗ
• Ονοματεπώνυμο: ${info.name || '—'}
• Τμήμα: ${info.studentClass || '—'}
• Ημερομηνία: ${info.date}

📊 ΑΠΟΤΕΛΕΣΜΑΤΑ
• Ποσοστό: ${pct}%
• Βαθμοί: ${earnedPoints.toFixed(1)}/${totalPoints}
• Βαθμός: ${info.grade}

📈 ΑΝΑΛΥΤΙΚΑ
• ✓ Σωστές: ${correct}
• ◐ Μερικές: ${partial}
• ✗ Λάθος: ${wrong}

═══════════════════════════════
Quiz Generator v4.1`);
  
  window.open(`mailto:${email}?subject=${subject}&body=${body}`);
  showToast('Άνοιξε το email σας', 'info');
}

// ===== GOOGLE DRIVE =====
function shareToCloud() {
  const driveFolder = document.body.dataset.shareFolder;
  
  if (!driveFolder) {
    showToast('Δεν έχει οριστεί φάκελος Google Drive', 'error');
    return;
  }
  
  showToast('Ετοιμάζεται το PDF για ανέβασμα...', 'info');
  exportPDF();
  
  setTimeout(() => {
    showToast('Ανοίγει ο φάκελος Google Drive...', 'info');
    window.open(driveFolder, '_blank');
  }, 2000);
}

// ===== MARKDOWN EXPORT =====
function generateMarkdownResults() {
  const studentInfo = getStudentInfo();
  const { correct, wrong, unanswered, partial, totalPoints, earnedPoints } = quizState.results;
  const percentage = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0;
  
  const title = document.querySelector('.quiz-title')?.textContent || 'Quiz';
  const subject = document.querySelector('.quiz-meta .subject')?.textContent || '';
  
  let md = `# 📝 Αποτελέσματα Quiz\n\n`;
  md += `## ${title}\n`;
  md += `${subject}\n\n`;
  md += `---\n\n`;
  
  // Student Info
  md += `## 👤 Στοιχεία Μαθητή\n\n`;
  md += `| Πεδίο | Τιμή |\n`;
  md += `|-------|------|\n`;
  md += `| **Ονοματεπώνυμο** | ${studentInfo.name || '—'} |\n`;
  md += `| **Τμήμα** | ${studentInfo.studentClass || '—'} |\n`;
  md += `| **Ημερομηνία** | ${studentInfo.date || '—'} |\n`;
  md += `| **Βαθμός** | ${studentInfo.grade} |\n\n`;
  
  // Results Summary
  md += `## 📊 Συνολικά Αποτελέσματα\n\n`;
  md += `| Μετρική | Τιμή |\n`;
  md += `|---------|------|\n`;
  md += `| **Ποσοστό** | ${percentage}% |\n`;
  md += `| **Βαθμοί** | ${earnedPoints.toFixed(1)} / ${totalPoints} |\n`;
  md += `| ✓ Σωστές | ${correct} |\n`;
  md += `| ◐ Μερικώς σωστές | ${partial} |\n`;
  md += `| ✗ Λάθος | ${wrong} |\n`;
  md += `| ○ Αναπάντητες | ${unanswered} |\n\n`;
  
  // Performance indicator
  let performance = '';
  if (percentage >= 90) performance = '🏆 Εξαιρετική επίδοση!';
  else if (percentage >= 75) performance = '🌟 Πολύ καλή επίδοση!';
  else if (percentage >= 50) performance = '👍 Καλή επίδοση';
  else performance = '📚 Χρειάζεται περισσότερη μελέτη';
  
  md += `> ${performance}\n\n`;
  
  // Detailed Results
  md += `---\n\n`;
  md += `## 📋 Αναλυτικά Αποτελέσματα\n\n`;
  
  document.querySelectorAll('.question-card').forEach((card, index) => {
    const questionText = card.querySelector('.question-text')?.textContent?.trim() || '';
    const points = quizState.questionPoints[card.id] || 1;
    const type = card.dataset.type || 'single';
    
    const isCorrect = card.classList.contains('result-correct');
    const isPartial = card.classList.contains('result-partial');
    const isIncorrect = card.classList.contains('result-incorrect');
    
    let status = '';
    let earnedPts = 0;
    
    if (isCorrect) {
      status = '✓ Σωστό';
      earnedPts = points;
    } else if (isPartial) {
      status = '◐ Μερικώς';
      earnedPts = calculatePartialPoints(card, type, points);
    } else if (isIncorrect) {
      status = '✗ Λάθος';
      earnedPts = 0;
    } else {
      status = '○ Αναπάντητη';
      earnedPts = 0;
    }
    
    md += `### Ερώτηση ${index + 1} — ${status} (${earnedPts.toFixed(1)}/${points} β.)\n\n`;
    md += `> ${questionText}\n\n`;
    
    // Show user's answer based on type
    const userAnswer = quizState.answers[card.id];
    
    if (type === 'single' || type === 'truefalse') {
      const selectedOption = card.querySelector(`input[value="${userAnswer}"]`);
      const selectedLabel = selectedOption?.closest('.answer-option')?.querySelector('.answer-text')?.textContent || '—';
      md += `**Απάντηση:** ${selectedLabel}\n\n`;
      
      if (!isCorrect) {
        const correctValue = card.dataset.correct;
        const correctOption = card.querySelector(`input[value="${correctValue}"]`);
        const correctLabel = correctOption?.closest('.answer-option')?.querySelector('.answer-text')?.textContent || '';
        md += `**Σωστή απάντηση:** ${correctLabel}\n\n`;
      }
    } else if (type === 'multiple') {
      const selected = userAnswer || [];
      const selectedLabels = selected.map(val => {
        const opt = card.querySelector(`input[value="${val}"]`);
        return opt?.closest('.answer-option')?.querySelector('.answer-text')?.textContent || val;
      });
      md += `**Επιλογές:** ${selectedLabels.length > 0 ? selectedLabels.join(', ') : '—'}\n\n`;
    } else if (type === 'matching') {
      md += `**Αντιστοιχίσεις:**\n`;
      const matches = userAnswer || {};
      Object.entries(matches).forEach(([item, value]) => {
        const row = card.querySelector(`.matching-row[data-item="${item}"]`);
        const itemText = row?.querySelector('.matching-item')?.textContent || item;
        const isRowCorrect = row?.classList.contains('match-correct');
        md += `- ${itemText} → ${value} ${isRowCorrect ? '✓' : '✗'}\n`;
      });
      md += `\n`;
    } else if (type === 'ordering') {
      md += `**Σειρά:**\n`;
      card.querySelectorAll('.ordering-item').forEach((item, i) => {
        const text = item.querySelector('.ordering-text')?.textContent || '';
        const isOrderCorrect = item.classList.contains('order-correct');
        md += `${i + 1}. ${text} ${isOrderCorrect ? '✓' : '✗'}\n`;
      });
      md += `\n`;
    } else if (type === 'fillblank') {
      md += `**Απαντήσεις κενών:**\n`;
      const blanks = userAnswer || {};
      Object.entries(blanks).forEach(([blank, value]) => {
        const input = card.querySelector(`.fillblank-input[data-blank="${blank}"]`);
        const isBlankCorrect = input?.classList.contains('blank-correct');
        md += `- Κενό ${blank.replace('blank', '')}: "${value}" ${isBlankCorrect ? '✓' : '✗'}\n`;
      });
      md += `\n`;
    } else if (type === 'shortanswer') {
      md += `**Απάντηση:**\n\`\`\`\n${userAnswer || '(κενό)'}\n\`\`\`\n\n`;
      const sampleAnswer = card.dataset.sampleAnswer;
      if (sampleAnswer) {
        md += `**Ενδεικτική απάντηση:**\n\`\`\`\n${sampleAnswer.replace(/&#10;/g, '\n')}\n\`\`\`\n\n`;
      }
    }
  });
  
  // Footer
  md += `---\n\n`;
  md += `*Quiz Generator v4.1 — ${new Date().toLocaleString('el-GR')}*\n`;
  
  return md;
}

function calculatePartialPoints(card, type, maxPoints) {
  const userAnswer = quizState.answers[card.id];
  
  if (type === 'matching') {
    const correctMatches = JSON.parse(card.dataset.correct);
    const userMatches = userAnswer || {};
    let correctCount = 0;
    Object.entries(correctMatches).forEach(([item, correct]) => {
      if (userMatches[item] === correct) correctCount++;
    });
    return (correctCount / Object.keys(correctMatches).length) * maxPoints;
  } else if (type === 'ordering') {
    const correctOrder = card.dataset.correct.split(',').map(s => s.trim());
    const items = card.querySelectorAll('.ordering-item');
    let correctCount = 0;
    items.forEach((item, index) => {
      if (correctOrder[index] === item.dataset.id) correctCount++;
    });
    return (correctCount / correctOrder.length) * maxPoints;
  } else if (type === 'fillblank') {
    const correctAnswers = JSON.parse(card.dataset.correct);
    const userAnswers = userAnswer || {};
    let correctCount = 0;
    Object.entries(correctAnswers).forEach(([blank, correct]) => {
      const userVal = (userAnswers[blank] || '').toLowerCase();
      const correctOptions = correct.toLowerCase().split('|').map(s => s.trim());
      if (correctOptions.includes(userVal)) correctCount++;
    });
    return (correctCount / Object.keys(correctAnswers).length) * maxPoints;
  } else if (type === 'multiple') {
    const correctAnswer = card.dataset.correct.split(',').map(s => s.trim());
    const userSelected = userAnswer || [];
    let correctCount = 0;
    let wrongCount = 0;
    userSelected.forEach(val => {
      if (correctAnswer.includes(val)) correctCount++;
      else wrongCount++;
    });
    return Math.max(0, (correctCount - wrongCount) / correctAnswer.length * maxPoints);
  }
  
  return 0;
}

function exportMarkdown() {
  const md = generateMarkdownResults();
  const studentInfo = getStudentInfo();
  
  const filename = generateFilename('md');
  
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  showToast('Το Markdown αποθηκεύτηκε!', 'success');
}

// ===== GOOGLE DOCS EXPORT =====
function exportToGoogleDocs() {
  const googleDocsUrl = document.body.dataset.googleDocs;
  const studentInfo = getStudentInfo();
  
  if (!googleDocsUrl) {
    showToast('Δεν έχει οριστεί Google Docs URL', 'error');
    return;
  }
  
  // Generate markdown content
  const md = generateMarkdownResults();
  
  // Copy to clipboard
  navigator.clipboard.writeText(md).then(() => {
    showToast('Αποτελέσματα αντιγράφηκαν! Ανοίγει το Google Docs...', 'success');
    
    // Open Google Docs in new tab with student name in title
    const studentName = studentInfo.name || 'Μαθητής';
    const studentClass = studentInfo.studentClass || '';
    
    // Add a small delay then open Google Docs
    setTimeout(() => {
      const newTab = window.open(googleDocsUrl, `Quiz_${studentClass}_${studentName}`);
      
      // Show instructions
      setTimeout(() => {
        showToast('Κάντε επικόλληση (Ctrl+V) στο Google Docs!', 'info');
      }, 1000);
    }, 500);
    
  }).catch(err => {
    console.error('Clipboard error:', err);
    showToast('Σφάλμα αντιγραφής. Δοκιμάστε ξανά.', 'error');
  });
}

// ===== COPY MARKDOWN TO CLIPBOARD =====
function copyMarkdownToClipboard() {
  const md = generateMarkdownResults();
  
  navigator.clipboard.writeText(md).then(() => {
    showToast('Αποτελέσματα αντιγράφηκαν στο clipboard!', 'success');
  }).catch(() => {
    showToast('Σφάλμα αντιγραφής', 'error');
  });
}
