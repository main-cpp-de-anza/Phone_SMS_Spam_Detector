// ============================================================
// Interactive Model Playground Script
// ============================================================

const PRESET_MESSAGES = {
  lottery: "CONGRATULATIONS, you just won $500 cash! Visit bit.ly/claim or call 800-555-0199 now!",
  delivery: "USPS alert: Your package is stuck at transit. Pay 15 dollars fee at https://usps-redelivery.com/pay",
  casual: "Hey Mom, are we meeting for lunch at 12:30 tomorrow?",
  trap: "Grandma said I won the family burping contest! Are you free for lunch tomorrow? Haha"
};

document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("sms-input");
  const charCounter = document.getElementById("char-count");
  const analyzeBtn = document.getElementById("btn-analyze");

  // Character counter
  textarea.addEventListener("input", () => {
    const len = textarea.value.length;
    charCounter.textContent = `${len} characters`;
  });

  // Preset button clicks
  document.querySelectorAll(".preset-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      const type = btn.getAttribute("data-preset");
      if (PRESET_MESSAGES[type]) {
        textarea.value = PRESET_MESSAGES[type];
        charCounter.textContent = `${textarea.value.length} characters`;
        runPrediction();
      }
    });
  });

  // Analyze button click
  analyzeBtn.addEventListener("click", () => {
    runPrediction();
  });

  // Ctrl+Enter or Cmd+Enter to submit
  textarea.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runPrediction();
    }
  });

  async function runPrediction() {
    const text = textarea.value.trim();
    if (!text) {
      alert("Please enter an SMS message to analyze.");
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="animate-spin" style="animation: spin 1s linear infinite;">
        <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
        <path d="M12 2a10 10 0 0 1 10 10"></path>
      </svg>
      Analyzing...
    `;

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      renderResults(data);
    } catch (err) {
      console.error("Prediction error:", err);
      alert("Error analyzing message. Is the server running?");
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        Analyze Message
      `;
    }
  }

  function renderResults(data) {
    // 1. Engine 1: Naive
    const naiveBadge = document.getElementById("naive-badge");
    const naiveDetails = document.getElementById("naive-details");
    const isNaiveSpam = data.naive.verdict === "SPAM";

    naiveBadge.textContent = data.naive.verdict;
    naiveBadge.className = `status-badge ${isNaiveSpam ? "badge-spam" : "badge-ham"}`;

    if (data.naive.matched_keywords && data.naive.matched_keywords.length > 0) {
      naiveDetails.innerHTML = `
        <div class="result-detail-line"><strong>Flagged keyword:</strong></div>
        <div class="hits-container">
          ${data.naive.matched_keywords.map(kw => `<span class="hit-tag positive">"${kw}"</span>`).join("")}
        </div>
        <div style="margin-top: 0.6rem; font-size: 0.8rem; color: var(--text-muted);">
          Triggered instant spam block.
        </div>
      `;
    } else {
      naiveDetails.innerHTML = `
        <div class="result-detail-line">No banned keywords found in text.</div>
      `;
    }

    // 2. Engine 2: SpamAssassin
    const saBadge = document.getElementById("sa-badge");
    const saDetails = document.getElementById("sa-details");
    const isSaSpam = data.spamassassin.verdict === "SPAM";

    saBadge.textContent = data.spamassassin.verdict;
    saBadge.className = `status-badge ${isSaSpam ? "badge-spam" : "badge-ham"}`;

    let hitsHtml = "";
    if (data.spamassassin.hits && data.spamassassin.hits.length > 0) {
      hitsHtml = `
        <div style="margin-top: 0.6rem; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.3rem;"><strong>Rule Hits:</strong></div>
        <div class="hits-container">
          ${data.spamassassin.hits.map(h => {
            const isPos = h.points > 0;
            const sign = isPos ? `+${h.points}` : `${h.points}`;
            return `<span class="hit-tag ${isPos ? 'positive' : 'negative'}">${h.phrase} (${sign})</span>`;
          }).join("")}
        </div>
      `;
    } else {
      hitsHtml = `<div style="margin-top: 0.5rem; font-size: 0.82rem; color: var(--text-muted);">No dictionary rules triggered (0.0 pts).</div>`;
    }

    saDetails.innerHTML = `
      <div class="result-detail-line">
        <strong>Total Score:</strong> <span style="font-family: var(--font-mono); font-weight: 700;">${data.spamassassin.score > 0 ? '+' : ''}${data.spamassassin.score}</span>
        <span style="color: var(--text-muted); font-size: 0.8rem;">(Threshold: ${data.spamassassin.threshold})</span>
      </div>
      ${hitsHtml}
    `;

    // 3. Engine 3: Machine Learning (LinearSVC)
    const mlBadge = document.getElementById("ml-badge");
    const mlDetails = document.getElementById("ml-details");
    const isMlSpam = data.machine_learning.verdict === "SPAM";

    mlBadge.textContent = data.machine_learning.verdict;
    mlBadge.className = `status-badge ${isMlSpam ? "badge-spam" : "badge-ham"}`;

    const spamPct = data.machine_learning.spam_confidence_pct;
    const hamPct = data.machine_learning.ham_confidence_pct;
    const barWidth = isMlSpam ? spamPct : hamPct;
    const barColor = isMlSpam ? "var(--color-spam-text)" : "var(--color-ham-text)";

    mlDetails.innerHTML = `
      <div class="result-detail-line">
        <strong>Confidence:</strong> 
        <span style="font-family: var(--font-mono); font-weight: 700;">${isMlSpam ? spamPct : hamPct}%</span>
        <span style="color: var(--text-muted); font-size: 0.8rem;">(${isMlSpam ? 'Spam' : 'Ham'})</span>
      </div>
      <div class="confidence-bar-wrapper">
        <div class="confidence-bar-fill" style="width: ${barWidth}%; background-color: ${barColor};"></div>
      </div>
      <div style="margin-top: 0.8rem; font-size: 0.8rem; color: var(--text-secondary);">
        <strong>Hyperplane Distance:</strong> 
        <code style="font-family: var(--font-mono);">${data.machine_learning.decision_score > 0 ? '+' : ''}${data.machine_learning.decision_score}</code>
      </div>
      <div style="margin-top: 0.4rem; font-size: 0.78rem; color: var(--text-muted);">
        Normalized: <code>${data.machine_learning.cleaned_text}</code>
      </div>
    `;

    // Smooth scroll to results on small screens
    if (window.innerWidth < 840) {
      document.querySelector(".results-grid").scrollIntoView({ behavior: "smooth" });
    }
  }
});
