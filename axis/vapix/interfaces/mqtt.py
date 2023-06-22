"""MQTT Client api."""

from typing import Any

import orjson

from ..models.api_discovery import ApiId
from ..models.mqtt import (
    ActivateClientRequest,
    ClientConfig,
    ClientConfigStatus,
    ConfigureClientRequest,
    ConfigureEventPublicationRequest,
    DeactivateClientRequest,
    EventFilter,
    EventPublicationConfig,
    GetClientStatusRequest,
    GetEventPublicationConfigRequest,
)
from .api_handler import ApiHandler

URL = "/axis-cgi/mqtt"
URL_CLIENT = f"{URL}/client.cgi"
URL_EVENT = f"{URL}/event.cgi"

API_DISCOVERY_ID = "mqtt-client"
API_VERSION = "1.0"

DEFAULT_TOPICS = ["//."]


def mqtt_json_to_event(msg: str) -> dict[str, Any]:
    """Convert JSON message from MQTT to event format."""
    message = orjson.loads(msg)
    topic = message["topic"].replace("onvif", "tns1").replace("axis", "tnsaxis")

    source = source_idx = ""
    if message["message"]["source"]:
        source, source_idx = next(iter(message["message"]["source"].items()))

    data_type = data_value = ""
    if message["message"]["data"]:
        data_type, data_value = next(iter(message["message"]["data"].items()))

    return {
        "topic": topic,
        "source": source,
        "source_idx": source_idx,
        "type": data_type,
        "value": data_value,
    }


class MqttClientHandler(ApiHandler):
    """MQTT Client for Axis devices."""

    api_id = ApiId.MQTT_CLIENT
    api_request = None

    async def configure_client(self, client_config: ClientConfig) -> None:
        """Configure MQTT Client."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(
            ConfigureClientRequest(discovery_item.version, client_config=client_config)
        )

    async def activate(self) -> None:
        """Activate MQTT Client."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(ActivateClientRequest(discovery_item.version))

    async def deactivate(self) -> None:
        """Deactivate MQTT Client."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(
            DeactivateClientRequest(discovery_item.version)
        )

    async def get_client_status(self) -> ClientConfigStatus:
        """Get MQTT Client status."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(GetClientStatusRequest(discovery_item.version))

    async def get_event_publication_config(self) -> EventPublicationConfig:
        """Get MQTT Client event publication config."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(
            GetEventPublicationConfigRequest(discovery_item.version)
        )

    async def configure_event_publication(
        self, topics: list[str] = DEFAULT_TOPICS
    ) -> None:
        """Configure MQTT Client event publication."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        event_filters = EventFilter.from_list(
            [{"topicFilter": topic} for topic in topics]
        )
        config = EventPublicationConfig(event_filter_list=event_filters)
        return await self.vapix.request2(
            ConfigureEventPublicationRequest(discovery_item.version, config=config)
        )
