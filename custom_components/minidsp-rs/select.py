from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MiniDSPCoordinator

_LOGGER = logging.getLogger(__name__)

# Map friendly labels to API values
_SOURCE_MAP = {
    "Analog": "Analog",
    "TOSLINK": "Toslink",
    "SPDIF": "Spdif",
    "USB": "Usb",
    "Bluetooth": "Bluetooth",
}

_PRESET_MAP = {
    "Preset 1": 0,
    "Preset 2": 1,
    "Preset 3": 2,
    "Preset 4": 3,
}

class MiniDSPSourceSelect(CoordinatorEntity[MiniDSPCoordinator], SelectEntity):
    """Select entity to change MiniDSP input source."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:import"

    def __init__(self, coordinator: MiniDSPCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.address}_source"
        self._attr_name = "Input Source"
        self._attr_options = list(_SOURCE_MAP.keys())

    @property
    def current_option(self):
        raw = (self.coordinator.data or {}).get("master", {}).get("source")
        for label, raw_val in _SOURCE_MAP.items():
            if raw_val == raw:
                return label
        return raw

    async def async_select_option(self, option: str):
        raw_val = _SOURCE_MAP.get(option, option)
        self.coordinator.async_update_master_optimistic("source", raw_val)
        await self.coordinator._api.async_set_source(raw_val)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.address)},
            "name": self.coordinator.name,
        }

class MiniDSPPresetSelect(CoordinatorEntity[MiniDSPCoordinator], SelectEntity):
    """Select entity to change MiniDSP preset."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:tune"

    def __init__(self, coordinator: MiniDSPCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.address}_preset"
        self._attr_name = "Preset"
        self._attr_options = list(_PRESET_MAP.keys())

    @property
    def current_option(self):
        raw = (self.coordinator.data or {}).get("master", {}).get("preset")
        for label, raw_val in _PRESET_MAP.items():
            if raw_val == raw:
                return label
        if raw is not None:
            return f"Preset {int(raw) + 1}"
        return None

    async def async_select_option(self, option: str):
        raw_val = _PRESET_MAP.get(option)
        if raw_val is not None:
            self.coordinator.async_update_master_optimistic("preset", raw_val)
            await self.coordinator._api.async_set_preset(raw_val)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.address)},
            "name": self.coordinator.name,
        }

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    stored = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinator: MiniDSPCoordinator | None = stored.get("coordinator")
    if coordinator is None:
        _LOGGER.error("Coordinator not found during select platform setup")
        return

    async_add_entities([MiniDSPSourceSelect(coordinator), MiniDSPPresetSelect(coordinator)])
