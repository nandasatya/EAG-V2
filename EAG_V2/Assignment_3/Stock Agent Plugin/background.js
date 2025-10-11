// Stock Agent Plugin - Background Script
let monitoringInterval = null;
let monitoringConfig = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getStockPrice') {
        handleStockPriceRequest(request, sendResponse);
        return true; // Keep the message channel open for async response
    } else if (request.action === 'startMonitoring') {
        handleStartMonitoring(request, sendResponse);
        return true;
    } else if (request.action === 'stopMonitoring') {
        handleStopMonitoring(request, sendResponse);
        return true;
    }
});

async function handleStockPriceRequest(request, sendResponse) {
    try {
        const { ticker, apiKey } = request;
        
        console.log(`🚀 [STOCK AGENT] ===== STARTING REQUEST =====`);
        console.log(`📊 [STOCK AGENT] Ticker: ${ticker}`);
        console.log(`🔑 [STOCK AGENT] API Key: ${apiKey ? 'Present' : 'Missing'}`);
        
        // System prompt for the AI agent
        const systemPrompt = `You are a stock agent solving problems in iterations. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: function_name|input
2. FINAL_ANSWER: [result]

where function_name is one of the following:
1. get_price: takes the stock ticker (e.g., "MSFT"), gets the current price
2. print_price: takes the stock ticker (e.g., "MSFT"), gets the price internally, and displays it
3. send_telegram_alert: takes a message string and sends it via Telegram

IMPORTANT: Both get_price and print_price take the SAME ticker symbol as input. Do NOT pass price values to print_price.
For send_telegram_alert, pass a complete message string.
DO NOT include multiple responses. Give ONE response at a time.`;

        const query = `Get the stock price of ${ticker}`;
        
        console.log(`🤖 [GEMINI AI] ===== ITERATION 1 =====`);
        console.log(`📝 [GEMINI AI] System Prompt: ${systemPrompt}`);
        console.log(`📝 [GEMINI AI] Query: ${query}`);
        
        // First iteration with AI
        let aiResponse1;
        try {
            aiResponse1 = await callGeminiAPI(systemPrompt, query, apiKey);
            console.log(`🤖 [GEMINI AI] Response 1: ${aiResponse1}`);
        } catch (error) {
            console.error(`❌ [GEMINI AI] API Error: ${error.message}`);
            // Fallback to simple stock price display without AI
            const currentPrice = await getStockPrice(ticker);
            const fallbackResult = {
                stockInfo: {
                    ticker: ticker,
                    price: currentPrice
                },
                aiResponse: `AI temporarily unavailable. Current price: $${currentPrice.toFixed(2)}`,
                functionCalls: []
            };
            
            sendResponse({
                success: true,
                data: fallbackResult
            });
            return;
        }
        
        let stockInfo = null;
        let functionCalls = [];
        
        if (aiResponse1.startsWith('FUNCTION_CALL:')) {
            console.log(`⚙️ [FUNCTION CALL] Parsing function call: ${aiResponse1}`);
            const call1 = parseFunctionCall(aiResponse1);
            if (call1) {
                console.log(`⚙️ [FUNCTION CALL] Function: ${call1.function}, Params: ${call1.params}`);
                console.log(`⚙️ [FUNCTION CALL] Executing function...`);
                const result1 = await executeFunction(call1.function, call1.params);
                console.log(`⚙️ [FUNCTION CALL] Result: ${result1}`);
                
                functionCalls.push({
                    function: call1.function,
                    params: call1.params,
                    result: result1
                });
                
                if (call1.function === 'get_price') {
                    stockInfo = {
                        ticker: call1.params,
                        price: result1
                    };
                    console.log(`📊 [STOCK INFO] Captured stock info:`, stockInfo);
                }
                
                // Second iteration
                console.log(`🤖 [GEMINI AI] ===== ITERATION 2 =====`);
                const iteration2 = `In the first iteration you called ${call1.function} with ${call1.params} parameters, and the function returned ${result1}. What should I do next?`;
                const prompt2 = `${systemPrompt}\n\nQuery: ${query}\n\n${iteration2}`;
                console.log(`📝 [GEMINI AI] Iteration 2 prompt: ${prompt2}`);
                
                const aiResponse2 = await callGeminiAPI(prompt2, '', apiKey);
                console.log(`🤖 [GEMINI AI] Response 2: ${aiResponse2}`);
                
                if (aiResponse2.startsWith('FUNCTION_CALL:')) {
                    console.log(`⚙️ [FUNCTION CALL] Parsing second function call: ${aiResponse2}`);
                    const call2 = parseFunctionCall(aiResponse2);
                    if (call2) {
                        console.log(`⚙️ [FUNCTION CALL] Function 2: ${call2.function}, Params: ${call2.params}`);
                        console.log(`⚙️ [FUNCTION CALL] Executing function 2...`);
                        const result2 = await executeFunction(call2.function, call2.params);
                        console.log(`⚙️ [FUNCTION CALL] Result 2: ${result2}`);
                        
                        functionCalls.push({
                            function: call2.function,
                            params: call2.params,
                            result: result2
                        });
                    }
                } else {
                    console.log(`🤖 [GEMINI AI] Second response is not a function call: ${aiResponse2}`);
                }
            }
        } else {
            console.log(`🤖 [GEMINI AI] First response is not a function call: ${aiResponse1}`);
        }
        
        console.log(`✅ [STOCK AGENT] ===== FINAL RESULT =====`);
        console.log(`📊 [STOCK AGENT] Stock Info:`, stockInfo);
        console.log(`⚙️ [STOCK AGENT] Function Calls:`, functionCalls);
        console.log(`🤖 [STOCK AGENT] AI Response: ${aiResponse1}`);
        
        sendResponse({
            success: true,
            data: {
                stockInfo,
                aiResponse: aiResponse1,
                functionCalls
            }
        });
        
    } catch (error) {
        console.error('Error in background script:', error);
        sendResponse({
            success: false,
            error: error.message
        });
    }
}

