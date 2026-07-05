import subprocess
import threading
import time
import re
import os
import sys
import webbrowser
import socket
import atexit
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 7860))
HOST = "0.0.0.0"

# Gömülü HTML + CSS + JS Arayüzü (NiNA Translate)
HTML_CONTENT = """<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script>
      // Mobil cihazlarda mikrofon izni ve ses tanıma için HTTPS'i zorunlu kıl
      if (window.location.protocol === 'http:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        window.location.href = window.location.href.replace('http:', 'https:');
      }
    </script>
    <title>Simültane Çeviri</title>
    <style>
      :root {
        color-scheme: dark;
        font-family: Inter, Arial, sans-serif;
      }
      body {
        margin: 0;
        background: linear-gradient(135deg, #0a1b3a, #15325b, #0a1b3a);
        color: #f4f7fb;
        min-height: 100vh;
        display: grid;
        place-items: center;
      }
      .card {
        position: relative;
        width: min(900px, 92vw);
        background: rgba(8, 26, 48, 0.94);
        border: 1px solid rgba(124, 156, 255, 0.2);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 20px 45px rgba(0,0,0,0.45);
      }
      /* Brand Header */
      .brand-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
      }
      .brand-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
      }
      .brand-svg {
        width: 32px;
        height: 32px;
        animation: brandPulse 3s ease-in-out infinite, brandColorShift 16s linear infinite;
      }
      @keyframes brandPulse {
        0% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(124, 156, 255, 0)); }
        50% { transform: scale(1.05); filter: drop-shadow(0 0 6px currentColor); }
        100% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(124, 156, 255, 0)); }
      }
      @keyframes brandColorShift {
        0% { color: #7c9cff; }
        25% { color: #a78bfa; }
        50% { color: #f472b6; }
        75% { color: #34d399; }
        100% { color: #7c9cff; }
      }
      h1 { margin-top: 0; font-size: 1.8rem; }
      .controls { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }
      .controls label { display: flex; flex-direction: column; gap: 6px; font-size: 0.85rem; color: #b8c2cf; font-weight: 500; }
      select, button { padding: 10px 12px; border-radius: 10px; border: none; font-size: 1rem; }
      button { background: #3aa8ff; color: white; cursor: pointer; font-weight: 600; }
      button.secondary { background: #6c757d; }
      button.active-tts { background: #2ecc71; color: white; }
      button.recording { background: #ef4444; color: white; }
      
      /* Swap Button Styling */
      .swap-btn {
        background: #1e293b;
        color: #7c9cff;
        border: 1px solid rgba(124, 156, 255, 0.25);
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-top: 20px;
        padding: 0;
      }
      .swap-btn:hover {
        background: #7c9cff;
        color: white;
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(124, 156, 255, 0.4);
      }
      .swap-btn:active {
        transform: scale(0.95);
      }
      
      /* Dil Seçici Kapsül Buton */
      .lang-switch-container {
        position: absolute;
        top: 24px;
        right: 24px;
        display: flex;
        background: #172435;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        overflow: hidden;
        cursor: pointer;
        user-select: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
      }
      .lang-switch-option {
        padding: 6px 16px;
        font-size: 0.8rem;
        font-weight: bold;
        color: #7b8f9e;
        transition: background 0.2s, color 0.2s;
        text-align: center;
      }
      .lang-switch-option.active {
        background: #7c9cff;
        color: white;
      }

      .panels { display: grid; gap: 16px; grid-template-columns: repeat(2, minmax(0,1fr)); }
      .panel { background: rgba(124, 156, 255, 0.06); border: 1px solid rgba(124, 156, 255, 0.1); border-radius: 14px; padding: 14px; min-height: 220px; }
      .panel h2 { margin-top: 0; font-size: 1rem; color: #8fd2ff; }
      .output { white-space: pre-wrap; line-height: 1.5; }
      .status { margin-top: 10px; color: #9fe5b5; font-weight: 600; }
      .hint { margin-top: 8px; color: #b8c2cf; font-size: 0.95rem; }
       @media (max-width: 760px) { 
        .panels { grid-template-columns: 1fr; } 
      }
    </style>
  </head>
  <body>
    <div class="card">
      <div class="brand-header">
        <svg class="brand-svg" viewBox="0 0 24 24">
          <!-- Sparkles -->
          <path d="M22,1 Q22,3 20,3 Q22,3 22,5 Q22,3 24,3 Q22,3 22,1 Z" fill="currentColor" />
          <path d="M17.5,2.5 Q17.5,6.5 13.5,6.5 Q17.5,6.5 17.5,10.5 Q17.5,6.5 21.5,6.5 Q17.5,6.5 17.5,2.5 Z" fill="currentColor" />
          <path d="M6,15.5 Q6,18.5 3,18.5 Q6,18.5 6,21.5 Q6,18.5 9,18.5 Q6,18.5 6,15.5 Z" fill="currentColor" />
          <!-- Squares -->
          <rect x="2" y="5.5" width="11" height="11" rx="3" fill="none" stroke="currentColor" stroke-width="1.8" />
          <text x="7.5" y="14" font-size="8" font-family="system-ui, sans-serif" font-weight="900" text-anchor="middle" fill="currentColor">A</text>
          <rect x="10.5" y="10.5" width="11" height="11" rx="3" fill="#08131f" stroke="currentColor" stroke-width="1.8" />
          <text x="16" y="19" font-size="8" font-family="system-ui, sans-serif" font-weight="900" text-anchor="middle" fill="currentColor">文</text>
        </svg>
        <span class="brand-name">NiNA Translate v 0.1</span>
      </div>
      <div class="lang-switch-container" id="uiLangBtn">
        <span class="lang-switch-option active" id="uiLangTR">TR</span>
        <span class="lang-switch-option" id="uiLangEN">EN</span>
      </div>
      <h1 id="appTitle">Toplantı İçin Simültane Çeviri</h1>
      <p id="appSubtitle">Tarayıcının mikrofonunu kullanarak konuşmanızı dinler, metni çevirir ve canlı bir pano üzerinde gösterir.</p>
      <div class="controls">
        <label>
          <span id="lblSourceLang">Kaynak dil</span>
          <select id="sourceLang">
            <option value="tr" selected>Türkçe</option>
            <option value="en">İngilizce</option>
            <option value="de">Almanca</option>
            <option value="fr">Fransızca</option>
            <option value="es">İspanyolca</option>
            <option value="it">İtalyanca</option>
            <option value="nl">Hollandaca</option>
            <option value="pt">Portekizce</option>
            <option value="ru">Rusça</option>
            <option value="ar">Arapça</option>
            <option value="zh">Çince</option>
            <option value="ja">Japonca</option>
            <option value="ko">Korece</option>
          </select>
        </label>
        <button id="swapLangBtn" class="swap-btn" type="button" title="Dilleri Değiştir">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M7 16V4M7 4L3 8M7 4L11 8M17 8v12M17 20l-4-4M17 20l4-4"/>
          </svg>
        </button>
        <label>
          <span id="lblTargetLang">Hedef dil</span>
          <select id="targetLang">
            <option value="tr">Türkçe</option>
            <option value="en" selected>İngilizce</option>
            <option value="de">Almanca</option>
            <option value="fr">Fransızca</option>
            <option value="es">İspanyolca</option>
            <option value="it">İtalyanca</option>
            <option value="nl">Hollandaca</option>
            <option value="pt">Portekizce</option>
            <option value="ru">Rusça</option>
            <option value="ar">Arapça</option>
            <option value="zh">Çince</option>
            <option value="ja">Japonca</option>
            <option value="ko">Korece</option>
          </select>
        </label>
        <button id="toggleBtn">Mikrofonu Başlat</button>
        <button id="ttsToggleBtn" class="active-tts">🔊 Ses Açık</button>
        <button id="clearBtn" class="secondary">Temizle</button>

        <button id="qrBtn" class="secondary" onclick="showQrModal()">📱 Mobil</button>

      </div>
      <div class="status" id="status">Hazır. Mikrofonu başlatmak için butona basın.</div>
      
      <!-- Ses Türü Rozeti -->
      <div id="voiceBadgeContainer" style="display: none; align-items: center; gap: 8px; margin-top: 8px; margin-bottom: 8px; font-size: 0.9rem; background: rgba(124, 156, 255, 0.1); border: 1px solid rgba(124, 156, 255, 0.2); padding: 8px 12px; border-radius: 10px; width: fit-content; transition: all 0.3s ease;">
        <span id="lblVoiceType" style="color: #b8c2cf;">Ses Türü:</span>
        <strong id="voiceVal" style="color: #7c9cff;">-</strong>
      </div>

      <div class="hint" id="appHint">Not: Bu prototip tarayıcı destekli ses tanıma kullanır. Chrome veya Edge önerilir.</div>
      <div class="panels">
        <div class="panel">
          <h2 id="lblPanelSpeech">Ses Tanıma Metni</h2>
          <div class="output" id="transcript">Bekliyor...</div>
        </div>
        <div class="panel">
          <h2 id="lblPanelTranslation">Çevrilmiş Metin</h2>
          <div class="output" id="translation">Çeviri burada görünür.</div>
        </div>
      </div>
    </div>

    <script>
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = SpeechRecognition ? new SpeechRecognition() : null;
      const toggleBtn = document.getElementById('toggleBtn');
      const ttsToggleBtn = document.getElementById('ttsToggleBtn');
      const clearBtn = document.getElementById('clearBtn');
      const sourceLang = document.getElementById('sourceLang');
      const targetLang = document.getElementById('targetLang');
      const transcriptEl = document.getElementById('transcript');
      const translationEl = document.getElementById('translation');
      const statusEl = document.getElementById('status');
      const uiLangBtn = document.getElementById('uiLangBtn');

      let listening = false;
      let shouldBeListening = false;
      let lastSentText = '';
      let consecutiveErrors = 0;
      let reconnectTimer = null;
      let translateTimer = null;
      let firstSentenceFinished = false;
      
      let ttsEnabled = true;
      let currentUtterance = null;
      
      let currentUiLang = 'en';
      let statusState = 'ready'; // 'ready', 'listening', 'stopped', 'reconnecting', 'no-support', 'error-network', 'error-permission'

      const TRANSLATIONS = {
        tr: {
          brandName: "NiNA Çeviri v 0.1",
          title: "Toplantı İçin Simültane Çeviri",
          subtitle: "Tarayıcının mikrofonunu kullanarak konuşmanızı dinler, metni çevirir ve canlı bir pano üzerinde gösterir.",
          srcLangLabel: "Kaynak dil",
          tgtLangLabel: "Hedef dil",
          startMic: "Mikrofonu Başlat",
          stopMic: "Mikrofonu Durdur",
          soundOff: "🔇 Ses Kapalı",
          soundOn: "🔊 Ses Açık",
          clearBtn: "Temizle",
          statusReady: "Hazır. Mikrofonu başlatmak için butona basın.",
          statusListening: "Dinliyorum...",
          statusStopped: "Dinleme durdu.",
          statusReconnecting: "Bağlantı kesildi, yeniden bağlanılıyor...",
          statusNoSupport: "Bu tarayıcı ses tanıma desteği sunmuyor. Chrome veya Edge kullanın.",
          statusNetworkErr: "Ses tanıma hatası: Google servislerine bağlanılamıyor. Lütfen internet bağlantınızı, VPN veya proxy ayarlarınızı kontrol edin.",
          statusPermissionErr: "Ses tanıma hatası: Mikrofon izni reddedildi. Lütfen tarayıcı adres satırındaki kilit simgesine tıklayıp mikrofona izin verin.",
          hint: "Not: Bu prototip tarayıcı destekli ses tanıma kullanır. Chrome veya Edge önerilir.",
          panelSpeech: "Ses Tanıma Metni",
          panelTranslation: "Çevrilmiş Metin",
          waiting: "Bekliyor...",
          translationHere: "Çeviri burada görünür.",
          langTr: "Türkçe",
          langEn: "İngilizce",
          langDe: "Almanca",
          langFr: "Fransızca",
          langEs: "İspanyolca",
          langIt: "İtalyanca",
          langNl: "Hollandaca",
          langPt: "Portekizce",
          langRu: "Rusça",
          langAr: "Arapça",
          langZh: "Çince",
          langJa: "Japonca",
          langKo: "Korece",
          lblVoiceType: "Ses Türü:",
          voiceMale: "Erkek 🧑",
          voiceFemale: "Kadın 👩",
          voiceChild: "Çocuk 🧒",
          voiceDetecting: "Tespit ediliyor..."
        },
        en: {
          brandName: "NiNA Translate v 0.1",
          title: "Simultaneous Translation for Meetings",
          subtitle: "Listens to your speech using the browser microphone, translates it, and displays it on a live dashboard.",
          srcLangLabel: "Source language",
          tgtLangLabel: "Target language",
          startMic: "Start Microphone",
          stopMic: "Stop Microphone",
          soundOff: "🔇 Sound Off",
          soundOn: "🔊 Sound On",
          clearBtn: "Clear",
          statusReady: "Ready. Press the button to start the microphone.",
          statusListening: "Listening...",
          statusStopped: "Listening stopped.",
          statusReconnecting: "Connection lost, reconnecting...",
          statusNoSupport: "This browser does not support speech recognition. Use Chrome or Edge.",
          statusNetworkErr: "Speech recognition error: Cannot connect to Google services. Please check your internet, VPN or proxy settings.",
          statusPermissionErr: "Speech recognition error: Microphone permission denied. Please click the lock icon in the address bar and allow microphone access.",
          hint: "Note: This prototype uses browser-based speech recognition. Chrome or Edge is recommended.",
          panelSpeech: "Speech Recognition Text",
          panelTranslation: "Translated Text",
          waiting: "Waiting...",
          translationHere: "Translation appears here.",
          langTr: "Turkish",
          langEn: "English",
          langDe: "German",
          langFr: "French",
          langEs: "Spanish",
          langIt: "Italian",
          langNl: "Dutch",
          langPt: "Portuguese",
          langRu: "Russian",
          langAr: "Arabic",
          langZh: "Chinese",
          langJa: "Japanese",
          langKo: "Korean",
          lblVoiceType: "Voice Type:",
          voiceMale: "Male 🧑",
          voiceFemale: "Female 👩",
          voiceChild: "Child 🧒",
          voiceDetecting: "Detecting..."
        }
      };

      // 2 harfli kodları Web Speech API'nin (BCP-47) formatına eşle
      function getBCP47Language(lang) {
        const langMap = {
          "tr": "tr-TR",
          "en": "en-US",
          "de": "de-DE",
          "fr": "fr-FR",
          "es": "es-ES",
          "it": "it-IT",
          "nl": "nl-NL",
          "pt": "pt-PT",
          "ru": "ru-RU",
          "ar": "ar-SA",
          "zh": "zh-CN",
          "ja": "ja-JP",
          "ko": "ko-KR"
        };
        return langMap[lang] || lang;
      }

      // Pitch Detection and Voice Classification (Web Audio API)
      let audioCtx = null;
      let audioStream = null;
      let audioSource = null;
      let analyser = null;
      let pitchHistory = [];
      let pitchAnalysisInterval = null;

      async function startAudioAnalysis() {
        if (audioStream) return;
        pitchHistory = [];
        try {
          const AudioContextClass = window.AudioContext || window.webkitAudioContext;
          if (!AudioContextClass) return;
          
          if (!audioCtx) {
            audioCtx = new AudioContextClass();
          }
          
          audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
          audioSource = audioCtx.createMediaStreamSource(audioStream);
          analyser = audioCtx.createAnalyser();
          analyser.fftSize = 2048;
          audioSource.connect(analyser);
          
          if (audioCtx.state === 'suspended') {
            await audioCtx.resume();
          }
          
          pitchAnalysisInterval = setInterval(() => {
            if (!analyser) return;
            const buffer = new Float32Array(analyser.fftSize);
            analyser.getFloatTimeDomainData(buffer);
            const pitch = autoCorrelate(buffer, audioCtx.sampleRate);
            if (pitch > 60 && pitch < 500) {
              pitchHistory.push(pitch);
              if (pitchHistory.length > 100) {
                pitchHistory.shift();
              }
            }
          }, 50);
        } catch (e) {
          console.error("Audio analysis failed", e);
        }
      }

      function stopAudioAnalysis() {
        if (pitchAnalysisInterval) {
          clearInterval(pitchAnalysisInterval);
          pitchAnalysisInterval = null;
        }
        if (audioStream) {
          audioStream.getTracks().forEach(track => track.stop());
          audioStream = null;
        }
        if (audioSource) {
          audioSource.disconnect();
          audioSource = null;
        }
        pitchHistory = [];
      }

      function autoCorrelate(buf, sampleRate) {
        const SIZE = buf.length;
        let rms = 0;
        for (let i = 0; i < SIZE; i++) {
          const val = buf[i];
          rms += val * val;
        }
        rms = Math.sqrt(rms / SIZE);
        if (rms < 0.015) return -1;

        let r1 = 0, r2 = SIZE - 1;
        const thres = 0.2;
        for (let i = 0; i < SIZE / 2; i++) {
          if (Math.abs(buf[i]) < thres) { r1 = i; break; }
        }
        for (let i = SIZE - 1; i >= SIZE / 2; i--) {
          if (Math.abs(buf[i]) < thres) { r2 = i; break; }
        }

        const slicedBuf = buf.slice(r1, r2);
        const slicedSize = slicedBuf.length;
        if (slicedSize < 4) return -1;

        const correlations = new Float32Array(slicedSize);
        for (let i = 0; i < slicedSize; i++) {
          for (let j = 0; j < slicedSize - i; j++) {
            correlations[i] += slicedBuf[j] * slicedBuf[j + i];
          }
        }

        let d = 0;
        while (correlations[d] > correlations[d + 1]) d++;
        let maxval = -1, maxpos = -1;
        for (let i = d; i < slicedSize; i++) {
          if (correlations[i] > maxval) {
            maxval = correlations[i];
            maxpos = i;
          }
        }
        let T0 = maxpos;
        if (T0 <= 0 || T0 >= slicedSize - 1) return -1;

        const x1 = correlations[T0 - 1];
        const x2 = correlations[T0];
        const x3 = correlations[T0 + 1];
        const a = (x1 + x3 - 2 * x2) / 2;
        const b = (x3 - x1) / 2;
        if (a) T0 = T0 - b / (2 * a);

        return sampleRate / T0;
      }

      function getDetectedSpeakerType() {
        if (pitchHistory.length === 0) return 'female';
        const sorted = [...pitchHistory].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        
        console.log("Speaker Pitch (median):", median);
        
        // Pitch limits:
        // Male: < 155 Hz
        // Female: 155 Hz - 245 Hz
        // Child: >= 245 Hz
        if (median < 155) return 'male';
        if (median >= 155 && median < 245) return 'female';
        return 'child';
      }

      function updateVoiceBadge(speakerType) {
        const trans = TRANSLATIONS[currentUiLang];
        const valEl = document.getElementById('voiceVal');
        if (!valEl) return;
        if (speakerType === 'male') {
          valEl.textContent = trans.voiceMale;
          valEl.style.color = '#3aa8ff';
        } else if (speakerType === 'female') {
          valEl.textContent = trans.voiceFemale;
          valEl.style.color = '#a78bfa';
        } else if (speakerType === 'child') {
          valEl.textContent = trans.voiceChild;
          valEl.style.color = '#34d399';
        } else {
          valEl.textContent = trans.voiceDetecting;
          valEl.style.color = '#7c9cff';
        }
      }

      function findVoice(gender, bcpLang) {
        if (!window.speechSynthesis) return null;
        const voices = window.speechSynthesis.getVoices();
        const baseLang = bcpLang.split('-')[0].toLowerCase();
        
        const langVoices = voices.filter(v => 
          v.lang.toLowerCase() === bcpLang.toLowerCase() || 
          v.lang.toLowerCase().startsWith(baseLang)
        );
        
        if (langVoices.length === 0) return null;

        const maleKeywords = [
          'male', 'david', 'george', 'ravi', 'tolga', 'mark', 'pavel', 
          'stefan', 'heiko', 'daniel', 'sean', 'richard', 'james', 'karsten', 
          'stefano', 'paul', 'filip', 'lusz', 'prakash', 'siddharth'
        ];
        
        const femaleKeywords = [
          'female', 'emel', 'zira', 'hazel', 'susan', 'heera', 'haruka', 
          'yuna', 'helen', 'linda', 'catherine', 'zofia', 'anri', 'tessa',
          'google', 'elsbeth', 'moira', 'sin-ji', 'mei-jia'
        ];

        if (gender === 'male') {
          let voice = langVoices.find(v => 
            maleKeywords.some(kw => v.name.toLowerCase().includes(kw))
          );
          if (voice) return voice;
          voice = langVoices.find(v => 
            !femaleKeywords.some(kw => v.name.toLowerCase().includes(kw))
          );
          if (voice) return voice;
        } else {
          let voice = langVoices.find(v => 
            femaleKeywords.some(kw => v.name.toLowerCase().includes(kw))
          );
          if (voice) return voice;
          voice = langVoices.find(v => 
            !maleKeywords.some(kw => v.name.toLowerCase().includes(kw))
          );
          if (voice) return voice;
        }
        return langVoices[0];
      }

      // Mobil tarayıcılarda (iOS/Android) ses çalma kilidini açmak için
      let ttsUnlocked = false;

      function unlockTTS() {
        if (ttsUnlocked || !window.speechSynthesis) return;
        try {
          const silentUtterance = new SpeechSynthesisUtterance(' ');
          silentUtterance.volume = 0;
          window.speechSynthesis.speak(silentUtterance);
          ttsUnlocked = true;
          console.log("TTS unlocked successfully");
        } catch (e) {
          console.error("TTS unlock failed", e);
        }
      }
      window.addEventListener('click', unlockTTS, { once: true });
      window.addEventListener('touchstart', unlockTTS, { once: true });
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = () => { window.speechSynthesis.getVoices(); };
      }

      function speak(text, langCode) {
        if (!window.speechSynthesis) return;
        
        unlockTTS();
        
        const utter = new SpeechSynthesisUtterance(text);
        const bcpLang = getBCP47Language(langCode);
        utter.lang = bcpLang;
        
        const speakerType = getDetectedSpeakerType();
        updateVoiceBadge(speakerType);

        const voiceGender = (speakerType === 'male') ? 'male' : 'female';
        
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        if (!isIOS) {
          const selectedVoice = findVoice(voiceGender, bcpLang);
          if (selectedVoice) {
            utter.voice = selectedVoice;
          }
        }

        if (speakerType === 'male') {
          utter.pitch = 0.85;
          utter.rate = 0.98;
        } else if (speakerType === 'female') {
          utter.pitch = 1.1;
          utter.rate = 1.0;
        } else if (speakerType === 'child') {
          utter.pitch = 1.5;
          utter.rate = 1.08;
        }
        
        utter.volume = 1.0;
        currentUtterance = utter;
        
        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel();
          setTimeout(() => {
            window.speechSynthesis.speak(utter);
          }, 50);
        } else {
          window.speechSynthesis.speak(utter);
        }
      }

      function updateStatusText() {
        const trans = TRANSLATIONS[currentUiLang];
        if (statusState === 'ready') {
          statusEl.textContent = trans.statusReady;
          statusEl.style.color = '#f4f7fb';
        } else if (statusState === 'listening') {
          statusEl.textContent = trans.statusListening;
          statusEl.style.color = '#9fe5b5';
        } else if (statusState === 'stopped') {
          statusEl.textContent = trans.statusStopped;
          statusEl.style.color = '#f4f7fb';
        } else if (statusState === 'reconnecting') {
          statusEl.textContent = trans.statusReconnecting;
          statusEl.style.color = '#ffb3b3';
        } else if (statusState === 'no-support') {
          statusEl.textContent = trans.statusNoSupport;
          statusEl.style.color = '#ffb3b3';
        } else if (statusState === 'error-network') {
          statusEl.textContent = trans.statusNetworkErr;
          statusEl.style.color = '#ffb3b3';
        } else if (statusState === 'error-permission') {
          statusEl.textContent = trans.statusPermissionErr;
          statusEl.style.color = '#ffb3b3';
        }
      }

      function updateButtonTexts() {
        const trans = TRANSLATIONS[currentUiLang];
        const isActive = (listening || shouldBeListening);
        toggleBtn.textContent = isActive ? trans.stopMic : trans.startMic;
        if (isActive) {
          toggleBtn.classList.add('recording');
        } else {
          toggleBtn.classList.remove('recording');
        }
        ttsToggleBtn.textContent = ttsEnabled ? trans.soundOn : trans.soundOff;
        clearBtn.textContent = trans.clearBtn;
      }

      function applyTranslations(lang) {
        const trans = TRANSLATIONS[lang];
        
        document.title = trans.brandName;
        document.querySelector('.brand-name').textContent = trans.brandName;
        document.getElementById('appTitle').textContent = trans.title;
        document.getElementById('appSubtitle').textContent = trans.subtitle;
        document.getElementById('lblSourceLang').textContent = trans.srcLangLabel;
        document.getElementById('lblTargetLang').textContent = trans.tgtLangLabel;
        document.getElementById('lblPanelSpeech').textContent = trans.panelSpeech;
        document.getElementById('lblPanelTranslation').textContent = trans.panelTranslation;
        document.getElementById('appHint').textContent = trans.hint;
        
        if (document.getElementById('lblVoiceType')) {
          document.getElementById('lblVoiceType').textContent = trans.lblVoiceType;
        }
        
        const voiceValEl = document.getElementById('voiceVal');
        if (voiceValEl) {
          const currentText = voiceValEl.textContent.trim();
          const prevTrans = TRANSLATIONS[lang === 'tr' ? 'en' : 'tr'];
          if (currentText === prevTrans.voiceMale) voiceValEl.textContent = trans.voiceMale;
          else if (currentText === prevTrans.voiceFemale) voiceValEl.textContent = trans.voiceFemale;
          else if (currentText === prevTrans.voiceChild) voiceValEl.textContent = trans.voiceChild;
          else if (currentText === prevTrans.voiceDetecting) voiceValEl.textContent = trans.voiceDetecting;
        }

        const sourceSelect = document.getElementById('sourceLang');
        const targetSelect = document.getElementById('targetLang');
        const optionsMap = {
          "tr": trans.langTr,
          "en": trans.langEn,
          "de": trans.langDe,
          "fr": trans.langFr,
          "es": trans.langEs,
          "it": trans.langIt,
          "nl": trans.langNl,
          "pt": trans.langPt,
          "ru": trans.langRu,
          "ar": trans.langAr,
          "zh": trans.langZh,
          "ja": trans.langJa,
          "ko": trans.langKo
        };
        [sourceSelect, targetSelect].forEach(select => {
          Array.from(select.options).forEach(opt => {
            if (optionsMap[opt.value]) {
              opt.textContent = optionsMap[opt.value];
            }
          });
        });

        updateButtonTexts();
        updateStatusText();

        const placeholders = ['Bekliyor...', 'Waiting...', 'Çeviri burada görünür.', 'Translation appears here.'];
        if (placeholders.includes(transcriptEl.textContent.trim())) {
          transcriptEl.textContent = trans.waiting;
        }
        if (placeholders.includes(translationEl.textContent.trim())) {
          translationEl.textContent = trans.translationHere;
        }

        if (lang === 'tr') {
          document.getElementById('uiLangTR').classList.add('active');
          document.getElementById('uiLangEN').classList.remove('active');
        } else {
          document.getElementById('uiLangTR').classList.remove('active');
          document.getElementById('uiLangEN').classList.add('active');
        }
      }

      if (!recognition) {
        statusState = 'no-support';
        updateStatusText();
        toggleBtn.disabled = true;
      } else {
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = getBCP47Language(sourceLang.value);

        recognition.onstart = () => {
          listening = true;
          consecutiveErrors = 0;
          statusState = 'listening';
          updateStatusText();
          updateButtonTexts();
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          
          if (event.error === 'no-speech' || event.error === 'aborted') {
            return;
          }

          consecutiveErrors++;

          if (event.error === 'network') {
            if (consecutiveErrors >= 3) {
              statusState = 'error-network';
              updateStatusText();
              shouldBeListening = false;
              recognition.stop();
              stopAudioAnalysis();
              document.getElementById('voiceBadgeContainer').style.display = 'none';
            } else {
              statusState = 'reconnecting';
              updateStatusText();
            }
          } else if (event.error === 'not-allowed') {
            statusState = 'error-permission';
            updateStatusText();
            shouldBeListening = false;
            recognition.stop();
            stopAudioAnalysis();
            document.getElementById('voiceBadgeContainer').style.display = 'none';
          } else {
            statusEl.style.color = '#ffb3b3';
            statusEl.textContent = (currentUiLang === 'tr' ? 'Ses tanıma hatası: ' : 'Speech recognition error: ') + event.error;
          }
        };

        recognition.onend = () => {
          listening = false;
          
          if (shouldBeListening) {
            clearTimeout(reconnectTimer);
            reconnectTimer = setTimeout(() => {
              if (shouldBeListening) {
                try {
                  recognition.lang = getBCP47Language(sourceLang.value);
                  recognition.start();
                } catch (e) {
                  console.error('Yeniden başlatma başarısız:', e);
                }
              }
            }, 1000);
          } else {
            statusState = 'stopped';
            updateStatusText();
            updateButtonTexts();
          }
        };

        recognition.onresult = (event) => {
          let interimText = '';
          let finalText = '';
          let hasFinal = false;
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            const text = result[0].transcript.trim();
            if (result.isFinal) {
              finalText += (finalText ? ' ' : '') + text;
              hasFinal = true;
            } else {
              interimText += (interimText ? ' ' : '') + text;
            }
          }

          if (hasFinal) {
            firstSentenceFinished = true;
          }

          const fullText = [finalText, interimText].filter(Boolean).join(' ');
          transcriptEl.textContent = fullText;

          if (firstSentenceFinished && fullText && fullText !== lastSentText) {
            lastSentText = fullText;
            
            clearTimeout(translateTimer);
            translateTimer = setTimeout(() => {
              translateText(fullText, hasFinal);
            }, 50);
          }
        };
      }

      toggleBtn.addEventListener('click', () => {
        if (!recognition) return;
        if (listening || shouldBeListening) {
          shouldBeListening = false;
          listening = false;
          clearTimeout(reconnectTimer);
          try {
            recognition.stop();
          } catch(e) {
            console.error(e);
          }
          statusState = 'stopped';
          updateStatusText();
          updateButtonTexts();
          
          stopAudioAnalysis();
          document.getElementById('voiceBadgeContainer').style.display = 'none';
        } else {
          shouldBeListening = true;
          consecutiveErrors = 0;
          firstSentenceFinished = false;
          recognition.lang = getBCP47Language(sourceLang.value);
          try {
            recognition.start();
          } catch(e) {
            statusEl.textContent = (currentUiLang === 'tr' ? 'Başlatma hatası: ' : 'Startup error: ') + e.message;
          }
          
          startAudioAnalysis();
          document.getElementById('voiceVal').textContent = TRANSLATIONS[currentUiLang].voiceDetecting;
          document.getElementById('voiceBadgeContainer').style.display = 'flex';
        }
      });

      ttsToggleBtn.addEventListener('click', () => {
        ttsEnabled = !ttsEnabled;
        updateButtonTexts();
        if (ttsEnabled) {
          ttsToggleBtn.classList.remove('secondary');
          ttsToggleBtn.classList.add('active-tts');
        } else {
          ttsToggleBtn.classList.remove('active-tts');
          ttsToggleBtn.classList.add('secondary');
          if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
          }
        }
      });

      document.getElementById('uiLangTR').addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentUiLang !== 'tr') {
          currentUiLang = 'tr';
          applyTranslations(currentUiLang);
        }
      });

      document.getElementById('uiLangEN').addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentUiLang !== 'en') {
          currentUiLang = 'en';
          applyTranslations(currentUiLang);
        }
      });

      clearBtn.addEventListener('click', () => {
        const trans = TRANSLATIONS[currentUiLang];
        transcriptEl.textContent = trans.waiting;
        translationEl.textContent = trans.translationHere;
        lastSentText = '';
        firstSentenceFinished = false;
        if (window.speechSynthesis) {
          window.speechSynthesis.cancel();
        }
        pitchHistory = [];
        document.getElementById('voiceVal').textContent = trans.voiceDetecting;
        document.getElementById('voiceVal').style.color = '#7c9cff';
      });

      async function translateText(text, isFinal = false) {
        try {
          const source_code = sourceLang.value;
          const target_code = targetLang.value;
          const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${source_code}&tl=${target_code}&dt=t&q=${encodeURIComponent(text)}`;
          
          const response = await fetch(url);
          const data = await response.json();
          
          let translated = "";
          if (data && data[0]) {
            data[0].forEach(chunk => {
              if (chunk && chunk[0]) {
                translated += chunk[0];
              }
            });
          }
          
          translationEl.textContent = translated || (currentUiLang === 'tr' ? 'Çeviri bulunamadı.' : 'Translation not found.');
          if (isFinal && ttsEnabled && translated) {
            speak(translated, targetLang.value);
            pitchHistory = [];
          }
        } catch (e) {
          translationEl.textContent = (currentUiLang === 'tr' ? 'Çeviri hatası: ' : 'Translation error: ') + e.message;
        }
      }

      function showQrModal() {
        const modal = document.getElementById('qrModal');
        const img = document.getElementById('qrImg');
        const link = document.getElementById('qrLink');
        const currentUrl = window.location.href;
        
        link.textContent = currentUrl;
        img.src = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(currentUrl)}&bgcolor=ffffff&color=08131f&margin=0`;
        modal.style.display = 'flex';
      }

      function closeQrModal() {
        document.getElementById('qrModal').style.display = 'none';
      }

      // Swap languages button functionality
      const swapLangBtn = document.getElementById('swapLangBtn');
      swapLangBtn.addEventListener('click', () => {
        const temp = sourceLang.value;
        sourceLang.value = targetLang.value;
        targetLang.value = temp;
        
        if (listening) {
          shouldBeListening = true;
          recognition.stop();
        }
      });

      // Initialize UI language to English at startup
      applyTranslations(currentUiLang);
    </script>

    <!-- Mobil QR Modal -->
    <div id="qrModal" style="display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.85);backdrop-filter:blur(8px);align-items:center;justify-content:center;" onclick="closeQrModal()">
      <div style="background:#08131f;border:1px solid rgba(255,255,255,0.12);border-radius:20px;padding:30px;max-width:360px;width:90%;text-align:center;box-shadow:0 20px 45px rgba(0,0,0,0.5);" onclick="event.stopPropagation()">
        <h3 style="margin-top:0;margin-bottom:8px;font-size:18px;color:#fff;">📱 Mobil Erişim</h3>
        <p style="font-size:13px;color:#b8c2cf;margin-bottom:20px;">Aşağıdaki QR kodu taratarak çeviriye cep telefonunuzdan erişebilirsiniz.</p>
        <div style="background:#fff;padding:12px;border-radius:12px;display:inline-block;margin-bottom:16px;">
          <img id="qrImg" src="" alt="QR Code" style="width:160px;height:160px;display:block;">
        </div>
        <div style="font-size:12px;color:#3aa8ff;word-break:break-all;font-family:monospace;margin-bottom:20px;" id="qrLink"></div>
        <button onclick="closeQrModal()" style="width:100%;padding:10px;background:#3aa8ff;color:#fff;border:none;border-radius:10px;font-weight:bold;cursor:pointer;">Kapat</button>
      </div>
    </div>
  </body>
</html>
"""

class MyHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Keep logs clean by ignoring standard requests logging
        pass

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            body = HTML_CONTENT.encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def run_server():
    server = HTTPServer((HOST, PORT), MyHandler)
    print(f"[*] Server started at http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        sys.exit(0)
