const API = "http://127.0.0.1:8000";
let pressing = false;

async function post(path) {
  try {
    const response = await fetch(`${API}${path}`, { method: "POST" });
    return await response.json();
  } catch (error) {
    console.error("NOVA enhancement request failed:", error);
    return null;
  }
}

async function pressToTalkStart() {
  if (pressing) return;
  pressing = true;
  document.body.classList.add("nova-ptt-active");
  await post("/listen");
}

function pressToTalkRelease() {
  pressing = false;
  document.body.classList.remove("nova-ptt-active");
}

function installPushToTalk() {
  const button = document.querySelector(".listen-button");
  if (!button || button.dataset.pttReady === "true") return;
  button.dataset.pttReady = "true";
  button.title = "Press to talk. NOVA listens in a short bounded window and then processes your command.";
  button.addEventListener("pointerdown", (event) => { event.preventDefault(); pressToTalkStart(); });
  button.addEventListener("pointerup", (event) => { event.preventDefault(); pressToTalkRelease(); });
  button.addEventListener("pointercancel", pressToTalkRelease);
  button.addEventListener("pointerleave", (event) => { if (event.buttons) pressToTalkRelease(); });
  button.addEventListener("click", (event) => { event.preventDefault(); event.stopPropagation(); }, true);
}

function installKeyboardPushToTalk() {
  window.addEventListener("keydown", (event) => {
    if (event.code !== "Space" || event.repeat) return;
    const tag = document.activeElement?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "BUTTON") return;
    event.preventDefault();
    pressToTalkStart();
  });
  window.addEventListener("keyup", (event) => {
    if (event.code !== "Space") return;
    const tag = document.activeElement?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "BUTTON") return;
    event.preventDefault();
    pressToTalkRelease();
  });
  window.addEventListener("blur", pressToTalkRelease);
}

function renderConfirmation(data) {
  let overlay = document.querySelector(".nova-confirmation");
  const confirmation = data.confirmation;
  if (data.state !== "confirmation" || !confirmation) {
    overlay?.remove();
    return;
  }

  if (!overlay) {
    overlay = document.createElement("div");
    overlay.className = "nova-confirmation";
    overlay.innerHTML = `
      <div class="nova-confirmation-card">
        <div class="nova-confirmation-kicker">NOVA // PERMISSION REQUEST</div>
        <div class="nova-confirmation-icon">!</div>
        <div class="nova-confirmation-title">CONFIRM ACTION</div>
        <div class="nova-confirmation-label"></div>
        <div class="nova-confirmation-warning">This action requires your approval before NOVA can execute it.</div>
        <div class="nova-confirmation-actions">
          <button class="nova-confirm nova-confirm-yes">CONFIRM</button>
          <button class="nova-confirm nova-confirm-no">CANCEL</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    overlay.querySelector(".nova-confirm-yes").addEventListener("click", async () => {
      await post("/confirm");
      await refreshReactiveState();
    });
    overlay.querySelector(".nova-confirm-no").addEventListener("click", async () => {
      await post("/cancel");
      await refreshReactiveState();
    });
  }
  overlay.querySelector(".nova-confirmation-label").textContent = confirmation.label || "Protected desktop action";
}

async function refreshReactiveState() {
  try {
    const response = await fetch(`${API}/state`);
    if (!response.ok) return;
    const data = await response.json();
    document.body.dataset.novaState = data.state || "idle";
    renderConfirmation(data);
  } catch {
    // The main React app already reports backend connectivity problems.
  }
}

function boot() {
  installPushToTalk();
  installKeyboardPushToTalk();
  refreshReactiveState();
  window.setInterval(refreshReactiveState, 600);
  const observer = new MutationObserver(installPushToTalk);
  observer.observe(document.body, { childList: true, subtree: true });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot, { once: true });
} else {
  boot();
}

export { pressToTalkStart, pressToTalkRelease };
