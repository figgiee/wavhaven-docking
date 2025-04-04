// Vignette.jsx - A component that adds a subtle darkening effect around the edges
const Vignette = {
    init() {
        return {
            // Component state
            opacity: 0.35, // Default opacity for the vignette effect
            
            // Initialize the component
            initVignette() {
                // Create the vignette gradient on mount
                this.createVignetteGradient();
                
                // Add resize listener for responsive updates
                window.addEventListener('resize', () => this.createVignetteGradient());
                
                // Clean up on component destroy
                this.$cleanup = () => {
                    window.removeEventListener('resize', () => this.createVignetteGradient());
                };
            },
            
            // Create the vignette gradient effect
            createVignetteGradient() {
                const canvas = this.$refs.canvas;
                if (!canvas) return;
                
                // Get the container dimensions
                const container = canvas.parentElement;
                const { width, height } = container.getBoundingClientRect();
                
                // Set canvas size with proper DPI scaling
                const dpr = window.devicePixelRatio || 1;
                canvas.width = width * dpr;
                canvas.height = height * dpr;
                
                // Get context and scale for DPI
                const ctx = canvas.getContext('2d');
                ctx.scale(dpr, dpr);
                
                // Create radial gradient
                const gradient = ctx.createRadialGradient(
                    width / 2, height / 2, 0,           // Inner circle center and radius
                    width / 2, height / 2, height / 1.5 // Outer circle center and radius
                );
                
                // Add gradient color stops
                gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');          // Center - transparent
                gradient.addColorStop(0.7, `rgba(0, 0, 0, ${this.opacity * 0.5})`); // Mid - semi-transparent
                gradient.addColorStop(1, `rgba(0, 0, 0, ${this.opacity})`);         // Edge - most opaque
                
                // Apply gradient
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, width, height);
            },
            
            // Update opacity
            setOpacity(value) {
                this.opacity = value;
                this.createVignetteGradient();
            }
        };
    }
};

// Register the component with Alpine.js
document.addEventListener('alpine:init', () => {
    Alpine.data('vignette', Vignette.init);
}); 