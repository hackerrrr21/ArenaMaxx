"""
simulation.py — Real-time Crowd & Washroom Simulation Engine for ArenaMaxx.

Simulates stadium crowd movement and washroom occupancy using a background
daemon thread. Broadcasts live updates to connected clients via WebSockets
(Flask-SocketIO).

This module drives the real-time data shown in:
  - Dashboard: Active Attendees, Venue Zone Density
  - Washrooms: Live Occupancy Status & Wait Times
"""

from __future__ import annotations

import threading
import time
import random
import logging
from typing import Any

from flask_socketio import SocketIO

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────
NUM_BOTS: int = 100
BOUNDS_X: tuple[int, int] = (0, 800)
BOUNDS_Y: tuple[int, int] = (0, 600)
BOT_STEP_SIZE: int = 10
REFRESH_RATE_HZ: float = 1.0  # 1 update per second


class CrowdSimulator:
    """
    Simulates real-time crowd flow and washroom occupancy for a stadium event.

    Uses a daemon thread to periodically:
      1. Move simulated attendee bots within the stadium bounding box.
      2. Fluctuate washroom occupancy to mimic natural usage patterns.
      3. Emit live WebSocket events to all connected dashboard clients.

    Attributes:
        socketio: The Flask-SocketIO instance for broadcasting events.
        is_running: Whether the simulation loop is currently active.
        num_bots: Total number of simulated attendees.
        bots: List of bot position dicts with keys 'id', 'x', 'y'.
        washroom_blocks: Dict of washroom block states with occupancy data.
    """

    def __init__(self, socketio: SocketIO) -> None:
        """
        Initialize the crowd simulator with a SocketIO instance.

        Args:
            socketio: Flask-SocketIO server instance for live event broadcasting.
        """
        self.socketio: SocketIO = socketio
        self.is_running: bool = False
        self.thread: threading.Thread | None = None
        self.num_bots: int = NUM_BOTS
        self.bots: list[dict[str, Any]] = [
            {"id": i, "x": random.randint(*BOUNDS_X), "y": random.randint(*BOUNDS_Y)}
            for i in range(self.num_bots)
        ]
        self.washroom_blocks: dict[str, dict[str, Any]] = {
            "Block_A": {"name": "Block A Restroom", "capacity": 20, "occupied": 5},
            "Block_B": {"name": "Block B Restroom", "capacity": 30, "occupied": 28},
            "Block_C": {"name": "Block C Restroom", "capacity": 15, "occupied": 2},
        }
        self.zone_stats: dict[str, int] = {}

    def start(self) -> None:
        """
        Start the background simulation daemon thread.

        Safe to call multiple times — no-op if already running.
        The thread is set as a daemon so it exits when the main process exits.
        """
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run, name="CrowdSimThread")
            self.thread.daemon = True
            self.thread.start()
            logger.info(f"CrowdSimulator started with {self.num_bots} simulated attendees.")

    def stop(self) -> None:
        """
        Signal the simulation loop to stop on the next iteration.

        Note: Does not immediately terminate the background thread.
        """
        self.is_running = False
        logger.info("CrowdSimulator stopping.")

    def _move_bots(self) -> None:
        """Advance each bot by a random step within the stadium bounding box."""
        for bot in self.bots:
            bot["x"] = max(BOUNDS_X[0], min(BOUNDS_X[1], bot["x"] + random.randint(-BOT_STEP_SIZE, BOT_STEP_SIZE)))
            bot["y"] = max(BOUNDS_Y[0], min(BOUNDS_Y[1], bot["y"] + random.randint(-BOT_STEP_SIZE, BOT_STEP_SIZE)))

    def _fluctuate_washrooms(self) -> None:
        """Randomly adjust washroom occupancy each tick to simulate natural usage."""
        for block in self.washroom_blocks.values():
            delta = random.choice([-1, 0, 0, 1])
            block["occupied"] = max(0, min(block["capacity"], block["occupied"] + delta))

    def _calculate_congestion(self) -> None:
        """Identify high-density zones and emit alerts if needed."""
        zones = {
            'VIP Zone': 0, 'Food Court': 0, 
            'East Gate Area': 0, 'West Gate Area': 0
        }
        for p in self.bots:
            if p['x'] < 400 and p['y'] < 300: zones['VIP Zone'] += 1
            elif p['x'] >= 400 and p['y'] < 300: zones['Food Court'] += 1
            elif p['x'] >= 400 and p['y'] >= 300: zones['East Gate Area'] += 1
            else: zones['West Gate Area'] += 1
        
        self.zone_stats = zones
        
        # If any zone exceeds 35% of total bots, trigger a coordination alert
        congestion_threshold = self.num_bots * 0.35
        for zone, count in zones.items():
            if count > congestion_threshold:
                self.socketio.emit('stadium_alert', {
                    'type': 'CONGESTION',
                    'zone': zone,
                    'message': f"High density detected in {zone}. Rerouting suggested.",
                    'timestamp': time.time()
                })

    def _run(self) -> None:
        """
        Main simulation loop. Runs at REFRESH_RATE_HZ until stopped.

        Broadcasts two events per tick:
          - 'crowd_flow': Updated bot positions and total count.
          - 'washroom_status': Updated occupancy for all washroom blocks.
        """
        while self.is_running:
            self._move_bots()
            self._fluctuate_washrooms()
            self._calculate_congestion()
            
            self.socketio.emit('crowd_flow', {
                'total': self.num_bots,
                'positions': self.bots,
                'zone_stats': self.zone_stats
            })
            self.socketio.emit('washroom_status', self.washroom_blocks)
            time.sleep(1.0 / REFRESH_RATE_HZ)
