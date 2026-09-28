// FRIDAY Sci-Fi Hologram HUD Controller

document.addEventListener("DOMContentLoaded", () => {
  const clockEl = document.getElementById("system-time");
  const cpuBar = document.getElementById("cpu-bar");
  const cpuVal = document.getElementById("cpu-val");
  const memBar = document.getElementById("mem-bar");
  const memVal = document.getElementById("mem-val");
  const netVal = document.getElementById("net-val");
  const batVal = document.getElementById("bat-val");
  const tempVal = document.getElementById("temp-val");
  const uptimeVal = document.getElementById("uptime-val");
  const procVal = document.getElementById("proc-val");
  const osVal = document.getElementById("os-val");
  const subtitleEl = document.getElementById("subtitle-text");
  const statusLabel = document.getElementById("status-label");
  const statusDot = document.getElementById("status-dot");
  const waveform = document.getElementById("waveform");
  const tacticalLog = document.getElementById("tactical-log");
  const cmdInput = document.getElementById("cmd-input");
  const micBtn = document.getElementById("mic-btn");
  const sendBtn = document.getElementById("send-btn");
  const attachBtn = document.getElementById("attach-btn");
  const fileBadge = document.getElementById("file-attachment-badge");
  const fileBadgeName = document.getElementById("file-badge-name");
  const removeFileBtn = document.getElementById("remove-file-btn");
  const arcReactor = document.getElementById("arc-reactor");
  const avatarContainer = document.getElementById("avatar-container");
  const avatarImg = document.getElementById("friday-avatar");
  const widgetToggleBtn = document.getElementById("widget-toggle-btn");
  const widgetRestoreBtn = document.getElementById("widget-restore-btn");

  let attachedFilePath = null;

  function setAttachedFile(filePath) {
    if (!filePath) return;
    attachedFilePath = filePath;
    const fileName = filePath.split(/[\\/]/).pop();
    if (fileBadgeName) fileBadgeName.textContent = fileName;
    if (fileBadge) fileBadge.style.display = "flex";
    if (attachBtn) attachBtn.classList.add("attached");
    if (cmdInput) {
      cmdInput.placeholder = `Ask anything about ${fileName}...`;
      cmdInput.focus();
    }
  }

  function clearAttachedFile() {
    attachedFilePath = null;
    if (fileBadge) fileBadge.style.display = "none";
    if (attachBtn) attachBtn.classList.remove("attached");
    if (cmdInput) {
      cmdInput.placeholder = "Type a command or attach file (PDF, DOCX, PNG)...";
    }
  }

  // --- Viseme Lip-Sync Animation Engine ---
  const VISEME_FRAMES = [
    "friday_face_f0.png", // 0: Closed / Resting
    "friday_face_f1.png", // 1: Slightly parted
    "friday_face_f2.png", // 2: Medium open
    "friday_face_f3.png", // 3: Wide open
    "friday_face_f4.png", // 4: Squeezed O
    "friday_face_f5.png"  // 5: Soft smile / open
  ];

  // Pre-cache all frames in memory for 0ms latency switching
  VISEME_FRAMES.forEach((src) => {
    const img = new Image();
    img.src = src;
  });

  // Natural speech viseme patterns simulating syllables and phonemes
  const SPEECH_PATTERNS = [
    [1, 2, 3, 2, 1, 0],
    [1, 4, 3, 2, 1],
    [2, 5, 2, 1, 0],
    [1, 2, 4, 1, 0],
    [2, 3, 5, 2, 1]
  ];

  let speechTimer = null;
  let patternIdx = 0;
  let stepIdx = 0;

  function startLipSync() {
    if (speechTimer) return;

    let currentPattern = SPEECH_PATTERNS[0];
    patternIdx = 0;
    stepIdx = 0;

    function step() {
      if (!avatarImg) return;

      const frameNum = currentPattern[stepIdx];
      avatarImg.src = VISEME_FRAMES[frameNum];

      stepIdx++;
      if (stepIdx >= currentPattern.length) {
        stepIdx = 0;
        patternIdx = (patternIdx + 1) % SPEECH_PATTERNS.length;
        currentPattern = SPEECH_PATTERNS[patternIdx];
      }

      // Natural cadence variation: 80ms - 130ms per viseme transition
      const delay = Math.floor(Math.random() * 50) + 80;
      speechTimer = setTimeout(step, delay);
    }

    step();
  }

  function stopLipSync() {
    if (speechTimer) {
      clearTimeout(speechTimer);
      speechTimer = null;
    }
    if (avatarImg) {
      avatarImg.src = VISEME_FRAMES[0]; // Return to resting closed lips
    }
  }

  // --- Real-time Clock ---
  function updateClock() {
    const now = new Date();
    clockEl.textContent = now.toTimeString().split(" ")[0];
  }
  setInterval(updateClock, 1000);
  updateClock();

  // --- Global HUD Interface (Callable from Python) ---
  window.fridayHUD = {
    updateTelemetry: function (stats) {
      if (stats.cpu !== undefined && cpuBar && cpuVal) {
        cpuBar.style.width = stats.cpu + "%";
        cpuVal.textContent = stats.cpu + "%";
      }
      if (stats.mem !== undefined && memBar && memVal) {
        memBar.style.width = stats.mem + "%";
        memVal.textContent = stats.mem + "%";
      }
      if (stats.net !== undefined && netVal) netVal.textContent = stats.net;
      if (stats.bat !== undefined && batVal) batVal.textContent = stats.bat;
      if (stats.temp !== undefined && tempVal) tempVal.textContent = stats.temp;
      if (stats.uptime !== undefined && uptimeVal) uptimeVal.textContent = stats.uptime;
      if (stats.proc !== undefined && procVal) procVal.textContent = stats.proc;
      if (stats.os !== undefined && osVal) osVal.textContent = stats.os;
    },

    setStatus: function (state, text) {
      state = (state || "STANDBY").toUpperCase();
      statusLabel.textContent = state;

      if (state === "SPEAKING") {
        statusDot.style.background = "#00f0ff";
        statusDot.style.boxShadow = "0 0 12px #00f0ff";
        statusLabel.style.color = "#00f0ff";
        waveform.classList.add("speaking");
        if (avatarContainer) avatarContainer.className = "hologram-avatar-container speaking";
        startLipSync();
      } else if (state === "LISTENING") {
        stopLipSync();
        statusDot.style.background = "#ff7700";
        statusDot.style.boxShadow = "0 0 10px #ff7700";
        statusLabel.style.color = "#ff7700";
        waveform.classList.remove("speaking");
        if (avatarContainer) avatarContainer.className = "hologram-avatar-container listening";
      } else if (state === "THINKING") {
        stopLipSync();
        statusDot.style.background = "#00f0ff";
        statusDot.style.boxShadow = "0 0 10px #00f0ff";
        statusLabel.style.color = "#00f0ff";
        waveform.classList.remove("speaking");
        if (avatarContainer) avatarContainer.className = "hologram-avatar-container thinking";
      } else {
        // STANDBY / READY
        stopLipSync();
        statusDot.style.background = "#5c8ca6";
        statusDot.style.boxShadow = "none";
        statusLabel.style.color = "#5c8ca6";
        waveform.classList.remove("speaking");
        if (avatarContainer) avatarContainer.className = "hologram-avatar-container";
      }

      if (text) {
        subtitleEl.textContent = text.toUpperCase();
      }
    },

    appendLog: function (type, message) {
      const entry = document.createElement("div");
      entry.className = `log-entry ${type}`;
      entry.textContent = `[${type.toUpperCase()}] ${message}`;
      tacticalLog.appendChild(entry);
      tacticalLog.scrollTop = tacticalLog.scrollHeight;
    }
  };

  // --- Interaction Handlers ---
  function sendUserCommand(customText) {
    const query = (customText || cmdInput.value).trim();
    if (!query && !attachedFilePath) return;

    const finalQuery = query || "Please analyze and summarize this attached document in detail.";
    const filePathToSend = attachedFilePath;

    window.fridayHUD.setStatus("THINKING", `PROCESSING: "${finalQuery}"`);
    cmdInput.value = "";
    clearAttachedFile();

    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.process_user_query(finalQuery, filePathToSend);
    } else {
      console.log("Python bridge not connected. Query:", finalQuery, "File:", filePathToSend);
    }
  }

  // File Attachment Handlers
  if (attachBtn) {
    attachBtn.addEventListener("click", () => {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.select_file) {
        window.pywebview.api.select_file().then((selectedPath) => {
          if (selectedPath) {
            setAttachedFile(selectedPath);
          }
        });
      }
    });
  }

  if (removeFileBtn) {
    removeFileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      clearAttachedFile();
    });
  }

  // Drag and drop onto HUD
  window.addEventListener("dragover", (e) => {
    e.preventDefault();
    document.body.classList.add("drag-over");
  });

  window.addEventListener("dragleave", (e) => {
    if (e.relatedTarget === null) {
      document.body.classList.remove("drag-over");
    }
  });

  window.addEventListener("drop", (e) => {
    e.preventDefault();
    document.body.classList.remove("drag-over");
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.path) {
        setAttachedFile(file.path);
      }
    }
  });

  function triggerVoice() {
    window.fridayHUD.setStatus("LISTENING", "LISTENING FOR COMMAND...");
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.trigger_mic();
    }
  }

  sendBtn.addEventListener("click", () => sendUserCommand());
  cmdInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendUserCommand();
  });

  micBtn.addEventListener("click", triggerVoice);
  arcReactor.addEventListener("click", triggerVoice);

  // Widget Mode Toggles
  function handleWidgetToggle() {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.toggle_widget_mode) {
      window.pywebview.api.toggle_widget_mode();
    } else {
      document.body.classList.toggle("widget-mode");
    }
  }

  if (widgetToggleBtn) widgetToggleBtn.addEventListener("click", handleWidgetToggle);
  if (widgetRestoreBtn) widgetRestoreBtn.addEventListener("click", handleWidgetToggle);

  // Quick Action Chip Clicks
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const cmd = chip.getAttribute("data-cmd");
      if (cmd) {
        sendUserCommand(cmd);
      }
    });
  });

  // PyWebView Bridge Ready Listener
  window.addEventListener("pywebviewready", () => {
    console.log("PyWebView bridge active.");
  });
});
