class ParticleEffect {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.mousePosition = { x: null, y: null };
    this.init();
    this.animate();
    this.addEventListeners();
  }

  init() {
    // Set canvas size
    this.resizeCanvas();
    
    // Create initial particles
    for (let i = 0; i < 150; i++) {  // Increased number of particles
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        radius: Math.random() * 3 + 2,  // Larger particles
        dx: (Math.random() - 0.5) * 1,  // Faster movement
        dy: (Math.random() - 0.5) * 1,
        opacity: Math.random() * 0.7 + 0.3  // More visible particles
      });
    }
  }

  resizeCanvas() {
    // Get the actual size of the container
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  addEventListeners() {
    window.addEventListener('resize', () => {
      this.resizeCanvas();
    });

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mousePosition.x = e.clientX - rect.left;
      this.mousePosition.y = e.clientY - rect.top;
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.mousePosition.x = null;
      this.mousePosition.y = null;
    });
  }

  drawParticle(particle) {
    this.ctx.beginPath();
    this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
    
    // Create gradient for each particle
    const gradient = this.ctx.createRadialGradient(
      particle.x, particle.y, 0,
      particle.x, particle.y, particle.radius
    );
    gradient.addColorStop(0, `rgba(99, 102, 241, ${particle.opacity})`);  // Indigo core
    gradient.addColorStop(1, `rgba(79, 70, 229, ${particle.opacity * 0.5})`);  // Purple edge
    
    this.ctx.fillStyle = gradient;
    this.ctx.fill();
  }

  drawConnections() {
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 150) {  // Increased connection distance
          this.ctx.beginPath();
          const opacity = 0.3 * (1 - distance / 150);  // Increased opacity
          this.ctx.strokeStyle = `rgba(99, 102, 241, ${opacity})`;
          this.ctx.lineWidth = 2;  // Thicker lines
          this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
          this.ctx.stroke();
        }
      }

      // Draw connections to mouse if nearby
      if (this.mousePosition.x !== null && this.mousePosition.y !== null) {
        const dx = this.particles[i].x - this.mousePosition.x;
        const dy = this.particles[i].y - this.mousePosition.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 200) {  // Increased mouse interaction distance
          this.ctx.beginPath();
          const opacity = 0.5 * (1 - distance / 200);  // Increased opacity
          this.ctx.strokeStyle = `rgba(99, 102, 241, ${opacity})`;
          this.ctx.lineWidth = 2;
          this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx.lineTo(this.mousePosition.x, this.mousePosition.y);
          this.ctx.stroke();
        }
      }
    }
  }

  updateParticles() {
    for (const particle of this.particles) {
      particle.x += particle.dx;
      particle.y += particle.dy;

      // Wrap around edges instead of bouncing
      if (particle.x < 0) particle.x = this.canvas.width;
      if (particle.x > this.canvas.width) particle.x = 0;
      if (particle.y < 0) particle.y = this.canvas.height;
      if (particle.y > this.canvas.height) particle.y = 0;
    }
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.updateParticles();
    this.drawConnections();
    
    for (const particle of this.particles) {
      this.drawParticle(particle);
    }

    requestAnimationFrame(() => this.animate());
  }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('particle-canvas');
  if (canvas) {
    new ParticleEffect(canvas);
  }
}); 