async function callGeminiAPI(prompt, query, apiKey, retryCount = 0) {
    const maxRetries = 3;
    const retryDelay = 2000; // 2 seconds
    
    console.log(`🌐 [GEMINI API] ===== MAKING API CALL (Attempt ${retryCount + 1}/${maxRetries + 1}) =====`);
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
    console.log(`🌐 [GEMINI API] URL: ${url}`);
    console.log(`🌐 [GEMINI API] API Key: ${apiKey ? 'Present' : 'Missing'}`);
    
    const requestBody = {
        contents: [{
            parts: [{
                text: `${prompt}\n\nQuery: ${query}`
            }]
        }]
    };
    
    console.log(`🌐 [GEMINI API] Request Body:`, JSON.stringify(requestBody, null, 2));
    console.log(`🌐 [GEMINI API] Full Prompt: ${prompt}\n\nQuery: ${query}`);
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log(`🌐 [GEMINI API] Response Status: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`❌ [GEMINI API] Error Response:`, errorText);
            
            // Handle specific error codes
            if (response.status === 503) {
                if (retryCount < maxRetries) {
                    console.log(`🔄 [GEMINI API] Service unavailable (503), retrying in ${retryDelay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, retryDelay));
                    return await callGeminiAPI(prompt, query, apiKey, retryCount + 1);
                } else {
                    throw new Error(`Gemini API is temporarily unavailable (503). Tried ${maxRetries + 1} times. Please try again later.`);
                }
            } else if (response.status === 429) {
                if (retryCount < maxRetries) {
                    console.log(`🔄 [GEMINI API] Rate limit exceeded (429), retrying in ${retryDelay * 2}ms...`);
                    await new Promise(resolve => setTimeout(resolve, retryDelay * 2));
                    return await callGeminiAPI(prompt, query, apiKey, retryCount + 1);
                } else {
                    throw new Error(`Gemini API rate limit exceeded (429). Tried ${maxRetries + 1} times. Please wait before making more requests.`);
                }
            } else if (response.status === 401) {
                throw new Error(`Gemini API authentication failed (401). Please check your API key.`);
            } else if (response.status === 400) {
                throw new Error(`Gemini API bad request (400). Please check your request format.`);
            } else {
                throw new Error(`Gemini API error: ${response.status} ${response.statusText}. Details: ${errorText}`);
            }
        }
        
        const data = await response.json();
        console.log(`🌐 [GEMINI API] Raw Response:`, JSON.stringify(data, null, 2));
        
        const aiText = data.candidates[0].content.parts[0].text;
        console.log(`🌐 [GEMINI API] Extracted Text: ${aiText}`);
        console.log(`🌐 [GEMINI API] ===== API CALL COMPLETE =====`);
        
        return aiText;
        
    } catch (error) {
        if (retryCount < maxRetries && (error.message.includes('503') || error.message.includes('network'))) {
            console.log(`🔄 [GEMINI API] Network error, retrying in ${retryDelay}ms...`);
            await new Promise(resolve => setTimeout(resolve, retryDelay));
            return await callGeminiAPI(prompt, query, apiKey, retryCount + 1);
        }
        throw error;
    }
}

