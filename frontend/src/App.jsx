import { Canvas, useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { useEffect, useRef, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function NovaCore({ state }) {
  const core = useRef();
  const rings = [useRef(), useRef(), useRef(), useRef(), useRef()];
  const fields = [useRef(), useRef(), useRef()];
  const shock = useRef();

  useFrame((scene, delta) => {
    const time = scene.clock.elapsedTime;
    if (!core.current) return;
    const profiles = {
      idle: { speed: 0.28, pulse: 0.018, frequency: 1.2, scale: 1 },
      listening: { speed: 0.75, pulse: 0.08, frequency: 4, scale: 1.04 },
      thinking: { speed: 1.15, pulse: 0.12, frequency: 6, scale: 1.08 },
      speaking: { speed: 0.95, pulse: 0.1, frequency: 7, scale: 1.05 },
      executing: { speed: 1.45, pulse: 0.15, frequency: 9, scale: 1.11 },
      confirmation: { speed: 0.55, pulse: 0.07, frequency: 2.5, scale: 1.03 },
      success: { speed: 1.1, pulse: 0.2, frequency: 11, scale: 1.08 },
      error: { speed: 1.25, pulse: 0.18, frequency: 13, scale: 1.06 },
    };
    const profile = profiles[state] || profiles.idle;
    core.current.rotation.x += delta * profile.speed;
    core.current.rotation.y += delta * profile.speed * 1.35;
    core.current.rotation.z += delta * profile.speed * 0.25;
    core.current.scale.setScalar(profile.scale + Math.sin(time * profile.frequency) * profile.pulse);
    rings.forEach((ring, index) => {
      if (!ring.current) return;
      ring.current.rotation.x += delta * profile.speed * (index % 2 ? -0.7 : 0.55);
      ring.current.rotation.y += delta * profile.speed * (0.25 + index * 0.12);
      ring.current.rotation.z += delta * profile.speed * 0.16;
    });
    fields.forEach((field, index) => {
      if (!field.current) return;
      field.current.rotation.y += delta * profile.speed * (0.35 + index * 0.2);
      field.current.rotation.x += delta * profile.speed * (index % 2 ? -0.12 : 0.16);
    });
    if (shock.current) {
      const active = state === "success" || state === "error";
      const phase = (time % 1.15) / 1.15;
      shock.current.scale.setScalar(active ? 0.6 + phase * 2.2 : 0.001);
      shock.current.material.opacity = active ? (1 - phase) * 0.5 : 0;
    }
  });

  return <group>
    <points ref={fields[0]}><sphereGeometry args={[2.7, 16, 16]} /><pointsMaterial color="#00d9ff" size={0.032} transparent opacity={0.62} /></points>
    <points ref={fields[1]}><sphereGeometry args={[3.35, 14, 14]} /><pointsMaterial color="#765cff" size={0.022} transparent opacity={0.42} /></points>
    <points ref={fields[2]}><sphereGeometry args={[3.95, 10, 10]} /><pointsMaterial color="#00aaff" size={0.015} transparent opacity={0.25} /></points>
    <mesh ref={core}><icosahedronGeometry args={[1.18, 2]} /><meshStandardMaterial color="#9feaff" emissive="#007cff" emissiveIntensity={3.5} metalness={0.88} roughness={0.14} /></mesh>
    <mesh scale={0.56}><sphereGeometry args={[1, 24, 24]} /><meshBasicMaterial color="#ffffff" transparent opacity={0.94} /></mesh>
    <mesh ref={rings[0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[1.65, 0.026, 8, 64]} /><meshBasicMaterial color="#00e5ff" /></mesh>
    <mesh ref={rings[1]} rotation={[0.7, 0.4, 0]}><torusGeometry args={[1.95, 0.018, 8, 64]} /><meshBasicMaterial color="#8a6aff" /></mesh>
    <mesh ref={rings[2]} rotation={[1.1, 0.2, 0.5]}><torusGeometry args={[2.25, 0.012, 8, 56]} /><meshBasicMaterial color="#008cff" transparent opacity={0.62} /></mesh>
    <mesh ref={rings[3]} rotation={[0.35, 0.9, 0]}><torusGeometry args={[2.58, 0.009, 8, 56]} /><meshBasicMaterial color="#00d9ff" transparent opacity={0.4} /></mesh>
    <mesh ref={rings[4]} rotation={[1.7, 0.2, 0.8]}><torusGeometry args={[2.86, 0.006, 6, 48]} /><meshBasicMaterial color="#9a7cff" transparent opacity={0.28} /></mesh>
    <mesh ref={shock}><torusGeometry args={[1.3, 0.02, 8, 64]} /><meshBasicMaterial color="#ffffff" transparent opacity={0} /></mesh>
    <pointLight position={[0, 0, 2]} intensity={18} color="#00e5ff" />
    <pointLight position={[2, 2, -2]} intensity={8} color="#684cff" />
  </group>;
}

function TelemetryBar({ value }) {
  return <div className="telemetry-bar"><div className="telemetry-bar-fill" style={{ width: `${Math.min(Math.max(value ?? 0, 0), 100)}%` }} /></div>;
}

function SystemTelemetry({ telemetry }) {
  if (!telemetry) return <aside className="panel telemetry-panel"><div className="panel-head"><span>SYSTEM TELEMETRY</span><b>OFFLINE</b></div><div className="telemetry-loading">INITIALIZING...</div></aside>;
  const gpu = telemetry.gpu || {};
  return <aside className="panel telemetry-panel">
    <div className="panel-head"><span>SYSTEM TELEMETRY</span><b>● LIVE</b></div>
    <section className="telemetry-block"><div className="block-label">MEMORY</div><div className="metric-line"><strong>{telemetry.ram.total} GB</strong><span>RAM</span></div><TelemetryBar value={telemetry.ram.percent} /><div className="metric-sub"><span>{telemetry.ram.used} GB USED</span><span>{telemetry.ram.available} GB FREE</span></div></section>
    <section className="telemetry-block"><div className="block-label">CPU</div><div className="metric-line"><strong>{telemetry.cpu.percent}%</strong><span>LOAD</span></div><TelemetryBar value={telemetry.cpu.percent} /><div className="metric-sub"><span>{telemetry.cpu.temperature_c != null ? `${telemetry.cpu.temperature_c}°C` : "TEMP N/A"}</span><span>CPU</span></div></section>
    <section className="telemetry-block"><div className="block-label">GPU</div><div className="metric-line"><strong>{gpu.percent ?? 0}%</strong><span>LOAD</span></div><TelemetryBar value={gpu.percent ?? 0} /><div className="metric-sub"><span>{gpu.temperature_c != null ? `${gpu.temperature_c}°C` : "TEMP N/A"}</span><span>GPU</span></div></section>
    <section className="telemetry-block"><div className="block-label">VRAM</div><div className="vram-readout"><strong>{gpu.vram_used_mb ?? 0}</strong><span>/ {gpu.vram_total_mb ?? 0} MB</span></div></section>
    <section className="telemetry-block"><div className="block-label">NETWORK</div><div className="metric-sub large"><span>↓ {telemetry.network?.download_kbps ?? 0} KB/s</span><span>↑ {telemetry.network?.upload_kbps ?? 0} KB/s</span></div></section>
    <section className="telemetry-block"><div className="block-label">BATTERY</div><div className="metric-line"><strong>{telemetry.battery?.percent ?? "--"}%</strong><span>{telemetry.battery?.plugged ? "CHARGING" : "BATTERY"}</span></div></section>
    <div className="panel-foot">{telemetry.system.name}</div>
  </aside>;
}

function ActivityHUD({ items }) {
  return <aside className="panel activity-panel">
    <div className="panel-head"><span>NOVA ACTIVITY</span><b>LIVE</b></div>
    <div className="activity-list">{items.length === 0 ? <div className="activity-empty"><span>◉</span><p>Awaiting command</p><small>Voice interactions will appear here</small></div> : items.map((item, index) => <div className="activity-item" key={`${item.time}-${index}`}><div className={`activity-dot ${item.type}`} /><div><time>{item.time}</time><p>{item.text}</p></div></div>)}</div>
  </aside>;
}

function App() {
  const [nova, setNova] = useState({ state: "idle", message: "Ready.", confirmation: null });
  const [telemetry, setTelemetry] = useState(null);
  const [startingVoice, setStartingVoice] = useState(false);
  const [activity, setActivity] = useState([]);

  const addActivity = (text, type = "info") => setActivity((old) => [{ time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }), text, type }, ...old].slice(0, 12));

  useEffect(() => {
    const getState = async () => { try { const response = await fetch(`${API}/state`); if (!response.ok) return; setNova(await response.json()); } catch {} };
    getState(); const interval = setInterval(getState, 500); return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let mounted = true;
    const getTelemetry = async () => { try { const response = await fetch(`${API}/system`); if (!response.ok) return; const data = await response.json(); if (mounted) setTelemetry(data); } catch {} };
    getTelemetry(); const interval = setInterval(getTelemetry, 3000); return () => { mounted = false; clearInterval(interval); };
  }, []);

  useEffect(() => {
    const onKeyDown = (event) => { if (event.code !== "Space" || event.repeat) return; const tag = document.activeElement?.tagName; if (["INPUT", "TEXTAREA", "BUTTON"].includes(tag)) return; event.preventDefault(); startListening(); };
    window.addEventListener("keydown", onKeyDown); return () => window.removeEventListener("keydown", onKeyDown);
  });

  useEffect(() => {
    if (nova.message && nova.message !== "Ready.") {
      const type = nova.state === "error" ? "error" : nova.state === "success" ? "success" : nova.state === "executing" ? "action" : "info";
      setActivity((old) => old[0]?.text === nova.message ? old : [{ time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }), text: nova.message, type }, ...old].slice(0, 12));
    }
  }, [nova.message, nova.state]);

  async function startListening() {
    if (startingVoice) return;
    setStartingVoice(true); addActivity("Activating voice engine...", "action");
    try {
      const response = await fetch(`${API}/listen`, { method: "POST" });
      const data = await response.json();
      if (!data.success) { setNova((old) => ({ ...old, state: "error", message: data.message || "Voice engine could not start." })); addActivity(data.message || "Voice engine could not start.", "error"); }
      else addActivity("Voice engine online. Listening...", "success");
    } catch { setNova((old) => ({ ...old, state: "error", message: "Cannot reach NOVA backend." })); addActivity("Cannot reach NOVA backend.", "error"); }
    finally { setStartingVoice(false); }
  }

  async function confirmAction() { const response = await fetch(`${API}/confirm`, { method: "POST" }); const data = await response.json(); addActivity(data.message || "Action confirmed.", data.success ? "success" : "error"); }
  async function cancelAction() { await fetch(`${API}/cancel`, { method: "POST" }); addActivity("Action cancelled.", "info"); }

  const stateLabels = { idle: "READY", listening: "LISTENING", thinking: "THINKING", speaking: "SPEAKING", executing: "EXECUTING", success: "SUCCESS", error: "ERROR", confirmation: "CONFIRMATION" };
  const displayState = stateLabels[nova.state] || "READY";

  return <main className="nova-app" data-state={nova.state}>
    <div className="nova-background"><div className="nova-grid" /><div className="nova-scanlines" /><div className="nova-vignette" /></div>
    <header className="nova-header">
      <div className="brand"><div className="brand-orb">N</div><div><h1>NOVA</h1><p>NEURAL OPERATIONS & VOICE ASSISTANT</p></div></div>
      <div className={`status-pill status-${nova.state}`}><span />{displayState}</div>
      <div className="header-meta"><span>LOCAL CONTROL</span><i /> <span>GEMINI LINK</span><i className="live-dot" /></div>
    </header>
    <section className="nova-layout">
      <SystemTelemetry telemetry={telemetry} />
      <section className="core-column">
        <div className="core-topline"><span>CORE 2.0</span><div /><span>HIGH PERFORMANCE MODE</span></div>
        <div className="core-frame"><div className="core-corner tl" /><div className="core-corner tr" /><div className="core-corner bl" /><div className="core-corner br" /><Canvas camera={{ position: [0, 0, 7], fov: 46 }} dpr={[1, 1.35]} gl={{ antialias: true, powerPreference: "high-performance" }}><color attach="background" args={["#02070d"]} /><Stars radius={65} depth={35} count={500} factor={1.7} saturation={0} fade speed={0.25} /><NovaCore state={nova.state} /></Canvas><div className="core-scan" /></div>
        <div className="core-status"><span className="state-ring" /><strong>{displayState}</strong><span className="state-line" /></div>
        <p className="core-message">{nova.message}</p>
        <button className={`activate-button ${startingVoice ? "loading" : ""}`} onClick={startListening} disabled={startingVoice}><span>{startingVoice ? "INITIALIZING" : "ACTIVATE NOVA"}</span><kbd>SPACE</kbd></button>
      </section>
      <ActivityHUD items={activity} />
    </section>
    <footer className="nova-footer"><span>NOVA // DESKTOP AI</span><span>VOICE • AUTOMATION • TELEMETRY</span><span>v2.0</span></footer>
    {nova.confirmation && <div className="confirm-overlay"><div className="confirm-card"><div className="confirm-kicker">NOVA // PERMISSION REQUEST</div><div className="confirm-icon">!</div><h2>CONFIRM ACTION</h2><p className="confirm-label">{nova.confirmation.label}</p><p className="confirm-warning">This action requires your approval before NOVA can execute it.</p><div className="confirm-actions"><button onClick={confirmAction}>CONFIRM</button><button className="cancel" onClick={cancelAction}>CANCEL</button></div></div></div>}
  </main>;
}

export default App;
