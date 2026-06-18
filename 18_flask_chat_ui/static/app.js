const appConfig = window.APP_CONFIG || {};
const isDemoMode = new URLSearchParams(window.location.search).get('demo') === '1';
const mobileQuery = window.matchMedia('(max-width: 760px)');
document.body.classList.add(isDemoMode ? 'demo-mode' : 'web-demo-mode');
function syncResponsiveMode() {
  document.body.classList.toggle('mobile-clean-mode', !isDemoMode && mobileQuery.matches);
}
syncResponsiveMode();
mobileQuery.addEventListener?.('change', syncResponsiveMode);

const chatHistory = document.querySelector('#chat-history');
const chatForm = document.querySelector('#chat-form');
const questionInput = document.querySelector('#question-input');
const sendButton = document.querySelector('#send-button');
const connectionStatus = document.querySelector('#connection-status');
const sampleList = document.querySelector('#sample-list');
const keywordList = document.querySelector('#keyword-list');
const sessionIdNode = document.querySelector('#session-id');
const clearHistoryButton = document.querySelector('#clear-history');
const modeButtons = Array.from(document.querySelectorAll('[data-mode]'));
const searchModeInput = document.querySelector('#search-mode');
const topKInput = document.querySelector('#top-k');
const filterSelect = document.querySelector('#filter-select');
const debugPasswordWrap = document.querySelector('#debug-password-wrap');
const debugPasswordInput = document.querySelector('#debug-password');
const inspectorEyebrow = document.querySelector('#inspector-eyebrow');
const inspectorTitle = document.querySelector('#inspector-title');
const inspectorContent = document.querySelector('#inspector-content');
const copyPayloadButton = document.querySelector('#copy-payload');

const STORAGE_KEY = 'bti_chat_history';
const SESSION_KEY = 'bti_session_id';
const MODE_KEY = 'bti_mode';
const API_STATS_KEY = 'bti_api_stats';
const MAX_STORED_MESSAGES = 40;
const MAX_RENDERED_MESSAGES = 24;

const sampleQuestions = [
  'Who is Rajesh Arigala?',
  'Why is Rajesh suitable for business-tech hybrid roles?',
  'What experience does Rajesh have with BPCL?'
];

const keywordQuestions = [
  { label: "AI", question: "What is Rajesh's AI experience and how does it connect to business outcomes?" },
  { label: "MLOps", question: "Show Rajesh's MLOps capability with project evidence." },
  { label: "Kubernetes", question: "Which Rajesh projects show Kubernetes capability?" },
  { label: "Business", question: "Summarize Rajesh's business leadership experience." },
  { label: "BPCL", question: "What experience does Rajesh have with BPCL?" },
  { label: "R-Cafe", question: "What is Rajesh's R-Cafe experience and current entrepreneurial context?" },
  { label: "Transition", question: "Why is Rajesh transitioning toward AI and business-tech roles?" },
  { label: "Role Fit", question: "What roles is Rajesh qualified for across business and technology?" }
];

let currentMode = (!isDemoMode && mobileQuery.matches) ? 'user' : (localStorage.getItem(MODE_KEY) || 'user');
let sessionId = getOrCreateSessionId();
let messages = loadMessages();
let lastPayload = null;
let isSubmitting = false;
let apiStats = loadApiStats();


function attachToolActionHandlers() {
  document.querySelectorAll('[data-tool-actions] .tool-action').forEach((button) => {
    button.addEventListener('click', () => {
      const labels = {
        whatsapp: 'WhatsApp/call tool will be connected later.',
        facetime: 'FaceTime tool will be connected later.',
        speak: 'Voice/speak tool will be connected later.',
        email: 'Email drafting tool will be connected later.',
        review: 'Review/feedback tool will be connected later.',
        github: 'GitHub access will be connected later.',
        linkedin: 'LinkedIn access will be connected later.'
      };
      setStatus(labels[button.dataset.tool] || 'Tool action planned', 'loading');
      window.setTimeout(() => setStatus('Ready'), 1800);
    });
  });
}

