// Stock Agent Plugin - Popup Script
document.addEventListener('DOMContentLoaded', function() {
    const tickerInput = document.getElementById('tickerInput');
    const getPriceBtn = document.getElementById('getPriceBtn');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const saveApiKeyBtn = document.getElementById('saveApiKey');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const resultContent = document.getElementById('resultContent');
    const errorContent = document.getElementById('errorContent');

    // Load saved API key
    loadApiKey();

    // Event listeners
    getPriceBtn.addEventListener('click', handleGetPrice);
    saveApiKeyBtn.addEventListener('click', saveApiKey);
    tickerInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleGetPrice();
        }
    });

    async function loadApiKey() {
        try {
            const result = await chrome.storage.local.get(['geminiApiKey']);
            if (result.geminiApiKey) {
                apiKeyInput.value = result.geminiApiKey;
            }
        } catch (err) {
            console.error('Error loading API key:', err);
        }
    }

    async function saveApiKey() {
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            showError('Please enter a valid API key');
            return;
        }

        try {
            await chrome.storage.local.set({ geminiApiKey: apiKey });
            showSuccess('API key saved successfully!');
        } catch (err) {
            showError('Failed to save API key');
        }
    }

    async function handleGetPrice() {
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            showError('Please enter a stock ticker symbol');
            return;
        }

        // Check if API key is saved
        const result = await chrome.storage.local.get(['geminiApiKey']);
        if (!result.geminiApiKey) {
            showError('Please enter and save your Gemini API key first');
            return;
        }

        showLoading();
        hideError();
        hideResults();

        try {
            // Send message to background script
            const response = await chrome.runtime.sendMessage({
                action: 'getStockPrice',
                ticker: ticker,
                apiKey: result.geminiApiKey
            });

            if (response.success) {
                showResults(response.data);
            } else {
                showError(response.error || 'Failed to get stock price');
            }
        } catch (err) {
            showError('Error: ' + err.message);
        } finally {
            hideLoading();
        }
    }

    function showLoading() {
        loading.classList.remove('hidden');
    }

    function hideLoading() {
        loading.classList.add('hidden');
    }

    function showResults(data) {
        resultContent.innerHTML = formatResults(data);
        results.classList.remove('hidden');
    }

    function hideResults() {
        results.classList.add('hidden');
    }

    function showError(message) {
        errorContent.textContent = message;
        error.classList.remove('hidden');
    }

    function hideError() {
        error.classList.add('hidden');
    }

    function showSuccess(message) {
        // Create a temporary success message
        const successDiv = document.createElement('div');
        successDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #27ae60;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            z-index: 1000;
            font-size: 14px;
        `;
        successDiv.textContent = message;
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            document.body.removeChild(successDiv);
        }, 3000);
    }

    function formatResults(data) {
        let html = '';
        
        if (data.stockInfo) {
            html += `
                <div class="stock-info">
                    <div class="stock-ticker">${data.stockInfo.ticker}</div>
                    <div class="stock-price">$${data.stockInfo.price}</div>
                    <div class="stock-details">
                        Current Price: $${data.stockInfo.price}
                    </div>
                </div>
            `;
        }

        if (data.aiResponse) {
            html += `
                <div class="ai-response">
                    <strong>AI Agent Response:</strong><br>
                    ${data.aiResponse}
                </div>
            `;
        }

        if (data.functionCalls) {
            html += `
                <div class="ai-response">
                    <strong>Function Calls:</strong><br>
                    ${data.functionCalls.map(call => 
                        `${call.function}: ${call.params} → ${call.result}`
                    ).join('<br>')}
                </div>
            `;
        }

        return html;
    }
});
