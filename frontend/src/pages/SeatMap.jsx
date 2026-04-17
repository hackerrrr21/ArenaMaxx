import React, { useState } from 'react';
import { CreditCard, Info, ArrowLeft, Ticket } from 'lucide-react';

function describeSector(x, y, rInX, rInY, rOutX, rOutY, startAngle, endAngle) {
  const polarToCartesian = (centerX, centerY, radiusX, radiusY, angleInDegrees) => {
    var angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
      x: centerX + (radiusX * Math.cos(angleInRadians)),
      y: centerY + (radiusY * Math.sin(angleInRadians))
    };
  };

  const startOut = polarToCartesian(x, y, rOutX, rOutY, endAngle);
  const endOut = polarToCartesian(x, y, rOutX, rOutY, startAngle);
  const startIn = polarToCartesian(x, y, rInX, rInY, endAngle);
  const endIn = polarToCartesian(x, y, rInX, rInY, startAngle);

  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

  const d = [
    "M", startOut.x, startOut.y, 
    "A", rOutX, rOutY, 0, largeArcFlag, 0, endOut.x, endOut.y,
    "L", endIn.x, endIn.y,
    "A", rInX, rInY, 0, largeArcFlag, 1, startIn.x, startIn.y,
    "Z"
  ].join(" ");

  const midAngle = startAngle + (endAngle - startAngle) / 2;
  const midRadX = rInX + (rOutX - rInX) / 2;
  const midRadY = rInY + (rOutY - rInY) / 2;
  const centerPos = polarToCartesian(x, y, midRadX, midRadY, midAngle);

  return { d, centerPos };
}

