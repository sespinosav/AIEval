// Configuration
const API_ENDPOINT = 'https://t82wqf0so0.execute-api.us-east-1.amazonaws.com/Prod/evaluator';
let points = 0;

// Sample list of common words (a subset; ideally replace with the full 500-word list)
// Each word object includes a "word" and a "difficulty" property. 
// (For example, you might mark lower-frequency words as "difficult".)
// For demonstration, a few sample words are given.
const commonWords = [
  { word: "the",           difficulty: "easy" },
  { word: "of",            difficulty: "easy" },
  { word: "and",           difficulty: "easy" },
  { word: "a",             difficulty: "easy" },
  { word: "to",            difficulty: "easy" },
  { word: "in",            difficulty: "easy" },
  { word: "is",            difficulty: "easy" },
  { word: "you",           difficulty: "easy" },
  { word: "that",          difficulty: "easy" },
  { word: "it",            difficulty: "easy" },
  { word: "he",            difficulty: "easy" },
  { word: "was",           difficulty: "easy" },
  { word: "for",           difficulty: "easy" },
  { word: "on",            difficulty: "easy" },
  { word: "are",           difficulty: "easy" },
  { word: "as",            difficulty: "easy" },
  { word: "with",          difficulty: "easy" },
  { word: "his",           difficulty: "easy" },
  { word: "they",          difficulty: "easy" },
  { word: "I",             difficulty: "easy" },
  { word: "at",            difficulty: "easy" },
  { word: "be",            difficulty: "easy" },
  { word: "this",          difficulty: "easy" },
  { word: "have",          difficulty: "easy" },
  { word: "from",          difficulty: "easy" },
  { word: "or",            difficulty: "easy" },
  { word: "one",           difficulty: "easy" },
  { word: "had",           difficulty: "easy" },
  { word: "by",            difficulty: "easy" },
  { word: "word",          difficulty: "easy" },
  { word: "but",           difficulty: "easy" },
  { word: "not",           difficulty: "easy" },
  { word: "what",          difficulty: "easy" },
  { word: "all",           difficulty: "easy" },
  { word: "were",          difficulty: "easy" },
  { word: "we",            difficulty: "easy" },
  { word: "when",          difficulty: "easy" },
  { word: "your",          difficulty: "easy" },
  { word: "can",           difficulty: "easy" },
  { word: "said",          difficulty: "easy" },
  { word: "there",         difficulty: "medium" },
  { word: "use",           difficulty: "easy" },
  { word: "an",            difficulty: "easy" },
  { word: "each",          difficulty: "easy" },
  { word: "which",         difficulty: "medium" },
  { word: "she",           difficulty: "easy" },
  { word: "do",            difficulty: "easy" },
  { word: "how",           difficulty: "easy" },
  { word: "their",         difficulty: "medium" },
  { word: "if",            difficulty: "easy" },
  { word: "will",          difficulty: "easy" },
  { word: "up",            difficulty: "easy" },
  { word: "other",         difficulty: "medium" },
  { word: "about",         difficulty: "medium" },
  { word: "out",           difficulty: "easy" },
  { word: "many",          difficulty: "easy" },
  { word: "then",          difficulty: "easy" },
  { word: "them",          difficulty: "easy" },
  { word: "these",         difficulty: "medium" },
  { word: "so",            difficulty: "easy" },
  { word: "some",          difficulty: "easy" },
  { word: "her",           difficulty: "easy" },
  { word: "would",         difficulty: "medium" },
  { word: "make",          difficulty: "easy" },
  { word: "like",          difficulty: "easy" },
  { word: "him",           difficulty: "easy" },
  { word: "into",          difficulty: "easy" },
  { word: "time",          difficulty: "easy" },
  { word: "has",           difficulty: "easy" },
  { word: "look",          difficulty: "easy" },
  { word: "two",           difficulty: "easy" },
  { word: "more",          difficulty: "easy" },
  { word: "write",         difficulty: "medium" },
  { word: "go",            difficulty: "easy" },
  { word: "see",           difficulty: "easy" },
  { word: "number",        difficulty: "medium" },
  { word: "no",            difficulty: "easy" },
  { word: "way",           difficulty: "easy" },
  { word: "could",         difficulty: "medium" },
  { word: "people",        difficulty: "medium" },
  { word: "my",            difficulty: "easy" },
  { word: "than",          difficulty: "easy" },
  { word: "first",         difficulty: "medium" },
  { word: "water",         difficulty: "medium" },
  { word: "been",          difficulty: "easy" },
  { word: "call",          difficulty: "easy" },
  { word: "who",           difficulty: "easy" },
  { word: "oil",           difficulty: "easy" },
  { word: "its",           difficulty: "easy" },
  { word: "now",           difficulty: "easy" },
  { word: "find",          difficulty: "easy" },
  { word: "long",          difficulty: "easy" },
  { word: "down",          difficulty: "easy" },
  { word: "day",           difficulty: "easy" },
  { word: "did",           difficulty: "easy" },
  { word: "get",           difficulty: "easy" },
  { word: "come",          difficulty: "easy" },
  { word: "made",          difficulty: "easy" },
  { word: "may",           difficulty: "easy" },
  { word: "part",          difficulty: "easy" },
  { word: "over",          difficulty: "easy" },
  { word: "new",           difficulty: "easy" },
  { word: "sound",         difficulty: "medium" },
  { word: "take",          difficulty: "easy" },
  { word: "only",          difficulty: "easy" },
  { word: "little",        difficulty: "medium" },
  { word: "work",          difficulty: "easy" },
  { word: "know",          difficulty: "easy" },
  { word: "place",         difficulty: "medium" },
  { word: "year",          difficulty: "easy" },
  { word: "live",          difficulty: "easy" },
  { word: "me",            difficulty: "easy" },
  { word: "back",          difficulty: "easy" },
  { word: "give",          difficulty: "easy" },
  { word: "most",          difficulty: "easy" },
  { word: "very",          difficulty: "easy" },
  { word: "after",         difficulty: "medium" },
  { word: "thing",         difficulty: "medium" },
  { word: "our",           difficulty: "easy" },
  { word: "just",          difficulty: "easy" },
  { word: "name",          difficulty: "easy" },
  { word: "good",          difficulty: "easy" },
  { word: "sentence",      difficulty: "difficult" },
  { word: "man",           difficulty: "easy" },
  { word: "think",         difficulty: "medium" },
  { word: "say",           difficulty: "easy" },
  { word: "great",         difficulty: "medium" },
  { word: "where",         difficulty: "medium" },
  { word: "help",          difficulty: "easy" },
  { word: "through",       difficulty: "medium" },
  { word: "much",          difficulty: "easy" },
  { word: "before",        difficulty: "medium" },
  { word: "line",          difficulty: "easy" },
  { word: "right",         difficulty: "medium" },
  { word: "too",           difficulty: "easy" },
  { word: "mean",          difficulty: "easy" },
  { word: "old",           difficulty: "easy" },
  { word: "any",           difficulty: "easy" },
  { word: "same",          difficulty: "easy" },
  { word: "tell",          difficulty: "easy" },
  { word: "boy",           difficulty: "easy" },
  { word: "follow",        difficulty: "medium" },
  { word: "came",          difficulty: "easy" },
  { word: "want",          difficulty: "easy" },
  { word: "show",          difficulty: "easy" },
  { word: "also",          difficulty: "easy" },
  { word: "around",        difficulty: "medium" },
  { word: "form",          difficulty: "easy" },
  { word: "three",         difficulty: "medium" },
  { word: "small",         difficulty: "medium" },
  { word: "set",           difficulty: "easy" },
  { word: "put",           difficulty: "easy" },
  { word: "end",           difficulty: "easy" },
  { word: "does",          difficulty: "easy" },
  { word: "another",       difficulty: "medium" },
  { word: "well",          difficulty: "easy" },
  { word: "large",         difficulty: "medium" },
  { word: "must",          difficulty: "easy" },
  { word: "big",           difficulty: "easy" },
  { word: "even",          difficulty: "easy" },
  { word: "such",          difficulty: "easy" },
  { word: "because",       difficulty: "medium" },
  { word: "turn",          difficulty: "easy" },
  { word: "here",          difficulty: "easy" },
  { word: "why",           difficulty: "easy" },
  { word: "ask",           difficulty: "easy" },
  { word: "went",          difficulty: "easy" },
  { word: "men",           difficulty: "easy" },
  { word: "read",          difficulty: "easy" },
  { word: "need",          difficulty: "easy" },
  { word: "land",          difficulty: "easy" },
  { word: "different",     difficulty: "difficult" },
  { word: "home",          difficulty: "easy" },
  { word: "us",            difficulty: "easy" },
  { word: "move",          difficulty: "easy" },
  { word: "try",           difficulty: "easy" },
  { word: "kind",          difficulty: "easy" },
  { word: "hand",          difficulty: "easy" },
  { word: "picture",       difficulty: "medium" },
  { word: "again",         difficulty: "medium" },
  { word: "change",        difficulty: "medium" },
  { word: "off",           difficulty: "easy" },
  { word: "play",          difficulty: "easy" },
  { word: "spell",         difficulty: "medium" },
  { word: "air",           difficulty: "easy" },
  { word: "away",          difficulty: "easy" },
  { word: "animal",        difficulty: "medium" },
  { word: "house",         difficulty: "medium" },
  { word: "point",         difficulty: "medium" },
  { word: "page",          difficulty: "easy" },
  { word: "letter",        difficulty: "medium" },
  { word: "mother",        difficulty: "medium" },
  { word: "answer",        difficulty: "medium" },
  { word: "found",         difficulty: "medium" },
  { word: "study",         difficulty: "medium" },
  { word: "still",         difficulty: "medium" },
  { word: "learn",         difficulty: "medium" },
  { word: "should",        difficulty: "medium" },
  { word: "America",       difficulty: "medium" },
  { word: "world",         difficulty: "medium" },

  { word: "inconceivable",   difficulty: "difficult" },
  { word: "perspicacious",   difficulty: "difficult" },
  { word: "obfuscate",       difficulty: "difficult" },
  { word: "idiosyncratic",   difficulty: "difficult" },
  { word: "antediluvian",    difficulty: "difficult" },
  { word: "sesquipedalian",  difficulty: "difficult" },
  { word: "ephemeral",       difficulty: "difficult" },
  { word: "magnanimous",     difficulty: "difficult" },
  { word: "obstreperous",    difficulty: "difficult" },
  { word: "esoteric",        difficulty: "difficult" },
  { word: "inscrutable",     difficulty: "difficult" },
  { word: "recalcitrant",    difficulty: "difficult" },
  { word: "cognizant",       difficulty: "difficult" },
  { word: "gregarious",      difficulty: "difficult" },
  { word: "perfunctory",     difficulty: "difficult" }
];


