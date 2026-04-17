import React, { useEffect, useState } from 'react';
import '../assets/splash.css';

export default function SplashScreen({ onComplete }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // The entire animation resolves in ~4.5s. Unmount at 5s.
    const timer = setTimeout(() => {
      setVisible(false);
      if (onComplete) onComplete();
    }, 4500);
    
    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!visible) return null;

  return (
    <div className="splash-container">
      
      {/* 1. The Athlete Slideshow */}
      <div className="athlete-slideshow-container">
        <div className="athlete-slide slide-1" style={{ backgroundImage: "url('/soccer_static.png')" }}></div>
        <div className="athlete-slide slide-2" style={{ backgroundImage: "url('/tennis_static.png')" }}></div>
        <div className="athlete-slide slide-3" style={{ backgroundImage: "url('/batter_static.png')" }}></div>
      </div>
      
      {/* 2. Ball Block Deleted */}
      
      {/* 3. The Logo Reveal */}
      <div className="splash-logo-container">
        <div className="splash-logo-text">ArenaMaxx</div>
        <div className="splash-sub">Platform Initializing...</div>
      </div>
      
    </div>
  );
}
