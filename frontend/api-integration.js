/**
 * Frontend-Backend Integration for TrafficSafe Biratnagar
 * Refactored to use structured accident severity analysis
 * Calls /api/analyze-severity endpoint for EDA + ML-based severity insights
 */

// Backend API Base URL - adjust if your backend is on a different host/port
const API_BASE_URL = "http://localhost:5000/api";

// Map frontend time slots to backend time ranges
const TIME_SLOT_MAP = {
  morning: "06:00-12:00",
  afternoon: "12:00-18:00",
  evening: "18:00-00:00",
  night: "00:00-06:00",
};

/**
 * Main analyze function - Refactored for structured severity analysis
 * Calls backend /api/analyze-severity endpoint
 */
async function analyzeRisk() {
  const ward = document.getElementById("ward").value;
  const location = document.getElementById("location").value;
  const month = document.getElementById("month").value;
  const timeSlot = document.getElementById("time").value;
  const roadType = document.getElementById("roadtype").value;

  // Validation
  if (!ward || !location || !month || !timeSlot) {
    alert(
      "Please fill in all required fields: Ward, Location, Month, and Time Slot.",
    );
    return;
  }

  const btn = document.getElementById("analyzeBtn");
  btn.classList.add("loading");
  btn.querySelector("span").textContent = "⟳ Analyzing...";
  btn.disabled = true;

  try {
    // Normalize inputs
    const normalizedLocation = location.toLowerCase().trim();
    const normalizedRoadType = roadType.toLowerCase().trim();
    const timeRange = TIME_SLOT_MAP[timeSlot] || "06:00-12:00";

    // Prepare request body for /api/analyze-severity
    const requestBody = {
      ward: parseInt(ward),
      location: normalizedLocation,
      month: parseInt(month),
      time_range: timeRange,
      road_type: normalizedRoadType,
    };

    const placeholder = document.getElementById("placeholder");
    const resultContent = document.getElementById("resultContent");

    // Call backend API
    const response = await fetch(`${API_BASE_URL}/analyze-severity`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `API Error: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Unknown error from backend");
    }

    console.log("✅ Severity Analysis Success:", data);
    console.log("Analysis Type:", data.analysis_type);
    console.log("Has Exact Data:", data.has_exact_data);

    // Process and display results
    setTimeout(() => {
      btn.classList.remove("loading");
      btn.querySelector("span").textContent = "▶ Run Risk Analysis";
      btn.disabled = false;

      // Hide placeholder, show results
      placeholder.style.display = "none";
      resultContent.style.display = "flex";

      // Display severity analysis
      displaySeverityAnalysis(data);
    }, 800);
  } catch (error) {
    btn.classList.remove("loading");
    btn.querySelector("span").textContent = "▶ Run Risk Analysis";
    btn.disabled = false;

    console.error("❌ Analysis Error:", error);
    alert(
      `Error: ${error.message}\n\nMake sure:\n1. Backend is running (python run_server.py)\n2. Backend is on http://localhost:5000\n3. Location exists in database\n4. Road type is valid\n\nCheck browser console for details.`,
    );
  }
}

/**
 * Display structured severity analysis results
 */
