/**
 * Frontend-Backend Integration for TrafficSafe Biratnagar
 * Connects home.html UI to the Python Flask backend API
 * This file overrides the analyzeRisk function to use real backend data
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
 * Main analyze function - overrides the original in home.html
 * Calls backend /api/risk-assessment endpoint
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
    // Normalize inputs - strip whitespace and lowercase for comparison with backend
    const normalizedLocation = location.toLowerCase().trim();
    const normalizedRoadType = roadType.toLowerCase().trim();

    // Prepare request body
    const requestBody = {
      ward: parseInt(ward),
      location: normalizedLocation,
      month: parseInt(month),
      time_slot: timeSlot,
      road_type: normalizedRoadType,
    };

    // Show loading state
    const placeholder = document.getElementById("placeholder");
    const resultContent = document.getElementById("resultContent");

    // Call backend API
    const response = await fetch(`${API_BASE_URL}/risk-assessment`, {
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

    console.log("✅ Risk Assessment Success:", data);
    console.log("Risk Score:", data.score);
    console.log("Total Accidents Found:", data.total_accidents);
    console.log("Location Query:", data.query);

    // Process and display results
    setTimeout(() => {
      // Hide loading state
      btn.classList.remove("loading");
      btn.querySelector("span").textContent = "▶ Run Risk Analysis";
      btn.disabled = false;

      // Hide placeholder, show results
      placeholder.style.display = "none";
      resultContent.style.display = "flex";

      // Animate gauge
      animGauge(data.score);

      // Update score display
      const scoreNum = document.getElementById("scoreNum");
      scoreNum.style.color = data.risk_color;

      // Update risk chip
      const chip = document.getElementById("riskChip");
      chip.innerHTML = `<div class="chip-dot"></div><span>${data.risk_label}</span>`;
      chip.className = `risk-chip ${data.risk_level}`;

      // Update weather cells with actual data
      const factorValues = data.factor_values || {};

      document.getElementById("wWard").textContent =
        `${factorValues["Ward / Location Zone"] || 0}/20`;
      document.getElementById("wWard").style.color = getColorForValue(
        factorValues["Ward / Location Zone"] || 0,
        20,
      );

      document.getElementById("wSeason").textContent =
        `${factorValues["Seasonal Pattern"] || 0}/22`;
      document.getElementById("wSeason").style.color = getColorForValue(
        factorValues["Seasonal Pattern"] || 0,
        22,
      );

      document.getElementById("wTime").textContent =
        `${factorValues["Time of Day"] || 0}/20`;
      document.getElementById("wTime").style.color = getColorForValue(
        factorValues["Time of Day"] || 0,
        20,
      );

      document.getElementById("wWeather").textContent = "Standard";
      document.getElementById("wWeather").style.color = "#00d2ff";

      // Build factor bars from backend data
      buildFactorsFromBackend(data);

      // Build insights from backend data
      buildInsightsFromBackend(data);

      // Build comparison from backend data
      buildCompareFromBackend(data);

      // Show factors tab by default
      showTab("factors");
    }, 1200);
  } catch (error) {
    // Error handling
    btn.classList.remove("loading");
    btn.querySelector("span").textContent = "▶ Run Risk Analysis";
    btn.disabled = false;

    console.error("❌ Analysis Error:", error);
    console.error("Request was sent:", requestBody);
    alert(
      `Error: ${error.message}\n\nMake sure:\n1. Backend is running (python run_server.py)\n2. Backend is on http://localhost:5000\n3. Location exists in database (e.g., 'rani', 'oil nigam', 'traffic chowk')\n4. Road type is valid (highway, inner paved road, inner unpaved road)\n\nCheck browser console for details.`,
    );
  }
}

/**
 * Get color based on value and max
 */
function getColorForValue(value, max) {
  const percent = value / max;
  if (percent > 0.75) return "#ff2d4e"; // red
  if (percent > 0.5) return "#ff8c42"; // orange
  return "#00d2ff"; // cyan
}

/**
 * Build factor bars from backend data
 */
function buildFactorsFromBackend(data) {
  const factorPercents = data.factors || {};
  const factorValues = data.factor_values || {};

  const factors = [
    { name: "Ward / Location Zone", color: "#00d2ff" },
    { name: "Seasonal Pattern", color: "#ff8c42" },
    { name: "Time of Day", color: "#ff2d4e" },
    { name: "Road Type", color: "#00e5a0" },
  ];

  const el = document.getElementById("factorBars");
  el.innerHTML = "";

  factors.forEach((f) => {
    const pct = factorPercents[f.name] || 0;
    const val = factorValues[f.name] || 0;

    el.innerHTML += `
            <div class="factor-item">
                <div class="factor-top">
                    <div class="factor-name">${f.name}</div>
                    <div class="factor-pct" style="color:${f.color}">${pct}%</div>
                </div>
                <div class="factor-track">
                    <div class="factor-fill" style="background:${f.color};color:${f.color}" data-val="${pct}"></div>
                </div>
            </div>`;
  });

  // Animate bars
  setTimeout(() => {
    document.querySelectorAll(".factor-fill").forEach((e) => {
      e.style.width = e.dataset.val + "%";
    });
  }, 50);
}

/**
 * Build insights from backend data
 */
function buildInsightsFromBackend(data) {
  const insights = data.insights || [];
  const el = document.getElementById("insightList");
  el.innerHTML = "";

  insights.forEach((insight) => {
    el.innerHTML += `
            <div class="insight-item ${insight.type}">
                <div class="insight-icon">${insight.icon}</div>
                <div class="insight-text">${insight.text}</div>
            </div>`;
  });
}

/**
 * Build comparison from backend data
 */
function buildCompareFromBackend(data) {
  const comp = data.comparison || {};
  const query = data.query || {};

  const el = document.getElementById("compareContent");
  el.innerHTML = `
        <div class="sys-info" style="margin-bottom:0.75rem">
            <div class="sys-row">
                <span>YOUR SCORE</span>
                <em style="color:${data.risk_color}">${data.score} / 100</em>
            </div>
            <div class="sys-row">
                <span>CITY AVERAGE</span>
                <em>${comp.city_average || 58} / 100</em>
            </div>
            <div class="sys-row">
                <span>DIFFERENCE</span>
                <em style="color:${comp.above_average ? "#ff2d4e" : "#00e5a0"}">
                    ${comp.difference > 0 ? "+" : ""}${comp.difference} vs CITY AVG
                </em>
            </div>
            <div class="sys-row">
                <span>TOTAL INCIDENTS</span>
                <em>${data.total_accidents || 0} records</em>
            </div>
            <div class="sys-row">
                <span>LOCATION</span>
                <em>${query.location || "-"} (Ward ${query.ward || "-"})</em>
            </div>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.57rem;letter-spacing:1.5px;color:var(--muted2);line-height:2">
            ${comp.comparison_text || ""}
        </div>`;
}

/**
 * Initialize - load form options from backend when page loads
 */
async function initializeForm() {
  try {
    const response = await fetch(`${API_BASE_URL}/options`);
    if (response.ok) {
      const options = await response.json();

      // Populate locations dropdown if available
      // Note: The current form has location as a text input, so this is just for reference
      console.log("Available locations:", options.locations);
      console.log("Available wards:", options.wards);
    } else {
      console.warn("Could not load form options from backend");
    }
  } catch (error) {
    console.warn("Form initialization warning:", error.message);
    // Continue anyway - form has hardcoded options
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

console.log("✓ API Integration loaded. Backend API: " + API_BASE_URL);
