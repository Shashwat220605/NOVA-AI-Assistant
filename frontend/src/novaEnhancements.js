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

async function pressToTalkStop() {
  if (!pressing) return;
  pressing = false;
  document.body.classList.remove("nova-ptt-active");
  await post("/stop");
}

function installPushToTalk() {
  const button = document.querySelector(".listen-button");
  if (!button || button.dataset.pttReady === "true") return;
  button.dataset.pttReady = "true";
  button.title = "Hold to talk. Release to stop. Space also works while the page is focused.";

  button.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    pressToTalkStart();
  });
  button.addEventListener("pointerup", (event) => {
    event.preventDefault();
    pressToTalkStop();
  });
  button.addEventListener("pointercancel", pressToTalkStop);
  button.addEventListener("pointerleave", (event) => {
    if (event.buttons) pressToTalkStop();
  });
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  }, true);
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
    pressToTalkStop();
  });
  window.addEventListener("pointerup", pressToTalkStop);
  window.addEventListener("blur", pressToTalkStop);
}

async function refreshReactiveState() {
  try {
    const response = await fetch(`${API}/state`);
    if (!response.ok) return;
    const data = await response.json();
    document.body.dataset.novaState = data.state || "idle";
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

export { pressToTalkStart, pressToTalkStop };
