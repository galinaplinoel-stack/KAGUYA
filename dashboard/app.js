// KAGUYA Dashboard — Real-time personality visualization
const API_BASE = window.location.origin;
const WS_BASE = `ws://${window.location.host}`;
let ws = null;
let timeline = [];

const EMOTION_ICONS = {
    joy: "😊", sadness: "😢", anger: "😠", fear: "😨",
    surprise: "😲", disgust: "🤢", trust: "🤝", anticipation: "🤔",
    neutral: "😐",
};

function connect(profileId = "default") {
    if (ws) ws.close();
    try {
        ws = new WebSocket(`${WS_BASE}/ws/${profileId}`);
        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            updateDashboard(data);
        };
        ws.onclose = () => setTimeout(() => connect(profileId), 3000);
        ws.onerror = () => {};
    } catch(e) {
        setTimeout(() => connect(profileId), 3000);
    }
}

function updateDashboard(data) {
    // Update emotion
    const emo = data.emotion;
    document.getElementById("emotion-icon").textContent = EMOTION_ICONS[emo.primary] || "😐";
    document.getElementById("emotion-name").textContent = emo.primary;
    document.getElementById("intensity-fill").style.width = `${emo.intensity * 100}%`;
    document.getElementById("intensity-value").textContent = `${Math.round(emo.intensity * 100)}%`;

    // Valence & Arousal
    const vFill = document.getElementById("valence-fill");
    vFill.style.width = `${((emo.valence + 1) / 2) * 100}%`;
    document.getElementById("arousal-fill").style.width = `${emo.arousal * 100}%`;

    // Tone
    if (data.tone) {
        Object.entries(data.tone).forEach(([key, val]) => {
            const el = document.getElementById(`tone-${key}`);
            if (el) el.textContent = `${Math.round(val * 100)}%`;
        });
    }

    // Trait bars
    if (data.traits) {
        const container = document.getElementById("trait-bars");
        container.innerHTML = Object.entries(data.traits)
            .map(([name, val]) => `
                <div class="trait-bar">
                    <label><span>${name}</span><span>${Math.round(val * 100)}%</span></label>
                    <div class="bar"><div class="fill" style="width:${val * 100}%"></div></div>
                </div>
            `).join("");
    }

    // Timeline
    timeline.push({ time: Date.now(), valence: emo.valence, arousal: emo.arousal });
    if (timeline.length > 50) timeline.shift();
    drawTimeline();
}

function drawTimeline() {
    const canvas = document.getElementById("timeline-chart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    if (timeline.length < 2) return;

    // Draw valence line
    ctx.strokeStyle = "#7c5cff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    timeline.forEach((p, i) => {
        const x = (i / (timeline.length - 1)) * w;
        const y = h / 2 - (p.valence * h / 4);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Draw arousal line
    ctx.strokeStyle = "#ff5caa";
    ctx.beginPath();
    timeline.forEach((p, i) => {
        const x = (i / (timeline.length - 1)) * w;
        const y = h - (p.arousal * h * 0.8);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Legend
    ctx.font = "11px sans-serif";
    ctx.fillStyle = "#7c5cff";
    ctx.fillText("— Valence", 10, 15);
    ctx.fillStyle = "#ff5caa";
    ctx.fillText("— Arousal", 80, 15);
}

// Init
connect();
