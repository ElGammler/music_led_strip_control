from __future__ import annotations

import platform
import re
import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import psutil
from icmplib import ping
from libs.webserver.executer_base import ExecuterBase

__version__ = "2.3 Dev"

try:
    flask_version = version("flask")
except PackageNotFoundError:
    flask_version = "Unknown"


class BuildServiceInfo:
    """Service information builder."""

    def __init__(self: BuildServiceInfo, name: str, status: int = 9999, running: bool = False, not_found: bool = True) -> None:
        self.name = name
        self.status = status
        self.running = running
        self.not_found = not_found

    def update(self: BuildServiceInfo, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def as_dict(self: BuildServiceInfo) -> dict:
        return self.__dict__


class SystemInfoExecuter(ExecuterBase):

    def get_system_info_performance(self: SystemInfoExecuter) -> dict:
        """Return system performance information."""
        return {
            "system": {
                "cpu_info": self.get_cpu_info(),
                "memory_info": self.get_memory_info(),
                "disk_info": self.get_disk_info(),
                "network_info": self.get_network_info()
            }
        }

    def get_cpu_info(self: SystemInfoExecuter) -> dict:
        """Return CPU information."""
        cpu_freq = psutil.cpu_freq()._asdict()
        cpu_usage = psutil.cpu_times_percent(0.0)._asdict()
        cpu_percent = float(f'{(cpu_usage["system"] + cpu_usage["user"]):0.1f}')

        return {
            "frequency": cpu_freq["current"],
            "percent": cpu_percent
        }

    def get_memory_info(self: SystemInfoExecuter) -> dict:
        """Return memory information."""
        return psutil.virtual_memory()._asdict()

    def get_disk_info(self: SystemInfoExecuter) -> dict:
        """Return disk information."""
        return psutil.disk_usage("/")._asdict()

    def get_network_info(self: SystemInfoExecuter) -> list[dict]:
        """Return network information."""
        network_info = []
        all_network_info = psutil.net_if_addrs()
        for current_nic in all_network_info:
            for current_address_family in all_network_info[current_nic]:
                if current_address_family.family == 2:
                    io_counters = psutil.net_io_counters(pernic=True)[current_nic]._asdict()
                    network_info.append({
                        "name": current_nic,
                        "address": current_address_family.address,
                        "netmask": current_address_family.netmask,
                        "bytes_recv": io_counters["bytes_recv"],
                        "bytes_sent": io_counters["bytes_sent"]
                    })

        return network_info

    def get_system_info_temperature(self: SystemInfoExecuter) -> dict:
        """Interface to get system temperature from API."""
        return {
            "system": self.get_raspi_temp()
        }

    def get_raspi_temp(self: SystemInfoExecuter) -> dict:
        """Return system temperature."""
        if platform.system() != "Linux" or not Path("/usr/bin/vcgencmd").exists():
            return {
                "raspi": {
                    "celsius": 0,
                    "fahrenheit": 0
                }
            }

        temp = subprocess.check_output(["/usr/bin/vcgencmd", "measure_temp"], stderr=subprocess.STDOUT)
        cpu_temp_c = float(re.findall(r"\d+\.\d+", temp.decode("utf-8"))[0])
        cpu_temp_f = float(f"{(cpu_temp_c * 1.8 + 32):0.1f}")

        return {
            "raspi": {
                "celsius": cpu_temp_c,
                "fahrenheit": cpu_temp_f
            }
        }

    def get_services(self: SystemInfoExecuter) -> dict[str, list[str]]:
        """Return list of system services."""
        return {
            "services": ["mlsc", "hostapd", "dhcpcd", "dnsmasq"]
        }

    def get_system_info_services(self: SystemInfoExecuter) -> dict[str, list[dict]]:
        """Interface to get system service information from API."""
        return {
            "services": [self.get_service_status(service) for service in self.get_services()["services"]]
        }

    def get_service_status(self: SystemInfoExecuter, service_name: str) -> dict:
        """Return service status details."""
        service_info = BuildServiceInfo(service_name)

        if platform.system() != "Linux":
            service_info.update(status=4, running=False, not_found=True)
            return service_info.as_dict()

        try:
            # If service is running (0), it should return b'', else caught as exception.
            subprocess.check_output(f"systemctl status {service_name} >/dev/null 2>&1", shell=True)
            service_info.update(status=0, running=True, not_found=False)
        except subprocess.CalledProcessError as grepexc:
            # Catch error code if service is stopped (3), or not found (4).
            service_info.update(status=grepexc.returncode)
            if grepexc.returncode == 3:
                service_info.update(not_found=False)
            elif grepexc.returncode == 4:
                service_info.update(not_found=True)
            service_info.update(running=False)
        except Exception:  # noqa: BLE001
            self.logger.debug(f"Could not get service status: {service_name}")

        return service_info.as_dict()

    def get_system_info_device_status(self: SystemInfoExecuter) -> dict[str, list[dict]]:
        """Return device status information."""
        devices = []
        for device in self._config["device_configs"]:
            current_device = {}
            current_device_config = self._config["device_configs"][device]

            current_device["name"] = current_device_config["device_name"]
            current_device["id"] = device
            try:
                if current_device_config["output_type"] == "output_udp":
                    current_device["connected"] = self.check_device_status(current_device_config["output"]["output_udp"]["udp_client_ip"])
                else:
                    current_device["connected"] = True
            except Exception:
                self.logger.exception(f"Could not get device status of: {current_device['name']} - {current_device['id']}")
                current_device["connected"] = False

            devices.append(current_device)

        return {
            "devices": devices
        }

    def check_device_status(self: SystemInfoExecuter, address: str) -> bool:
        """Return True if host (str) responds to a ping request.

        A host may not respond to a ping (ICMP) request even if the host name is valid.
        """
        host = ping(address, count=1, interval=0.2)
        return host.is_alive

    def get_system_version(self: SystemInfoExecuter) -> dict[str, list[dict]]:
        """Return system version information."""
        return {
            "versions": [
                {
                    "name": "mlsc",
                    "version": __version__
                },
                {
                    "name": "python",
                    "version": platform.python_version()
                },
                {
                    "name": "flask",
                    "version": flask_version
                }
            ]
        }