function getOrCreateSessionId() {
  const existing = localStorage.getItem(SESSION_KEY);
  if (existing) return existing;
  const next = `BTI-${new Date().toISOString().slice(0,10).replaceAll('-', '')}-${Math.random().toString(36).slice(2,7).toUpperCase()}`;
  localStorage.setItem(SESSION_KEY, next);
  return next;
}

function loadMessages() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]').slice(-MAX_STORED_MESSAGES); } catch { return []; }
}

function saveMessages() {
  if (messages.length > MAX_STORED_MESSAGES) messages = messages.slice(-MAX_STORED_MESSAGES);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
}


function loadApiStats() {
  const defaults = {
    health_status: 'unchecked',
    health_code: null,
    health_latency_ms: null,
    health_checked_at: null,
    total_calls: 0,
    success_calls: 0,
    failed_calls: 0,
    retry_count: 0,
    last_chat_status_code: null,
    last_chat_latency_ms: null,
    last_error: null,
    last_request_id: null,
    last_call_at: null
  };
  try { return { ...defaults, ...JSON.parse(localStorage.getItem(API_STATS_KEY) || '{}') }; } catch { return defaults; }
}

function saveApiStats() { localStorage.setItem(API_STATS_KEY, JSON.stringify(apiStats)); }

function updateApiStats(partial) {
  apiStats = { ...apiStats, ...partial };
  saveApiStats();
  if (currentMode === 'observability') renderInspector();
}

async function checkApiHealth() {
  const started = performance.now();
  try {
    const response = await fetch('/health', { cache: 'no-store' });
    let payload = {};
    try { payload = await response.json(); } catch { payload = {}; }
    updateApiStats({
      health_status: response.ok ? (payload.status || 'healthy') : 'unhealthy',
      health_code: response.status,
      health_latency_ms: Math.round(performance.now() - started),
      health_checked_at: new Date().toISOString(),
      last_error: response.ok ? apiStats.last_error : `Health returned HTTP ${response.status}`
    });
  } catch (error) {
    updateApiStats({
      health_status: 'unreachable',
      health_code: 0,
      health_latency_ms: Math.round(performance.now() - started),
      health_checked_at: new Date().toISOString(),
      last_error: error.message
    });
  }
}

function setStatus(text, state = 'ready') {
  connectionStatus.textContent = text;
  connectionStatus.className = `status-pill ${state}`;
}

function setMode(mode) {
  currentMode = mode;
  localStorage.setItem(MODE_KEY, mode);
  modeButtons.forEach((button) => button.classList.toggle('active', button.dataset.mode === mode));
  debugPasswordWrap?.classList.toggle('is-hidden', mode === 'user');
  document.body.classList.toggle('user-mode', mode === 'user');
  if (mode === 'observability' && apiStats.health_status === 'unchecked') checkApiHealth();
  renderInspector();
}

function submitEmbeddedQuestion(question) {
  if (sendButton.disabled) return;
  questionInput.value = question;
  chatForm.requestSubmit();
}

function renderSamples() {
  sampleList.innerHTML = '';
  sampleQuestions.forEach((question) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'sample-button';
    button.textContent = question;
    button.addEventListener('click', () => submitEmbeddedQuestion(question));
    sampleList.appendChild(button);
  });
}

function renderKeywords() {
  if (!keywordList) return;
  keywordList.innerHTML = '';
  keywordQuestions.forEach((item) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'keyword-button';
    button.textContent = item.label;
    button.title = item.question;
    button.addEventListener('click', () => submitEmbeddedQuestion(item.question));
    keywordList.appendChild(button);
  });
}