function parseFunctionCall(response) {
    if (!response.startsWith('FUNCTION_CALL:')) {
        return null;
    }
    
    const parts = response.split('|');
    if (parts.length !== 2) {
        return null;
    }
    
    return {
        function: parts[0].replace('FUNCTION_CALL: ', '').trim(),
        params: parts[1].trim()
    };
}

async function executeFunction(functionName, params) {
    console.log(`⚙️ [FUNCTION EXEC] Executing function: ${functionName} with params: ${params}`);
    
    switch (functionName) {
        case 'get_price':
            console.log(`⚙️ [FUNCTION EXEC] Calling getStockPrice for: ${params}`);
            const price = await getStockPrice(params);
            console.log(`⚙️ [FUNCTION EXEC] getStockPrice result: ${price}`);
            return price;
        case 'print_price':
            console.log(`⚙️ [FUNCTION EXEC] Calling getStockPrice for print_price: ${params}`);
            const printPrice = await getStockPrice(params);
            const result = `The current price of ${params} is $${printPrice.toFixed(2)}`;
            console.log(`⚙️ [FUNCTION EXEC] print_price result: ${result}`);
            return result;
        case 'send_telegram_alert':
            console.log(`📱 [FUNCTION EXEC] Sending Telegram alert: ${params}`);
            const telegramResult = await sendTelegramAlert(params);
            console.log(`📱 [FUNCTION EXEC] Telegram result: ${telegramResult}`);
            return telegramResult;
        default:
            console.log(`❌ [FUNCTION EXEC] Unknown function: ${functionName}`);
            return `Function ${functionName} not found`;
    }
}

async function getStockPrice(ticker) {
    try {
        console.log(`💰 [YAHOO FINANCE] Fetching price for ticker: ${ticker}`);
        // Use Yahoo Finance API (free alternative to yfinance)
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}`;
        console.log(`💰 [YAHOO FINANCE] URL: ${url}`);
        
        const response = await fetch(url);
        console.log(`💰 [YAHOO FINANCE] Response Status: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch stock data: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`💰 [YAHOO FINANCE] Raw Response:`, JSON.stringify(data, null, 2));
        
        if (!data.chart || !data.chart.result || data.chart.result.length === 0) {
            throw new Error(`No data found for ticker: ${ticker}`);
        }
        
        const result = data.chart.result[0];
        const meta = result.meta;
        console.log(`💰 [YAHOO FINANCE] Meta data:`, meta);
        
        if (!meta.regularMarketPrice) {
            throw new Error(`No price data available for ${ticker}`);
        }
        
        const price = meta.regularMarketPrice;
        console.log(`💰 [YAHOO FINANCE] Final price: $${price}`);
        
        return price;
        
    } catch (error) {
        console.error('❌ [YAHOO FINANCE] Error fetching stock price:', error);
        throw new Error(`Failed to get price for ${ticker}: ${error.message}`);
    }
}

async function handleStartMonitoring(request, sendResponse) {
    try {
        const { ticker, threshold, interval, telegramEnabled } = request;
        
        console.log(`📊 [MONITORING] ===== STARTING MONITORING =====`);
        console.log(`📊 [MONITORING] Ticker: ${ticker}`);
        console.log(`📊 [MONITORING] Threshold: $${threshold}`);
        console.log(`📊 [MONITORING] Interval: ${interval}ms (${getIntervalText(interval)})`);
        console.log(`📊 [MONITORING] Telegram Enabled: ${telegramEnabled}`);
        
        // Stop any existing monitoring
        if (monitoringInterval) {
            console.log(`📊 [MONITORING] Stopping existing monitoring...`);
            clearInterval(monitoringInterval);
        }
        
        // Load Telegram config from storage
        console.log(`📊 [MONITORING] Loading Telegram config...`);
        const telegramConfig = await loadTelegramConfig();
        console.log(`📊 [MONITORING] Telegram config:`, telegramConfig);
        
        monitoringConfig = {
            ticker,
            threshold,
            interval,
            telegramEnabled,
            telegramConfig
        };
        
        console.log(`📊 [MONITORING] Monitoring config set:`, monitoringConfig);
        
        // Start monitoring with the specified interval
        console.log(`📊 [MONITORING] Starting interval (${getIntervalText(interval)})...`);
        monitoringInterval = setInterval(async () => {
            await checkPriceAndNotify();
        }, interval);
        
        // Check immediately
        console.log(`📊 [MONITORING] Running initial check...`);
        await checkPriceAndNotify();
        
        console.log(`📊 [MONITORING] ===== MONITORING STARTED =====`);
        sendResponse({ success: true });
    } catch (error) {
        console.error('❌ [MONITORING] Error starting monitoring:', error);
        sendResponse({ success: false, error: error.message });
    }
}

