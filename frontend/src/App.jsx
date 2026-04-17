import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useLocation, Outlet, useNavigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import SeatMap from './pages/SeatMap';
import Concessions from './pages/Concessions';
import Washrooms from './pages/Washrooms';
import Wayfinding from './pages/Wayfinding';
import SplashScreen from './components/SplashScreen';
import GeminiChat from './components/GeminiChat';
import './App.css';

function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const isTicketing = location.pathname.startsWith('/tickets');

  const handleLogoClick = () => {
    if (location.pathname === '/dashboard') {
      navigate('/');
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="app-container">
      <header className="nav-header">
        <div className="nav-brand" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>ArenaMaxx</div>
        <nav className="nav-links">
          {isTicketing ? (
            <NavLink to="/tickets" className={({ isActive }) => (isActive ? 'active' : '')}>Tickets</NavLink>
          ) : (
            <>
              <NavLink to="/dashboard" end className={({ isActive }) => (isActive ? 'active' : '')}>Dashboard</NavLink>
              <NavLink to="/food" className={({ isActive }) => (isActive ? 'active' : '')}>Food</NavLink>
              <NavLink to="/washrooms" className={({ isActive }) => (isActive ? 'active' : '')}>Washrooms</NavLink>
              <NavLink to="/wayfinding" className={({ isActive }) => (isActive ? 'active' : '')}>AR Map</NavLink>
            </>
          )}
        </nav>
      </header>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <Outlet />
      </div>
    </div>
  );
}

function App() {
  const [showSplash, setShowSplash] = useState(true);

  return (
    <>
      {showSplash && <SplashScreen onComplete={() => setShowSplash(false)} />}
      <div style={{ opacity: showSplash ? 0 : 1, transition: 'opacity 0.5s ease' }}>
        <BrowserRouter>
          <GeminiChat />
          <Routes>
        <Route path="/" element={<Landing />} />
        
        {/* Protected behind contextual Layout */}
        <Route element={<AppLayout />}>
          <Route path="/tickets" element={<SeatMap />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/food" element={<Concessions />} />
          <Route path="/washrooms" element={<Washrooms />} />
          <Route path="/wayfinding" element={<Wayfinding />} />
        </Route>
      </Routes>
    </BrowserRouter>
      </div>
    </>
  );
}

export default App;
