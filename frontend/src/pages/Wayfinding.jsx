import React, { useState, useEffect } from 'react';
import { Navigation, Camera, MapPin, Compass, Map, Navigation2 } from 'lucide-react';

const poiData = {
    Sections: ['Premium Section G', 'Premium Section H', 'Standard Block D', 'Standard Block F', 'Gondola B', 'Press Box South'],
    Washrooms: ['Block A Washroom (Men)', 'Block A Washroom (Women)', 'Gate C Restrooms', 'Premium Suite Bathrooms'],
    Gates: ['Gate A Entry', 'Gate B Exit', 'Gate C Entry', 'Gate D Exit']
};

export default function Wayfinding() {
  const [locationGranted, setLocationGranted] = useState(false);
  const [category, setCategory] = useState('Sections');
  const [destination, setDestination] = useState('');
  const [activeRoute, setActiveRoute] = useState(null); // The route actually being walked
  const [distance, setDistance] = useState(0);

  // Triggered when destination is confirmed via form
  const handleRouteSelect = (e) => {
      e.preventDefault();
      // Generate a mock realistic distance depending on destination string length just to vary the walk
      const mockInitialDist = 120 + destination.length * 3;
      setActiveRoute(destination);
      setDistance(mockInitialDist);
  };

  useEffect(() => {
    // Simulate walking closer to destination if we have a parsed target
    if (distance > 0 && activeRoute) {
        const interval = setInterval(() => {
        setDistance(prev => {
            if (prev <= 10) {
            clearInterval(interval);
            return 0;
            }
            // Faster walking down longer distances
            const marchRate = prev > 100 ? 5 : 2;
            return prev - marchRate;
        });
        }, 1000);
        return () => clearInterval(interval);
    }
  }, [distance, activeRoute]);

  // Stage 1: Location Permission Gate
  if (!locationGranted) {
      return (
          <div className="glass-panel" style={{ maxWidth: '600px', margin: '60px auto', padding: '50px', textAlign: 'center' }}>
             <Compass size={72} color="var(--stadium-green)" style={{ margin: '0 auto 25px auto' }} />
             <h2 style={{ marginBottom: '20px', fontSize: '2rem' }}>Location Access Required</h2>
             <p style={{ color: 'var(--text-muted)', marginBottom: '40px', lineHeight: '1.6', fontSize: '1.1rem' }}>
                 ArenaMaxx AR Wayfinding requires access to your device's location to correctly trace routes and calculate vectors from your current viewport to the destination.
             </p>
             <button 
                className="btn-primary" 
                onClick={() => setLocationGranted(true)}
                style={{ width: '100%', justifyContent: 'center', padding: '15px', fontSize: '1.1rem', fontWeight: 'bold', borderRadius: '10px' }}>
                    Allow Location Services
             </button>
             <button 
                onClick={() => window.history.back()}
                style={{ background: 'none', border: 'none', color: '#64748b', marginTop: '25px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1rem' }}>
                    Cancel & Return
             </button>
          </div>
      );
  }

  // Stage 2: Selection Menu Layer mapped alongside AR
  return (
    <div style={{ maxWidth: '850px', margin: '0 auto', paddingBottom: '40px' }}>
      
      {/* Route Dashboard UI */}
       <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: 0, marginBottom: '20px', fontSize: '1.3rem', color: '#1e293b' }}><Map size={24} color="var(--stadium-green)" /> Plot Destination</h2>
          
          <form onSubmit={handleRouteSelect} className="content-flex" style={{ alignItems: 'flex-end' }}>
              <div style={{ flex: 1, width: '100%' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase' }}>Category</label>
                  <select 
                     value={category} 
                     onChange={(e) => {
                         setCategory(e.target.value);
                         setDestination(''); 
                     }}
                     style={{ width: '100%', padding: '12px', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#f8fafc', fontSize: '1rem', color: '#1e293b' }}
                  >
                      <option value="Sections">Seating Sections</option>
                      <option value="Washrooms">Washrooms</option>
                      <option value="Gates">Exterior Gates</option>
                  </select>
              </div>
              
              <div style={{ flex: 2, width: '100%' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase' }}>Location Point</label>
                  <select 
                     value={destination} 
                     onChange={(e) => setDestination(e.target.value)}
                     style={{ width: '100%', padding: '12px', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#ffffff', fontSize: '1rem', color: '#1e293b' }}
                  >
                      <option value="" disabled>Select physical route...</option>
                      {poiData[category].map(loc => (
                          <option key={loc} value={loc}>{loc}</option>
                      ))}
                  </select>
              </div>
              
              <button 
                 type="submit" 
                 disabled={!destination}
                 className="btn-primary" 
                 style={{ padding: '12px 20px', fontSize: '1rem', fontWeight: 'bold', opacity: !destination ? 0.5 : 1, cursor: !destination ? 'not-allowed' : 'pointer', height: '48px', minWidth: '120px' }}>
                     Plot Route
              </button>
          </form>
       </div>

      {/* AR View Layer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '1.8rem', margin: 0 }}>Live Camera View</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', backgroundColor: '#f1f5f9', padding: '8px 15px', borderRadius: '20px', fontSize: '0.9rem', fontWeight: 'bold' }}>
          <Camera size={18} />
          <span>Camera Simulated</span>
        </div>
      </div>

      <div className="glass-panel" style={{ 
        position: 'relative', 
        height: '550px', 
        backgroundColor: activeRoute ? '#111827' : '#f8fafc', 
        overflow: 'hidden',
        borderRadius: '24px',
        border: '3px solid',
        borderColor: activeRoute ? '#334155' : '#e2e8f0',
        transition: 'all 0.5s ease',
        boxShadow: activeRoute ? 'inset 0 0 50px rgba(0,0,0,0.5)' : 'none'
      }}>
        
        {!activeRoute ? (
            // Empty State
            <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: '#94a3b8' }}>
                <Navigation2 size={72} style={{ marginBottom: '25px', opacity: 0.3 }} />
                <h3 style={{ margin: 0, fontSize: '1.5rem', color: '#64748b' }}>Awaiting Routing Feed</h3>
                <p style={{ marginTop: '10px' }}>Select a destination and click Plot Route to initialize overlay.</p>
            </div>
        ) : (
            // Active AR Render
            <>
                <div style={{
                position: 'absolute',
                inset: 0,
                backgroundSize: '80px 80px',
                backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.03) 2px, transparent 2px), linear-gradient(to bottom, rgba(255,255,255,0.03) 2px, transparent 2px)'
                }}></div>

                {/* HUD Elements */}
                <div style={{ position: 'absolute', top: '30px', left: '30px', right: '30px', display: 'flex', justifyContent: 'space-between', color: 'white' }}>
                <div style={{ background: 'rgba(0,0,0,0.6)', padding: '15px 25px', borderRadius: '15px', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{ fontSize: '0.9rem', opacity: 0.7, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '5px' }}>Navigating To</div>
                    <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>{activeRoute}</div>
                </div>
                
                <div style={{ background: 'var(--stadium-green)', color: 'white', padding: '15px 25px', borderRadius: '15px', fontWeight: 'bold', fontSize: '1.5rem', display: 'flex', alignItems: 'center', boxShadow: '0 4px 15px rgba(34, 197, 94, 0.4)' }}>
                    {distance}m
                </div>
                </div>

                {/* Dynamic AR Arrow Overlay */}
                <div style={{
                position: 'absolute',
                top: '55%',
                left: '50%',
                transform: `translate(-50%, -50%) perspective(600px) rotateX(${distance < 30 ? 0 : 40}deg)`,
                transition: 'all 0.5s ease',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center'
                }}>
                {distance > 0 ? (
                    <>
                    <Navigation size={100} color="var(--stadium-green)" style={{ filter: 'drop-shadow(0 10px 20px rgba(34, 197, 94, 0.6))' }} />
                    <div style={{ color: 'var(--stadium-green)', fontWeight: 'bold', marginTop: '30px', fontSize: '1.5rem', textShadow: '0 2px 10px rgba(0,0,0,0.8)' }}>
                        {distance < 50 ? 'Turn Left Ahead' : 'Keep Straight'}
                    </div>
                    </>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', animation: 'pulse 2s infinite' }}>
                      <MapPin size={100} color="#3b82f6" style={{ filter: 'drop-shadow(0 0 20px rgba(59, 130, 246, 0.8))' }} />
                      <div style={{ color: '#3b82f6', fontWeight: 'bold', marginTop: '30px', fontSize: '1.8rem', textShadow: '0 2px 10px rgba(0,0,0,0.8)' }}>
                          You Have Arrived
                      </div>
                    </div>
                )}
                </div>
            </>
        )}
      </div>
    </div>
  );
}