let currentWord = null;

// DOM Elements
const sentenceInput = document.getElementById('sentence');
const evaluateButton = document.getElementById('evaluate');
const resultDiv = document.getElementById('result');
const resultContent = document.getElementById('result-content');
const historyDiv = document.getElementById('history');
const pointsDisplay = document.getElementById('points');
const displayWordSpan = document.getElementById('display-word');

// On page load, select a random word
selectRandomWord();

function selectRandomWord() {
  currentWord = commonWords[Math.floor(Math.random() * commonWords.length)];
  displayWordSpan.textContent = currentWord.word;
}

evaluateButton.addEventListener('click', evaluateUsage);
sentenceInput.addEventListener('keypress', handleEnter);

function handleEnter(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    evaluateUsage();
  }
}

// Helper function to check punctuation:
// Checks if sentence starts with uppercase letter and ends with proper punctuation (. ! ?)
function checkPunctuation(sentence) {
  let score = 0;
  let explanation = '';
  if (sentence[0] && sentence[0] === sentence[0].toUpperCase()) {
    score++;
  } else {
    explanation += "Sentence should start with a capital letter. ";
  }
  if (/[.!?]$/.test(sentence.trim())) {
    score++;
  } else {
    explanation += "Sentence should end with a punctuation mark (. ! ?). ";
  }
  return { score, explanation };
}

