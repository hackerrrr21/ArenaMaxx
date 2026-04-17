import threading
import time
import random
from flask_socketio import SocketIO

class CrowdSimulator:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.is_running = False
        self.thread = None
        self.num_bots = 100
        # Simple coordinate bounding box for stadium map
        self.bounds_x = (0, 800)
        self.bounds_y = (0, 600)
        self.bots = [{"id": i, "x": random.randint(*self.bounds_x), "y": random.randint(*self.bounds_y)} for i in range(self.num_bots)]
        
        # Simulate initial washroom loads
        self.washroom_blocks = {
            "Block_A": {"name": "Block A Restroom", "capacity": 20, "occupied": 5},
            "Block_B": {"name": "Block B Restroom", "capacity": 30, "occupied": 28},
            "Block_C": {"name": "Block C Restroom", "capacity": 15, "occupied": 2}
        }
        
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.is_running = False
        
    def _run(self):
        while self.is_running:
            # Move bots organically to simulate flow
            for bot in self.bots:
                bot["x"] += random.randint(-10, 10)
                bot["y"] += random.randint(-10, 10)
                bot["x"] = max(self.bounds_x[0], min(self.bounds_x[1], bot["x"]))
                bot["y"] = max(self.bounds_y[0], min(self.bounds_y[1], bot["y"]))
                
            # Fluctuate washroom load
            for k, block in self.washroom_blocks.items():
                change = random.choice([-1, 0, 1])
                block["occupied"] = max(0, min(block["capacity"], block["occupied"] + change))

            # Broadcast WebSocket updates
            self.socketio.emit('crowd_flow', {'total': self.num_bots, 'positions': self.bots})
            self.socketio.emit('washroom_status', self.washroom_blocks)
            
            time.sleep(1.0) # Refresh rate: 1 hertz