function displaySeverityAnalysis(data) {
  const query = data.query || {};
  const exact = data.exact || {};
  const monthly = data.monthly || {};
  const timeBased = data.time_based || {};
  const mlPred = data.ml_prediction;
  const precautions = data.precautions || [];
  const hasExactData = data.has_exact_data;
  const analysisType = data.analysis_type || "unknown";

  // ── SUMMARY SECTION ──────────────────────────────────────
  // Use exact data if available, otherwise use monthly
  const dataToDisplay = hasExactData ? exact : monthly;

  document.getElementById("summaryTotal").textContent =
    dataToDisplay.total || 0;
  document.getElementById("summaryHigh").textContent = dataToDisplay.high || 0;
  document.getElementById("summaryLow").textContent = dataToDisplay.low || 0;

  // ── DATA SOURCE BADGE ────────────────────────────────────
  const sourceBadge = document.getElementById("sourceBadge");
  const sourceText = document.getElementById("dataSourceText");

  if (hasExactData && analysisType === "exact") {
    sourceBadge.className = "source-badge exact";
    sourceBadge.textContent = "✓ Exact Scenario";
    sourceText.textContent = `(${query.month_name} • ${query.time_label} • Ward ${query.ward})`;
  } else if (analysisType === "fallback") {
    sourceBadge.className = "source-badge fallback";
    sourceBadge.textContent = "⚠ Fallback Data";
    sourceText.textContent = "No exact data found. Using broader analysis.";
  } else {
    sourceBadge.className = "source-badge fallback";
    sourceBadge.textContent = "⚠ Insufficient Data";
    sourceText.textContent = "Using ML predictions and historical patterns.";
  }

  // ── SCENARIO COVERAGE ────────────────────────────────────
  // Calculate coverage percentage (exact as % of monthly)
  let coveragePercent = 0;
  if (monthly.total > 0) {
    coveragePercent = Math.round((exact.total / monthly.total) * 100);
  }

  document.getElementById("coveragePercent").textContent = hasExactData
    ? `${exact.high_pct}%`
    : "—";

  const coverageText = hasExactData
    ? `${exact.high_pct}% of accidents in ${query.month_name} are HIGH severity`
    : "No exact scenario data available";

  document.getElementById("coverageText").textContent = coverageText;

  // ── FALLBACK DATA SECTION ────────────────────────────────
  const fallbackSection = document.getElementById("fallbackSection");
  if (!hasExactData && (monthly.total > 0 || timeBased.total > 0)) {
    fallbackSection.style.display = "block";

    document.getElementById("monthlyTotal").textContent = monthly.total || 0;
    document.getElementById("monthlyHigh").textContent = monthly.high || 0;
    document.getElementById("monthlyLow").textContent = monthly.low || 0;

    document.getElementById("timeTotal").textContent = timeBased.total || 0;
    document.getElementById("timeHigh").textContent = timeBased.high || 0;
    document.getElementById("timeLow").textContent = timeBased.low || 0;
  } else {
    fallbackSection.style.display = "none";
  }

  // ── ML PREDICTION SECTION ────────────────────────────────
  const mlSection = document.getElementById("mlSection");
  if (mlPred) {
    mlSection.style.display = "block";

    const predClass = mlPred.prediction === "HIGH" ? "high" : "low";
    document.getElementById("mlPrediction").className =
      `ml-metric-value ${predClass}`;
    document.getElementById("mlPrediction").textContent = mlPred.prediction;

    document.getElementById("mlProbHigh").textContent = mlPred.prob_high + "%";
    document.getElementById("mlProbLow").textContent = mlPred.prob_low + "%";
  } else {
    mlSection.style.display = "none";
  }

  // ── PRECAUTIONS SECTION ──────────────────────────────────
  const precautionsList = document.getElementById("precautionsList");
  precautionsList.innerHTML = "";

  if (precautions && precautions.length > 0) {
    precautions.forEach((precaution) => {
      const item = document.createElement("div");
      item.className = "precaution-item";
      item.innerHTML = `
        <div class="precaution-icon">⚠️</div>
        <div class="precaution-text">${precaution}</div>
      `;
      precautionsList.appendChild(item);
    });
  } else {
    precautionsList.innerHTML = `
      <div class="precaution-item">
        <div class="precaution-icon">ℹ️</div>
        <div class="precaution-text">Follow standard traffic safety practices and obey all traffic rules.</div>
      </div>
    `;
  }
}

/**
 * Initialize - load form options from backend when page loads
 */
async function initializeForm() {
  try {
    const response = await fetch(`${API_BASE_URL}/options`);
    if (response.ok) {
      const options = await response.json();
      console.log("✓ Available locations:", options.locations);
      console.log("✓ Available wards:", options.wards);
    } else {
      console.warn("Could not load form options from backend");
    }
  } catch (error) {
    console.warn("Form initialization warning:", error.message);
  }
}

// Allow Enter key to trigger analysis
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    analyzeRisk();
  }
});

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", initializeForm);

console.log("✓ API Integration loaded (Refactored for Severity Analysis)");
console.log("✓ Backend API: " + API_BASE_URL);
