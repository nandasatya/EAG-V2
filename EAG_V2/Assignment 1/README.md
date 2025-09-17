# Tab Memory Monitor

A Chrome extension that monitors JavaScript heap memory usage across browser tabs and windows, helping you identify memory-intensive tabs and manage browser performance.

## Features

### 🔧 **Current Window Monitoring**
- View memory usage for all tabs in the current Chrome window
- See percentage distribution of memory across tabs
- Color-coded memory indicators (High/Medium/Low)
- Close tabs directly from the extension popup

### 🪟 **Multi-Window Support**
- Switch between "Current Window" and "All Windows" views
- See memory usage across all open Chrome windows
- Focus on any window with a single click
- Window-level memory summaries

### 📊 **Memory Visualization**
- Visual progress bars showing memory usage
- Real-time memory data via Chrome Debugger API
- JavaScript heap size monitoring
- Memory classification (High: 80MB+, Low: 20MB-)

## Installation

### From Source
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd TabMemoryMonitor
   ```

2. Open Chrome and navigate to `chrome://extensions/`

3. Enable "Developer mode" in the top right

4. Click "Load unpacked" and select the `TabMemoryMonitor` folder

5. The extension icon (🔧) will appear in your Chrome toolbar

## Usage

### Current Window View (Default)
- Click the extension icon to see tabs in your current window
- Each tab shows:
  - Favicon and title
  - Memory usage with percentage
  - Visual memory bar
  - Close button

### All Windows View
- Click the 📋 button to switch to all windows view
- See all open Chrome windows with their tabs
- Click "Focus" on any window to switch to it
- Each window shows summary statistics

### Memory Indicators
- **🟢 Green (Low)**: ≤ 20MB - Efficient memory usage
- **🟡 Yellow (Medium)**: 20-80MB - Moderate memory usage  
- **🔴 Red (High)**: ≥ 80MB - High memory usage

## Technical Details

### Memory Measurement
- Uses Chrome Debugger API to access DevTools Protocol
- Measures JavaScript heap usage via `Performance.getMetrics`
- Reports `JSHeapUsedSize` metric for each tab
- Real-time data collection with automatic refresh

### Permissions
- `tabs`: Access tab information
- `windows`: Manage and focus windows
- `debugger`: Access memory metrics via DevTools Protocol
- `storage`: Store extension preferences

### Architecture
- **Manifest V3** compatible
- Service worker for background processing
- Popup interface for user interaction
- Real-time communication between popup and service worker

## Development

### Project Structure
```
TabMemoryMonitor/
├── manifest.json          # Extension configuration
├── service_worker.js      # Background script
├── popup.html            # Extension popup UI
├── popup.css             # Styling
├── popup.js              # Popup functionality
└── icons/                # Extension icons
    ├── icon16.png
    ├── icon32.png
    ├── icon48.png
    └── icon128.png
```

### Key Functions
- `getTabMetricsViaDebugger()`: Collects memory data from tabs
- `buildWindowSnapshot()`: Creates memory snapshots for windows
- `renderCurrentWindow()`: Displays current window data
- `renderAllWindows()`: Displays all windows data

## Browser Compatibility

- **Chrome**: Version 116+ (Manifest V3 support required)
- **Edge**: Version 116+ (Chromium-based)
- **Other Chromium browsers**: May work with Manifest V3 support

## Limitations

- Requires "debugger" permission (user approval needed)
- Only measures JavaScript heap memory, not total tab memory
- Memory data may not be available for some system tabs
- Performance impact during data collection

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Troubleshooting

### Extension Not Loading
- Ensure Chrome version 116+ is installed
- Check that Developer mode is enabled
- Verify all files are present in the extension folder

### No Memory Data
- Grant debugger permission when prompted
- Some tabs (chrome:// pages) may not report memory data
- Try refreshing the extension popup

### Performance Issues
- The extension may cause brief slowdowns during data collection
- Consider closing unnecessary tabs before monitoring
- Use the refresh button sparingly

## Changelog

### Version 1.0.0
- Initial release
- Current window memory monitoring
- Multi-window support
- Memory visualization and classification
- Tab closing functionality
- Window focusing capabilities

---

**Note**: This extension requires the debugger permission to function. Chrome will prompt you to approve this permission when you first use the extension.
