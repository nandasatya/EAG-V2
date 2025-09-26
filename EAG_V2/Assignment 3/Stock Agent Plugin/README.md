# Stock Agent Chrome Plugin

An AI-powered Chrome extension that uses Google Gemini AI to get and display stock prices. This plugin replicates the functionality of the Python stock agent in a browser extension format.

## Features

- 🤖 **AI-Powered**: Uses Google Gemini AI to intelligently process stock requests
- 📈 **Real-time Stock Data**: Fetches current stock prices from Yahoo Finance
- 🔄 **Iterative Processing**: AI agent works through multiple steps to get accurate results
- 💾 **Secure Storage**: API keys are stored locally in the browser
- 🎨 **Modern UI**: Clean, responsive interface with gradient design

## How It Works

1. **User Input**: Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
2. **AI Processing**: Gemini AI analyzes the request and decides which functions to call
3. **Function Execution**: The plugin executes stock price functions based on AI decisions
4. **Results Display**: Shows stock price and AI reasoning process

## Installation

### Prerequisites

- Google Chrome browser
- Gemini API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Setup Steps

1. **Download the Plugin**
   ```bash
   git clone <repository-url>
   cd "Stock Agent Plugin"
   ```

2. **Load in Chrome**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the "Stock Agent Plugin" folder

3. **Configure API Key**
   - Click the plugin icon in your browser toolbar
   - Enter your Gemini API key in the settings section
   - Click "Save"

4. **Start Using**
   - Enter a stock ticker symbol (e.g., AAPL)
   - Click "Get Stock Price"
   - Watch the AI agent work!

## Usage

### Getting Stock Prices

1. Click the Stock Agent icon in your browser toolbar
2. Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
3. Click "Get Stock Price"
4. The AI agent will:
   - Analyze your request
   - Call appropriate functions
   - Fetch real-time stock data
   - Display the results

### Supported Tickers

The plugin supports all major stock tickers available on Yahoo Finance:
- **US Stocks**: AAPL, MSFT, GOOGL, AMZN, TSLA, etc.
- **International**: ASML, TSMC, etc.
- **ETFs**: SPY, QQQ, etc.

## Technical Details

### Architecture

- **Manifest V3**: Uses the latest Chrome extension format
- **Service Worker**: Background script handles API calls
- **Content Security**: Secure API key storage
- **CORS Handling**: Proper permissions for external APIs

### API Integration

- **Google Gemini AI**: For intelligent request processing
- **Yahoo Finance API**: For real-time stock data
- **Chrome Storage API**: For secure local storage

### Function Mapping

The plugin replicates the Python version's function structure:

```javascript
// Python equivalent functions
get_price(ticker)     // Fetches current stock price
print_price(ticker)   // Gets price and formats display
```

## File Structure

```
Stock Agent Plugin/
├── manifest.json          # Extension configuration
├── popup.html            # Main UI interface
├── popup.css             # Styling and layout
├── popup.js              # Frontend logic
├── background.js         # API calls and AI processing
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md            # This file
```

## Security

- **Local Storage**: API keys are stored locally in your browser
- **No Data Collection**: The plugin doesn't collect or transmit personal data
- **Secure APIs**: Uses official Google and Yahoo APIs
- **CORS Protection**: Proper permission handling

## Troubleshooting

### Common Issues

1. **"Please enter and save your Gemini API key first"**
   - Solution: Get an API key from Google AI Studio and save it in the plugin

2. **"Failed to get stock price"**
   - Check your internet connection
   - Verify the ticker symbol is correct
   - Ensure the API key is valid

3. **Plugin not loading**
   - Make sure Developer mode is enabled in Chrome
   - Check that all files are in the correct directory

### API Key Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it into the plugin settings

## Development

### Local Development

1. Make changes to the plugin files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the Stock Agent Plugin
4. Test your changes

### Debugging

- Open Chrome DevTools (F12)
- Go to the Extensions tab
- Click "Inspect views: popup.html" to debug the popup
- Check the Console for any errors

## License

This project is for educational purposes. Please respect the terms of service for:
- Google Gemini AI API
- Yahoo Finance API
- Chrome Extension policies

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your API key is correct
3. Ensure you have a stable internet connection
4. Check Chrome's extension permissions

---

**Note**: This plugin requires an active internet connection and a valid Gemini API key to function properly.