function renderMessages() {
  sessionIdNode.textContent = sessionId;
  chatHistory.innerHTML = '';
  const intro = { role: 'assistant', text: `Hello, I'm RABBIT, Rajesh Arigala's AI assistant. May I know your name, profession, and role?`, meta: 'Business-Tech RAG' };
  const visibleMessages = messages.slice(-MAX_RENDERED_MESSAGES);
  const messageOffset = messages.length - visibleMessages.length;
  [intro, ...visibleMessages.map((message, index) => ({ ...message, messageIndex: String(messageOffset + index) }))].forEach((message) => {
    const article = document.createElement('article');
    article.className = `message ${message.role}`;
    const name = message.role === 'user' ? 'You' : 'RABBIT';
    article.innerHTML = `
      <div class="message-head"><strong>${escapeHtml(name)}</strong>${message.meta ? `<span>${escapeHtml(message.meta)}</span>` : ''}</div>
      <div class="message-body">${formatText(message.text || '')}${renderSources(message.sources || [])}</div>
      ${message.retry ? `<button type="button" class="retry-button" data-message-index="${escapeAttr(message.messageIndex)}">Retry</button>` : ''}`;
    chatHistory.appendChild(article);
  });
  attachRetryHandlers();
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function renderSources(sources) {
  if (!sources.length) return '';
  const unique = [];
  const seen = new Set();
  sources.forEach((source) => {
    const key = source.source_url || `${source.page_id}|${source.title}`;
    if (!seen.has(key)) { seen.add(key); unique.push(source); }
  });
  if (!unique.length) return '';
  return `<div class="sources"><div class="sources-title">Relevant links</div>${unique.slice(0, 2).map((source) => `<a class="source-link" href="${escapeAttr(source.source_url || '#')}" target="_blank" rel="noreferrer"><span class="source-title">${escapeHtml(source.title || source.page_id || 'Open page')}</span><span class="source-url">${escapeHtml(source.source_url || '')}</span></a>`).join('')}</div>`;
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (isSubmitting) return;
  const question = questionInput.value.trim();
  if (!question) return;
  if (currentMode !== 'user' && debugPasswordInput && !debugPasswordInput.value.trim()) {
    setStatus('Password Required', 'error');
    debugPasswordInput.focus();
    return;
  }
  messages.push({ role: 'user', text: question });
  messages.push({ role: 'assistant', text: 'Working through the evidence...', meta: 'Thinking' });
  questionInput.value = '';
  saveMessages();
  renderMessages();
  isSubmitting = true;
  sendButton.disabled = true;
  questionInput.disabled = true;
  setStatus('Thinking', 'loading');

  try {
    const payload = await callChat(question);
    lastPayload = payload;
    const answer = normalizeAnswer(payload.user?.answer || 'No answer returned.');
    messages[messages.length - 1] = { role: 'assistant', text: '', meta: 'Answer', sources: [] };
    setStatus(payload.status === 'success' ? 'Connected' : 'Issue', payload.status === 'success' ? 'ready' : 'error');
    renderInspector();
    await streamAssistantMessage(answer, payload.user?.links || []);
  } catch (error) {
    const errorText = error.message === 'Load failed'
      ? 'I could not complete the request. The live service may still be waking up or the network call was interrupted. Please use Retry.'
      : `I could not complete the request. ${error.message}`;
    messages[messages.length - 1] = { role: 'assistant', text: errorText, meta: 'Request failed', retry: { question } };
    setStatus('Error', 'error');
  } finally {
    saveMessages();
    renderMessages();
    isSubmitting = false;
    sendButton.disabled = false;
    questionInput.disabled = false;
    questionInput.focus();
  }
});

