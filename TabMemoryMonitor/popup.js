const listEl = document.getElementById('list');
const windowsListEl = document.getElementById('windowsList');
const sourceLabel = document.getElementById('sourceLabel');
const summaryEl = document.getElementById('summary');
const refreshBtn = document.getElementById('refreshBtn');
const viewModeBtn = document.getElementById('viewModeBtn');
const currentWindowView = document.getElementById('currentWindowView');
const allWindowsView = document.getElementById('allWindowsView');

let currentViewMode = 'current'; // 'current' or 'all'

function classify(bytes) {
  if (bytes === null) return {label: 'n/a', className: ''};
  if (bytes >= 80 * 1024 * 1024) return {label: 'High', className: 'warn'};
  if (bytes <= 20 * 1024 * 1024) return {label: 'Low', className: 'ok'};
  return {label: 'Medium', className: ''};
}

function pct(bytes, totalBytes = null) {
  if (bytes === null) return 0;
  if (totalBytes === null || totalBytes === 0) {
    // Fallback to fixed max when no total is provided
    const max = 120 * 1024 * 1024; // 120 MB max for JS heap
    return Math.min(100, Math.round(100 * bytes / max));
  }
  return Math.round(100 * bytes / totalBytes);
}

function el(tag, attrs={}, children=[]) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2).toLowerCase(), v);
    else e.setAttribute(k, v);
  }
  children.forEach(c => e.appendChild(c));
  return e;
}

function rowCard(item, showPercentage = false, totalBytes = null) {
  const cls = classify(item.memoryBytes);
  const card = el('div', {class: 'card'});
  card.appendChild(el('div', {class: 'row'}, [
    el('div', {class: 'favicon'}, [el('img', {src: item.favIconUrl || '', alt: '', onerror: function() { this.style.display = 'none'; }})]),
    el('div', {text: item.title || '(untitled)'})
  ]));
  card.appendChild(el('button', {class: 'closeBtn', text: 'Close', onclick: async () => {
    await chrome.runtime.sendMessage({type: "CLOSE_TAB", tabId: item.tabId});
    await load();
  }}));
  
  const percentage = pct(item.memoryBytes, totalBytes);
  const memoryText = showPercentage ? 
    `${item.memoryText} (${percentage}%)` : 
    item.memoryText;
    
  card.appendChild(el('div', {class: 'barWrap'}, [
    el('div', {class: 'bar'}, [el('div', {class: 'fill', style: `width:${percentage}%`})]),
    el('div', {class: `badge ${cls.className}`, text: `${cls.label} • ${memoryText}`})
  ]));
  return card;
}

function windowCard(windowData) {
  const windowCard = el('div', {class: 'window-card'});
  
  // Window header
  windowCard.appendChild(el('div', {class: 'window-header'}, [
    el('div', {class: 'window-title'}, [
      el('span', {text: '🪟'}),
      el('span', {text: `Window ${windowData.windowId}${windowData.focused ? ' (Current)' : ''}`})
    ]),
    el('button', {
      class: 'window-focus-btn', 
      text: 'Focus', 
      onclick: async () => {
        await chrome.runtime.sendMessage({type: "FOCUS_WINDOW", windowId: windowData.windowId});
        await load();
      }
    })
  ]));
  
  // Window summary stats
  const highTabs = windowData.tabs.filter(t => t.high).length;
  const lowTabs = windowData.tabs.filter(t => t.low).length;
  
  windowCard.appendChild(el('div', {class: 'window-summary'}, [
    el('div', {class: 'window-stat'}, [
      el('div', {class: 'label', text: 'Tabs'}),
      el('div', {class: 'value', text: windowData.tabs.length.toString()})
    ]),
    el('div', {class: 'window-stat'}, [
      el('div', {class: 'label', text: 'High/Low'}),
      el('div', {class: 'value', text: `${highTabs}/${lowTabs}`})
    ]),
    el('div', {class: 'window-stat'}, [
      el('div', {class: 'label', text: 'Total'}),
      el('div', {class: 'value', text: formatBytes(windowData.totalMemory)})
    ])
  ]));
  
  // Tabs in this window
  const tabsContainer = el('div', {class: 'tabs-in-window'});
  windowData.tabs.forEach(tab => {
    tabsContainer.appendChild(rowCard(tab, false, windowData.totalMemory));
  });
  windowCard.appendChild(tabsContainer);
  
  return windowCard;
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return 'n/a';
  const units = ['B','KB','MB','GB','TB'];
  let i = 0, b = bytes;
  while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
  return `${b.toFixed(b >= 10 ? 0 : 1)} ${units[i]}`;
}

