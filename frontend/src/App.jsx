import { Canvas, useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { useEffect, useRef, useState } from "react";
import "./App.css";

function NovaCore({ state }) {
  const core = useRef();
  const ring1 = useRef(); const ring2 = useRef(); const ring3 = useRef();
  const field1 = useRef(); const field2 = useRef(); const field3 = useRef();
  const pulseRing = useRef(); const shardRing = useRef();
  const shock = useRef();

  useFrame((scene, delta) => {
    const time = scene.clock.elapsedTime;
    if (!core.current) return;
    const profiles = {
      idle: { r: .22, p: 1.0, a: .018, f: .12, s: 1 },
      listening: { r: .7, p: 3.5, a: .085, f: .85, s: 1.08 },
      thinking: { r: 1.25, p: 5.5, a: .12, f: 1.5, s: 1.13 },
      speaking: { r: .9, p: 7, a: .15, f: 1.1, s: 1.04 },
      executing: { r: 1.6, p: 8, a: .17, f: 2.1, s: 1.16 },
      confirmation: { r: .55, p: 2.5, a: .08, f: .55, s: 1.1 },
      success: { r: 1.0, p: 10, a: .2, f: 1.8, s: 1.08 },
      error: { r: 1.8, p: 13, a: .18, f: 2.5, s: 1.05 },
    };
    const profile = profiles[state] || profiles.idle;
    core.current.rotation.x += delta * profile.r;
    core.current.rotation.y += delta * profile.r * 1.35;
    const pulse = 1 + Math.sin(time * profile.p) * profile.a;
    core.current.scale.setScalar(pulse);

    [[ring1, 1, .35], [ring2, -.7, .4], [ring3, .5, .5], [pulseRing, .8, .2], [shardRing, -.6, .7]].forEach(([ref, speed, z]) => {
      if (!ref.current) return;
      ref.current.rotation.x += delta * profile.r * speed;
      ref.current.rotation.y += delta * profile.r * z;
      ref.current.rotation.z += delta * profile.r * .25;
    });
    [[field1, 1, .2], [field2, -.7, .4], [field3, .5, .3]].forEach(([ref, speed, z]) => {
      if (!ref.current) return;
      ref.current.rotation.y += delta * profile.f * speed;
      ref.current.rotation.x += delta * profile.f * z;
      ref.current.scale.setScalar(profile.s + Math.sin(time * 2 + z) * .025);
    });

    if (shock.current) {
      const active = state === "success" || state === "error";
      const phase = (time % 1.15) / 1.15;
      shock.current.scale.setScalar(active ? .8 + phase * 1.8 : .001);
      shock.current.material.opacity = active ? (1 - phase) * .45 : 0;
    }
  });

  return <group>
    <points ref={field1}><sphereGeometry args={[2.8, 18, 18]} /><pointsMaterial color="#00d9ff" size={.035} transparent opacity={.68} sizeAttenuation /></points>
    <points ref={field2}><sphereGeometry args={[3.45, 15, 15]} /><pointsMaterial color="#725cff" size={.024} transparent opacity={.45} sizeAttenuation /></points>
    <points ref={field3}><sphereGeometry args={[4.05, 11, 11]} /><pointsMaterial color="#00aaff" size={.017} transparent opacity={.28} sizeAttenuation /></points>

    <mesh ref={core}><icosahedronGeometry args={[1.25, 2]} /><meshStandardMaterial color="#0cecff" emissive="#006eff" emissiveIntensity={3.2} metalness={.86} roughness={.16} /></mesh>
    <mesh scale={.58}><sphereGeometry args={[1, 28, 28]} /><meshBasicMaterial color="#ffffff" transparent opacity={.92} /></mesh>

    <mesh ref={ring1} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[1.75, .025, 10, 64]} /><meshBasicMaterial color="#00e5ff" /></mesh>
    <mesh ref={ring2} rotation={[.7, .4, 0]}><torusGeometry args={[2.05, .018, 10, 64]} /><meshBasicMaterial color="#7c5cff" /></mesh>
    <mesh ref={ring3} rotation={[1.1, .2, .5]}><torusGeometry args={[2.35, .012, 8, 56]} /><meshBasicMaterial color="#008cff" transparent opacity={.58} /></mesh>
    <mesh ref={pulseRing} rotation={[.35, .9, 0]}><torusGeometry args={[2.65, .009, 8, 56]} /><meshBasicMaterial color="#00d9ff" transparent opacity={.4} /></mesh>
    <mesh ref={shardRing} rotation={[1.7, .2, .8]}><torusGeometry args={[2.9, .006, 6, 48]} /><meshBasicMaterial color="#9a7cff" transparent opacity={.3} /></mesh>

    <mesh ref={shock}><torusGeometry args={[1.35, .018, 8, 64]} /><meshBasicMaterial color="#ffffff" transparent opacity={0} /></mesh>
    <pointLight position={[0, 0, 2]} intensity={20} color="#00e5ff" />
    <pointLight position={[2, 2, -2]} intensity={9} color="#684cff" />
  </group>;
}

