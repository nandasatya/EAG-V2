// Stock Agent Plugin - Background Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getStockPrice') {
        handleStockPriceRequest(request, sendResponse);
        return true; // Keep the message channel open for async response
    }
});

async function handleStockPriceRequest(request, sendResponse) {
    try {
        const { ticker, apiKey } = request;
        
        // System prompt for the AI agent
        const systemPrompt = `You are a stock agent solving problems in iterations. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: function_name|input
2. FINAL_ANSWER: [result]

where function_name is one of the following:
1. get_price: takes the stock ticker (e.g., "MSFT"), gets the current price
2. print_price: takes the stock ticker (e.g., "MSFT"), gets the price internally, and displays it

IMPORTANT: Both functions take the SAME ticker symbol as input. Do NOT pass price values to print_price.
DO NOT include multiple responses. Give ONE response at a time.`;

        const query = `Get the stock price of ${ticker}`;
        
        // First iteration with AI
        const aiResponse1 = await callGeminiAPI(systemPrompt, query, apiKey);
        console.log('AI Response 1:', aiResponse1);
        
        let stockInfo = null;
        let functionCalls = [];
        
        if (aiResponse1.startsWith('FUNCTION_CALL:')) {
            const call1 = parseFunctionCall(aiResponse1);
            if (call1) {
                const result1 = await executeFunction(call1.function, call1.params);
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
                }
                
                // Second iteration
                const iteration2 = `In the first iteration you called ${call1.function} with ${call1.params} parameters, and the function returned ${result1}. What should I do next?`;
                const prompt2 = `${systemPrompt}\n\nQuery: ${query}\n\n${iteration2}`;
                
                const aiResponse2 = await callGeminiAPI(prompt2, '', apiKey);
                console.log('AI Response 2:', aiResponse2);
                
                if (aiResponse2.startsWith('FUNCTION_CALL:')) {
                    const call2 = parseFunctionCall(aiResponse2);
                    if (call2) {
                        const result2 = await executeFunction(call2.function, call2.params);
                        functionCalls.push({
                            function: call2.function,
                            params: call2.params,
                            result: result2
                        });
                    }
                }
            }
        }
        
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

async function callGeminiAPI(prompt, query, apiKey) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
    
    const requestBody = {
        contents: [{
            parts: [{
                text: `${prompt}\n\nQuery: ${query}`
            }]
        }]
    };
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
        throw new Error(`Gemini API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.candidates[0].content.parts[0].text;
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
    switch (functionName) {
        case 'get_price':
            return await getStockPrice(params);
        case 'print_price':
            const price = await getStockPrice(params);
            return `The current price of ${params} is $${price.toFixed(2)}`;
        default:
            return `Function ${functionName} not found`;
    }
}

async function getStockPrice(ticker) {
    try {
        // Use Yahoo Finance API (free alternative to yfinance)
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch stock data: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.chart || !data.chart.result || data.chart.result.length === 0) {
            throw new Error(`No data found for ticker: ${ticker}`);
        }
        
        const result = data.chart.result[0];
        const meta = result.meta;
        
        if (!meta.regularMarketPrice) {
            throw new Error(`No price data available for ${ticker}`);
        }
        
        return meta.regularMarketPrice;
        
    } catch (error) {
        console.error('Error fetching stock price:', error);
        throw new Error(`Failed to get price for ${ticker}: ${error.message}`);
    }
}