export default function SeatMap() {
  const [selectedSection, setSelectedSection] = useState(null);
  const [selectedSpecificSeats, setSelectedSpecificSeats] = useState([]);

  const handleBook = () => {
    if (selectedSpecificSeats.length === 0) return;
    const seatNames = selectedSpecificSeats.map(s => `${s.row}${s.number}`).join(', ');
    alert(`Section ${selectedSection.id}, Seats: ${seatNames} Booked Successfully!`);
    setSelectedSpecificSeats([]);
    setSelectedSection(null);
  };

  const isAvailable = (id) => {
    const avail = ['106','107','109','112','114','115','116','117','119','122','125','M2','M7','M14','M15','M18','M21','M29','M32','210','211','212','213','216','217','218','220','221','226','227','228'];
    return avail.includes(id);
  };

  const handleSectionClick = (id, type, price, categoryColor) => {
    if (!isAvailable(id)) return;
    setSelectedSection({ id, type, price, categoryColor });
    setSelectedSpecificSeats([]); 
  };

  const toggleSeat = (row, number) => {
    const exists = selectedSpecificSeats.find(s => s.row === row && s.number === number);
    if (exists) {
      setSelectedSpecificSeats(selectedSpecificSeats.filter(s => s.row !== row || s.number !== number));
    } else {
      if (selectedSpecificSeats.length < 5) {
        setSelectedSpecificSeats([...selectedSpecificSeats, { row, number }]);
      } else {
        alert('You can only select up to 5 seats per transaction.');
      }
    }
  };

  const renderRings = () => {
    const cx = 500;
    const cy = 450;
    const items = [];

    // Ring 1 (Inner Premium - Green): 101 - 126
    const ring1OuterX = 300, ring1OuterY = 220;
    const ring1InnerX = 200, ring1InnerY = 140;
    const numRing1 = 26;
    for(let i=0; i<numRing1; i++) {
      const anglePerBlock = 360 / numRing1;
      const startG = i * anglePerBlock;
      const endG = startG + anglePerBlock - 1; 
      
      const id = `${101 + i}`;
      const sector = describeSector(cx, cy, ring1InnerX, ring1InnerY, ring1OuterX, ring1OuterY, startG, endG);
      
      if(startG > 250 && startG < 290) continue; 
      
      const avail = isAvailable(id);
      const isSelected = selectedSection?.id === id;
      const color = '#22c55e'; // Green
      
      items.push(
        <g key={id} onClick={() => handleSectionClick(id, 'Premium (Inner)', 4500, color)} style={{ cursor: avail ? 'pointer' : 'default' }}>
          <path d={sector.d} fill={isSelected ? '#000000' : (avail ? color : '#ffffff')} stroke={isSelected ? '#fde047' : '#cbd5e1'} strokeWidth={isSelected ? "4" : "2"} opacity={avail ? 1 : 0.6} />
          <text x={sector.centerPos.x} y={sector.centerPos.y} fill={avail ? 'white' : '#64748b'} fontSize="14" fontWeight="bold" textAnchor="middle" dominantBaseline="middle">
            {id}
          </text>
        </g>
      );
    }

    // Ring 2 (Middle Best - Blue): M1 - M34
    const ring2OuterX = 360, ring2OuterY = 280;
    const ring2InnerX = 305, ring2InnerY = 225;
    const numRing2 = 34;
    for(let i=0; i<numRing2; i++) {
      const anglePerBlock = 360 / numRing2;
      const startG = i * anglePerBlock;
      const endG = startG + anglePerBlock - 0.5;
      const id = `M${1 + i}`;
      const sector = describeSector(cx, cy, ring2InnerX, ring2InnerY, ring2OuterX, ring2OuterY, startG, endG);
      
      if(startG > 260 && startG < 280) continue; 

      const avail = isAvailable(id);
      const isSelected = selectedSection?.id === id;
      const color = '#3b82f6'; // Blue

      items.push(
        <g key={id} onClick={() => handleSectionClick(id, 'Best (Middle)', 2500, color)} style={{ cursor: avail ? 'pointer' : 'default' }}>
          <path d={sector.d} fill={isSelected ? '#000000' : (avail ? color : '#ffffff')} stroke={isSelected ? '#fde047' : '#cbd5e1'} strokeWidth={isSelected ? "4" : "2"} opacity={avail ? 1 : 0.6} />
          <text x={sector.centerPos.x} y={sector.centerPos.y} fill={avail ? 'white' : '#64748b'} fontSize="10" textAnchor="middle" dominantBaseline="middle">
            {id}
          </text>
        </g>
      );
    }

    // Ring 3 (Outer Standard - Yellow): 201 - 232
    const ring3OuterX = 430, ring3OuterY = 340;
    const ring3InnerX = 365, ring3InnerY = 285;
    const numRing3 = 32;
    for(let i=0; i<numRing3; i++) {
      const anglePerBlock = 360 / numRing3;
      const startG = i * anglePerBlock;
      const endG = startG + anglePerBlock - 0.5;
      const id = `${201 + i}`;
      const sector = describeSector(cx, cy, ring3InnerX, ring3InnerY, ring3OuterX, ring3OuterY, startG, endG);
      
      if(startG > 260 && startG < 280) continue; 

      const avail = isAvailable(id);
      const isSelected = selectedSection?.id === id;
      const color = '#eab308'; // Yellow

      items.push(
        <g key={id} onClick={() => handleSectionClick(id, 'Standard (Outer)', 1000, color)} style={{ cursor: avail ? 'pointer' : 'default' }}>
          <path d={sector.d} fill={isSelected ? '#000000' : (avail ? color : '#ffffff')} stroke={isSelected ? '#64748b' : '#cbd5e1'} strokeWidth={isSelected ? "4" : "2"} opacity={avail ? 1 : 0.6} />
          <text x={sector.centerPos.x} y={sector.centerPos.y} fill={avail ? 'white' : '#64748b'} fontSize="12" fontWeight="bold" textAnchor="middle" dominantBaseline="middle">
            {id}
          </text>
        </g>
      );
    }

    return items;
  };

  const renderStructures = () => {
    const cx = 500, cy = 450;
    const pb1 = describeSector(cx, cy, 440, 350, 470, 380, -45, 45); 
    const pb2 = describeSector(cx, cy, 480, 390, 510, 420, -50, 50);

    const gb1 = describeSector(cx, cy, 440, 350, 470, 380, 135, 225);
    const gb2 = describeSector(cx, cy, 480, 390, 510, 420, 130, 230);

    return (
      <g>
        {/* Top Press Boxes */}
        <path d={pb1.d} fill="white" stroke="#94a3b8" strokeWidth="2" />
        <text x="500" y={cy - 360} fontSize="16" fill="#334155" textAnchor="middle" fontWeight="800">PRESS BOX</text>

        <path d={pb2.d} fill="white" stroke="#94a3b8" strokeWidth="2" />
        <text x="500" y={cy - 400} fontSize="14" fill="#475569" textAnchor="middle" fontWeight="bold">PRESS BOX LEVEL 2</text>

        {/* Bottom Gondolas */}
        <path d={gb1.d} fill="white" stroke="#94a3b8" strokeWidth="2" />
        <text x="500" y={cy + 370} fontSize="16" fill="#334155" textAnchor="middle" fontWeight="800">LOWER GONDOLA</text>

        <path d={gb2.d} fill="white" stroke="#94a3b8" strokeWidth="2" />
        <text x="500" y={cy + 410} fontSize="14" fill="#475569" textAnchor="middle" fontWeight="bold">UPPER GONDOLA</text>

        {/* Entry/Exit Gates with outlines (Attached directly to boundary walls) */}
        {[
          { text: 'ENTRY A', x: 900, y: 160, rot: 35 },
          { text: 'EXIT B', x: 900, y: 740, rot: -35 },
          { text: 'ENTRY C', x: 100, y: 740, rot: 35 },
          { text: 'EXIT D', x: 100, y: 160, rot: -35 }
        ].map((gate, i) => (
          <g key={i} transform={`translate(${gate.x}, ${gate.y}) rotate(${gate.rot})`}>
            <rect x="-40" y="-18" width="80" height="36" rx="18" fill="white" stroke="var(--stadium-green)" strokeWidth="3" />
            <text x="0" y="5" fill="#334155" fontSize="11" fontWeight="bold" textAnchor="middle">{gate.text}</text>
          </g>
        ))}
      </g>
    );
  };

  const renderSpecificSeats = () => {
    const rows = ['A', 'B', 'C', 'D', 'E'];
    const cols = 10;
    
    return (
      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3 style={{ margin: 0 }}>Select Seats</h3>
          <button onClick={() => setSelectedSection(null)} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <ArrowLeft size={16} /> Back to Map
          </button>
        </div>
        
        <div style={{ width: '100%', height: '30px', backgroundColor: '#cbd5e1', borderRadius: '4px', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#64748b', fontSize: '0.7rem', fontWeight: 'bold', marginBottom: '15px', letterSpacing: '1px' }}>
          FIELD / PITCH DIRECTION
        </div>
 
        <div style={{ paddingBottom: '10px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', alignItems: 'center', overflowX: 'auto', overflowY: 'hidden', padding: '10px 0', webkitOverflowScrolling: 'touch' }}>
            {rows.map(row => (
              <div key={row} className="seat-row" style={{ minWidth: 'fit-content', padding: '0 10px' }}>
                <span style={{ width: '20px', fontWeight: 'bold', color: '#64748b', textAlign: 'center', flexShrink: 0, fontSize: '0.8rem' }}>{row}</span>
                {Array.from({ length: cols }).map((_, i) => {
                  const seatNum = i + 1;
                  const isTaken = (seatNum * row.charCodeAt(0)) % 7 === 0;
                  const isSelected = selectedSpecificSeats.find(s => s.row === row && s.number === seatNum);
 
                  return (
                    <button
                      key={`${row}${seatNum}`}
                      disabled={isTaken}
                      onClick={() => toggleSeat(row, seatNum)}
                      className="seat-btn"
                      style={{
                        border: isSelected ? '3px solid #111827' : 'none',
                        backgroundColor: isTaken ? '#cbd5e1' : selectedSection.categoryColor,
                        color: isTaken ? '#94a3b8' : 'white',
                        cursor: isTaken ? 'not-allowed' : 'pointer',
                        transition: 'transform 0.1s ease',
                        transform: isSelected ? 'scale(1.1)' : 'scale(1)',
                        opacity: isTaken ? 0.6 : (isSelected ? 1 : 0.8),
                        flexShrink: 0
                      }}
                    >
                      {seatNum}
                    </button>
                  )
                })}
              </div>
            ))}
          </div>
          <p className="mobile-only" style={{ textAlign: 'center', fontSize: '0.75rem', color: '#94a3b8', margin: '5px 0 0 0', fontStyle: 'italic' }}>← Swipe to see more seats →</p>
        </div>
        <p style={{textAlign:'center', fontSize: '0.85rem', color: '#64748b', marginTop: '15px'}}>Max 5 seats perfectly adjacent</p>
      </div>
    );
  };

  const totalPrice = selectedSection ? (selectedSpecificSeats.length * selectedSection.price) : 0;

  return (
    <div className="content-flex" style={{ gap: '30px' }}>
      <div className="glass-panel" style={{ flex: 3, padding: '20px', display: 'flex', justifyContent: 'center', backgroundColor: '#f8fafc', overflow: 'hidden' }}>
        <svg width="100%" height="auto" viewBox="-60 0 1120 900" style={{ maxWidth: '800px', height: 'auto', display: 'block' }}>
          
          {/* Big Stadium Boundary */}
          <g>
             <ellipse cx="500" cy="450" rx="530" ry="435" fill="#ffffff" stroke="#cbd5e1" strokeWidth="8" />
             <ellipse cx="500" cy="450" rx="550" ry="445" fill="none" stroke="#94a3b8" strokeWidth="2" strokeDasharray="10 10" />
          </g>
 
          {/* Pitch */}
          <g>
            <rect x="330" y="340" width="340" height="220" fill="#4ade80" stroke="#ffffff" strokeWidth="4" rx="110" opacity="0.9" />
            <path d="M 500 340 L 500 560" stroke="#ffffff" strokeWidth="3" opacity="0.6" />
            <circle cx="500" cy="450" r="35" fill="none" stroke="#ffffff" strokeWidth="3" opacity="0.6" />
            <text x="500" y="450" fill="rgba(255, 255, 255, 1)" fontSize="20" fontWeight="bold" textAnchor="middle" dominantBaseline="middle" textShadow="1px 1px 2px rgba(0,0,0,0.3)">PITCH</text>
          </g>
 
          {renderStructures()}
          {renderRings()}
        </svg>
      </div>
 
      <div className="glass-panel" style={{ flex: 1.5, padding: '30px', height: 'fit-content' }}>
        <h2>Ticket Selection</h2>
        
        {/* Pricing Legend */}
        <div style={{ display: 'flex', gap: '10px', fontSize: '0.85rem', margin: '15px 0', padding: '10px', background: '#f1f5f9', borderRadius: '8px', flexWrap: 'wrap' }}>
            <span style={{display:'flex', alignItems:'center', gap:'5px'}}><span style={{display:'block', width:12, height:12, background:'#22c55e', borderRadius:'50%'}}></span>Premium</span>
            <span style={{display:'flex', alignItems:'center', gap:'5px'}}><span style={{display:'block', width:12, height:12, background:'#3b82f6', borderRadius:'50%'}}></span>Best</span>
            <span style={{display:'flex', alignItems:'center', gap:'5px'}}><span style={{display:'block', width:12, height:12, background:'#eab308', borderRadius:'50%'}}></span>Standard</span>
        </div>

        {!selectedSection && (
          <div style={{ margin: '20px 0', padding: '15px', backgroundColor: '#e0f2fe', borderRadius: '8px', fontSize: '0.9rem', color: '#0369a1', display: 'flex', gap: '10px' }}>
            <Info size={20} />
            <p>Click on any highlighted section to view seats.</p>
          </div>
        )}

        {selectedSection && (
          <>
            <div style={{ marginTop: '10px', paddingBottom: '15px', borderBottom: '1px solid var(--glass-border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', fontSize: '1.2rem' }}>
                <span>Section</span>
                <strong style={{ color: selectedSection.categoryColor }}>{selectedSection.id}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span>Type</span>
                <strong>{selectedSection.type}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.2rem' }}>
                <span>Unit Price</span>
                <strong>₹{selectedSection.price}</strong>
              </div>
            </div>

            {renderSpecificSeats()}

            <div style={{ marginTop: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.3rem', marginBottom: '15px' }}>
                <span>Total ({selectedSpecificSeats.length} seats)</span>
                <strong>₹{totalPrice}</strong>
              </div>

              <button 
                className="btn-primary" 
                onClick={handleBook} 
                disabled={selectedSpecificSeats.length === 0}
                style={{ 
                  width: '100%', 
                  justifyContent: 'center', 
                  padding: '15px', 
                  fontSize: '1.1rem',
                  opacity: selectedSpecificSeats.length > 0 ? 1 : 0.5,
                  cursor: selectedSpecificSeats.length > 0 ? 'pointer' : 'not-allowed',
                  backgroundColor: selectedSection.categoryColor
                }}
              >
                <CreditCard size={20} />
                {selectedSpecificSeats.length > 0 
                  ? `Purchase ${selectedSpecificSeats.length} Tickets` 
                  : 'Select up to 5 seats'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