function normalizeAnswer(text) {
  return String(text || '')
    .replace(/Why It Matters\s*:?/gi, 'Context:')
    .replace(/Why it matters\s*:?/gi, 'Context:')
    .replace(/Role-Fit Angle\s*:?/gi, 'Context:')
    .replace(/Direct Answer\s*:?/gi, 'Direct Answer:')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function splitForStreaming(text) {
  const parts = String(text || '').match(/[^.!?\n]+[.!?]?|\n+/g) || [text];
  const chunks = [];
  let buffer = '';
  parts.forEach((part) => {
    buffer += part;
    if (buffer.length >= 80 || /\n+/.test(part)) {
      chunks.push(buffer);
      buffer = '';
    }
  });
  if (buffer) chunks.push(buffer);
  return chunks;
}

async function streamAssistantMessage(answer, sources) {
  const chunks = splitForStreaming(answer);
  let shown = '';
  for (const chunk of chunks) {
    shown += chunk;
    messages[messages.length - 1] = { role: 'assistant', text: shown, meta: 'Answer', sources: [] };
    renderMessages();
    await new Promise((resolve) => setTimeout(resolve, 45));
  }
  messages[messages.length - 1] = { role: 'assistant', text: answer, meta: 'Answer', sources };
  saveMessages();
  renderMessages();
}

async function callChat(question) {
  const started = performance.now();
  let response;
  let payload = {};
  try {
    response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        mode: currentMode,
        session_id: sessionId,
        search_mode: searchModeInput?.value || 'hybrid',
        top_k: Number(topKInput?.value || 5),
        filter: filterSelect?.value || null,
        debug_password: debugPasswordInput ? debugPasswordInput.value : ''
      })
    });
    try { payload = await response.json(); } catch { payload = {}; }
    const latency = Math.round(performance.now() - started);
    const ok = response.ok && payload.status !== 'error' && payload.status !== 'failed';
    updateApiStats({
      total_calls: apiStats.total_calls + 1,
      success_calls: apiStats.success_calls + (ok ? 1 : 0),
      failed_calls: apiStats.failed_calls + (ok ? 0 : 1),
      last_chat_status_code: response.status,
      last_chat_latency_ms: latency,
      last_request_id: payload.observability?.request_id || payload.traceability?.request_id || null,
      last_call_at: new Date().toISOString(),
      last_error: ok ? null : (payload.error || payload.observability?.error || `HTTP ${response.status}`)
    });
    if (!response.ok) throw new Error(payload.error || payload.observability?.error || `HTTP ${response.status}`);
    return payload;
  } catch (error) {
    if (!response) {
      updateApiStats({
        total_calls: apiStats.total_calls + 1,
        failed_calls: apiStats.failed_calls + 1,
        last_chat_status_code: 0,
        last_chat_latency_ms: Math.round(performance.now() - started),
        last_call_at: new Date().toISOString(),
        last_error: error.message
      });
    }
    throw error;
  }
}

function renderInspector() {
  const titles = { user: 'User Mode', debug: 'Debug Mode', observability: 'Observability Mode', tech: 'Tech Mode' };
  inspectorEyebrow.textContent = currentMode;
  inspectorTitle.textContent = titles[currentMode] || 'Mode Panel';
  if (!lastPayload) {
    if (currentMode === 'user') {
      inspectorContent.innerHTML = '';
      return;
    }
    if (currentMode === 'observability') {
      renderObservabilityInspector();
      return;
    }
    if (currentMode === 'tech') {
      renderTechInspector();
      return;
    }
    inspectorContent.innerHTML = `<p class="muted">Ask a question to populate ${escapeHtml(titles[currentMode] || currentMode)}.</p>`;
    return;
  }
  if (currentMode === 'user') {
    inspectorContent.innerHTML = '';
    return;
  }
  if (currentMode === 'debug') renderDebugInspector();
  if (currentMode === 'observability') renderObservabilityInspector();
  if (currentMode === 'tech') renderTechInspector();
}

function renderUserInspector() {
  const user = lastPayload.user || {};
  inspectorContent.innerHTML = `
    <div class="debug-card"><h3>Answer Confidence</h3><div class="metric-grid">
      ${metric('Label', user.answer_confidence_label)}
      ${metric('Score', user.answer_confidence_score)}
    </div><p class="muted">${escapeHtml(user.answer_confidence_reason || '')}</p></div>
    <div class="debug-card"><h3>Sources</h3>${(user.sources || []).map((s) => `<div class="chunk"><strong>${escapeHtml(s.page_id || '')}</strong><p>${escapeHtml(s.title || '')}<br>${escapeHtml(s.source_url || '')}</p></div>`).join('')}</div>`;
}

