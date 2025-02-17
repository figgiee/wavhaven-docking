document.addEventListener('alpine:init', () => {
    Alpine.data('audioPlayer', () => ({
        currentTrack: null,
        isPlaying: false,
        isMuted: false,
        isFavorite: false,
        volume: 80,
        audio: new Audio(),
        currentTime: 0,
        duration: 0,
        progress: 0,
        isVisible: false,
        queue: [],
        currentIndex: -1,

        init() {
            // Initialize audio player
            this.audio.addEventListener('ended', () => {
                this.isPlaying = false;
                this.nextTrack();
            });

            this.audio.addEventListener('timeupdate', () => {
                this.currentTime = this.audio.currentTime;
                this.progress = (this.currentTime / this.duration) * 100;
            });

            this.audio.addEventListener('loadedmetadata', () => {
                this.duration = this.audio.duration;
            });

            this.audio.addEventListener('play', () => {
                this.isPlaying = true;
                this.showPlayer();
            });

            this.audio.addEventListener('pause', () => {
                this.isPlaying = false;
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

            // Listen for add to queue events
            window.addEventListener('add-to-queue', (event) => {
                this.addToQueue(event.detail);
            });

            // Set initial volume
            this.audio.volume = this.volume / 100;

            // Handle keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                
                if (e.code === 'Space') {
                    e.preventDefault();
                    this.togglePlay();
                } else if (e.code === 'ArrowLeft' && e.altKey) {
                    this.previousTrack();
                } else if (e.code === 'ArrowRight' && e.altKey) {
                    this.nextTrack();
                }
            });
        },

        showPlayer() {
            this.isVisible = true;
            document.querySelector('.audio-player-container').classList.add('active');
        },

        hidePlayer() {
            if (!this.isPlaying) {
                this.isVisible = false;
                document.querySelector('.audio-player-container').classList.remove('active');
            }
        },

        loadTrack(track) {
            this.currentTrack = track;
            this.audio.src = track.audioUrl;
            this.play();
            
            // Update queue if track is not in current queue
            if (!this.queue.find(t => t.id === track.id)) {
                this.queue.push(track);
                this.currentIndex = this.queue.length - 1;
            } else {
                this.currentIndex = this.queue.findIndex(t => t.id === track.id);
            }
        },

        addToQueue(track) {
            this.queue.push(track);
            if (this.currentIndex === -1) {
                this.currentIndex = 0;
                this.loadTrack(track);
            }
        },

        play() {
            this.audio.play();
            this.isPlaying = true;
            this.showPlayer();
        },

        togglePlay() {
            if (this.isPlaying) {
                this.audio.pause();
            } else {
                this.audio.play();
            }
            this.isPlaying = !this.isPlaying;
        },

        toggleMute() {
            this.audio.muted = !this.audio.muted;
            this.isMuted = this.audio.muted;
        },

        toggleFavorite() {
            this.isFavorite = !this.isFavorite;
            // Add API call to save favorite status
        },

        nextTrack() {
            if (this.currentIndex < this.queue.length - 1) {
                this.currentIndex++;
                this.loadTrack(this.queue[this.currentIndex]);
            }
        },

        previousTrack() {
            if (this.currentIndex > 0) {
                this.currentIndex--;
                this.loadTrack(this.queue[this.currentIndex]);
            }
        },

        seek(event) {
            const rect = event.currentTarget.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const percent = x / rect.width;
            this.audio.currentTime = percent * this.duration;
        },

        updateVolume() {
            this.audio.volume = this.volume / 100;
            if (this.volume > 0) {
                this.audio.muted = false;
                this.isMuted = false;
            }
        },

        formatTime(seconds) {
            if (!seconds) return '0:00';
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
    }));
}); 