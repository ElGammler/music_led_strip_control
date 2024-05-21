import copy

import pytest

from libs.device import Device
from libs.effects.effect import Effect
from libs.unit_tests.testfixtures.demodevice import DemoDevice
from libs.unit_tests.testfixtures.helper_functions import generate_random_demo_audiodata


class TestEffect:

    @pytest.fixture()
    def _setup_fixture(self):
        self.demodevice = DemoDevice()

    def test_init_single_effect(self, setup_fixture):
        """Init a device without other calls."""
        self.effect = Effect(self.demodevice)

        assert isinstance(self.effect, Effect)
        assert isinstance(self.demodevice, Device)

    def test_run(self, setup_fixture):
        """Run should throw not implemented exception."""
        exception_found = False

        self.effect = Effect(self.demodevice)

        try:
            self.effect.run()
        except NotImplementedError:
            exception_found = True
            assert True
        except Exception:
            pytest.fail("Unexpected exception")

        assert exception_found

    def test_update_freq_channels(self, setup_fixture):
        """Try to use the update_freq_channels."""
        self.effect = Effect(self.demodevice)

        freq_channels_0 = None
        freq_channels_1 = None
        freq_channels_2 = None

        for i in range(self.effect.freq_channel_history + 10):
            random_audio = generate_random_demo_audiodata(
                self.demodevice.config, self.demodevice.device_config)
            y = self.effect.get_mel(random_audio)

            self.effect.update_freq_channels(y)

            if self.effect.freq_channel_history + 1 == i:
                freq_channels_0 = copy.deepcopy(self.effect.freq_channels)
            if self.effect.freq_channel_history + 2 == i:
                freq_channels_1 = copy.deepcopy(self.effect.freq_channels)
            if self.effect.freq_channel_history + 3 == i:
                freq_channels_2 = copy.deepcopy(self.effect.freq_channels)

        assert len(
            freq_channels_0) == self.demodevice.config["general_settings"]["n_fft_bins"]
        assert len(
            freq_channels_0[0]) == self.effect.freq_channel_history

        assert len(
            freq_channels_1) == self.demodevice.config["general_settings"]["n_fft_bins"]
        assert len(
            freq_channels_1[0]) == self.effect.freq_channel_history

        assert len(
            freq_channels_2) == self.demodevice.config["general_settings"]["n_fft_bins"]
        assert len(
            freq_channels_2[0]) == self.effect.freq_channel_history
        assert id(freq_channels_0) != id(freq_channels_1)
        assert id(freq_channels_1) != id(freq_channels_2)
