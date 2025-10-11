// Stock Agent Plugin - Popup Script
document.addEventListener('DOMContentLoaded', function() {
    const tickerInput = document.getElementById('tickerInput');
    const getPriceBtn = document.getElementById('getPriceBtn');
    const thresholdInput = document.getElementById('thresholdInput');
    const monitoringInterval = document.getElementById('monitoringInterval');
    const monitoringEnabled = document.getElementById('monitoringEnabled');
    const startMonitoringBtn = document.getElementById('startMonitoringBtn');
    const stopMonitoringBtn = document.getElementById('stopMonitoringBtn');
    const monitoringStatus = document.getElementById('monitoringStatus');
    const monitoringIntervalText = document.getElementById('monitoringIntervalText');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const resultContent = document.getElementById('resultContent');
    const errorContent = document.getElementById('errorContent');

    // Load API key from config
    loadFromConfig();

    // Event listeners
    getPriceBtn.addEventListener('click', handleGetPrice);
    startMonitoringBtn.addEventListener('click', startMonitoring);
    stopMonitoringBtn.addEventListener('click', stopMonitoring);
    tickerInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleGetPrice();
        }
    });
    
    // Preset threshold buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            thresholdInput.value = value;
        });
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
                            
                            console.log('✅ API key loaded from config.txt');
                        }
                    }
                    
                    if (line.includes('PRICE_THRESHOLD=') && !line.startsWith('#')) {
                        const threshold = line.split('=')[1].trim();
                        if (threshold && threshold !== '150.00') {
                            thresholdInput.value = threshold;
                            console.log('✅ Default threshold loaded from config.txt');
                        }
                    }
                    
                    if (line.includes('MONITORING_ENABLED=') && !line.startsWith('#')) {
                        const enabled = line.split('=')[1].trim().toLowerCase();
                        if (enabled === 'true') {
                            monitoringEnabled.checked = true;
                            console.log('✅ Telegram notifications enabled from config.txt');
                        }
                    }
                }
            }
        } catch (error) {
            console.log('No config.txt file found or error reading it');
        }
    }

    async function startMonitoring() {
        const ticker = tickerInput.value.trim().toUpperCase();
        const threshold = parseFloat(thresholdInput.value);
        const interval = parseInt(monitoringInterval.value);
        
        if (!ticker) {
            showError('Please enter a stock ticker symbol');
            return;
        }
        
        if (!threshold || threshold <= 0) {
            showError('Please enter a valid price threshold (must be greater than $0)');
            return;
        }
        
        if (threshold < 0.01) {
            showError('Price threshold must be at least $0.01');
            return;
        }

        try {
            // Start monitoring in background script
            const response = await chrome.runtime.sendMessage({
                action: 'startMonitoring',
                ticker: ticker,
                threshold: threshold,
                interval: interval,
                telegramEnabled: monitoringEnabled.checked
            });

            if (response.success) {
                startMonitoringBtn.style.display = 'none';
                stopMonitoringBtn.style.display = 'inline-block';
                monitoringStatus.classList.remove('hidden');
                const intervalText = getIntervalText(interval);
                monitoringIntervalText.textContent = `(checking every ${intervalText})`;
                showSuccess(`Monitoring started for ${ticker} at $${threshold}! Checking every ${intervalText}. You will receive notifications when the price exceeds the threshold.`);
            } else {
                showError(response.error || 'Failed to start monitoring');
            }
        } catch (err) {
            showError('Error starting monitoring: ' + err.message);
        }
    }

    async function stopMonitoring() {
        try {
            const response = await chrome.runtime.sendMessage({
                action: 'stopMonitoring'
            });

            if (response.success) {
                startMonitoringBtn.style.display = 'inline-block';
                stopMonitoringBtn.style.display = 'none';
                monitoringStatus.classList.add('hidden');
                monitoringIntervalText.textContent = '';
                showSuccess('Monitoring stopped.');
            } else {
                showError(response.error || 'Failed to stop monitoring');
            }
        } catch (err) {
            showError('Error stopping monitoring: ' + err.message);
        }
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

    function getIntervalText(intervalMs) {
        const intervals = {
            900000: '15 minutes',
            3600000: '1 hour',
            7200000: '2 hours',
            21600000: '6 hours'
        };
        return intervals[intervalMs] || 'unknown interval';
    }
});