function renderCurrentWindow(snapshot) {
  sourceLabel.textContent = 'Source: Debugger (JS Heap) - Current Window';
  listEl.innerHTML = '';
  summaryEl.innerHTML = '';

  const totalMemory = snapshot.tabs.reduce((acc, t) => acc + (t.memoryBytes || 0), 0);

  summaryEl.appendChild(el('div', {class: 'stat'}, [
    el('div', {class: 'label', text: 'Open tabs'}),
    el('div', {class: 'value', text: snapshot.tabs.length.toString()})
  ]));
  summaryEl.appendChild(el('div', {class: 'stat'}, [
    el('div', {class: 'label', text: 'High / Low'}),
    el('div', {class: 'value', text: `${snapshot.tabs.filter(t => t.high).length} / ${snapshot.tabs.filter(t => t.low).length}`})
  ]));
  summaryEl.appendChild(el('div', {class: 'stat'}, [
    el('div', {class: 'label', text: 'Total (approx.)'}),
    el('div', {class: 'value', text: formatBytes(totalMemory)})
  ]));

  snapshot.tabs.forEach(item => listEl.appendChild(rowCard(item, true, totalMemory)));
}

function renderAllWindows(snapshot) {
  sourceLabel.textContent = 'Source: Debugger (JS Heap) - All Windows';
  windowsListEl.innerHTML = '';
  summaryEl.innerHTML = '';

  const totalTabs = snapshot.windows.reduce((acc, w) => acc + w.tabs.length, 0);
  const totalHigh = snapshot.windows.reduce((acc, w) => acc + w.tabs.filter(t => t.high).length, 0);
  const totalLow = snapshot.windows.reduce((acc, w) => acc + w.tabs.filter(t => t.low).length, 0);
  const totalMemory = snapshot.windows.reduce((acc, w) => acc + w.totalMemory, 0);

  summaryEl.appendChild(el('div', {class: 'stat'}, [
    el('div', {class: 'label', text: 'Windows'}),
    el('div', {class: 'value', text: snapshot.windows.length.toString()})
  ]));
  summaryEl.appendChild(el('div', {class: 'stat'}, [
    el('div', {class: 'label', text: 'Total tabs'}),
    el('div', {class: 'value', text: totalTabs.toString()})
  ]));
  summaryEl.appendChild(el('div', {class: 'stat'}, [
    el('div', {class: 'label', text: 'High / Low'}),
    el('div', {class: 'value', text: `${totalHigh} / ${totalLow}`})
  ]));
  summaryEl.appendChild(el('div', {class: 'stat'}, [
    el('div', {class: 'label', text: 'Total memory'}),
    el('div', {class: 'value', text: formatBytes(totalMemory)})
  ]));

  snapshot.windows.forEach(windowData => {
    windowsListEl.appendChild(windowCard(windowData));
  });
}

function switchView() {
  if (currentViewMode === 'current') {
    currentViewMode = 'all';
    viewModeBtn.textContent = '🪟';
    viewModeBtn.title = 'Current Window View';
    currentWindowView.classList.add('hidden');
    allWindowsView.classList.remove('hidden');
  } else {
    currentViewMode = 'current';
    viewModeBtn.textContent = '📋';
    viewModeBtn.title = 'All Windows View';
    currentWindowView.classList.remove('hidden');
    allWindowsView.classList.add('hidden');
  }
  load();
}

async function load() {
  try {
    let res;
    if (currentViewMode === 'current') {
      res = await chrome.runtime.sendMessage({type: "GET_CURRENT_WINDOW_SNAPSHOT"});
      if (res?.ok) renderCurrentWindow(res.snapshot);
    } else {
      res = await chrome.runtime.sendMessage({type: "GET_ALL_WINDOWS_SNAPSHOT"});
      if (res?.ok) renderAllWindows(res.snapshot);
    }
    
    if (!res?.ok) {
      const errorEl = currentViewMode === 'current' ? listEl : windowsListEl;
      errorEl.textContent = res?.error || "Failed to load data.";
    }
  } catch (error) {
    const errorEl = currentViewMode === 'current' ? listEl : windowsListEl;
    errorEl.textContent = "Failed to load data.";
  }
}

// Event listeners
refreshBtn.addEventListener('click', load);
viewModeBtn.addEventListener('click', switchView);
document.addEventListener('DOMContentLoaded', load);