function renderDebugInspector() {
  const debug = lastPayload.debug || {};
  const user = lastPayload.user || {};
  const chunks = debug.retrieved_chunks || [];
  const confidence = debug.answer_confidence || {};
  const lineage = debug.source_lineage || [];
  inspectorContent.innerHTML = `
    <div class="debug-card"><h3>Answer Confidence</h3><div class="metric-grid">
      ${metric('Label', confidence.label || user.answer_confidence_label)}${metric('Score', confidence.score || user.answer_confidence_score)}
    </div><p class="muted">${escapeHtml(confidence.reason || user.answer_confidence_reason || '')}</p></div>
    <div class="debug-card"><h3>Retrieval</h3><div class="metric-grid">
      ${metric('Mode', debug.search_mode)}${metric('Top K', debug.top_k)}${metric('Filter', debug.filter || 'none')}${metric('Chunks', chunks.length)}
    </div></div>
    <div class="debug-card"><h3>Source Links</h3>${lineage.map((s) => `<div class="chunk"><strong>${escapeHtml(s.page_id || '')}</strong><p>${escapeHtml(s.section_id || '')}<br><a class="source-link" href="${escapeAttr(s.source_url || '#')}" target="_blank" rel="noreferrer">${escapeHtml(s.source_url || '')}</a><br>Chunk: ${escapeHtml(s.chunk_index ?? 'n/a')} | Score: ${escapeHtml(s.score ?? 'n/a')}</p></div>`).join('') || '<p class="muted">No sources returned.</p>'}</div>
    <div class="debug-card"><h3>Retrieved Chunks</h3>${chunks.map((c) => `<details class="chunk"><summary>#${c.rank} ${escapeHtml(c.page_id || '')} - ${Number(c.retrieval_score_relative_percent || 0).toFixed(2)}%</summary><div class="metric-grid">${metric('Raw score', c.retrieval_score_raw)}${metric('Hybrid score', c.hybrid_score_raw)}${metric('Vector score', c.vector_score_raw ?? 'n/a')}${metric('Keyword score', c.keyword_score_raw ?? 'n/a')}</div><p>${escapeHtml(c.snippet || '')}</p></details>`).join('')}</div>
    <div class="debug-card"><h3>Prompt Preview</h3><pre>${escapeHtml(debug.prompt_preview || '')}</pre></div>`;
}

function renderObservabilityInspector() {
  const o = lastPayload?.observability || {};
  inspectorContent.innerHTML = `
    <div class="debug-card"><h3>API Health</h3><div class="metric-grid">${metric('Health', apiStats.health_status)}${metric('Health code', apiStats.health_code)}${metric('Health latency', apiStats.health_latency_ms ? `${apiStats.health_latency_ms} ms` : '-')}${metric('Checked at', formatTime(apiStats.health_checked_at))}</div><button type="button" class="api-button" id="api-health-refresh">Refresh API Health</button></div>
    <div class="debug-card"><h3>API Calls</h3><div class="metric-grid">${metric('Total calls', apiStats.total_calls)}${metric('Success calls', apiStats.success_calls)}${metric('Failed calls', apiStats.failed_calls)}${metric('Retry clicks', apiStats.retry_count)}</div></div>
    <div class="debug-card"><h3>Last API Response</h3><div class="metric-grid">${metric('HTTP code', apiStats.last_chat_status_code)}${metric('Latency', apiStats.last_chat_latency_ms ? `${apiStats.last_chat_latency_ms} ms` : '-')}${metric('Request ID', apiStats.last_request_id)}${metric('Last call', formatTime(apiStats.last_call_at))}</div>${apiStats.last_error ? `<p class="api-error">${escapeHtml(apiStats.last_error)}</p>` : ''}</div>
    <div class="debug-card"><h3>Request</h3><div class="metric-grid">${metric('Status', o.status)}${metric('Request ID', o.request_id)}${metric('Session', o.session_id)}${metric('Index', o.index_name)}</div></div>
    <div class="debug-card"><h3>Latency</h3><div class="metric-grid">${metric('Embedding ms', o.embedding_latency_ms)}${metric('Search ms', o.search_latency_ms)}${metric('Answer ms', o.answer_latency_ms)}${metric('Total ms', o.total_latency_ms)}</div></div>
    <div class="debug-card"><h3>Retrieval Scores</h3><div class="metric-grid">${metric('Top 1', o.top_1_score)}${metric('Min', o.min_retrieval_score)}${metric('Max', o.max_retrieval_score)}${metric('Spread', o.score_spread)}${metric('Avg', o.average_score)}${metric('Source diversity', o.source_diversity_count)}</div></div>
    <div class="debug-card"><h3>Models</h3><div class="metric-grid">${metric('Embedding', o.embedding_deployment)}${metric('Chat', o.chat_deployment)}${metric('Retrieved chunks', o.retrieved_chunk_count)}${metric('Confidence', o.answer_confidence_label)}</div></div>`;
  document.querySelector('#api-health-refresh')?.addEventListener('click', checkApiHealth);
}

function renderTechInspector() {
  const tech = lastPayload?.tech || {};
  const trace = lastPayload?.traceability || {};
  const apiBackend = {
    health_endpoint: '/health',
    chat_endpoint: '/api/chat',
    retry_scope: 'available from failed chat messages in every mode',
    api_metrics_home: 'Observability Mode',
    log_files: lastPayload?.logging || 'available after first request',
    storage_note: 'browser localStorage stores UI counters; Flask JSONL logs store backend events'
  };
  inspectorContent.innerHTML = `
    <div class="debug-card"><h3>Tech Mode</h3><p class="muted">${escapeHtml(tech.message || 'Planned placeholder for backend/API internals.')}</p></div>
    <div class="debug-card"><h3>API Backend Contract</h3><pre>${escapeHtml(JSON.stringify(apiBackend, null, 2))}</pre></div>
    <div class="debug-card"><h3>Traceability Available Now</h3><pre>${escapeHtml(JSON.stringify(trace, null, 2))}</pre></div>`;
}

function attachRetryHandlers() {
  chatHistory.querySelectorAll('.retry-button').forEach((button) => {
    button.addEventListener('click', () => {
      const index = Number(button.dataset.messageIndex);
      const retryPayload = messages[index]?.retry;
      if (!retryPayload?.question) return;
      updateApiStats({ retry_count: apiStats.retry_count + 1 });
      questionInput.value = retryPayload.question;
      chatForm.requestSubmit();
    });
  });
}

function formatTime(value) {
  if (!value) return '-';
  try { return new Date(value).toLocaleTimeString(); } catch { return String(value); }
}

function metric(label, value) {
  const shown = value === null || value === undefined || value === '' ? '-' : String(value);
  return `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(shown)}</strong></div>`;
}

function formatText(text) {
  const safe = escapeHtml(text || '');
  const html = safe
    .replace(/^### (.*)$/gm, '<h3>$1</h3>')
    .replace(/^\d+\. \*\*(.*?)\*\*: ?(.*)$/gm, '<div class="answer-bullet"><strong>$1:</strong> $2</div>')
    .replace(/^[-*] (.*)$/gm, '<div class="answer-bullet">$1</div>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
  return linkify(html);
}

function linkify(html) {
  return String(html || '').replace(/(https?:\/\/[^\s<]+)/g, '<a class="inline-link" href="$1" target="_blank" rel="noreferrer">$1</a>');
}

function escapeHtml(value) {
  return String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
}
function escapeAttr(value) { return escapeHtml(value); }

modeButtons.forEach((button) => button.addEventListener('click', () => setMode(button.dataset.mode)));
clearHistoryButton?.addEventListener('click', () => { messages = []; lastPayload = null; saveMessages(); renderMessages(); renderInspector(); });
copyPayloadButton?.addEventListener('click', async () => { if (lastPayload) await navigator.clipboard.writeText(JSON.stringify(lastPayload, null, 2)); });
questionInput.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); chatForm.requestSubmit(); } });

renderSamples();
renderKeywords();
attachToolActionHandlers();
setMode(currentMode);
renderMessages();
setStatus('Ready');
