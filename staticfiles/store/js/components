import React from 'react';

const Vignette = ({ children, className = '', intensity = 'subtle' }) => {
  // Intensity presets for the vignette effect
  const intensityMap = {
    subtle: 'bg-[radial-gradient(circle_at_center,transparent_0%,transparent_75%,rgba(10,10,12,0.3)_100%)]',
    light: 'bg-[radial-gradient(circle_at_center,transparent_0%,transparent_70%,rgba(10,10,12,0.4)_100%)]',
    medium: 'bg-[radial-gradient(circle_at_center,transparent_0%,transparent_60%,rgba(10,10,12,0.5)_100%)]',
    strong: 'bg-[radial-gradient(circle_at_center,transparent_0%,transparent_50%,rgba(10,10,12,0.6)_100%)]'
  };

  return (
    <div className={`relative ${className}`}>
      {/* Vignette overlay */}
      <div 
        className={`absolute inset-0 pointer-events-none ${intensityMap[intensity] || intensityMap.subtle}`}
        style={{
          mixBlendMode: 'multiply',
        }}
        aria-hidden="true"
      />
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

export default Vignette; 