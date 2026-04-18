/**
 * @fileoverview Root application component for ArenaMaxx Stadium Platform.
 *
 * Implements client-side routing with React Router v7, the persistent Gemini
 * AI chat widget, and an animated splash screen on first load.
 *
 * Routes:
 *   /           → Landing (entry point)
 *   /dashboard  → Live stadium overview
 *   /tickets    → Interactive seat selection
 *   /food       → Food & beverage ordering
 *   /washrooms  → Washroom live status & booking
 *   /wayfinding → AR navigation map
 *
 * @module App
 */

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { BrowserRouter, Routes, Route, NavLink, useLocation, Outlet, useNavigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import SeatMap from './pages/SeatMap';
import Concessions from './pages/Concessions';
import Washrooms from './pages/Washrooms';
import Wayfinding from './pages/Wayfinding';
import SplashScreen from './components/SplashScreen';
import GeminiChat from './components/GeminiChat';
import { logAnalyticsEvent } from './services/firebase';
import './App.css';

/**
 * Application navigation layout, rendered for all authenticated/interior routes.
 *
 * Renders the top navigation bar with smart logo-click behavior:
 * - If on /dashboard, navigates to the landing page.
 * - Otherwise, navigates to the dashboard.
 *
 * @component
 * @returns {React.ReactElement} The nav header with an outlet for child routes.
 */
function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const isTicketing = location.pathname.startsWith('/tickets');

  /**
   * Handle logo click — toggles between dashboard and landing page.
   * @returns {void}
   */
  const handleLogoClick = () => {
    if (location.pathname === '/dashboard') {
      navigate('/');
    } else {
      navigate('/dashboard');
    }
    logAnalyticsEvent('logo_click', { from: location.pathname });
  };

  return (
    <div className="app-container">
      <header className="nav-header" role="banner">
        <div
          className="nav-brand"
          onClick={handleLogoClick}
          role="button"
          tabIndex={0}
          aria-label="ArenaMaxx — Return to home or dashboard"
          onKeyDown={(e) => e.key === 'Enter' && handleLogoClick()}
          style={{ cursor: 'pointer' }}
        >
          ArenaMaxx
        </div>
        <nav className="nav-links" role="navigation" aria-label="Main navigation">
          {isTicketing ? (
            <NavLink to="/tickets" className={({ isActive }) => (isActive ? 'active' : '')}>
              Tickets
            </NavLink>
          ) : (
            <>
              <NavLink to="/dashboard" end className={({ isActive }) => (isActive ? 'active' : '')}>
                Dashboard
              </NavLink>
              <NavLink to="/food" className={({ isActive }) => (isActive ? 'active' : '')}>
                Food
              </NavLink>
              <NavLink to="/washrooms" className={({ isActive }) => (isActive ? 'active' : '')}>
                Washrooms
              </NavLink>
              <NavLink to="/wayfinding" className={({ isActive }) => (isActive ? 'active' : '')}>
                AR Map
              </NavLink>
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

/**
 * Root application component. Manages splash screen lifecycle and renders the
 * full BrowserRouter with Gemini AI overlay and all page routes.
 *
 * @component
 * @returns {React.ReactElement} The fully-routed application shell.
 */
function App() {
  const [showSplash, setShowSplash] = useState(true);

  /**
   * Called by SplashScreen when its animation completes.
   * Hides the splash and reveals the main app with a fade transition.
   * @returns {void}
   */
  const handleSplashComplete = () => {
    setShowSplash(false);
    logAnalyticsEvent('splash_complete');
  };

  return (
    <>
      {showSplash && <SplashScreen onComplete={handleSplashComplete} />}
      <div style={{ opacity: showSplash ? 0 : 1, transition: 'opacity 0.5s ease' }}>
        <BrowserRouter>
          <GeminiChat />
          <Routes>
            <Route path="/" element={<Landing />} />

            {/* Interior routes wrapped in the navigation AppLayout */}
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
