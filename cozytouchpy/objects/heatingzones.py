"""Describe objects for cozytouch."""
import logging
from ..constant import DeviceCommand, DeviceType, DeviceState, OnOffState
from ..exception import CozytouchException
from .device import CozytouchDevice

logger = logging.getLogger(__name__)


class CozytouchHeatingZone(CozytouchDevice):
    """Heating Zone Box."""

    @property
    def name(self):
        """Name."""
        return self.data["label"]

    @property
    def is_on(self):
        """Heater is on."""
        return self.get_state(DeviceState.HEATING_ON_OFF_STATE) == OnOffState.ON

    @property
    def is_away(self):
        """Not implemented."""

    @property
    def state(self):
        """Return Configuration state."""
        return self.get_state(DeviceState.THERMAL_CONFIGURATION_STATE)

    @property
    def temperature(self):
        """Return temperature."""
        sensor = self.get_sensors(DeviceType.TEMPERATURE)
        if sensor is None:
            return 0
        return sensor.temperature

    @property
    def target_temperature(self):
        """Return target temperature."""
        return self.get_state(DeviceState.COMFORT_TARGET_TEMPERATURE_STATE)

    @property
    def comfort_temperature(self):
        """Return comfort temperature."""
        return self.get_state(DeviceState.COMFORT_HEATING_TARGET_TEMPERATURE_STATE)

    @property
    def eco_temperature(self):
        """Return economic temperature."""
        return self.get_state(DeviceState.ECO_HEATING_TARGET_TEMPERATURE_STATE)

    @property
    def operating_mode(self):
        """Return operation mode."""
        return self.get_state(DeviceState.PASS_APC_HEATING_MODE_STATE)

    @property
    def operating_mode_list(self):
        """Return operating mode list."""
        return self.get_definition(DeviceState.PASS_APC_HEATING_MODE_STATE)

    @property
    def supported_states(self) -> dict:
        """Supported states."""
        supported_states = [state["name"] for state in self.states]
        for sensor in self.sensors:
            sensor_states = [state["name"] for state in sensor.states]
            supported_states = list(set(supported_states + sensor_states))
        return supported_states

    def is_state_supported(self, state):
        """Return is supported ."""
        return state in self.supported_states

    async def set_operating_mode(self, mode):
        """Set operating mode."""
        mode_state = DeviceState.PASS_APC_HEATING_MODE_STATE
        actions = [
            {"action": DeviceCommand.SET_PASS_APC_HEATING_MODE, "value": mode},
            {"action": DeviceCommand.REFRESH_PASS_APC_HEATING_MODE},
        ]
        await self.set_mode(mode_state, actions)
        self.set_state(mode_state, mode)

    async def set_eco_temperature(self, temperature):
        """Set eco temperature."""
        mode_state = DeviceState.ECO_HEATING_TARGET_TEMPERATURE_STATE
        actions = [
            {
                "action": DeviceCommand.SET_ECO_HEATING_TARGET_TEMPERATURE,
                "value": temperature,
            },
            {"action": DeviceCommand.REFRESH_ECO_HEATING_TARGET_TEMPERATURE},
        ]
        await self.set_mode(mode_state, actions)
        self.set_state(mode_state, temperature)

    async def set_comfort_temperature(self, temperature):
        """Set comfort temperature."""
        mode_state = DeviceState.COMFORT_HEATING_TARGET_TEMPERATURE_STATE
        actions = [
            {
                "action": DeviceCommand.SET_COMFORT_HEATING_TARGET_TEMPERATURE,
                "value": temperature,
            },
            {"action": DeviceCommand.REFRESH_COMFORT_HEATING_TARGET_TEMPERATURE},
        ]
        await self.set_mode(mode_state, actions)
        self.set_state(mode_state, temperature)

    async def turn_on(self):
        """Set on."""
        mode_state = DeviceState.HEATING_ON_OFF_STATE
        actions = [
            {"action": DeviceCommand.SET_HEATING_ON_OFF_STATE, "value": OnOffState.ON}
        ]
        await self.set_mode(mode_state, actions)
        self.set_state(mode_state, OnOffState.ON)

    async def turn_off(self):
        """Set off."""
        mode_state = DeviceState.HEATING_ON_OFF_STATE
        actions = [
            {"action": DeviceCommand.SET_HEATING_ON_OFF_STATE, "value": OnOffState.OFF}
        ]
        await self.set_mode(mode_state, actions)
        self.set_state(mode_state, OnOffState.OFF)

    async def update(self):
        """Update heating zone box."""
        if self.client is None:
            raise CozytouchException("Unable to update heating zone box")
        for sensor in self.sensors:
            logger.debug("Heating Zone: Update sensor")
            await sensor.update()
        await super(CozytouchHeatingZone, self).update()
