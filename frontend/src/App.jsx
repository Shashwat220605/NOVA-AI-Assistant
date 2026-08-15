import { Canvas, useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { useEffect, useRef, useState } from "react";
import "./App.css";


/* =========================================================
   NOVA 3D CORE
========================================================= */

function NovaCore({ state }) {

  const core = useRef();
  const ring1 = useRef();
  const ring2 = useRef();
  const ring3 = useRef();

  const field1 = useRef();
  const field2 = useRef();
  const field3 = useRef();


  useFrame((scene, delta) => {

    const time =
      scene.clock.elapsedTime;


    if (!core.current) return;


    let rotation = 0.25;
    let pulseSpeed = 1.2;
    let pulseAmount = 0.025;
    let fieldSpeed = 0.15;
    let fieldScale = 1;


    if (state === "listening") {

      rotation = 0.7;
      pulseSpeed = 3;
      pulseAmount = 0.09;
      fieldSpeed = 0.8;
      fieldScale = 1.08;

    }


    if (state === "thinking") {

      rotation = 1.3;
      pulseSpeed = 5;
      pulseAmount = 0.13;
      fieldSpeed = 1.5;
      fieldScale = 1.15;

    }


    if (state === "speaking") {

      rotation = 0.8;
      pulseSpeed = 7;
      pulseAmount = 0.16;
      fieldSpeed = 1;
      fieldScale =
        1 + Math.sin(time * 7) * 0.08;

    }


    core.current.rotation.x +=
      delta * rotation;

    core.current.rotation.y +=
      delta * rotation * 1.4;


    const pulse =
      1 +
      Math.sin(
        time * pulseSpeed
      ) *
      pulseAmount;


    core.current.scale.set(
      pulse,
      pulse,
      pulse
    );


    if (ring1.current) {

      ring1.current.rotation.x +=
        delta * rotation;

      ring1.current.rotation.y +=
        delta * rotation * 0.4;

    }


    if (ring2.current) {

      ring2.current.rotation.z +=
        delta * rotation;

      ring2.current.rotation.x -=
        delta * rotation * 0.3;

    }


    if (ring3.current) {

      ring3.current.rotation.y +=
        delta * rotation * 0.5;

      ring3.current.rotation.z -=
        delta * rotation * 0.4;

    }


    if (field1.current) {

      field1.current.rotation.y +=
        delta * fieldSpeed;

      field1.current.rotation.x +=
        delta * fieldSpeed * 0.2;

      field1.current.scale.setScalar(
        fieldScale
      );

    }


    if (field2.current) {

      field2.current.rotation.x -=
        delta * fieldSpeed * 0.7;

      field2.current.rotation.z +=
        delta * fieldSpeed * 0.4;

      field2.current.scale.setScalar(
        fieldScale
      );

    }


    if (field3.current) {

      field3.current.rotation.z +=
        delta * fieldSpeed * 0.5;

      field3.current.rotation.y -=
        delta * fieldSpeed * 0.3;

      field3.current.scale.setScalar(
        fieldScale
      );

    }

  });


  return (

    <group>

      <points ref={field1}>

        <sphereGeometry
          args={[2.8, 20, 20]}
        />

        <pointsMaterial
          color="#00d9ff"
          size={0.035}
          transparent
          opacity={0.7}
          sizeAttenuation
        />

      </points>


      <points ref={field2}>

        <sphereGeometry
          args={[3.4, 16, 16]}
        />

        <pointsMaterial
          color="#587cff"
          size={0.025}
          transparent
          opacity={0.45}
          sizeAttenuation
        />

      </points>


      <points ref={field3}>

        <sphereGeometry
          args={[4, 12, 12]}
        />

        <pointsMaterial
          color="#00aaff"
          size={0.018}
          transparent
          opacity={0.3}
          sizeAttenuation
        />

      </points>


      <mesh ref={core}>

        <icosahedronGeometry
          args={[1.25, 3]}
        />

        <meshStandardMaterial
          color="#0cecff"
          emissive="#006eff"
          emissiveIntensity={2.5}
          metalness={0.85}
          roughness={0.18}
        />

      </mesh>


      <mesh scale={0.58}>

        <sphereGeometry
          args={[1, 32, 32]}
        />

        <meshBasicMaterial
          color="#ffffff"
          transparent
          opacity={0.9}
        />

      </mesh>


      <mesh
        ref={ring1}
        rotation={[
          Math.PI / 2,
          0,
          0
        ]}
      >

        <torusGeometry
          args={[
            1.75,
            0.025,
            12,
            80
          ]}
        />

        <meshBasicMaterial
          color="#00e5ff"
        />

      </mesh>


      <mesh
        ref={ring2}
        rotation={[
          0.7,
          0.4,
          0
        ]}
      >

        <torusGeometry
          args={[
            2.05,
            0.018,
            12,
            80
          ]}
        />

        <meshBasicMaterial
          color="#7c5cff"
        />

      </mesh>


      <mesh
        ref={ring3}
        rotation={[
          1.1,
          0.2,
          0.5
        ]}
      >

        <torusGeometry
          args={[
            2.35,
            0.012,
            10,
            70
          ]}
        />

        <meshBasicMaterial
          color="#008cff"
          transparent
          opacity={0.6}
        />

      </mesh>


      <pointLight
        position={[0, 0, 2]}
        intensity={18}
        color="#00e5ff"
      />

      <pointLight
        position={[2, 2, -2]}
        intensity={8}
        color="#684cff"
      />

    </group>

  );

}


/* =========================================================
   TELEMETRY BAR
========================================================= */

function TelemetryBar({
  value
}) {

  return (

    <div className="telemetry-bar">

      <div
        className="telemetry-bar-fill"
        style={{
          width: `${Math.min(
            Math.max(value, 0),
            100
          )}%`
        }}
      />

    </div>

  );

}


/* =========================================================
   SYSTEM TELEMETRY
========================================================= */

function SystemTelemetry({
  telemetry
}) {

  if (!telemetry) {

    return (

      <aside className="telemetry-panel">

        <div className="telemetry-header">

          <span>
            SYSTEM TELEMETRY
          </span>

          <span className="telemetry-live">
            ● LIVE
          </span>

        </div>

        <div className="telemetry-loading">
          INITIALIZING...
        </div>

      </aside>

    );

  }


  return (

    <aside className="telemetry-panel">

      <div className="telemetry-header">

        <span>
          SYSTEM TELEMETRY
        </span>

        <span className="telemetry-live">
          ● LIVE
        </span>

      </div>


      {/* RAM */}

      <div className="telemetry-section">

        <div className="telemetry-section-title">
          MEMORY
        </div>


        <div className="telemetry-name">

          {telemetry.ram.total} GB RAM

        </div>


        <TelemetryBar
          value={telemetry.ram.percent}
        />


        <div className="telemetry-values">

          <span>
            {telemetry.ram.used} GB USED
          </span>

          <span>
            {telemetry.ram.available} GB FREE
          </span>

        </div>

      </div>


      {/* STORAGE */}

      <div className="telemetry-section">

        <div className="telemetry-section-title">
          STORAGE
        </div>


        <div className="telemetry-name">

          {telemetry.storage.drive}

        </div>


        <TelemetryBar
          value={telemetry.storage.percent}
        />


        <div className="telemetry-values">

          <span>
            {telemetry.storage.used} GB USED
          </span>

          <span>
            {telemetry.storage.free} GB FREE
          </span>

        </div>

      </div>


      {/* CPU */}

      <div className="telemetry-section">

        <div className="telemetry-section-title">
          CPU
        </div>


        <div className="telemetry-name telemetry-truncate">

          {telemetry.cpu.name}

        </div>


        <TelemetryBar
          value={telemetry.cpu.percent}
        />


        <div className="telemetry-values">

          <span>
            USAGE
          </span>

          <span>
            {telemetry.cpu.percent}%
          </span>

        </div>

      </div>


      {/* GPU */}

      <div className="telemetry-section gpu-section">

        <div className="telemetry-section-title">
          GPU
        </div>


        <div className="telemetry-name telemetry-truncate">

          {telemetry.gpu.name}

        </div>

      </div>


      {/* SYSTEM */}

      <div className="telemetry-system">

        {telemetry.system.name}

      </div>

    </aside>

  );

}


/* =========================================================
   CONVERSATION HUD
========================================================= */

function ConversationHUD({
  conversation
}) {

  return (

    <div className="conversation-hud">

      <div className="hud-header">

        <div className="hud-title">
          NOVA // CONVERSATION
        </div>

        <div className="hud-line"></div>

        <div className="hud-live">
          LIVE
        </div>

      </div>


      <div className="conversation-content">

        {conversation.length === 0 ? (

          <div className="conversation-empty">

            <div className="empty-symbol">
              ◉
            </div>

            <div>
              WAITING FOR CONVERSATION
            </div>

          </div>

        ) : (

          conversation.map(
            (item, index) => (

              <div
                className={
                  `conversation-item ${item.role}`
                }
                key={`${item.role}-${index}`}
              >

                <div className="conversation-role">

                  {item.role === "user"
                    ? "YOU"
                    : "NOVA"
                  }

                </div>


                <div className="conversation-text">

                  {item.text}

                </div>

              </div>

            )

          )

        )}

      </div>

    </div>

  );

}


/* =========================================================
   MAIN APP
========================================================= */

function App() {

  const [nova, setNova] = useState({

    state: "idle",

    message: "How can I help you?"

  });


  const [conversation, setConversation] =
    useState([]);


  const [telemetry, setTelemetry] =
    useState(null);


  const [startingVoice, setStartingVoice] =
    useState(false);


  /* =======================================================
     NOVA STATE
  ======================================================= */

  useEffect(() => {

    const getState = async () => {

      try {

        const response = await fetch(
          "http://127.0.0.1:8000/state"
        );


        if (!response.ok) {

          throw new Error(
            "State request failed"
          );

        }


        const data =
          await response.json();


        setNova(data);

      } catch (error) {

        console.error(
          "NOVA state error:",
          error
        );

      }

    };


    getState();


    const interval =
      setInterval(
        getState,
        500
      );


    return () => {

      clearInterval(interval);

    };

  }, []);


  /* =======================================================
     SYSTEM TELEMETRY
     
     Only requests every 2 seconds.
     This deliberately does NOT run every frame.
  ======================================================= */

  useEffect(() => {

    let mounted = true;


    const getTelemetry = async () => {

      try {

        const response = await fetch(
          "http://127.0.0.1:8000/system"
        );


        if (!response.ok) {

          throw new Error(
            "Telemetry request failed"
          );

        }


        const data =
          await response.json();


        if (mounted) {

          setTelemetry(data);

        }

      } catch (error) {

        console.error(
          "Telemetry error:",
          error
        );

      }

    };


    getTelemetry();


    const interval =
      setInterval(
        getTelemetry,
        2000
      );


    return () => {

      mounted = false;

      clearInterval(interval);

    };

  }, []);


  /* =======================================================
     START LISTENING
  ======================================================= */

  const startListening = async () => {

    if (startingVoice) {

      return;

    }


    try {

      setStartingVoice(true);


      const response = await fetch(

        "http://127.0.0.1:8000/listen",

        {
          method: "POST"
        }

      );


      const data =
        await response.json();


      console.log(
        "NOVA voice:",
        data
      );


      if (!data.success) {

        console.error(
          "NOVA could not start:",
          data.message
        );

      }

    } catch (error) {

      console.error(
        "Could not activate NOVA:",
        error
      );

    } finally {

      setStartingVoice(false);

    }

  };


  /* =======================================================
     STATE LABELS
  ======================================================= */

  const stateLabels = {

    idle: "READY",

    listening: "LISTENING",

    thinking: "THINKING",

    speaking: "SPEAKING"

  };


  const stateDescriptions = {

    idle:
      "Awaiting your command",

    listening:
      "Listening for your voice",

    thinking:
      "Processing your request",

    speaking:
      "NOVA is responding"

  };


  return (

    <div className="nova">

      <div className="grid-background"></div>

      <div className="scanline"></div>


      {/* =================================================
          HEADER
      ================================================= */}

      <header className="header">

        <div>

          <div className="logo">
            NOVA
          </div>

          <div className="subtitle">
            PERSONAL AI SYSTEM
          </div>

        </div>


        <div className="system-status">

          <span className="status-light"></span>

          <div>

            <div className="online">
              SYSTEM ONLINE
            </div>

            <div className="status-detail">
              LOCAL INTERFACE
            </div>

          </div>

        </div>

      </header>


      {/* =================================================
          LEFT PANEL
      ================================================= */}

      <aside className="panel left-panel">

        <div className="panel-title">
          SYSTEM
        </div>


        <div className="stat">

          <span>
            VOICE
          </span>

          <strong>
            ACTIVE
          </strong>

        </div>


        <div className="stat">

          <span>
            AI ENGINE
          </span>

          <strong>
            GEMINI
          </strong>

        </div>


        <div className="stat">

          <span>
            VISION
          </span>

          <strong>
            3D CORE
          </strong>

        </div>


        <div className="stat">

          <span>
            STATUS
          </span>

          <strong>
            {stateLabels[nova.state] || "READY"}
          </strong>

        </div>

      </aside>


      {/* =================================================
          TELEMETRY
      ================================================= */}

      <SystemTelemetry
        telemetry={telemetry}
      />


      {/* =================================================
          3D CORE
      ================================================= */}

      <main className="core-container">

        <div className="core-label">
          NOVA CORE
        </div>


        <div className="core-scene">

          <Canvas

            camera={{
              position: [
                0,
                0,
                7
              ],

              fov: 45
            }}

            dpr={[
              1,
              1.5
            ]}

            gl={{
              antialias: true,
              powerPreference:
                "high-performance"
            }}

          >

            <ambientLight
              intensity={0.15}
            />


            <Stars

              radius={35}

              depth={15}

              count={500}

              factor={1.2}

              saturation={0}

              fade

              speed={0.25}

            />


            <NovaCore
              state={nova.state}
            />

          </Canvas>

        </div>


        {/* =================================================
            STATE
        ================================================= */}

        <div className="core-state">

          <div className="state-indicator">

            <span
              className={
                `state-dot ${nova.state}`
              }
            ></span>

            {stateLabels[nova.state] || "READY"}

          </div>


          <div className="state-description">

            {
              stateDescriptions[nova.state]
              || "Awaiting your command"
            }

          </div>

        </div>


        {/* =================================================
            MESSAGE
        ================================================= */}

        <div className="nova-message">

          {nova.message}

        </div>


        {/* =================================================
            LISTEN BUTTON
        ================================================= */}

        <button

          className={
            `listen-button ${
              nova.state === "listening"
                ? "active"
                : ""
            }`
          }

          onClick={startListening}

          disabled={
            startingVoice ||
            nova.state === "listening"
          }

        >

          <span className="listen-icon">
            ◉
          </span>


          {startingVoice

            ? "ACTIVATING..."

            : nova.state === "listening"

              ? "LISTENING..."

              : "LISTEN"

          }

        </button>

      </main>


      {/* =================================================
          CONVERSATION HUD
      ================================================= */}

      <ConversationHUD
        conversation={conversation}
      />


      {/* =================================================
          FOOTER
      ================================================= */}

      <footer className="footer">

        <div>
          NOVA v1.0
        </div>


        <div className="footer-center">

          <span>
            VOICE INTERFACE
          </span>

          <span>
            •
          </span>

          <span>
            AI CORE
          </span>

          <span>
            •
          </span>

          <span>
            3D ENGINE
          </span>

        </div>


        <div>
          {nova.state.toUpperCase()}
        </div>

      </footer>

    </div>

  );

}


export default App;