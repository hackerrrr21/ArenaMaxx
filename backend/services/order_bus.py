"""
order_bus.py — Async Logistics Engine using Google Cloud Pub/Sub pattern.

Implements event-driven order fulfillment for ArenaMaxx concessions.
Uses Cloud Pub/Sub when available in GCP, with a graceful threading fallback
for local development environments.

Google Cloud Services:
  - Google Cloud Pub/Sub (topic: order-fulfillment)
"""
from __future__ import annotations

import os
import json
import threading
import logging

logger = logging.getLogger(__name__)


class OrderBus:
    """
    Asynchronous order logistics bus backed by Google Cloud Pub/Sub.

    In production (Cloud Run), publishes to a real Pub/Sub topic.
    In local development, simulates async processing via background threads.
    """

    def __init__(self) -> None:
        self.project_id: str = os.environ.get("GOOGLE_CLOUD_PROJECT", "arenamaxx")
        self.topic_id: str = "order-fulfillment"
        self._publisher = None
        self._topic_path: str = ""
        self._init_client()

    def _init_client(self) -> None:
        """Attempt to initialize the real Cloud Pub/Sub publisher client."""
        try:
            from google.cloud import pubsub_v1  # type: ignore
            self._publisher = pubsub_v1.PublisherClient()
            self._topic_path = self._publisher.topic_path(self.project_id, self.topic_id)
            logger.info("[OrderBus] ✅ Cloud Pub/Sub publisher initialized.")
        except (ImportError, Exception) as exc:
            self._publisher = None
            logger.info(f"[OrderBus] Running in mock mode (Pub/Sub unavailable): {exc}")

    def publish_order(self, order_data: dict) -> bool:
        """
        Publish a new order to the fulfillment topic.

        Args:
            order_data: Dictionary containing order details (id, items, queue_number).

        Returns:
            True if the order was successfully enqueued, False otherwise.
        """
        if self._publisher:
            try:
                payload = json.dumps(order_data).encode("utf-8")
                future = self._publisher.publish(self._topic_path, payload)
                future.result(timeout=5)  # confirm publish
                logger.info(f"[OrderBus] Order #{order_data.get('id')} published to Pub/Sub.")
                return True
            except Exception as exc:
                logger.error(f"[OrderBus] Pub/Sub publish failed: {exc}")
                return False

        # Local mock: simulate async processing in a background thread
        threading.Thread(
            target=self._mock_consumer,
            args=(order_data,),
            daemon=True,
        ).start()
        return True

    def _mock_consumer(self, order_data: dict) -> None:
        """Simulate Cloud Function consumer processing the order."""
        import time
        time.sleep(2)
        logger.info(f"[OrderBus-Mock] Order #{order_data.get('id')} fulfilled.")


# Module-level singleton
order_bus = OrderBus()
