import React, { useState, useEffect } from 'react';
import { ShoppingBag, Clock, Plus, Minus, Info } from 'lucide-react';

const MENU = [
  { id: 1, name: 'Stadium Vada Pav', price: 120 },
  { id: 2, name: 'Classic Chicken Burger', price: 350 },
  { id: 3, name: 'Masala Fries', price: 180 },
  { id: 4, name: 'Premium Beverage', price: 250 },
  { id: 5, name: 'Cold Coffee', price: 150 }
];

export default function Concessions() {
  const [cart, setCart] = useState([]);
  const [orderStatus, setOrderStatus] = useState(null);
  const [liveLoad, setLiveLoad] = useState('Low');

  useEffect(() => {
    // Simulate fetching stadium order load
    const loads = ['Low', 'Moderate', 'High', 'Steady'];
    const interval = setInterval(() => {
      setLiveLoad(loads[Math.floor(Math.random() * loads.length)]);
    }, 15000);
    return () => clearInterval(interval);
  }, []);
  
  const updateQuantity = (item, delta) => {
    setCart(prevCart => {
      const existing = prevCart.find(c => c.id === item.id);
      
      if (!existing) {
        if (delta > 0) return [...prevCart, { id: item.id, item, quantity: 1 }];
        return prevCart;
      }
      
      const newQuantity = existing.quantity + delta;
      
      if (newQuantity <= 0) {
        return prevCart.filter(c => c.id !== item.id);
      }
      
      // Enforce max 5
      if (newQuantity > 5) {
        return prevCart;
      }
      
      return prevCart.map(c => c.id === item.id ? { ...c, quantity: newQuantity } : c);
    });
  };

  const placeOrder = () => {
    const orderString = cart.map(c => `${c.quantity}x ${c.item.name}`).join(', ');
    const baseUrl = import.meta.env.PROD ? '' : 'http://localhost:5000';
    fetch(`${baseUrl}/api/concessions/order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items: orderString })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        setOrderStatus(data);
        setCart([]);
      }
    })
    .catch(() => alert('Could not place order. Please try again.'));
  };

  const total = cart.reduce((acc, curr) => acc + (curr.item.price * curr.quantity), 0);

  if (orderStatus) {
    return (
      <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', maxWidth: '600px', margin: '40px auto' }}>
        <Clock size={48} color="var(--stadium-green)" style={{ marginBottom: '20px' }} />
        <h2>Order Received!</h2>
        <div style={{ margin: '30px 0', fontSize: '1.2rem' }}>
          Your Virtual Queue Number is:<br/>
          <strong style={{ fontSize: '3rem', color: 'var(--stadium-green)' }}>#{orderStatus.queue_number}</strong>
        </div>
        <p style={{ color: 'var(--text-muted)' }}>Estimated wait time: {orderStatus.estimated_wait_mins} minutes</p>
        <p style={{ marginTop: '20px' }}>We will notify you when your order is ready for pickup at Pickup Counter 4.</p>
        <button className="btn-primary" onClick={() => setOrderStatus(null)} style={{ marginTop: '30px' }}>Order More</button>
      </div>
    );
  }

  return (
    <main className="content-flex" style={{ gap: '30px' }} role="main">
      <section className="glass-panel" style={{ flex: 2, padding: '30px' }} aria-label="Food and Beverage Menu">
        <h1>Food &amp; Beverages</h1>
        <div style={{ display: 'flex', gap: '15px', marginBottom: '25px', overflowX: 'auto', paddingBottom: '10px' }}>
          <div style={{ padding: '12px 20px', backgroundColor: '#f0fdf4', borderRadius: '12px', border: '1px solid #bbf7d0', minWidth: '180px' }}>
            <div style={{ fontSize: '0.8rem', color: '#166534', textTransform: 'uppercase', fontWeight: 'bold' }}>Queue Status</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#15803d', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={18} /> {liveLoad} Wait
            </div>
          </div>
          <div style={{ padding: '12px 20px', backgroundColor: '#eff6ff', borderRadius: '12px', border: '1px solid #bfdbfe', minWidth: '180px' }}>
            <div style={{ fontSize: '0.8rem', color: '#1e40af', textTransform: 'uppercase', fontWeight: 'bold' }}>Pickup Point</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#1d4ed8' }}>Level 2 South</div>
          </div>
          <div style={{ padding: '12px 20px', backgroundColor: '#fff7ed', borderRadius: '12px', border: '1px solid #fed7aa', minWidth: '180px' }}>
            <div style={{ fontSize: '0.8rem', color: '#9a3412', textTransform: 'uppercase', fontWeight: 'bold' }}>Live Offers</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#c2410c' }}>Free 500ml Water</div>
          </div>
        </div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Skip the line! Order from your seat and join the virtual queue.</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(1, 1fr)', gap: '15px' }}>
          {MENU.map(item => {
            const cartItem = cart.find(c => c.id === item.id);
            const qty = cartItem ? cartItem.quantity : 0;
            
            return (
              <div key={item.id} className="glass-panel" role="listitem" style={{ padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '1.1rem' }}>{item.name}</h4>
                  <div style={{ color: 'var(--stadium-green)', fontWeight: 'bold' }}>₹{item.price}</div>
                </div>
                
                {qty === 0 ? (
                  <button 
                    onClick={() => updateQuantity(item, 1)}
                    aria-label={`Add ${item.name} to cart`}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '6px',
                      border: '1px solid var(--stadium-green)',
                      background: 'transparent',
                      color: 'var(--stadium-green)',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    Add
                  </button>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px', backgroundColor: '#f8fafc', padding: '5px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <button 
                      onClick={() => updateQuantity(item, -1)}
                      aria-label={`Decrease ${item.name} quantity`}
                      style={{ padding: '6px', borderRadius: '4px', border: 'none', background: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                    >
                      <Minus size={16} color="#64748b" />
                    </button>
                    
                    <span style={{ fontWeight: 'bold', width: '20px', textAlign: 'center', fontSize: '1.1rem' }}>{qty}</span>
                    
                    <button 
                      onClick={() => updateQuantity(item, 1)}
                      disabled={qty >= 5}
                      aria-label={`Increase ${item.name} quantity`}
                      style={{ padding: '6px', borderRadius: '4px', border: 'none', background: qty >= 5 ? '#e2e8f0' : 'white', cursor: qty >= 5 ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                    >
                      <Plus size={16} color={qty >= 5 ? "#94a3b8" : "var(--stadium-green)"} />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <aside className="glass-panel" style={{ flex: 1, padding: '30px', height: 'fit-content' }} aria-label="Shopping Cart">
        <h2>Your Cart</h2>
        {cart.length > 0 ? (
          <div style={{ marginTop: '20px' }}>
            {cart.map(c => (
              <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span><span style={{ color: 'var(--text-muted)' }}>{c.quantity}x</span> {c.item.name}</span>
                <strong>₹{c.item.price * c.quantity}</strong>
              </div>
            ))}
            <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid var(--glass-border)' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', fontSize: '1.2rem' }}>
              <span>Total</span>
              <strong>₹{total}.00</strong>
            </div>
            <button className="btn-primary" onClick={placeOrder} style={{ width: '100%', justifyContent: 'center' }}>
              <ShoppingBag size={18} /> Place Order
            </button>
          </div>
        ) : (
          <p style={{ marginTop: '20px', color: 'var(--text-muted)' }}>Your cart is empty. Add items from the menu.</p>
        )}
      </aside>
    </main>
  );
}