async function evaluateUsage() {
  const sentence = sentenceInput.value.trim();

  if (!sentence) {
    showError('Please enter a sentence.');
    return;
  }

  // Disable button and show loading state
  evaluateButton.disabled = true;
  evaluateButton.innerHTML = '<span class="animate-pulse">Evaluating...</span>';

  try {
    // Call your evaluator API with the current word and the sentence
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word: currentWord.word, sentence })
    });
    const data = await response.json();

    // Check punctuation
    const punctuationResult = checkPunctuation(sentence);

    // Compute points for this round
    let roundPoints = 0;
    if (data.correct) {
      roundPoints += 10; // base points for correct usage
      if (currentWord.difficulty === "difficult") {
        roundPoints += 5; // bonus for difficult word correct usage
      }
    } else {
      if (currentWord.difficulty === "easy") {
        roundPoints -= 5; // extra penalty for failing an easy word
      }
    }
    // Adjust points based on punctuation score:
    if (punctuationResult.score === 2) {
      roundPoints += 2;
    } else if (punctuationResult.score === 1) {
      roundPoints += 1;
    } else {
      roundPoints -= 2;
    }

    // Update result display with API explanation and punctuation explanation
    showResult(data, punctuationResult, roundPoints);
    updateHistory(data, sentence, roundPoints);
    updatePoints(roundPoints);
  } catch (error) {
    showError('Error connecting to the server');
  } finally {
    evaluateButton.disabled = false;
    evaluateButton.textContent = 'Evaluate';
    // Clear sentence input and choose a new word
    sentenceInput.value = '';
    selectRandomWord();
  }
}