function TelemetryBar({ value }) {
  return <div className="telemetry-bar"><div className="telemetry-bar-fill" style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }} /></div>;
}

function SystemTelemetry({ telemetry }) {
  if (!telemetry) return <aside className="telemetry-panel"><div className="telemetry-header"><span>SYSTEM TELEMETRY</span><span className="telemetry-live">● LIVE</span></div><div className="telemetry-loading">INITIALIZING...</div></aside>;
  return <aside className="telemetry-panel">
    <div className="telemetry-header"><span>SYSTEM TELEMETRY</span><span className="telemetry-live">● LIVE</span></div>
    <div className="telemetry-section"><div className="telemetry-section-title">MEMORY</div><div className="telemetry-name">{telemetry.ram.total} GB RAM</div><TelemetryBar value={telemetry.ram.percent} /><div className="telemetry-values"><span>{telemetry.ram.used} GB USED</span><span>{telemetry.ram.available} GB FREE</span></div></div>
    <div className="telemetry-section"><div className="telemetry-section-title">STORAGE</div><div className="telemetry-name">{telemetry.storage.drive}</div><TelemetryBar value={telemetry.storage.percent} /><div className="telemetry-values"><span>{telemetry.storage.used} GB USED</span><span>{telemetry.storage.free} GB FREE</span></div></div>
    <div className="telemetry-section"><div className="telemetry-section-title">CPU</div><div className="telemetry-name telemetry-truncate">{telemetry.cpu.name}</div><TelemetryBar value={telemetry.cpu.percent} /><div className="telemetry-values"><span>USAGE</span><span>{telemetry.cpu.percent}%</span></div></div>
    <div className="telemetry-section"><div className="telemetry-section-title">GPU</div><div className="telemetry-name telemetry-truncate">{telemetry.gpu.name}</div><div className="telemetry-values"><span>{telemetry.gpu.percent ?? 0}% LOAD</span><span>{telemetry.gpu.temperature != null ? `${telemetry.gpu.temperature}°C` : "TEMP N/A"}</span></div></div>
    <div className="telemetry-values"><span>VRAM</span><span>{telemetry.gpu.vram_used ?? 0}/{telemetry.gpu.vram_total ?? 0} MB</span></div>
    <div className="telemetry-values"><span>NET ↓ {telemetry.network?.download_kbps ?? 0} KB/s</span><span>↑ {telemetry.network?.upload_kbps ?? 0} KB/s</span></div>
    <div className="telemetry-values"><span>BATTERY</span><span>{telemetry.battery?.percent ?? "N/A"}% {telemetry.battery?.plugged ? "⚡" : ""}</span></div>
    <div className="telemetry-system">{telemetry.system.name}</div>
  </aside>;
}

