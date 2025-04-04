document.addEventListener('alpine:init', () => {
    Alpine.data('audioPlayer', () => ({
        currentTrack: null,
        isPlaying: false,
        volume: 100,
        isMuted: false,
        previousVolume: 75,
        isFavorite: false,
        isInCart: false,
        isShuffled: false,
        loopMode: 'off', // 'off', 'all', 'one'
        howl: null,
        queue: [],
        originalQueue: [],
        currentIndex: -1,
        isLoading: false,
        error: null,
        isMinimized: false,
        currentTime: 0,
        duration: 0,
        
        // Audio visualization properties
        analyser: null,
        audioSource: null,
        dataArray: null,
        animationFrame: null,
        canvas: null,
        canvasCtx: null,
        barWidth: 2,
        barGap: 1,
        barCount: 70,
        reconnectAttempts: 0,

        init() {
            // Load volume from localStorage
            const savedVolume = localStorage.getItem('playerVolume');
            if (savedVolume !== null) {
                this.volume = parseInt(savedVolume);
            }

            // Initialize canvas for visualization
            this.$nextTick(() => {
                this.canvas = this.$refs.visualizer;
                if (this.canvas) {
                    this.canvasCtx = this.canvas.getContext('2d');
                    this.resizeCanvas();
                    window.addEventListener('resize', () => this.resizeCanvas());
                }
            });

            // Clean up on page unload
            window.addEventListener('beforeunload', () => this.cleanup());
        },

        resizeCanvas() {
            if (!this.canvas) return;
            
            const container = this.canvas.parentElement;
            this.canvas.width = container.offsetWidth;
            this.canvas.height = container.offsetHeight;
            
            // Recalculate bar dimensions
            this.barWidth = Math.max(2, Math.floor(this.canvas.width / (this.barCount * 1.5)));
            this.barGap = Math.max(1, Math.floor(this.barWidth * 0.3));
        },

        initializeVisualization() {
            // Use Howler's AudioContext
            const ctx = Howler.ctx;
            
            if (!ctx) {
                console.warn('Howler AudioContext not available');
                return;
            }

            // Create analyzer if it doesn't exist
            if (!this.analyser) {
                this.analyser = ctx.createAnalyser();
                this.analyser.fftSize = 256;
                this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            }

            // Resume context if suspended
            if (ctx.state === 'suspended') {
                ctx.resume();
            }
        },

        disconnectAudioNodes() {
            try {
                if (this.analyser) {
                    this.analyser.disconnect();
                }
            } catch (error) {
                console.warn('Error disconnecting audio nodes:', error);
            }
        },

        connectAudioNodes() {
            if (!this.howl?._sounds[0]) {
                console.warn('No Howl sound available to connect');
                return false;
            }

            try {
                const ctx = Howler.ctx;
                if (!ctx) {
                    console.warn('Howler AudioContext not available');
                    return false;
                }

                // Get Howler's internal nodes
                const sound = this.howl._sounds[0];
                
                // Wait until Howler has created its internal nodes
                if (!sound._node) {
                    if (this.reconnectAttempts < 3) {
                        this.reconnectAttempts++;
                        setTimeout(() => this.connectAudioNodes(), 50 * Math.pow(2, this.reconnectAttempts));
                        return false;
                    }
                    console.warn('Howler nodes not ready after retries');
                    return false;
                }

                // Disconnect existing nodes
                this.disconnectAudioNodes();

                // Get or create the analyser node
                if (!this.analyser) {
                    this.analyser = ctx.createAnalyser();
                    this.analyser.fftSize = 256;
                    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
                }

                // Connect our analyser to Howler's node chain
                const gainNode = sound._node;
                gainNode.disconnect();
                gainNode.connect(this.analyser);
                this.analyser.connect(ctx.destination);

                return true;
            } catch (error) {
                console.warn('Audio visualization connection error:', error);
                if (this.reconnectAttempts < 3) {
                    this.reconnectAttempts++;
                    setTimeout(() => this.connectAudioNodes(), 50 * Math.pow(2, this.reconnectAttempts));
                    return false;
                }
                console.error('Failed to connect audio nodes after 3 attempts');
                return false;
            }
        },

        draw() {
            if (!this.analyser || !this.canvas || !this.isPlaying) {
                if (this.animationFrame) {
                    cancelAnimationFrame(this.animationFrame);
                    this.animationFrame = null;
                }
                return;
            }

            this.animationFrame = requestAnimationFrame(() => this.draw());

            const width = this.canvas.width;
            const height = this.canvas.height;
            const centerY = height / 2;

            this.analyser.getByteFrequencyData(this.dataArray);
            this.canvasCtx.clearRect(0, 0, width, height);

            // Calculate total width of all bars and gaps
            const totalBars = this.barCount;
            const totalWidth = (this.barWidth + this.barGap) * totalBars - this.barGap;
            let startX = (width - totalWidth) / 2;

            for (let i = 0; i < totalBars; i++) {
                // Get frequency value
                const dataIndex = Math.floor(i * this.analyser.frequencyBinCount / totalBars);
                const value = this.dataArray[dataIndex];
                
                // Calculate bar height based on frequency value
                const barHeight = (value / 255) * (height / 2);
                
                // Draw mirrored bars
                this.canvasCtx.fillStyle = `rgba(99, 102, 241, ${0.3 + (value / 255) * 0.7})`;
                
                // Top bar
                this.canvasCtx.fillRect(
                    startX,
                    centerY - barHeight,
                    this.barWidth,
                    barHeight
                );
                
                // Bottom bar (mirrored)
                this.canvasCtx.fillRect(
                    startX,
                    centerY,
                    this.barWidth,
                    barHeight
                );
                
                startX += this.barWidth + this.barGap;
            }
        },

        loadTrack(track) {
            if (!track?.audioUrl) {
                console.error('Invalid track data');
                return;
            }

            this.isLoading = true;
            this.error = null;
            this.reconnectAttempts = 0;

            try {
                // Clean up previous track completely
                this.cleanup();

                // Initialize visualization using Howler's context
                this.initializeVisualization();

                // Create new Howl instance
                this.howl = new Howl({
                    src: [track.audioUrl],
                    html5: true,
                    volume: this.volume / 100,
                    format: ['mp3', 'wav'],
                    onload: () => {
                        this.duration = this.howl.duration();
                        this.isLoading = false;
                        this.currentTrack = track;

                        // Wait for the first 'play' event to set up visualization
                        this.howl.once('play', () => {
                            // Wait for Howler to fully set up its nodes
                            requestAnimationFrame(() => {
                                // Start visualization only after a successful connection
                                if (this.connectAudioNodes()) {
                                    this.draw();
                                }
                            });
                            this.startTimeUpdate();
                        });

                        this.howl.play();
                        this.isPlaying = true;
                        this.dispatchPlayState();
                    },
                    onplay: () => {
                        this.isPlaying = true;
                        this.startTimeUpdate();
                        this.dispatchPlayState();
                    },
                    onpause: () => {
                        this.isPlaying = false;
                        this.stopTimeUpdate();
                        this.dispatchPlayState();
                    },
                    onstop: () => {
                        this.isPlaying = false;
                        this.currentTime = 0;
                        this.stopTimeUpdate();
                        this.dispatchPlayState();
                    },
                    onend: () => {
                        this.handleTrackEnd();
                        this.stopTimeUpdate();
                        this.dispatchPlayState();
                    },
                    onseek: () => {
                        this.currentTime = this.howl.seek();
                    },
                    onloaderror: (id, error) => {
                        console.error('Error loading audio:', error);
                        this.handleError('Error loading audio file');
                    },
                    onplayerror: (id, error) => {
                        console.error('Error playing audio:', error);
                        this.handleError('Error playing audio file');
                        // Try to recover from playback errors
                        this.cleanup();
                        setTimeout(() => this.loadTrack(track), 1000);
                    }
                });
            } catch (error) {
                console.error('Error initializing audio player:', error);
                this.handleError('Error initializing audio player');
            }
        },

        startTimeUpdate() {
            this.timeUpdateInterval = setInterval(() => {
                if (this.howl && this.isPlaying) {
                    this.currentTime = this.howl.seek();
                }
            }, 1000);
        },

        stopTimeUpdate() {
            if (this.timeUpdateInterval) {
                clearInterval(this.timeUpdateInterval);
            }
        },

        togglePlay() {
            if (!this.currentTrack) return;
            
            if (this.isPlaying) {
                this.howl?.pause();
            } else {
                this.howl?.play();
            }
        },

        updateVolume() {
            if (this.howl) {
                this.howl.volume(this.volume / 100);
            }
            this.isMuted = this.volume === 0;
            localStorage.setItem('playerVolume', this.volume);
        },

        toggleMute() {
            if (this.isMuted) {
                this.volume = this.previousVolume;
                this.isMuted = false;
            } else {
                this.previousVolume = this.volume;
                this.volume = 0;
                this.isMuted = true;
            }
            this.updateVolume();
        },

        seek(position) {
            if (this.howl) {
                this.howl.seek(position * this.duration);
            }
        },

        nextTrack() {
            if (this.queue.length === 0) return;
            
            this.currentIndex = (this.currentIndex + 1) % this.queue.length;
            const nextTrack = this.queue[this.currentIndex];
            this.loadTrack(nextTrack);
        },

        previousTrack() {
            if (this.queue.length === 0) return;
            
            this.currentIndex = this.currentIndex <= 0 ? this.queue.length - 1 : this.currentIndex - 1;
            const prevTrack = this.queue[this.currentIndex];
            this.loadTrack(prevTrack);
        },

        toggleShuffle() {
            this.isShuffled = !this.isShuffled;
            if (this.isShuffled) {
                this.originalQueue = [...this.queue];
                this.queue = this.shuffleArray([...this.queue]);
            } else {
                this.queue = [...this.originalQueue];
            }
        },

        toggleLoop() {
            const modes = ['off', 'all', 'one'];
            const currentIndex = modes.indexOf(this.loopMode);
            this.loopMode = modes[(currentIndex + 1) % modes.length];
        },

        shuffleArray(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
            return array;
        },

        formatTime(seconds) {
            if (!seconds) return '0:00';
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        },

        cleanup() {
            this.stopTimeUpdate();
            
            // Clean up Howler instance
            if (this.howl) {
                try {
                    // Disconnect our analyser if it exists
                    if (this.analyser) {
                        this.analyser.disconnect();
                    }
                    
                    // Restore Howler's original connections
                    const sound = this.howl._sounds[0];
                    if (sound && sound._node) {
                        sound._node.disconnect();
                        sound._node.connect(Howler.ctx.destination);
                    }
                } catch (error) {
                    console.warn('Error cleaning up audio nodes:', error);
                }

                this.howl.off();  // Remove all event listeners
                this.howl.unload();
                this.howl = null;
            }

            // Clean up animation
            if (this.animationFrame) {
                cancelAnimationFrame(this.animationFrame);
                this.animationFrame = null;
            }

            // Reset state
            this.currentTrack = null;
            this.isPlaying = false;
            this.reconnectAttempts = 0;
            this.dispatchPlayState();
        },

        updatePlayState() {
            if (!this.currentTrack) return;
            
            window.dispatchEvent(new CustomEvent('playstate-changed', {
                detail: {
                    trackId: this.currentTrack.id,
                    isPlaying: this.isPlaying
                }
            }));
        },

        handleTrackEnd() {
            if (this.loopMode === 'one') {
                this.howl.play();
            } else if (this.loopMode === 'all' && !this.hasNextTrack) {
                this.currentIndex = -1;
                this.nextTrack();
            } else {
                this.nextTrack();
            }
        },

        handleError(errorMessage) {
            this.error = errorMessage;
            this.isLoading = false;
        },

        setupVisualization() {
            this.draw();
        }
    }));
}); 