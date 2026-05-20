/**
 * Frontend-Backend Integration for TrafficSafe Biratnagar
 * Hierarchical analysis: Location → Ward → Ward+Location
 */

const API_BASE_URL = "http://localhost:5000/api";

const TIME_SLOT_MAP = {
  morning: "06:00-12:00",
  afternoon: "12:00-18:00",
  evening: "18:00-00:00",
  night: "00:00-06:00",
};

/**
 * Main analyze function - Fetches all three levels of analysis
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
    const normalizedLocation = location.toLowerCase().trim();
    const normalizedRoadType = roadType.toLowerCase().trim();
    const timeRange = TIME_SLOT_MAP[timeSlot] || "06:00-12:00";
    const wardNum = parseInt(ward);

    const placeholder = document.getElementById("placeholder");
    const resultContent = document.getElementById("resultContent");

    // Parallel fetch all three levels
    const [locationData, wardData, severityData] = await Promise.all([
      fetchLocationAnalysis(normalizedLocation),
      fetchWardAnalysis(wardNum),
      fetchSeverityAnalysis(
        wardNum,
        normalizedLocation,
        month,
        timeRange,
        normalizedRoadType,
      ),
    ]);

    console.log("✅ All analyses fetched successfully");
    console.log("Location data:", locationData);
    console.log("Ward data:", wardData);
    console.log("Severity data:", severityData);

    setTimeout(() => {
      btn.classList.remove("loading");
      btn.querySelector("span").textContent = "▶ Run Risk Analysis";
      btn.disabled = false;

      placeholder.style.display = "none";
      resultContent.style.display = "flex";

      // Display all three levels
      displayHierarchicalAnalysis(locationData, wardData, severityData);
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
 * Fetch location-level analysis
 */
async function fetchLocationAnalysis(location) {
  const encodedLocation = encodeURIComponent(location);
  const response = await fetch(
    `${API_BASE_URL}/location-analysis/${encodedLocation}`,
  );
  if (!response.ok) {
    throw new Error(`Location analysis failed: ${response.status}`);
  }
  return await response.json();
}

/**
 * Fetch ward-level analysis
 */
async function fetchWardAnalysis(ward) {
  const response = await fetch(`${API_BASE_URL}/ward-analysis/${ward}`);
  if (!response.ok) {
    throw new Error(`Ward analysis failed: ${response.status}`);
  }
  return await response.json();
}

/**
 * Fetch ward+location severity analysis
 */
async function fetchSeverityAnalysis(
  ward,
  location,
  month,
  timeRange,
  roadType,
) {
  const response = await fetch(`${API_BASE_URL}/analyze-severity`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ward: ward,
      location: location,
      month: parseInt(month),
      time_range: timeRange,
      road_type: roadType,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || `API Error: ${response.status}`);
  }

  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error || "Unknown error from backend");
  }
  return data;
}

/**
 * Display hierarchical analysis: Location → Ward → Ward+Location
 */