function ConversationHUD({ conversation }) {
  return <div className="conversation-hud"><div className="hud-header"><div className="hud-title">NOVA // CONVERSATION</div><div className="hud-line" /><div className="hud-live">LIVE</div></div><div className="conversation-content">
    {conversation.length === 0 ? <div className="conversation-empty"><div className="empty-symbol">◉</div><div>WAITING FOR CONVERSATION</div></div> : conversation.map((item, index) => <div className={`conversation-item ${item.role}`} key={`${item.role}-${index}`}><div className="conversation-role">{item.role === "user" ? "YOU" : "NOVA"}</div><div className="conversation-text">{item.text}</div></div>)}
  </div></div>;
}

function App() {
  const [nova, setNova] = useState({ state: "idle", message: "How can I help you?" });
  const [conversation, setConversation] = useState([]);
  const [telemetry, setTelemetry] = useState(null);
  const [startingVoice, setStartingVoice] = useState(false);

  useEffect(() => {
    const getState = async () => { try { const response = await fetch("http://127.0.0.1:8000/state"); if (!response.ok) throw new Error("State request failed"); setNova(await response.json()); } catch (error) { console.error("NOVA state error:", error); } };
    getState(); const interval = setInterval(getState, 500); return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let mounted = true;
    let last = null;
    const getTelemetry = async () => { try { const response = await fetch("http://127.0.0.1:8000/system"); if (!response.ok) throw new Error("Telemetry request failed"); const data = await response.json(); if (mounted) { setTelemetry(data); last = data; } } catch (error) { console.error("Telemetry error:", error); } };
    getTelemetry(); const interval = setInterval(getTelemetry, 3000); return () => { mounted = false; clearInterval(interval); };
  }, []);

  const startListening = async () => {
    if (startingVoice) return;
    try { setStartingVoice(true); const response = await fetch("http://127.0.0.1:8000/listen", { method: "POST" }); const data = await response.json(); if (!data.success) console.error("NOVA could not start:", data.message); }
    catch (error) { console.error("Could not activate NOVA:", error); } finally { setStartingVoice(false); }
  };

  const stateLabels = { idle: "READY", listening: "LISTENING", thinking: "THINKING", speaking: "SPEAKING", executing: "EXECUTING", success: "SUCCESS", error: "ERROR", confirmation: "CONFIRM" };
  const displayState = stateLabels[nova.state] || "READY";

  return <main className="nova-app">
    <div className="nova-background"><div className="nova-grid" /><div className="nova-vignette" /></div>
    <header className="nova-header"><div className="nova-brand"><span className="brand-mark">N</span><div><div className="brand-title">NOVA</div><div className="brand-subtitle">NEURAL OPERATIONS & VOICE ASSISTANT</div></div></div><div className={`nova-status status-${nova.state}`}><span className="status-dot" />{displayState}</div></header>
    <section className="nova-main">
      <aside className="nova-left"><SystemTelemetry telemetry={telemetry} /></aside>
      <section className="nova-center">
        <div className="core-scene"><Canvas camera={{ position: [0, 0, 7], fov: 48 }} dpr={[1, 1.5]} gl={{ antialias: true, powerPreference: "high-performance" }}><color attach="background" args={["#02070d"]} /><Stars radius={80} depth={40} count={700} factor={2} saturation={0} fade speed={0.35} /><NovaCore state={nova.state} /></Canvas></div>
        <div className="core-readout"><div className="core-label">{displayState}</div><div className="core-message">{nova.message}</div></div>
        <button className={`listen-button ${startingVoice ? "starting" : ""}`} onClick={startListening}>{startingVoice ? "INITIALIZING..." : "ACTIVATE NOVA"}</button>
      </section>
      <aside className="nova-right"><ConversationHUD conversation={conversation} /></aside>
    </section>
    <footer className="nova-footer"><span>NOVA CORE 2.0</span><span>LOCAL CONTROL ACTIVE</span><span>GEMINI LINK ONLINE</span></footer>
  </main>;
}

export default App;