function showResult(data, punctuationResult, roundPoints) {
  resultDiv.classList.remove('hidden');
  const resultIcon = data.correct ? '✅' : '❌';
  const resultClass = data.correct ? 'text-green-600' : 'text-red-600';
  resultContent.innerHTML = `
    <div class="text-2xl mb-3">${resultIcon}</div>
    <p class="font-bold ${resultClass} mb-2">
      ${data.correct ? 'Correct Usage!' : 'Incorrect Usage'}
    </p>
    <p class="text-gray-700">${data.explanation}</p>
    <p class="text-gray-700">${punctuationResult.explanation}</p>
    <p class="text-gray-700">Points earned this round: ${roundPoints}</p>
  `;
  resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function updateHistory(data, sentence, roundPoints) {
  const historyItem = document.createElement('div');
  historyItem.className = `bg-white rounded-lg shadow p-4 ${data.correct ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`;
  historyItem.innerHTML = `
    <div class="flex justify-between items-start">
      <div>
        <p class="font-medium text-gray-800">Word: ${currentWord.word} (${currentWord.difficulty})</p>
        <p class="text-gray-600 text-sm">${sentence}</p>
        <p class="text-gray-600 text-sm">Points: ${roundPoints}</p>
      </div>
      <span class="text-lg">${data.correct ? '✅' : '❌'}</span>
    </div>
  `;
  historyDiv.insertBefore(historyItem, historyDiv.firstChild);
}

function updatePoints(roundPoints) {
  points += roundPoints;
  pointsDisplay.textContent = points;
  pointsDisplay.classList.add('scale-up');
  setTimeout(() => pointsDisplay.classList.remove('scale-up'), 500);
}

function showError(message) {
  resultDiv.classList.remove('hidden');
  resultContent.innerHTML = `
    <div class="text-2xl mb-3">⚠️</div>
    <p class="text-red-600">${message}</p>
  `;
}