async function handleStopMonitoring(request, sendResponse) {
    try {
        if (monitoringInterval) {
            clearInterval(monitoringInterval);
            monitoringInterval = null;
            monitoringConfig = null;
        }
        
        sendResponse({ success: true });
    } catch (error) {
        console.error('Error stopping monitoring:', error);
        sendResponse({ success: false, error: error.message });
    }
}

async function checkPriceAndNotify() {
    if (!monitoringConfig) {
        console.log(`📊 [MONITORING] No monitoring config, skipping check`);
        return;
    }
    
    try {
        const { ticker, threshold, telegramEnabled, telegramConfig } = monitoringConfig;
        
        console.log(`📊 [MONITORING] ===== PRICE CHECK =====`);
        console.log(`📊 [MONITORING] Checking ${ticker} (threshold: $${threshold})`);
        
        // Get current price
        const currentPrice = await getStockPrice(ticker);
        
        console.log(`📊 [MONITORING] Current price: $${currentPrice} (threshold: $${threshold})`);
        
        // Check if price exceeds threshold
        if (currentPrice > threshold) {
            console.log(`🚨 [MONITORING] ===== ALERT TRIGGERED =====`);
            console.log(`🚨 [MONITORING] Price alert: $${currentPrice} > $${threshold}`);
            
            // Use Gemini AI to handle the alert
            await handlePriceAlertWithAI(ticker, currentPrice, threshold, telegramEnabled);
            
            // Stop monitoring after alert
            console.log(`📊 [MONITORING] Stopping monitoring after alert...`);
            if (monitoringInterval) {
                clearInterval(monitoringInterval);
                monitoringInterval = null;
                monitoringConfig = null;
            }
        } else {
            console.log(`📊 [MONITORING] Price below threshold, continuing monitoring...`);
        }
    } catch (error) {
        console.error('❌ [MONITORING] Error in price monitoring:', error);
    }
}

async function loadTelegramConfig() {
    try {
        // Try to load from config.txt first
        const response = await fetch('config.txt');
        if (response.ok) {
            const text = await response.text();
            const lines = text.split('\n');
            
            let botToken = null;
            let chatId = null;
            
            for (const line of lines) {
                if (line.includes('TELEGRAM_BOT_TOKEN=') && !line.startsWith('#')) {
                    botToken = line.split('=')[1].trim();
                }
                if (line.includes('TELEGRAM_CHAT_ID=') && !line.startsWith('#')) {
                    chatId = line.split('=')[1].trim();
                }
            }
            
            if (botToken && botToken !== 'your_telegram_bot_token_here' && 
                chatId && chatId !== 'your_telegram_chat_id_here') {
                return { botToken, chatId };
            }
        }
    } catch (error) {
        console.log('Could not load Telegram config from config.txt');
    }
    
    return { botToken: null, chatId: null };
}

async function sendTelegramMessage(botToken, chatId, message) {
    try {
        const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
        const data = {
            chat_id: chatId,
            text: message,
            parse_mode: 'HTML'
        };
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            console.log('Telegram message sent successfully');
            return true;
        } else {
            console.error('Failed to send Telegram message:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error sending Telegram message:', error);
        return false;
    }
}

async function sendTelegramAlert(message) {
    try {
        console.log(`📱 [TELEGRAM ALERT] Sending message: ${message}`);
        
        // Load Telegram config
        const telegramConfig = await loadTelegramConfig();
        
        if (!telegramConfig.botToken || !telegramConfig.chatId) {
            console.log(`📱 [TELEGRAM ALERT] Telegram not configured`);
            return "Telegram not configured - no bot token or chat ID found";
        }
        
        console.log(`📱 [TELEGRAM ALERT] Using bot token: ${telegramConfig.botToken ? 'Present' : 'Missing'}`);
        console.log(`📱 [TELEGRAM ALERT] Using chat ID: ${telegramConfig.chatId}`);
        
        const result = await sendTelegramMessage(telegramConfig.botToken, telegramConfig.chatId, message);
        
        if (result) {
            console.log(`📱 [TELEGRAM ALERT] Message sent successfully`);
            return "Telegram alert sent successfully";
        } else {
            console.log(`📱 [TELEGRAM ALERT] Failed to send message`);
            return "Failed to send Telegram alert";
        }
        
    } catch (error) {
        console.error('❌ [TELEGRAM ALERT] Error sending alert:', error);
        return `Error sending Telegram alert: ${error.message}`;
    }
}

