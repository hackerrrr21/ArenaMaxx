import React, { useEffect, useState } from 'react';
import socket from '../services/socket';
import { CalendarClock, Users, UserRound, Clock } from 'lucide-react';

export default function Washrooms() {
  const [washrooms, setWashrooms] = useState({ men: {}, women: {} });
  const [activeTab, setActiveTab] = useState('women');
  const [bookingMsg, setBookingMsg] = useState('');

  useEffect(() => {
    const handleStatus = (data) => {
        const splitData = { men: {}, women: {} };
        Object.entries(data).forEach(([key, block]) => {
            splitData.men[`${key}_m`] = { 
                ...block, 
                name: `${block.name} (Men's)`, 
                capacity: Math.floor(block.capacity / 2), 
                occupied: Math.floor(block.occupied / 2), 
                gender: 'men' 
            };
            splitData.women[`${key}_w`] = { 
                ...block, 
                name: `${block.name} (Women's)`, 
                capacity: Math.ceil(block.capacity / 2), 
                occupied: Math.max(0, Math.ceil(block.occupied / 2) + Math.floor(Math.random() * 3) - 1), 
                gender: 'women' 
            };
        });
        setWashrooms(splitData);
    };
    
    socket.on('washroom_status', handleStatus);
    return () => socket.off('washroom_status', handleStatus);
  }, []);

  const handleBook = (blockName) => {
    const baseUrl = import.meta.env.PROD ? '' : 'http://localhost:5000';
    fetch(`${baseUrl}/api/washrooms/book`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ block: blockName, time_slot: 'Next Available' })
    })
    .then(res => res.json())
    .then(data => {
      setBookingMsg(data.message || data.error || 'Booking updated.');
      setTimeout(() => setBookingMsg(''), 5000);
    })
    .catch(() => setBookingMsg('Could not connect to booking service.'));
  };

  return (
    <main className="glass-panel" style={{ padding: '40px', maxWidth: '850px', margin: '0 auto' }} role="main">
      <h1 style={{ fontSize: '2rem' }}>Washroom Live Status & Booking</h1>
      <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', marginBottom: '30px' }}>
        Check real-time availability and reserve a spot to avoid waiting in physical lines.
      </p>

      {/* Tabs Layout */}
      <div style={{ display: 'flex', gap: '15px', marginBottom: '30px', borderBottom: '2px solid #e2e8f0', paddingBottom: '25px' }}>
         <button 
            onClick={() => setActiveTab('women')}
            aria-pressed={activeTab === 'women'}
            aria-label="Show Women's Washrooms"
            style={{ flex: 1, padding: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', fontSize: '1.2rem', fontWeight: 'bold', border: 'none', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.3s ease', backgroundColor: activeTab === 'women' ? '#fce7f3' : '#f8fafc', color: activeTab === 'women' ? '#db2777' : '#64748b', boxShadow: activeTab === 'women' ? '0 4px 10px rgba(219, 39, 119, 0.2)' : 'none' }}>
            <Users size={24} aria-hidden="true" /> Women's Washrooms
         </button>
         <button 
            onClick={() => setActiveTab('men')}
            aria-pressed={activeTab === 'men'}
            aria-label="Show Men's Washrooms"
            style={{ flex: 1, padding: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', fontSize: '1.2rem', fontWeight: 'bold', border: 'none', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.3s ease', backgroundColor: activeTab === 'men' ? '#dbeafe' : '#f8fafc', color: activeTab === 'men' ? '#2563eb' : '#64748b', boxShadow: activeTab === 'men' ? '0 4px 10px rgba(37, 99, 235, 0.2)' : 'none' }}>
            <UserRound size={24} aria-hidden="true" /> Men's Washrooms
         </button>
      </div>

      {bookingMsg && (
        <div style={{ padding: '15px', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '8px', marginBottom: '20px', fontWeight: 'bold' }}>
          {bookingMsg}
        </div>
      )}

      <div style={{ display: 'grid', gap: '25px' }}>
        {Object.entries(washrooms[activeTab] || {}).map(([key, block]) => {
          const usage = (block.occupied / block.capacity) * 100;
          const isFull = usage >= 90;
          
          // Estimate calculation (1 minute per 2 people in queue if full)
          const waitTime = isFull ? Math.max(2, Math.floor(((usage - 90) * block.capacity / 100) / 2)) : 0;
          
          // Theme color dynamically mapped to active tab
          const themeColor = activeTab === 'women' ? '#db2777' : '#2563eb';
          
          return (
            <div key={key} className="glass-panel" style={{ padding: '30px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderLeft: `8px solid ${themeColor}` }}>
              <div style={{ flex: 1, paddingRight: '30px' }}>
                <h3 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.3rem' }}>
                   {block.name}
                   {isFull && <span style={{ padding: '4px 10px', backgroundColor: '#fee2e2', color: '#ef4444', fontSize: '0.8rem', borderRadius: '4px' }}>Queue Congested</span>}
                </h3>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', fontSize: '1.05rem', color: '#334155' }}>
                  <span>Capacity: {block.capacity} stalls</span>
                  <span style={{ color: isFull ? '#ef4444' : themeColor, fontWeight: 'bold' }}>
                    {isFull ? 'High Demand' : 'Available'} ({block.occupied} in use)
                  </span>
                </div>
                
                <div style={{ width: '100%', height: '12px', backgroundColor: '#e5e7eb', borderRadius: '6px', marginBottom: isFull ? '15px' : '0' }}>
                  <div style={{ 
                    width: `${Math.min(usage, 100)}%`, 
                    height: '100%', 
                    backgroundColor: isFull ? '#ef4444' : themeColor, 
                    borderRadius: '6px', 
                    transition: 'width 1s ease' 
                  }}></div>
                </div>
                
                {isFull && (
                   <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ef4444', fontSize: '1.05rem', fontWeight: 'bold' }}>
                      <Clock size={18} /> Estimated Wait Time: ~{waitTime} mins
                   </div>
                )}
              </div>
              
              <button 
                className="btn-primary" 
                onClick={() => handleBook(key)}
                disabled={isFull}
                style={{ height: 'fit-content', padding: '15px 20px', fontSize: '1.1rem', opacity: isFull ? 0.5 : 1, cursor: isFull ? 'not-allowed' : 'pointer', backgroundColor: themeColor, display: 'flex', alignItems: 'center', gap: '10px' }}
              >
                <CalendarClock size={20} /> Book Slot
              </button>
            </div>
          );
        })}
        {Object.keys(washrooms.women).length === 0 && <p role="status" aria-live="polite" style={{ color: '#64748b', textAlign: 'center', fontSize: '1.2rem' }}>Loading live sensor data...</p>}
      </div>
      {bookingMsg && (
        <div role="alert" aria-live="assertive" style={{ padding: '15px', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '8px', marginTop: '20px', fontWeight: 'bold' }}>
          {bookingMsg}
        </div>
      )}
    </main>
  );
}