function displayHierarchicalAnalysis(locationData, wardData, severityData) {
  // Update summary (Ward+Location exact scenario)
  const query = severityData.query || {};
  const exact = severityData.exact || {};
  const monthly = severityData.monthly || {};
  const mlPred = severityData.ml_prediction;
  const precautions = severityData.precautions || [];
  const hasExactData = severityData.has_exact_data;
  const analysisType = severityData.analysis_type || "unknown";

  // ── SUMMARY SECTION (Ward+Location) ──────────────────────
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

  document.getElementById("coveragePercent").textContent = hasExactData
    ? `${exact.high_pct}%`
    : "—";
  const coverageText = hasExactData
    ? `${exact.high_pct}% of accidents in ${query.month_name} are HIGH severity`
    : "No exact scenario data available";
  document.getElementById("coverageText").textContent = coverageText;

  // ── LOCATION-LEVEL ANALYSIS ─────────────────────────────
  displayLocationAnalysis(locationData);

  // ── WARD-LEVEL ANALYSIS ─────────────────────────────────
  displayWardAnalysis(wardData);

  // ── WARD+LOCATION DETAILED ANALYSIS ─────────────────────
  displayWardLocationAnalysis(severityData);

  // ── FALLBACK DATA SECTION ────────────────────────────────
  const fallbackSection = document.getElementById("fallbackSection");
  const monthly_data = severityData.monthly || {};
  const timeBased = severityData.time_based || {};

  if (!hasExactData && (monthly_data.total > 0 || timeBased.total > 0)) {
    fallbackSection.style.display = "block";
    document.getElementById("monthlyTotal").textContent =
      monthly_data.total || 0;
    document.getElementById("monthlyHigh").textContent = monthly_data.high || 0;
    document.getElementById("monthlyLow").textContent = monthly_data.low || 0;
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
 * Display location-level analysis
 */
function displayLocationAnalysis(data) {
  const section = document.getElementById("locationSection");

  if (data.error) {
    section.style.display = "none";
    return;
  }

  section.style.display = "block";

  const location = data.location || "Unknown Location";
  const totalAccidents = data.total_accidents || 0;
  const severity = data.severity_distribution || {};
  const injuries = data.injury_stats || {};

  // Calculate high severity percentage
  const highCount = parseInt(severity.high || 0);
  const highPct =
    totalAccidents > 0 ? ((highCount / totalAccidents) * 100).toFixed(1) : 0;

  document.getElementById("locationLabel").textContent =
    `${location.toUpperCase()} (All Wards)`;
  document.getElementById("locationTotal").textContent = totalAccidents;
  document.getElementById("locationHigh").textContent = highCount;
  document.getElementById("locationLow").textContent = parseInt(
    severity.low || 0,
  );
  document.getElementById("locationHighPct").textContent = `${highPct}%`;
  document.getElementById("locationMinorInjuries").textContent =
    injuries.minor_injuries || 0;
  document.getElementById("locationSevereInjuries").textContent =
    injuries.severe_injuries || 0;
  document.getElementById("locationDeaths").textContent = injuries.deaths || 0;
}

/**
 * Display ward-level analysis
 */
function displayWardAnalysis(data) {
  const section = document.getElementById("wardSection");

  if (data.error) {
    section.style.display = "none";
    return;
  }

  section.style.display = "block";

  const ward = data.ward || "Unknown Ward";
  const totalAccidents = data.total_accidents || 0;
  const severity = data.severity_distribution || {};
  const injuries = data.injury_stats || {};

  // Calculate high severity percentage
  const highCount = parseInt(severity.high || 0);
  const highPct =
    totalAccidents > 0 ? ((highCount / totalAccidents) * 100).toFixed(1) : 0;

  document.getElementById("wardLabel").textContent =
    `Ward ${ward} (All Locations)`;
  document.getElementById("wardTotal").textContent = totalAccidents;
  document.getElementById("wardHigh").textContent = highCount;
  document.getElementById("wardLow").textContent = parseInt(severity.low || 0);
  document.getElementById("wardHighPct").textContent = `${highPct}%`;
  document.getElementById("wardMinorInjuries").textContent =
    injuries.minor_injuries || 0;
  document.getElementById("wardSevereInjuries").textContent =
    injuries.severe_injuries || 0;
  document.getElementById("wardDeaths").textContent = injuries.deaths || 0;
}

/**
 * Display ward+location detailed analysis
 */
function displayWardLocationAnalysis(data) {
  const section = document.getElementById("wardLocationSection");
  section.style.display = "block";

  const query = data.query || {};
  const exact = data.exact || {};
  const monthly = data.monthly || {};
  const hasExactData = data.has_exact_data;

  // Use exact if available, otherwise monthly
  const dataToDisplay = hasExactData ? exact : monthly;
  const ward = query.ward || "Unknown";
  const location = query.location || "Unknown";

  const totalAccidents = dataToDisplay.total || 0;
  const highCount = dataToDisplay.high || 0;
  const lowCount = dataToDisplay.low || 0;
  const highPct = dataToDisplay.high_pct || 0;

  document.getElementById("wardLocationLabel").textContent =
    `Ward ${ward} + ${location.toUpperCase()} ${hasExactData ? "(Exact)" : "(Monthly)"}`;
  document.getElementById("wardLocationTotal").textContent = totalAccidents;
  document.getElementById("wardLocationHigh").textContent = highCount;
  document.getElementById("wardLocationLow").textContent = lowCount;
  document.getElementById("wardLocationHighPct").textContent = `${highPct}%`;

  // Get injuries from monthly data (ward+location overall)
  if (totalAccidents > 0) {
    const injuries =
      data.monthly && data.monthly.injury_stats
        ? data.monthly.injury_stats
        : {};
    document.getElementById("wardLocationMinorInjuries").textContent =
      injuries.total_minor_injuries || injuries.minor_injuries || 0;
    document.getElementById("wardLocationSevereInjuries").textContent =
      injuries.total_severe_injuries || injuries.severe_injuries || 0;
    document.getElementById("wardLocationDeaths").textContent =
      injuries.total_deaths || injuries.deaths || 0;
  } else {
    document.getElementById("wardLocationMinorInjuries").textContent = "0";
    document.getElementById("wardLocationSevereInjuries").textContent = "0";
    document.getElementById("wardLocationDeaths").textContent = "0";
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

console.log("✓ API Integration loaded (Hierarchical 3-level analysis)");
console.log("✓ Backend API: " + API_BASE_URL);
