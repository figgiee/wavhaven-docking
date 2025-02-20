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
        wavesurfer: null,
        howl: null,
        queue: [],
        originalQueue: [],
        currentIndex: -1,
        isLoading: false,
        error: null,
        isMinimized: false,

        init() {
            // Initialize WaveSurfer with improved configuration
            this.wavesurfer = WaveSurfer.create({
                container: '#waveform',
                height: 48,
                waveColor: 'rgba(255, 255, 255, 0.2)',
                progressColor: 'rgba(255, 255, 255, 0.8)',
                cursorColor: 'rgba(255, 255, 255, 0.5)',
                barWidth: 2,
                barGap: 1,
                barRadius: 3,
                responsive: true,
                interact: true,
                hideScrollbar: true,
                normalize: true,
                partialRender: true,
                pixelRatio: 1,
            });

            // WaveSurfer event listeners
            this.wavesurfer.on('ready', () => {
                this.isLoading = false;
                if (this.howl && this.isPlaying) {
                    this.howl.play();
                }
            });

            this.wavesurfer.on('error', (err) => {
                console.error('WaveSurfer error:', err);
                this.error = 'Error loading audio visualization';
            });

            // Load volume from localStorage
            const savedVolume = localStorage.getItem('playerVolume');
            if (savedVolume !== null) {
                this.volume = parseInt(savedVolume);
            }

            // Handle keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                
                if (e.code === 'Space' && this.currentTrack) {
                    e.preventDefault();
                    this.togglePlay();
                } else if (e.code === 'ArrowLeft' && e.altKey && this.currentTrack) {
                    this.previousTrack();
                } else if (e.code === 'ArrowRight' && e.altKey && this.currentTrack) {
                    this.nextTrack();
                } else if (e.code === 'KeyM' && this.currentTrack) {
                    this.toggleMute();
                } else if (e.code === 'KeyR') {
                    this.toggleLoop();
                } else if (e.code === 'KeyS') {
                    this.toggleShuffle();
                } else if (e.code === 'KeyF') {
                    this.toggleFavorite();
                }
            });

            // Listen for track play events
            window.addEventListener('play-track', (event) => {
                const track = event.detail;
                if (this.currentTrack?.id !== track.id) {
                    this.loadTrack(track);
                } else {
                    this.togglePlay();
                }
            });
        },

        loadTrack(track) {
            this.isLoading = true;
            this.error = null;
            this.currentTrack = track;
            this.isMinimized = false;

            // Check if track is favorited
            fetch(`/api/favorites/check/${track.id}/`)
                .then(response => response.json())
                .then(data => {
                    this.isFavorite = data.is_favorite;
                })
                .catch(error => {
                    console.error('Error checking favorite status:', error);
                });

            // Check if track is in cart
            fetch(`/api/cart/check/${track.id}/`)
                .then(response => response.json())
                .then(data => {
                    this.isInCart = data.in_cart;
                })
                .catch(error => {
                    console.error('Error checking cart status:', error);
                });

            // Stop current audio if playing
            if (this.howl) {
                this.howl.unload();
            }

            // Create new Howl instance
            this.howl = new Howl({
                src: [track.audioUrl],
                html5: true,
                volume: this.volume / 100,
                onplay: () => {
                    this.isPlaying = true;
                    requestAnimationFrame(this.step.bind(this));
                },
                onpause: () => {
                    this.isPlaying = false;
                },
                onstop: () => {
                    this.isPlaying = false;
                },
                onend: () => {
                    this.isPlaying = false;
                    if (this.loopMode === 'one') {
                        this.howl.play();
                    } else if (this.loopMode === 'all' && !this.hasNextTrack) {
                        this.currentIndex = -1;
                        this.nextTrack();
                    } else {
                        this.nextTrack();
                    }
                },
                onloaderror: (id, err) => {
                    console.error('Howler load error:', err);
                    this.error = 'Error loading audio file';
                    this.isLoading = false;
                },
                onplayerror: (id, err) => {
                    console.error('Howler play error:', err);
                    this.error = 'Error playing audio file';
                    this.isLoading = false;
                }
            });

            // Load waveform
            try {
                this.wavesurfer.load(track.audioUrl);
            } catch (err) {
                console.error('WaveSurfer load error:', err);
                this.error = 'Error loading audio visualization';
                this.isLoading = false;
            }

            // Update queue if track is not in current queue
            if (!this.queue.find(t => t.id === track.id)) {
                this.queue.push(track);
                this.originalQueue = [...this.queue];
                this.currentIndex = this.queue.length - 1;
            } else {
                this.currentIndex = this.queue.findIndex(t => t.id === track.id);
            }

            // Start playing
            this.play();
        },

        step() {
            if (this.howl && this.isPlaying) {
                const seek = this.howl.seek();
                this.wavesurfer.setCurrentTime(seek);
                requestAnimationFrame(this.step.bind(this));
            }
        },

        play() {
            if (!this.howl) return;
            this.howl.play();
            this.isPlaying = true;
        },

        togglePlay() {
            if (!this.currentTrack) return;
            
            if (this.isPlaying) {
                this.howl?.pause();
            } else {
                this.howl?.play();
            }
            this.isPlaying = !this.isPlaying;
        },

        seek(event) {
            if (!this.howl || !this.wavesurfer) return;
            
            const rect = event.currentTarget.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const percent = x / rect.width;
            const duration = this.howl.duration();
            const seekTime = duration * percent;
            
            this.howl.seek(seekTime);
            this.wavesurfer.setCurrentTime(seekTime);
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

        toggleShuffle() {
            this.isShuffled = !this.isShuffled;
            if (this.isShuffled) {
                // Save original queue
                this.originalQueue = [...this.queue];
                // Shuffle queue except current track
                const currentTrack = this.queue[this.currentIndex];
                const remainingTracks = this.queue.filter((_, i) => i !== this.currentIndex);
                for (let i = remainingTracks.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [remainingTracks[i], remainingTracks[j]] = [remainingTracks[j], remainingTracks[i]];
                }
                this.queue = [currentTrack, ...remainingTracks];
                this.currentIndex = 0;
            } else {
                // Restore original queue
                const currentTrack = this.currentTrack;
                this.queue = [...this.originalQueue];
                this.currentIndex = this.queue.findIndex(t => t.id === currentTrack.id);
            }
        },

        toggleLoop() {
            switch (this.loopMode) {
                case 'off': this.loopMode = 'all'; break;
                case 'all': this.loopMode = 'one'; break;
                case 'one': this.loopMode = 'off'; break;
            }
        },

        toggleFavorite() {
            if (!this.currentTrack) return;

            const method = this.isFavorite ? 'DELETE' : 'POST';
            fetch(`/api/favorites/${this.currentTrack.id}/`, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                this.isFavorite = !this.isFavorite;
                // Show success message
                this.showMessage(data.message);
            })
            .catch(error => {
                console.error('Error toggling favorite:', error);
                this.error = 'Error updating favorite status';
            });
        },

        addToCart() {
            if (!this.currentTrack || this.isInCart) return;

            fetch('/api/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    beat_id: this.currentTrack.id
                })
            })
            .then(response => response.json())
            .then(data => {
                this.isInCart = true;
                // Show success message
                this.showMessage(data.message);
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
                this.error = 'Error adding to cart';
            });
        },

        showMessage(message) {
            this.error = null;
            // You could implement a toast notification system here
            console.log(message);
        },

        minimizePlayer() {
            this.isMinimized = !this.isMinimized;
        },

        nextTrack() {
            if (!this.hasNextTrack) {
                if (this.loopMode === 'all') {
                    this.currentIndex = -1;
                    this.nextTrack();
                }
                return;
            }
            this.currentIndex++;
            this.loadTrack(this.queue[this.currentIndex]);
        },

        previousTrack() {
            if (!this.hasPreviousTrack) return;
            this.currentIndex--;
            this.loadTrack(this.queue[this.currentIndex]);
        },

        get currentTime() {
            return this.formatTime(this.howl?.seek() || 0);
        },

        get duration() {
            return this.formatTime(this.howl?.duration() || 0);
        },

        get progress() {
            if (!this.howl) return 0;
            return (this.howl.seek() / this.howl.duration()) * 100;
        },

        get volumeIcon() {
            if (this.isMuted || this.volume === 0) return 'fa-volume-mute';
            if (this.volume < 33) return 'fa-volume-off';
            if (this.volume < 67) return 'fa-volume-down';
            return 'fa-volume-up';
        },

        get hasNextTrack() {
            return this.currentIndex < this.queue.length - 1 || this.loopMode === 'all';
        },

        get hasPreviousTrack() {
            return this.currentIndex > 0;
        },

        formatTime(seconds) {
            if (!seconds) return '0:00';
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
    }));
}); 