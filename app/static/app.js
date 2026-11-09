/**
 * BhashaBridge Dashboard Script
 * Implements Live Microphone WAV Recording, Prisma STT Analysis,
 * Timbre TTS Synthesis, Evon Reasoning, and Benchmark Viewer.
 */

const $ = id => document.getElementById(id);

let currentMode = "mic"; // "mic" or "upload"
let recordedWavBlob = null;
let mediaStream = null;
let mediaRecorder = null;
let audioChunks = [];
let recordStartTime = null;
let recordTimerInterval = null;
let lastAnalysisResult = null;
let currentTtsUrl = null;

// Mode Switching
$("tabMic").addEventListener("click", () => {
  currentMode = "mic";
  $("tabMic").classList.add("active");
  $("tabUpload").classList.remove("active");
  $("micArea").hidden = false;
  $("uploadArea").hidden = true;
});

$("tabUpload").addEventListener("click", () => {
  currentMode = "upload";
  $("tabUpload").classList.add("active");
  $("tabMic").classList.remove("active");
  $("micArea").hidden = true;
  $("uploadArea").hidden = false;
});

// Helper: Convert AudioBuffer to standard 16-bit PCM WAV
function audioBufferToWav(buffer) {
  const numChannels = 1;
  const sampleRate = buffer.sampleRate;
  const bitDepth = 16;
  const samples = buffer.getChannelData(0);
  const dataSize = samples.length * (bitDepth / 8);
  const arrayBuffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(arrayBuffer);

  const writeString = (offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  writeString(0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true);
  view.setUint16(32, numChannels * (bitDepth / 8), true);
  view.setUint16(34, bitDepth, true);
  writeString(36, "data");
  view.setUint32(40, dataSize, true);

  let offset = 44;
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    offset += 2;
  }
  return new Blob([view], { type: "audio/wav" });
}

// Live Microphone Recording Controller
$("micBtn").addEventListener("click", async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    // Stop recording
    mediaRecorder.stop();
    if (mediaStream) {
      mediaStream.getTracks().forEach(t => t.stop());
    }
    clearInterval(recordTimerInterval);
    $("micBtn").classList.remove("recording");
    $("micStatus").textContent = "Processing recording to 16kHz WAV…";
    return;
  }

  // Start recording
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, sampleRate: 16000 }
    });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(mediaStream);

    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const rawBlob = new Blob(audioChunks);
      const arrayBuffer = await rawBlob.arrayBuffer();
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const decodedBuffer = await audioCtx.decodeAudioData(arrayBuffer);
      recordedWavBlob = audioBufferToWav(decodedBuffer);
      audioCtx.close();

      const preview = $("recordedAudioPreview");
      preview.src = URL.createObjectURL(recordedWavBlob);
      preview.hidden = false;
      $("micStatus").textContent = "Audio ready for analysis (Click Analyze below)";
    };

    mediaRecorder.start();
    $("micBtn").classList.add("recording");
    $("micStatus").textContent = "Recording in progress… Click again to stop";
    recordStartTime = Date.now();
    recordTimerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
      const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
      const s = String(elapsed % 60).padStart(2, "0");
      $("micTimer").textContent = `${m}:${s}`;
    }, 500);
  } catch (err) {
    alert("Microphone access failed: " + err.message);
    $("micStatus").textContent = "Microphone unavailable";
  }
});

