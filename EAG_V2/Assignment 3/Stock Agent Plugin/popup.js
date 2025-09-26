// Stock Agent Plugin - Popup Script
document.addEventListener('DOMContentLoaded', function() {
    const tickerInput = document.getElementById('tickerInput');
    const getPriceBtn = document.getElementById('getPriceBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const resultContent = document.getElementById('resultContent');
    const errorContent = document.getElementById('errorContent');

    // Load API key from config
    loadFromConfig();

    // Event listeners
    getPriceBtn.addEventListener('click', handleGetPrice);
    tickerInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleGetPrice();
        }
    });


    async function handleGetPrice() {
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            showError('Please enter a stock ticker symbol');
            return;
        }

        showLoading();
        hideError();
        hideResults();

        try {
            // Get API key from storage (loaded from config)
            const result = await chrome.storage.local.get(['geminiApiKey']);
            if (!result.geminiApiKey) {
                showError('API key not found. Please check your config.txt file.');
                return;
            }

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

    async function checkSetupStatus() {
        try {
            const result = await chrome.storage.local.get(['setupComplete', 'geminiApiKey']);
            if (!result.setupComplete || !result.geminiApiKey) {
                showSetupPrompt();
            }
        } catch (err) {
            console.error('Error checking setup status:', err);
        }
    }

    function showSetupPrompt() {
        const setupDiv = document.createElement('div');
        setupDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        setupDiv.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 400px; text-align: center;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">🔧 Setup Required</h3>
                <p style="margin-bottom: 20px;">Please configure your Gemini API key to use the Stock Agent plugin.</p>
                <button onclick="this.parentElement.parentElement.remove()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    Open Setup
                </button>
            </div>
        `;
        
        document.body.appendChild(setupDiv);
    }

    async function loadFromConfig() {
        try {
            // Try to load from config.txt file
            const response = await fetch('config.txt');
            if (response.ok) {
                const text = await response.text();
                const lines = text.split('\n');
                
                for (const line of lines) {
                    if (line.includes('GEMINI_API_KEY=') && !line.startsWith('#')) {
                        const apiKey = line.split('=')[1].trim();
                        if (apiKey && apiKey !== 'your_gemini_api_key_here') {
                            // Auto-save the API key from config
                            await chrome.storage.local.set({ 
                                geminiApiKey: apiKey,
                                setupComplete: true,
                                setupDate: new Date().toISOString()
                            });
                            
                            // API key loaded successfully
                            
                            console.log('✅ API key loaded from config.txt');
                            return;
                        }
                    }
                }
            }
        } catch (error) {
            console.log('No config.txt file found or error reading it');
        }
    }
});
