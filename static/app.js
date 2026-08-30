let pollInterval;
let audioContext;
let analyser;
let source;
let animationId;

async function generateAudio() {
    const text = document.getElementById('chapterText').value.trim();
    const btn = document.getElementById('generateBtn');
    const statusContainer = document.getElementById('statusContainer');
    const statusLabel = document.getElementById('statusLabel');
    const progressBar = document.getElementById('progressBar');
    const audioSection = document.getElementById('audioSection');
    const errorMsg = document.getElementById('errorMsg');
    const pulsingDot = document.getElementById('pulsingDot');
    const audioPlayer = document.getElementById('audioPlayer');

    if (!text) {
        showError("Please paste a chapter before generating.");
        return;
    }

    // Reset UI
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    errorMsg.style.display = 'none';
    audioSection.style.display = 'none';
    statusContainer.style.display = 'block';
    progressBar.style.width = '10%';
    pulsingDot.style.display = 'block';
    statusLabel.innerText = "Initializing connection...";
    
    // Stop any previous audio
    audioPlayer.pause();
    if (animationId) cancelAnimationFrame(animationId);

    try {
        const response = await fetch('/api/v1/upload-chapter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chapter_text: text })
        });

        if (!response.ok) throw new Error("Server rejected the request.");

        const data = await response.json();
        const jobId = data.id;

        // Start polling
        statusLabel.innerText = "Uploading chapter to Redis queue...";
        pollInterval = setInterval(() => checkStatus(jobId), 1500);

    } catch (err) {
        showError("Failed to connect to the server: " + err.message);
    }
}

async function checkStatus(jobId) {
    const statusLabel = document.getElementById('statusLabel');
    const progressBar = document.getElementById('progressBar');
    const audioSection = document.getElementById('audioSection');
    const audioPlayer = document.getElementById('audioPlayer');
    const btn = document.getElementById('generateBtn');
    const pulsingDot = document.getElementById('pulsingDot');

    try {
        const response = await fetch(`/api/v1/status/${jobId}`);
        const data = await response.json();

        const status = data.status;

        if (status === "Pending") {
            statusLabel.innerText = "In Queue (Waiting for Celery Worker)...";
            progressBar.style.width = '20%';
        } else if (status === "Processing Text") {
            statusLabel.innerText = "LangGraph Agent is writing the script...";
            progressBar.style.width = '50%';
        } else if (status === "processing_audio") {
            statusLabel.innerText = "Synthesizing AI voices concurrently with Edge-TTS...";
            progressBar.style.width = '80%';
        } else if (status === "Completed") {
            clearInterval(pollInterval);
            pulsingDot.style.display = 'none';
            statusLabel.innerText = "Finished successfully!";
            progressBar.style.width = '100%';
            
            // Show audio player
            audioPlayer.src = data.result_audio_url;
            audioSection.style.display = 'flex';
            
            // Init Visualizer once audio is ready
            const bgmTrack = data.script_json ? data.script_json.bgm_track : null;
            const sfxSchedule = data.script_json ? data.script_json.sfx_schedule : [];
            initVisualizer(bgmTrack, sfxSchedule);
            
            // Reset button
            btn.disabled = false;
            btn.innerHTML = 'Generate Another Scene';
        } else if (status === "Failed") {
            clearInterval(pollInterval);
            showError("Job failed during processing.");
        }

    } catch (err) {
        console.error("Polling error:", err);
    }
}

function showError(msg) {
    const btn = document.getElementById('generateBtn');
    const errorMsg = document.getElementById('errorMsg');
    const statusContainer = document.getElementById('statusContainer');
    
    clearInterval(pollInterval);
    statusContainer.style.display = 'none';
    errorMsg.innerText = msg;
    errorMsg.style.display = 'block';
    btn.disabled = false;
    btn.innerHTML = "Generate Audio Drama";
}

// ----------------------------------------------------
// Web Audio API Visualizer
// ----------------------------------------------------
function initVisualizer(bgmTrack = null, sfxSchedule = []) {
    const audioPlayer = document.getElementById('audioPlayer');
    const bgmPlayer = document.getElementById('bgmPlayer');
    const canvas = document.getElementById('visualizerCanvas');
    const ctx = canvas.getContext('2d');
    
    // Set up BGM
    if (bgmTrack) {
        bgmPlayer.src = `/static/bgm/${bgmTrack}.wav`;
        bgmPlayer.volume = 0.2; // Keep background music subtle
    } else {
        bgmPlayer.src = "";
    }
    
    // Set up SFX
    // Keep track of which SFX have already been played this loop
    let playedSfx = new Set();
    
    audioPlayer.ontimeupdate = () => {
        const currentTime = audioPlayer.currentTime;
        
        // Check if any SFX should be played
        if (sfxSchedule && sfxSchedule.length > 0) {
            sfxSchedule.forEach((sfxEvent, index) => {
                // If we've passed the trigger time by less than 0.5s and haven't played it yet
                if (currentTime >= sfxEvent.time && currentTime < sfxEvent.time + 0.5 && !playedSfx.has(index)) {
                    playedSfx.add(index);
                    
                    // Create a dynamic audio element for this SFX so they can overlap!
                    const sfxAudio = new Audio(`/static/sfx/${sfxEvent.sfx}.wav`);
                    sfxAudio.volume = 0.8;
                    sfxAudio.play().catch(e => console.log("Audio play blocked:", e));
                }
            });
        }
    };

    // Resize canvas to fit container properly
    const resizeCanvas = () => {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Only create audioContext once per page load to avoid warnings
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source = audioContext.createMediaElementSource(audioPlayer);
        source.connect(analyser);
        analyser.connect(audioContext.destination);
    }

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
        animationId = requestAnimationFrame(draw);

        analyser.getByteFrequencyData(dataArray);

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            barHeight = dataArray[i] / 2; // scale down height slightly

            // Create gradient for bars
            const gradient = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight);
            gradient.addColorStop(0, '#00f0ff');
            gradient.addColorStop(1, '#8a2be2');

            ctx.fillStyle = gradient;
            
            // Draw centered vertically from the bottom
            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            
            // Add a little glow effect on top of bars
            if(barHeight > 5) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                ctx.fillRect(x, canvas.height - barHeight - 2, barWidth, 2);
            }

            x += barWidth + 2;
        }
    }

    audioPlayer.onplay = () => {
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
        if (bgmPlayer.src && bgmPlayer.src !== window.location.href) {
            bgmPlayer.play();
        }
        draw();
    };
    
    audioPlayer.onpause = () => {
        bgmPlayer.pause();
        cancelAnimationFrame(animationId);
    };
    
    audioPlayer.onended = () => {
        bgmPlayer.pause();
        bgmPlayer.currentTime = 0;
        playedSfx.clear(); // Reset the SFX tracker for replay
    };
    
    // Also reset tracker if the user scrubs the audio manually
    audioPlayer.onseeked = () => {
        playedSfx.clear();
    };
}
