import React, { useEffect, useState } from 'react';
import socket from '../services/socket';
import { Activity, Users, ShieldAlert, LifeBuoy, AlertTriangle, ShieldCheck, Soup, X } from 'lucide-react';

// Help Modal Component internal to Dashboard
const HelpModal = ({ status, setStatus, setResponder, responder }) => {
  if (status === 'idle') return null;

  const handleSelect = (type) => {
    setStatus('searching');
    setTimeout(() => {
      let rType = 'MaxxKnight';
      let rName = 'Agent Davis';
      let rTime = '1 min 30 sec';
      
      if (type === 'food') {
         rType = 'MaxxVolunteers';
         rName = 'Sarah M.';
         rTime = '4 mins';
      } else if (type === 'women_sos') {
         rType = 'MaxxKnight (Priority)';
         rName = 'Officer Reyes';
         rTime = '45 seconds';
      }
      
      setResponder({ type: rType, name: rName, time: rTime });
      setStatus('dispatched');
    }, 2500);
  };

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(3px)', padding: '20px' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '400px', backgroundColor: 'white', padding: '30px', position: 'relative', boxShadow: '0 20px 40px rgba(0,0,0,0.2)' }}>
        <button onClick={() => setStatus('idle')} style={{ position: 'absolute', top: '15px', right: '15px', background: 'none', border: 'none', cursor: 'pointer' }}><X color="#64748b" /></button>
        
        {status === 'selecting' && (
          <div>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: 0, color: '#ef4444' }}>
               <LifeBuoy color="#ef4444" /> Emergency / Assistance
            </h2>
            <p style={{ color: '#64748b', marginBottom: '25px', lineHeight: '1.5' }}>What kind of help do you need right now? We will locate the nearest responder to assist you.</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button 
                onClick={() => handleSelect('food')} 
                style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '20px', backgroundColor: '#f1f5f9', color: '#334155', border: '1px solid #cbd5e1', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontWeight: 'bold' }}>
                <Soup size={28} color="#f59e0b" /> 
                <span style={{flex: 1, fontSize: '1.1rem'}}>Food Assistance / Spills<br/><small style={{color: '#64748b', fontWeight: 'normal', fontSize: '0.85rem'}}>Notify nearby MaxxVolunteers</small></span>
              </button>
              <button 
                onClick={() => handleSelect('women_sos')} 
                style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '20px', backgroundColor: '#fef2f2', color: '#b91c1c', border: '1px solid #fecaca', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontWeight: 'bold' }}>
                <AlertTriangle size={28} color="#ef4444" /> 
                <span style={{flex: 1, fontSize: '1.1rem'}}>Women's Safety (SOS)<br/><small style={{color: '#ef4444', fontWeight: 'normal', fontSize: '0.85rem'}}>Priority MaxxKnight response</small></span>
              </button>
              <button 
                onClick={() => handleSelect('guard')} 
                style={{ display: 'flex', alignItems: 'center', gap: '15px', padding: '20px', backgroundColor: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', borderRadius: '8px', cursor: 'pointer', textAlign: 'left', fontWeight: 'bold' }}>
                <ShieldCheck size={28} color="#22c55e" /> 
                <span style={{flex: 1, fontSize: '1.1rem'}}>General Security Assist<br/><small style={{color: '#166534', fontWeight: 'normal', fontSize: '0.85rem'}}>Request MaxxKnight personnel</small></span>
              </button>
            </div>
          </div>
        )}

        {status === 'searching' && (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
             <Activity size={48} color="#ef4444" style={{ margin: '0 auto', opacity: 0.8 }} />
             <h3 style={{ marginTop: '20px', color: '#334155' }}>Locating Nearest Responder...</h3>
             <p style={{ color: '#64748b' }}>Please stay in your current zone.</p>
          </div>
        )}

        {status === 'dispatched' && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ display: 'inline-flex', padding: '20px', backgroundColor: '#f0fdf4', borderRadius: '50%', marginBottom: '20px' }}>
              <ShieldCheck size={48} color="#22c55e" />
            </div>
            <h2 style={{ color: '#166534', margin: '0 0 10px 0' }}>Responder Assigned</h2>
            <div style={{ backgroundColor: '#f8fafc', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', textAlign: 'left', marginBottom: '20px', fontSize: '1.1rem' }}>
               <div style={{ marginBottom: '10px' }}><strong style={{ color: '#64748b', display: 'inline-block', width: '80px' }}>Service:</strong> {responder?.type}</div>
               <div style={{ marginBottom: '10px' }}><strong style={{ color: '#64748b', display: 'inline-block', width: '80px' }}>Name:</strong> <span style={{ fontWeight: 'bold' }}>{responder?.name}</span></div>
               <div><strong style={{ color: '#64748b', display: 'inline-block', width: '80px' }}>ETA:</strong> <span style={{ color: '#ef4444', fontWeight: 'bold' }}>{responder?.time}</span></div>
            </div>
            <button className="btn-primary" onClick={() => setStatus('idle')} style={{ width: '100%', justifyContent: 'center', padding: '15px', fontSize: '1.1rem' }}>Acknowledge & Close</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [crowdData, setCrowdData] = useState({ total: 0, positions: [] });
  const [washrooms, setWashrooms] = useState({});
  
  // States for Help Mechanism
  const [helpStatus, setHelpStatus] = useState('idle');
  const [responder, setResponder] = useState(null);

  useEffect(() => {
    socket.on('crowd_flow', (data) => {
      setCrowdData(data);
    });
    
    socket.on('washroom_status', (data) => {
      setWashrooms(data);
    });

    return () => {
      socket.off('crowd_flow');
      socket.off('washroom_status');
    };
  }, []);

  return (
    <div className="dashboard-page" style={{ position: 'relative', minHeight: '100vh', paddingTop: '10px' }}>
      <h1 className="dash-title">Stadium Live Overview</h1>
      
      <div className="stats-grid">
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '15px' }}>
          <Users size={32} color="var(--stadium-green)" />
          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Active Attendees</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{crowdData.total} Users</div>
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '15px' }}>
          <Activity size={32} color="#3b82f6" />
          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Queue Status</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>Moderate Flow</div>
          </div>
        </div>
        
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '15px' }}>
          <ShieldAlert size={32} color="#ef4444" />
          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Gate Congestion</div>
            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>Gate C - Busy</div>
          </div>
        </div>
      </div>

      <div className="content-flex">
        <div className="glass-panel" style={{ padding: '24px', flex: 2, display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginBottom: '20px', color: '#1e293b' }}>Venue Zone Density</h3>
          <p style={{ color: '#64748b', marginBottom: '25px', fontSize: '1.05rem' }}>Real-time sectoral congestion tracking.</p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
            {(() => {
              const zones = {
                'VIP Zone': 0,
                'Food Court': 0,
                'East Gate Area': 0,
                'West Gate Area': 0
              };
              
              crowdData.positions.forEach(p => {
                if (p.x < 400 && p.y < 300) zones['VIP Zone']++;
                else if (p.x >= 400 && p.y < 300) zones['Food Court']++;
                else if (p.x >= 400 && p.y >= 300) zones['East Gate Area']++;
                else zones['West Gate Area']++;
              });
              
              const zoneCapacity = 25; // Adjusted local cap threshold mapped to mock array sizes
              
              return Object.entries(zones).map(([zoneName, count]) => {
                const usagePercent = Math.min((count / zoneCapacity) * 100, 100);
                let color = 'var(--stadium-green)';
                let statusText = 'Low Traffic';
                
                if (usagePercent > 80) {
                   color = '#ef4444'; // Red
                   statusText = 'Congested';
                } else if (usagePercent > 50) {
                   color = '#f59e0b'; // Amber
                   statusText = 'Moderate';
                }
                
                return (
                  <div key={zoneName} style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                      <span style={{ fontWeight: 'bold', fontSize: '1.1rem', color: '#1e293b' }}>{zoneName}</span>
                      <span style={{ color: color, fontWeight: 'bold' }}>{statusText} ({count} attendees)</span>
                    </div>
                    <div style={{ width: '100%', height: '14px', backgroundColor: '#e2e8f0', borderRadius: '7px' }}>
                      <div style={{ 
                        width: `${usagePercent}%`, 
                        height: '100%', 
                        backgroundColor: color, 
                        borderRadius: '7px', 
                        transition: 'width 1s ease, background-color 1s ease',
                        boxShadow: `0 0 10px ${color}40`
                      }}></div>
                    </div>
                  </div>
                );
              });
            })()}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginBottom: '25px', color: '#1e293b' }}>Gate Information</h3>
          
          <div style={{ marginBottom: '25px' }}>
             <h4 style={{ color: '#64748b', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', marginBottom: '15px', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '0.05em' }}>Entry Gates</h4>
             
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', backgroundColor: '#f8fafc', borderRadius: '8px', marginBottom: '12px', border: '1px solid #e2e8f0' }}>
                <span style={{ fontWeight: 'bold', color: '#334155' }}>Gate A</span>
                <span style={{ padding: '6px 12px', backgroundColor: '#f1f5f9', color: '#64748b', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 'bold' }}>Closed (Opens 18:00)</span>
             </div>
             
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', backgroundColor: '#f0fdf4', borderRadius: '8px', marginBottom: '12px', border: '1px solid #bbf7d0' }}>
                <span style={{ fontWeight: 'bold', color: '#166534' }}>Gate C</span>
                <span style={{ padding: '6px 12px', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 'bold' }}>Open</span>
             </div>
          </div>
          
          <div>
             <h4 style={{ color: '#64748b', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', marginBottom: '15px', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '0.05em' }}>Exit Gates</h4>
             
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', backgroundColor: '#f0fdf4', borderRadius: '8px', marginBottom: '12px', border: '1px solid #bbf7d0' }}>
                <span style={{ fontWeight: 'bold', color: '#166534' }}>Gate B</span>
                <span style={{ padding: '6px 12px', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 'bold' }}>Open</span>
             </div>
             
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px', backgroundColor: '#f0fdf4', borderRadius: '8px', marginBottom: '12px', border: '1px solid #bbf7d0' }}>
                <span style={{ fontWeight: 'bold', color: '#166534' }}>Gate D</span>
                <span style={{ padding: '6px 12px', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 'bold' }}>Open</span>
             </div>
          </div>
        </div>
      </div>

      {/* Floating Action Button */}
      <button 
        onClick={() => setHelpStatus('selecting')}
        className="help-fab"
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
           <LifeBuoy size={34} />
           <span style={{ fontSize: '0.8rem', fontWeight: 'bold', marginTop: '4px' }}>HELP</span>
        </div>
      </button>

      <HelpModal status={helpStatus} setStatus={setHelpStatus} setResponder={setResponder} responder={responder} />
    </div>
  );
}
