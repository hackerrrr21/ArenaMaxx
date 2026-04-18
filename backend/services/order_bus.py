from google.cloud import pubsub_v1
import os
import json
import threading

class OrderBus:
    """
    Simulates Google Cloud Pub/Sub for high-scale stadium logistics.
    Used for order fulfillment and real-time inventory updates.
    """
    def __init__(self):
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'arenamaxx')
        self.topic_id = 'order-fulfillment'
        self.publisher = None
        self.subscriber = None
        self._init_client()

    def _init_client(self):
        try:
            # Real GCP Init
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)
        except Exception:
            # Mock for local dev
            self.publisher = None
            print("[PubSub] Running in Mock Mode for Local Development")

    def publish_order(self, order_data):
        """
        Publishes a new order to the Concession topic.
        """
        if self.publisher:
            try:
                data = json.dumps(order_data).encode("utf-16")
                self.publisher.publish(self.topic_path, data)
                return True
            except Exception as e:
                print(f"[PubSub] Publish failed: {e}")
                return False
        else:
            # Simulated Async Processing
            threading.Thread(target=self._mock_consumer, args=(order_data,)).start()
            return True

    def _mock_consumer(self, order_data):
        """
        Simulates the background Cloud Function that processes orders.
        """
        import time
        from .monitoring import log_event
        
        log_event(f"Processing Order #{order_data.get('id')}", severity='INFO', metadata=order_data)
        time.sleep(2) # Simulate processing delay
        log_event(f"Order #{order_data.get('id')} Fulfilled", metadata={'status': 'ready'})

# Singleton instance
order_bus = OrderBus()
