/* 
   Script for FundGuide Mutual Fund FAQ Assistant 
*/

const API_URL = 'http://localhost:8000';

// DOM Elements
const queryInput = document.getElementById('queryInput');
const clearBtn = document.getElementById('clearBtn');
const askBtn = document.getElementById('askBtn');

// State Cards
const stateEmpty = document.getElementById('stateEmpty');
const stateLoading = document.getElementById('stateLoading');
const stateSuccess = document.getElementById('stateSuccess');
const stateRefused = document.getElementById('stateRefused');
const stateError = document.getElementById('stateError');

// Success Data Elements
const successAnswer = document.getElementById('successAnswer');
const successSource = document.getElementById('successSource');
const successDate = document.getElementById('successDate');

// Refusal Data Elements
const refusedAnswer = document.getElementById('refusedAnswer');
const refusedLink = document.getElementById('refusedLink');

// Error Data Elements
const errorAnswer = document.getElementById('errorAnswer');

function hideAllStates() {
    stateEmpty.classList.remove('active');
    stateLoading.classList.remove('active');
    stateSuccess.classList.remove('active');
    stateRefused.classList.remove('active');
    stateError.classList.remove('active');
}

function showState(stateElement) {
    hideAllStates();
    stateElement.classList.add('active');
}

// Populate the input box with the pill text and submit automatically
function setQuery(text) {
    queryInput.value = text;
    submitQuery();
}

clearBtn.addEventListener('click', () => {
    queryInput.value = '';
    queryInput.focus();
    showState(stateEmpty);
});

askBtn.addEventListener('click', () => {
    submitQuery();
});

queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        submitQuery();
    }
});

async function submitQuery() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Show loading state
    showState(stateLoading);
    askBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const json = await response.json();
        const data = json.data;

        if (json.status === 'success') {
            // Extract a big percentage number if present to match UI mockup
            // The RAG just gives text, but we can do a quick check to see if it starts with a percentage 
            // For now, we'll just display the full text as the answer.
            let htmlAnswer = data.answer;
            
            // UI enhancement: If there's a percentage, make it big like the mockup "0.80%"
            // This is just a nice-to-have visual enhancement
            const percentMatch = data.answer.match(/(\d+\.\d+%)/);
            if(percentMatch) {
                const percent = percentMatch[0];
                const rest = data.answer.replace(percent, '').trim();
                htmlAnswer = `<h1 style="color: var(--success-blue); font-size: 2.5rem; margin-bottom: 0.5rem; line-height: 1;">${percent}</h1><p>${rest}</p>`;
            } else {
                htmlAnswer = `<p>${data.answer}</p>`;
            }
            
            successAnswer.innerHTML = htmlAnswer;
            
            if(data.source_url) {
                successSource.href = data.source_url;
                successSource.textContent = data.source_url;
            } else {
                successSource.textContent = 'N/A';
                successSource.removeAttribute('href');
            }
            
            successDate.textContent = data.last_updated || '--';
            
            showState(stateSuccess);
        } else if (json.status === 'refused') {
            refusedAnswer.textContent = data.answer;
            if(data.source_url) {
                refusedLink.href = data.source_url;
                refusedLink.style.display = 'inline-block';
            } else {
                refusedLink.style.display = 'none';
            }
            showState(stateRefused);
        } else {
            throw new Error("Unknown status received.");
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        errorAnswer.textContent = 'The system encountered an error while processing your request. Ensure the backend server is running.';
        showState(stateError);
    } finally {
        askBtn.disabled = false;
    }
}