async function handlePriceAlertWithAI(ticker, currentPrice, threshold, telegramEnabled) {
    try {
        console.log(`🤖 [AI ALERT] ===== USING GEMINI FOR ALERT =====`);
        console.log(`🤖 [AI ALERT] Ticker: ${ticker}, Price: $${currentPrice}, Threshold: $${threshold}`);
        
        // Get API key from storage
        const result = await chrome.storage.local.get(['geminiApiKey']);
        if (!result.geminiApiKey) {
            console.log(`❌ [AI ALERT] No Gemini API key found`);
            return;
        }
        
        // Create AI prompt for alert handling
        const systemPrompt = `You are a stock agent solving problems in iterations. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: function_name|input
2. FINAL_ANSWER: [result]

where function_name is one of the following:
1. get_price: takes the stock ticker (e.g., "MSFT"), gets the current price
2. print_price: takes the stock ticker (e.g., "MSFT"), gets the price internally, and displays it
3. send_telegram_alert: takes a message string and sends it via Telegram

IMPORTANT: Both get_price and print_price take the SAME ticker symbol as input. Do NOT pass price values to print_price.
For send_telegram_alert, pass a complete message string.
DO NOT include multiple responses. Give ONE response at a time.`;

        const query = `A stock price alert has been triggered! ${ticker} is now at $${currentPrice.toFixed(2)}, which exceeds the threshold of $${threshold}. Please send a Telegram alert about this price movement.`;
        
        console.log(`🤖 [AI ALERT] System Prompt: ${systemPrompt}`);
        console.log(`🤖 [AI ALERT] Query: ${query}`);
        
        // First iteration with AI
        const aiResponse1 = await callGeminiAPI(systemPrompt, query, result.geminiApiKey);
        console.log(`🤖 [AI ALERT] AI Response 1: ${aiResponse1}`);
        
        if (aiResponse1.startsWith('FUNCTION_CALL:')) {
            console.log(`⚙️ [AI ALERT] Parsing function call: ${aiResponse1}`);
            const call1 = parseFunctionCall(aiResponse1);
            if (call1) {
                console.log(`⚙️ [AI ALERT] Function: ${call1.function}, Params: ${call1.params}`);
                console.log(`⚙️ [AI ALERT] Executing function...`);
                const result1 = await executeFunction(call1.function, call1.params);
                console.log(`⚙️ [AI ALERT] Result: ${result1}`);
                
                // Second iteration if needed
                if (call1.function === 'send_telegram_alert') {
                    console.log(`🤖 [AI ALERT] Telegram alert sent via AI`);
                } else {
                    // AI might want to do additional processing
                    const iteration2 = `In the first iteration you called ${call1.function} with "${call1.params}" parameters, and the function returned "${result1}". What should I do next?`;
                    const prompt2 = `${systemPrompt}\n\nQuery: ${query}\n\n${iteration2}`;
                    
                    console.log(`🤖 [AI ALERT] Iteration 2 prompt: ${prompt2}`);
                    const aiResponse2 = await callGeminiAPI(prompt2, '', result.geminiApiKey);
                    console.log(`🤖 [AI ALERT] AI Response 2: ${aiResponse2}`);
                    
                    if (aiResponse2.startsWith('FUNCTION_CALL:')) {
                        const call2 = parseFunctionCall(aiResponse2);
                        if (call2) {
                            console.log(`⚙️ [AI ALERT] Function 2: ${call2.function}, Params: ${call2.params}`);
                            const result2 = await executeFunction(call2.function, call2.params);
                            console.log(`⚙️ [AI ALERT] Result 2: ${result2}`);
                        }
                    }
                }
            }
        } else {
            console.log(`🤖 [AI ALERT] AI response is not a function call: ${aiResponse1}`);
        }
        
        console.log(`🤖 [AI ALERT] ===== AI ALERT HANDLING COMPLETE =====`);
        
    } catch (error) {
        console.error('❌ [AI ALERT] Error in AI alert handling:', error);
    }
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
