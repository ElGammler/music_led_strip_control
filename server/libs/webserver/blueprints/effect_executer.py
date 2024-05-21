from __future__ import annotations

from copy import deepcopy
from secrets import choice

from libs.effects_enum import EffectNames
from libs.webserver.executer_base import ExecuterBase
from libs.webserver.messages import DeviceNotFound, DuplicateItem


class EffectExecuter(ExecuterBase):

    def is_cycle_job_running(self, device: str) -> dict[str, str | bool] | DeviceNotFound:
        """Check if Random Cycle effect is active for specified device."""
        if device == self.all_devices_id or (device.startswith("group_") and device in self._config["general_settings"]["device_groups"]):
            return {
                "device": device,
                "random_cycle_active": False
            }  # Does not work with groups yet.

        if device not in self._config["device_configs"]:
            return DeviceNotFound

        job = self.scheduler.get_job(device)

        return {
            "device": device,
            "random_cycle_active": bool(job and job.next_run_time)
        }

    def get_active_effect(self, device: str) -> dict[str, str] | DeviceNotFound:
        """Interface to get an active device effect from API."""
        if device not in self._config["device_configs"]:
            return DeviceNotFound

        return {
            "device": device,
            "effect": self._config["device_configs"][device]["effects"]["last_effect"]
        }

        # """
        # -> str | list[str] | DeviceNotFound:
        # Interface to get an active device effect from API.
        # If device is a group, return list of active effects.
        # If the list has only one effect, or has all same effects, return that effect.
        # """
        # if device == self.all_devices_id:
        #     active_effects = [d["effects"]["last_effect"] for d in self._config["device_configs"].values()]

        # elif device.startswith("group_") and device in self._config["general_settings"]["device_groups"]:
        #     active_effects = [d["effects"]["last_effect"] for d in self._config["device_configs"].values() if device in d["device_groups"]]

        # elif device in self._config["device_configs"]:
        #     active_effects = [self._config["device_configs"][device]["effects"]["last_effect"]]

        # if len(set(active_effects)) == 1:  # Length of a set with same items is 1.
        #     return active_effects[0]

        # return active_effects

    def _get_active_device_effects(self) -> list[dict]:
        """Return active effects for all devices."""
        return [
            {
                "device": device,
                "effect": self._config["device_configs"][device]["effects"]["last_effect"]
            }
            for device in self._config["device_configs"]
        ]

    def _get_active_group_effects(self) -> list[dict]:
        """Return active effects for each assigned group."""
        return [
            {
                "group": group,
                "effects": [d["effects"]["last_effect"] for d in self._config["device_configs"].values() if group in d["device_groups"]]
            }
            for group in self._config["general_settings"]["device_groups"]
            if any(group in d["device_groups"] for d in self._config["device_configs"].values())
        ]

    def get_active_effects(self) -> dict[str, list[dict]]:
        """Interface to get active effects for devices and groups from API."""
        return {
            "devices": self._get_active_device_effects(),
            "groups": self._get_active_group_effects()
        }

    def get_enabled_effects(self, device: str) -> list[str]:
        """Return list of effects enabled for Random Cycle.

        If less than two effects in list, return all effects.
        """
        effect_dict: dict = deepcopy(self._config["device_configs"][device]["effects"]["effect_random_cycle"])
        enabled_effects = [k for k, v in effect_dict.items() if v is True]
        if len(enabled_effects) < 2:
            effect_dict.pop("interval", None)
            return list(effect_dict)
        return enabled_effects

    def get_random_effect(self, device: str, effects: list[str]) -> str:
        """Return a random effect from effect list.

        Device is required to prevent repeating effects twice.
        """
        active_effect = self.get_active_effect(device)["effect"]

        if len(effects) < 2:
            return effects[0]

        if active_effect in effects:
            effects.remove(active_effect)
        return choice(effects)

    def add_cycle_job(self, device: str) -> None:
        """Add new Random Cycle Effect job for a device."""
        interval = self._config["device_configs"][device]["effects"]["effect_random_cycle"]["interval"]
        self.scheduler.add_job(
            func=self.run_cycle_job,
            id=device,
            trigger="interval",
            seconds=interval,
            args=(device,)
        )

    def control_cycle_job(self, device: str, effect: str) -> None:
        """Toggle Random Cycle Effect job on or off."""
        if effect == "effect_random_cycle":
            if not self.scheduler.get_job(device):
                self.add_cycle_job(device)
            else:
                self.scheduler.resume_job(device)
        else:  # noqa: PLR5501
            if self.scheduler.get_job(device):
                self.scheduler.pause_job(device)

    def run_cycle_job(self, device: str) -> None:
        """Run Random Cycle Effect as a separate Apscheduler job."""
        effect_list = self.get_enabled_effects(device)
        effect = self.get_random_effect(device, effect_list)
        self._config["device_configs"][device]["effects"]["last_effect"] = effect
        self.put_into_effect_queue(device, effect)

    def parse_special_effects(self, device: str, effect: str) -> str:
        """Return random effect based on selected special effect."""
        special_effects = ("effect_random_cycle", "effect_random_non_music", "effect_random_music")

        if effect not in special_effects:
            return effect

        if effect == special_effects[0]:
            effect_list = self.get_enabled_effects(device)

        elif effect == special_effects[1]:
            effect_list = [*EffectNames.non_music]

        elif effect == special_effects[2]:
            effect_list = [*EffectNames.music]

        return self.get_random_effect(device, effect_list)

    def set_active_effect(self, device: str, effect: str) -> dict | DeviceNotFound:
        """Set active effect for a specified device."""
        if device not in self._config["device_configs"]:
            return DeviceNotFound

        new_effect = self.parse_special_effects(device, effect)

        self.control_cycle_job(device, effect)
        self._config["device_configs"][device]["effects"]["last_effect"] = new_effect
        self.save_config()
        self.put_into_effect_queue(device, new_effect)

        return {
            "device": device,
            "effect": new_effect
        }

    def set_active_effect_for_multiple(self, devices: list[dict]) -> dict | DeviceNotFound | DuplicateItem:
        """Set active effect for multiple devices."""
        if any(item["device"] not in self._config["device_configs"] for item in devices):
            return DeviceNotFound

        if len({item["device"] for item in devices}) != len(devices):  # Check for device duplicates.
            return DuplicateItem

        if len(devices) == 0:
            return {
                "devices": []
            }

        results = [
            self.set_active_effect(item["device"], item["effect"])
            for item in devices
        ]

        return {
            "devices": results
        }

    def set_active_effect_for_all(self, effect: str, shuffle: bool = False) -> dict:
        """Set active effect for all devices.

        If a special effect is passed and `shuffle` is `True`, set a random effect for each device.
        Otherwise, if `shuffle` is `False`, all devices will be set to the same effect by default.
        """
        if len(self._config["device_configs"]) == 0:
            return {
                "effect": effect
            }

        new_effect = effect
        for index, device in enumerate(self._config["device_configs"]):
            if index == 0 or (index > 0 and shuffle):
                new_effect = self.parse_special_effects(device, effect)

            self.control_cycle_job(device, effect)
            self._config["device_configs"][device]["effects"]["last_effect"] = new_effect

        self.save_config()
        self.put_into_effect_queue(self.all_devices_id, new_effect)

        return {
            "effect": new_effect
        }