// Analyze Audio Sample
$("analyze").addEventListener("click", async () => {
  let fileToUpload = null;
  if (currentMode === "mic") {
    if (!recordedWavBlob) {
      // If manual transcript override is provided, allow empty dummy WAV
      const override = $("transcript").value.trim();
      if (!override) {
        alert("Please record audio or upload a WAV file first.");
        return;
      }
      // Generate 1-sec silent PCM WAV for transcript-only testing
      const emptyBuffer = new ArrayBuffer(44 + 32000);
      fileToUpload = new File([new Blob([emptyBuffer], { type: "audio/wav" })], "test_override.wav");
    } else {
      fileToUpload = new File([recordedWavBlob], "mic_recording.wav", { type: "audio/wav" });
    }
  } else {
    fileToUpload = $("audio").files[0];
    if (!fileToUpload) {
      alert("Please select a WAV file first.");
      return;
    }
  }

  const fd = new FormData();
  fd.append("file", fileToUpload);
  fd.append("language", $("language").value);
  fd.append("transcript_override", $("transcript").value.trim());

  $("analyze").disabled = true;
  $("state").textContent = "Analyzing…";

  try {
    const res = await fetch("/api/analyze", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Analysis failed");

    lastAnalysisResult = data;
    $("empty").hidden = true;
    $("report").hidden = false;
    $("state").textContent = "Analysis complete";

    // Transcript & ASR Metadata
    $("transcriptOut").textContent = data.asr.transcript;
    $("detectedLangBadge").textContent = data.asr.detected_language || $("language").value;
    $("provider").textContent = `Provider: ${data.asr.provider} · Model: ${data.asr.model}`;

    // Acoustic Metrics
    $("duration").textContent = data.audio_quality.duration_seconds + " s";
    $("rms").textContent = data.audio_quality.rms;
    $("clip").textContent = (100 * data.audio_quality.clipping_fraction).toFixed(2) + "%";
    $("silence").textContent = (100 * data.audio_quality.silence_fraction_heuristic).toFixed(1) + "%";

    // Semantic Slots
    const slotsDiv = $("slots");
    slotsDiv.innerHTML = "";
    if (data.semantic_slots && data.semantic_slots.length > 0) {
      data.semantic_slots.forEach(slot => {
        const chip = document.createElement("span");
        chip.className = `slot slot-${slot.type} slot-${slot.criticality}`;
        chip.textContent = `${slot.type.replace(/_/g, " ")}: ${slot.value}`;
        slotsDiv.appendChild(chip);
      });
    } else {
      slotsDiv.innerHTML = "<small class='muted'>No high-risk critical slots detected.</small>";
    }

    // Policy Decision
    const actionLabels = {
      confirm: "Confirm Critical Information (Readback Needed)",
      re_record: "Re-record (Acoustic Quality Issue Detected)",
      proceed_with_correction_option: "Safe to Proceed (Low Risk)"
    };
    const actionClass = data.verification.action;
    $("decision").className = `decision decision-${actionClass}`;
    $("decision").innerHTML = `
      <b>${actionLabels[actionClass] || actionClass}</b>
      <p>${data.verification.recommendation_text}</p>
      <div class="decision-triggers">
        <small>TRIGGERS: ${data.verification.reasons.join(" · ") || "None"}</small>
      </div>
    `;

    // Action Bar (Spoken Readback & Evon)
    $("actionBar").hidden = false;
    $("evonOutput").hidden = true;

  } catch (err) {
    $("state").textContent = "Error";
    alert(err.message);
  } finally {
    $("analyze").disabled = false;
  }
});

// Speak Readback via Gnani Timbre TTS
$("speakConfirmBtn").addEventListener("click", async () => {
  if (!lastAnalysisResult) return;
  const prompt = lastAnalysisResult.verification.readback_prompt || lastAnalysisResult.asr.transcript;
  $("ttsText").value = prompt;
  $("speakConfirmBtn").disabled = true;
  $("speakConfirmBtn").innerHTML = "<span>🔊</span> Synthesizing with Timbre…";

  try {
    const res = await fetch("/api/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: prompt,
        language: $("language").value.slice(0, 2),
        voice: $("ttsVoice").value
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Timbre synthesis failed");

    const raw = atob(data.audio_base64);
    const bytes = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
    const blob = new Blob([bytes], { type: data.content_type || "audio/mpeg" });

    if (currentTtsUrl) URL.revokeObjectURL(currentTtsUrl);
    currentTtsUrl = URL.createObjectURL(blob);
    $("ttsAudio").src = currentTtsUrl;
    $("ttsAudio").hidden = false;
    await $("ttsAudio").play();
  } catch (err) {
    alert("Timbre Voice Playback: " + err.message);
  } finally {
    $("speakConfirmBtn").disabled = false;
    $("speakConfirmBtn").innerHTML = "<span>🔊</span> Speak Readback (Gnani Timbre)";
  }
});

// Deep Intent Reasoning via Gnani Evon
$("evonReasonBtn").addEventListener("click", async () => {
  if (!lastAnalysisResult) return;
  $("evonReasonBtn").disabled = true;
  $("evonReasonBtn").innerHTML = "<span>🧠</span> Querying Gnani Evon…";

  try {
    const res = await fetch("/api/reason", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transcript: lastAnalysisResult.asr.transcript,
        language: $("language").value,
        provider: "auto"
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Evon reasoning failed");

    $("evonOutput").hidden = false;
    $("evonText").textContent = data.reasoning.text;
  } catch (err) {
    alert("Gnani Evon: " + err.message);
  } finally {
    $("evonReasonBtn").disabled = false;
    $("evonReasonBtn").innerHTML = "<span>🧠</span> Deep Intent Audit (Gnani Evon)";
  }
});

// Standalone Timbre Synthesis Panel
$("synthesize").addEventListener("click", async () => {
  const text = $("ttsText").value.trim();
  if (!text) {
    alert("Please enter text to synthesize.");
    return;
  }
  const btn = $("synthesize");
  btn.disabled = true;
  $("ttsState").textContent = "Generating speech with Gnani Timbre v3…";

  try {
    const res = await fetch("/api/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice: $("ttsVoice").value })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Timbre synthesis failed");

    const raw = atob(data.audio_base64);
    const bytes = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
    const blob = new Blob([bytes], { type: data.content_type || "audio/mpeg" });

    if (currentTtsUrl) URL.revokeObjectURL(currentTtsUrl);
    currentTtsUrl = URL.createObjectURL(blob);
    $("ttsAudio").src = currentTtsUrl;
    $("ttsAudio").hidden = false;
    $("ttsState").textContent = `Synthesized by Gnani Timbre (${data.voice})`;
    await $("ttsAudio").play();
  } catch (err) {
    $("ttsState").textContent = "Synthesis error: " + err.message;
    alert(err.message);
  } finally {
    btn.disabled = false;
  }
});

// Benchmark Suite Loader
async function loadBenchmarkData() {
  const btn = $("loadBenchmarkBtn");
  btn.disabled = true;
  btn.textContent = "Calculating…";

  try {
    const res = await fetch("/api/benchmark");
    const data = await res.json();
    if (!res.ok) return;

    if (data.metrics_summary) {
      const metric = (value) => value === null || value === undefined ? "Not measured" : `${value}%`;
      if ($("heroMcspVal")) $("heroMcspVal").textContent = metric(data.metrics_summary.bhashabridge_mcsp);
      if ($("heroNegVal")) $("heroNegVal").textContent = metric(data.metrics_summary.raw_negation_recall);
      if ($("heroWerVal")) $("heroWerVal").textContent = metric(data.metrics_summary.wer);
      if ($("benchNegVal")) $("benchNegVal").textContent = metric(data.metrics_summary.raw_negation_recall);
      if ($("benchMcspVal")) $("benchMcspVal").textContent = metric(data.metrics_summary.bhashabridge_mcsp);
      if ($("benchInvertVal")) $("benchInvertVal").textContent = data.metrics_summary.avoided_inversions ?? "Not measured";
    }

    const tbody = $("benchmarkBody");
    tbody.innerHTML = "";
    (data.sample_preview || []).forEach(s => {
      const tr = document.createElement("tr");
      const cells = [s.utterance_id, s.language, s.condition, s.reference, s.hypothesis,
        s.confirmation_required === "true" ? "Confirm Required" : "Proceed"];
      cells.forEach((value, index) => {
        const td = document.createElement("td");
        const safe = document.createElement("span");
        safe.textContent = value ?? "";
        if (index === 0) { const code = document.createElement("code"); code.textContent = safe.textContent; td.appendChild(code); }
        else if (index === 4) { const em = document.createElement("em"); em.textContent = safe.textContent; td.appendChild(em); }
        else td.appendChild(safe);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Failed to load benchmark:", e);
  } finally {
    btn.disabled = false;
    btn.textContent = "Refresh Metrics";
  }
}

$("loadBenchmarkBtn").addEventListener("click", loadBenchmarkData);
// Initial load
loadBenchmarkData();
