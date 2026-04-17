import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Ticket, Map, CalendarDays, KeyRound, ArrowRight } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();
  const [matchCode, setMatchCode] = useState('');

  const handleCodeSubmit = (e) => {
    e.preventDefault();
    if (matchCode.trim() !== '') {
      navigate('/dashboard');
    }
  };

  const matches = [
    { id: 1, team: "Arena FC vs Spartans", date: "Oct 14, 2026", time: "18:00", avail: "High" },
    { id: 2, team: "IPL: Mumbai Indians vs CSK", date: "Oct 21, 2026", time: "19:30", avail: "Limited" },
    { id: 3, team: "Global Athletics Meet", date: "Nov 02, 2026", time: "09:00", avail: "High" },
  ];

  return (
    <div style={{ minHeight: '100dvh', backgroundColor: '#f8fafc', display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
      <header style={{ padding: '20px 40px', backgroundColor: 'white', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'center' }}>
        <h1 
          className="hover-opacity"
          onClick={() => window.location.reload()}
          style={{ margin: 0, color: 'var(--stadium-green)', display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', transition: 'opacity 0.2s ease' }}
        >
          <Map size={32} /> ArenaMaxx
        </h1>
      </header>

      <main className="landing-container" style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'flex-start', padding: '20px' }}>
        <div className="landing-main" style={{ marginTop: '20px' }}>
          
          {/* Find Next Matches Panel */}
          <div className="glass-panel" style={{ flex: 1, padding: '40px' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: 0, color: '#334155' }}>
              <CalendarDays /> Find Next Matches
            </h2>
            <p style={{ color: '#64748b', marginBottom: '30px' }}>Select an upcoming event to explore the arena layout and book your tickets instantly.</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {matches.map(m => (
                <div key={m.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <div>
                    <strong style={{ display: 'block', fontSize: '1.15rem', color: '#0f172a', marginBottom: '5px' }}>{m.team}</strong>
                    <span style={{ color: '#64748b', fontSize: '0.9rem' }}>{m.date} • {m.time}</span>
                  </div>
                  <button 
                    onClick={() => navigate('/tickets')} 
                    style={{ backgroundColor: 'var(--stadium-green)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 'bold', fontSize: '1rem' }}
                    onMouseOver={(e) => e.target.style.opacity = '0.9'}
                    onMouseOut={(e) => e.target.style.opacity = '1'}
                  >
                    Tickets <ArrowRight size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="landing-divider" style={{ width: '2px', backgroundColor: '#e2e8f0', alignSelf: 'stretch' }}></div>

          {/* Attendee Portal Panel */}
          <div className="glass-panel" style={{ flex: 1, padding: '40px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: 0, color: '#334155' }}>
              <Ticket /> Attending a Match?
            </h2>
            <p style={{ color: '#64748b', marginBottom: '30px', lineHeight: '1.6' }}>Already have a ticket? Enter your match code to access the live stadium dashboard, order concessions, and use AR wayfinding.</p>

            <form onSubmit={handleCodeSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', border: '2px solid #e2e8f0', borderRadius: '8px', padding: '8px 15px', backgroundColor: 'white' }}>
                <KeyRound size={24} color="#94a3b8" style={{ marginRight: '15px' }} />
                <input 
                  type="text" 
                  placeholder="Enter Match Code (e.g. AX-202) ..."
                  value={matchCode}
                  onChange={(e) => setMatchCode(e.target.value)}
                  style={{ flex: 1, border: 'none', outline: 'none', padding: '10px 0', fontSize: '1.2rem', color: '#334155' }}
                />
              </div>
              <button 
                type="submit" 
                className="btn-primary" 
                disabled={matchCode.trim() === ''}
                style={{ 
                  justifyContent: 'center', 
                  padding: '16px', 
                  fontSize: '1.2rem', 
                  opacity: matchCode.trim() ? 1 : 0.5, 
                  cursor: matchCode.trim() ? 'pointer' : 'not-allowed',
                  marginTop: '10px',
                  borderRadius: '8px'
                }}
              >
                Access Dashboard
              </button>
            </form>
          </div>

        </div>
      </main>
    </div>
  );
}
