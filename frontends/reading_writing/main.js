const API_ENDPOINT_GENERATOR = 'https://qrzq57k6qc.execute-api.us-east-1.amazonaws.com/Prod/api/v1/reading-generator';
const API_ENDPOINT_EVALUATOR = 'https://qrzq57k6qc.execute-api.us-east-1.amazonaws.com/Prod/api/v1/writing-evaluator';

let currentArticle = '';
let totalScore = 0;
let timerInterval;
let timeLeft = 300; // 5 minutes in seconds

// DOM Elements
const timerElement = document.getElementById('timer');
const timerProgress = document.getElementById('timer-progress');
const articleContent = document.getElementById('article-content');
const startWritingBtn = document.getElementById('start-writing');
const articleSection = document.getElementById('article-section');
const writingSection = document.getElementById('writing-section');
const summaryInput = document.getElementById('summary-input');
const submitSummaryBtn = document.getElementById('submit-summary');
const resultsSection = document.getElementById('results-section');
const wordCountElement = document.getElementById('word-count');
const tryAgainBtn = document.getElementById('try-again');
const totalScoreDisplay = document.getElementById('total-score');
const historyDiv = document.getElementById('history');

// Initially hide the timer and the "I'm Ready to Write" button.
timerElement.style.display = 'none';
timerProgress.style.display = 'none';
startWritingBtn.style.display = 'none';

// Initialize: fetch the article once the window loads.
window.addEventListener('load', fetchNewArticle);

// Event Listeners
startWritingBtn.addEventListener('click', startWriting);
submitSummaryBtn.addEventListener('click', evaluateSummary);
tryAgainBtn.addEventListener('click', resetExercise);
summaryInput.addEventListener('input', updateWordCount);

async function fetchNewArticle() {
    // Show a loading message in the article section
    articleContent.innerHTML = '<p class="text-center text-gray-600">Loading article...</p>';

    try {
        const response = await fetch(API_ENDPOINT_GENERATOR);
        const data = await response.json();
        currentArticle = data.article+"...";

        // Use Marked to convert markdown to HTML.
        // This will convert markdown markers like ###, *phrase*, and \n to styled HTML.
        articleContent.innerHTML = marked.parse(currentArticle);

        // Now that the article has loaded, show the timer and the "I'm Ready to Write" button.
        timerElement.style.display = '';
        timerProgress.style.display = '';
        startWritingBtn.style.display = '';

        // Start the timer.
        startTimer();
    } catch (error) {
        console.error('Error fetching article:', error);
        articleContent.innerHTML = '<p>Error loading article. Please try again.</p>';
    }
}

function startTimer() {
    timeLeft = 300;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        updateProgressBar();

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            startWriting();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateProgressBar() {
    const percentage = (timeLeft / 300) * 100;
    timerProgress.style.width = `${percentage}%`;
}

function startWriting() {
    clearInterval(timerInterval);
    articleSection.classList.add('hidden');
    writingSection.classList.remove('hidden');
}

function updateWordCount() {
    const words = summaryInput.value.trim().split(/\s+/).filter(word => word.length > 0);
    wordCountElement.textContent = `Words: ${words.length}`;
}

async function evaluateSummary() {
    if (!summaryInput.value.trim()) {
        alert('Please write a summary before submitting.');
        return;
    }

    submitSummaryBtn.disabled = true;
    submitSummaryBtn.innerHTML = '<span class="animate-pulse">Evaluating...</span>';

    try {
        const response = await fetch(API_ENDPOINT_EVALUATOR, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                article: currentArticle,
                summary: summaryInput.value
            })
        });

        const evaluation = await response.json();
        displayResults(evaluation);
        updateHistory(evaluation);
    } catch (error) {
        console.error('Error evaluating summary:', error);
        alert('Error evaluating summary. Please try again.');
    } finally {
        submitSummaryBtn.disabled = false;
        submitSummaryBtn.textContent = 'Submit Summary';
    }
}

function displayResults(evaluation) {
    writingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Update score bars and feedback for each category
    updateScoreCategory('grammar', evaluation.grammar_spelling);
    updateScoreCategory('understanding', evaluation.understanding);
    updateScoreCategory('coherence', evaluation.coherence);

    // Calculate and update total score
    const newScore = Math.round(
        (evaluation.grammar_spelling.score +
         evaluation.understanding.score +
         evaluation.coherence.score) / 3
    );
    totalScore += newScore;
    totalScoreDisplay.textContent = totalScore;
    totalScoreDisplay.classList.add('scale-up');
    setTimeout(() => totalScoreDisplay.classList.remove('scale-up'), 500);
}

function updateScoreCategory(category, data) {
    const scoreBar = document.getElementById(`${category}-score-bar`);
    const scoreText = document.getElementById(`${category}-score`);
    const feedback = document.getElementById(`${category}-feedback`);

    scoreBar.style.width = `${data.score}%`;
    scoreText.textContent = `${data.score}/100`;
    feedback.textContent = data.feedback;
}

function updateHistory(evaluation) {
    const averageScore = Math.round(
        (evaluation.grammar_spelling.score +
         evaluation.understanding.score +
         evaluation.coherence.score) / 3
    );

    const historyItem = document.createElement('div');
    historyItem.className = `bg-white rounded-lg shadow p-4 ${averageScore >= 70 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'}`;
    historyItem.innerHTML = `
        <div class="flex justify-between items-center">
            <div>
                <h3 class="font-bold">Article Summary</h3>
                <p class="text-gray-600 text-sm">${summaryInput.value.substring(0, 100)}...</p>
            </div>
            <div class="text-xl font-bold ${averageScore >= 70 ? 'text-green-600' : 'text-red-600'}">
                ${averageScore}
            </div>
        </div>
    `;
    historyDiv.prepend(historyItem);
}

function resetExercise() {
    // Reset UI elements for a new round
    resultsSection.classList.add('hidden');
    writingSection.classList.add('hidden');
    articleSection.classList.remove('hidden');
    summaryInput.value = '';
    wordCountElement.textContent = 'Words: 0';
    // Hide the timer and button until the new article loads
    timerElement.style.display = 'none';
    timerProgress.style.display = 'none';
    startWritingBtn.style.display = 'none';
    fetchNewArticle();
}
