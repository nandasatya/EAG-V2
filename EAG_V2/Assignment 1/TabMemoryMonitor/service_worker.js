// service_worker.js — Stable Chrome version (Manifest V3)
// Always uses chrome.debugger + CDP Performance.getMetrics (JS heap).
// No usage of chrome.processes (Dev/Canary only).

// We explicitly never try processes API on stable:
const useProcessesAPI = false;

// Human-friendly bytes
function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return 'n/a';
  const units = ['B','KB','MB','GB','TB'];
  let i = 0;
  let b = Math.max(bytes, 0);
  while (b >= 1024 && i < units.length - 1) {
    b /= 1024;
    i++;
  }
  return `${b.toFixed(b >= 10 ? 0 : 1)} ${units[i]}`;
}

// Thresholds for JS heap classification
const HIGH_JS_HEAP_BYTES = 80 * 1024 * 1024; // 80 MB
const LOW_JS_HEAP_BYTES  = 20 * 1024 * 1024; // 20 MB

async function getAllTabs() {
  const tabs = await chrome.tabs.query({});
  return tabs.filter(t => typeof t.id === 'number');
}

async function getCurrentWindowTabs() {
  const currentWindow = await chrome.windows.getCurrent();
  const tabs = await chrome.tabs.query({windowId: currentWindow.id});
  return tabs.filter(t => typeof t.id === 'number');
}

async function getAllWindows() {
  const windows = await chrome.windows.getAll({populate: true});
  return windows.filter(w => w.type === 'normal'); // Only normal windows, not popups
}

async function safeDetach(tabId) {
  try { await chrome.debugger.detach({ tabId }); } catch (_) {}
}

// Read JS heap via DevTools Protocol
async function getTabMetricsViaDebugger(tabId) {
  const target = { tabId };
  try {
    // Attach debugger session to this tab
    await chrome.debugger.attach(target, "1.3");
    // Enable Performance domain, fetch metrics, then disable
    await chrome.debugger.sendCommand(target, "Performance.enable");
    const result = await chrome.debugger.sendCommand(target, "Performance.getMetrics");
    await chrome.debugger.sendCommand(target, "Performance.disable");
    await safeDetach(tabId);

    // Extract JSHeapUsedSize (in bytes)
    let used = null;
    if (result && Array.isArray(result.metrics)) {
      for (const m of result.metrics) {
        if (m.name === "JSHeapUsedSize") used = m.value;
      }
    }

    return {
      memoryBytes: used,
      memoryText: used != null ? `${formatBytes(used)} (JS Heap)` : "n/a",
      high: used != null ? (used >= HIGH_JS_HEAP_BYTES) : false,
      low:  used != null ? (used <= LOW_JS_HEAP_BYTES)  : false,
      source: "debugger"
    };
  } catch (e) {
    // Best effort detach in case of errors
    try { await safeDetach(tabId); } catch (_) {}
    return {
      memoryBytes: null,
      memoryText: "n/a",
      high: false,
      low: false,
      source: "debugger-error"
    };
  }
}

// Build a snapshot for tabs in a specific window
async function buildWindowSnapshot(windowId = null) {
  const tabs = windowId ? 
    await chrome.tabs.query({windowId}) : 
    await getCurrentWindowTabs();
  const results = [];

  for (const t of tabs) {
    const metrics = await getTabMetricsViaDebugger(t.id);
    results.push({
      tabId: t.id,
      title: t.title || "(untitled)",
      url: t.url || "",
      memoryBytes: metrics.memoryBytes,
      memoryText: metrics.memoryText,
      high: metrics.high,
      low: metrics.low,
      source: metrics.source,
      favIconUrl: t.favIconUrl || "",
      windowId: t.windowId
    });
  }

  return { useProcessesAPI, tabs: results, ts: Date.now() };
}

// Build a snapshot for all windows with their tabs
async function buildAllWindowsSnapshot() {
  const windows = await getAllWindows();
  const windowResults = [];

  for (const window of windows) {
    const tabs = window.tabs || [];
    const tabResults = [];

    for (const t of tabs) {
      const metrics = await getTabMetricsViaDebugger(t.id);
      tabResults.push({
        tabId: t.id,
        title: t.title || "(untitled)",
        url: t.url || "",
        memoryBytes: metrics.memoryBytes,
        memoryText: metrics.memoryText,
        high: metrics.high,
        low: metrics.low,
        source: metrics.source,
        favIconUrl: t.favIconUrl || "",
        windowId: t.windowId
      });
    }

    windowResults.push({
      windowId: window.id,
      focused: window.focused,
      tabs: tabResults,
      totalMemory: tabResults.reduce((acc, t) => acc + (t.memoryBytes || 0), 0)
    });
  }

  return { useProcessesAPI, windows: windowResults, ts: Date.now() };
}

// Message handler for popup
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      if (msg?.type === "GET_CURRENT_WINDOW_SNAPSHOT") {
        const snap = await buildWindowSnapshot();
        sendResponse({ ok: true, snapshot: snap });
      } else if (msg?.type === "GET_ALL_WINDOWS_SNAPSHOT") {
        const snap = await buildAllWindowsSnapshot();
        sendResponse({ ok: true, snapshot: snap });
      } else if (msg?.type === "GET_WINDOW_SNAPSHOT" && typeof msg.windowId === "number") {
        const snap = await buildWindowSnapshot(msg.windowId);
        sendResponse({ ok: true, snapshot: snap });
      } else if (msg?.type === "CLOSE_TAB" && typeof msg.tabId === "number") {
        await chrome.tabs.remove(msg.tabId);
        sendResponse({ ok: true });
      } else if (msg?.type === "FOCUS_WINDOW" && typeof msg.windowId === "number") {
        await chrome.windows.update(msg.windowId, {focused: true});
        sendResponse({ ok: true });
      } else {
        sendResponse({ ok: false, error: "unknown message" });
      }
    } catch (err) {
      sendResponse({ ok: false, error: String(err) });
    }
  })();
  return true; // keep channel open for async response
});
