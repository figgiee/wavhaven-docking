import React from 'react';

export const Vignette = ({ children, intensity = 'medium' }) => {
  const getIntensityStyles = () => {
    switch (intensity) {
      case 'light':
        return 'bg-gradient-to-b from-black/40 to-transparent';
      case 'strong':
        return 'bg-gradient-to-b from-black/80 to-transparent';
      case 'medium':
      default:
        return 'bg-gradient-to-b from-black/60 to-transparent';
    }
  };

  return (
    <div className="relative">
      <div
        className={`absolute inset-0 pointer-events-none ${getIntensityStyles()}`}
        aria-hidden="true"
      />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}; 