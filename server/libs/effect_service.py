import sys
from time import time

from loguru import logger

from libs.effects.effect_advanced_scroll import EffectAdvancedScroll
from libs.effects.effect_bars import EffectBars
from libs.effects.effect_beat import EffectBeat
from libs.effects.effect_beat_slide import EffectBeatSlide
from libs.effects.effect_beat_twinkle import EffectBeatTwinkle
from libs.effects.effect_border import EffectBorder
from libs.effects.effect_bubble import EffectBubble
from libs.effects.effect_direction_changer import EffectDirectionChanger
from libs.effects.effect_energy import EffectEnergy
from libs.effects.effect_fade import EffectFade
from libs.effects.effect_fireplace import EffectFireplace
from libs.effects.effect_gradient import EffectGradient
from libs.effects.effect_off import EffectOff
from libs.effects.effect_pendulum import EffectPendulum
from libs.effects.effect_power import EffectPower
from libs.effects.effect_rods import EffectRods
from libs.effects.effect_scroll import EffectScroll
from libs.effects.effect_segment_color import EffectSegmentColor
from libs.effects.effect_single import EffectSingle
from libs.effects.effect_slide import EffectSlide
from libs.effects.effect_spectrum_analyzer import EffectSpectrumAnalyzer
from libs.effects.effect_strobe import EffectStrobe
from libs.effects.effect_sync_fade import EffectSyncFade
from libs.effects.effect_twinkle import EffectTwinkle
from libs.effects.effect_vu_meter import EffectVuMeter
from libs.effects.effect_wave import EffectWave
from libs.effects.effect_wavelength import EffectWavelength
from libs.effects.effect_wiggle import EffectWiggle
from libs.effects_enum import EffectsEnum
from libs.fps_limiter import FPSLimiter
from libs.notification_enum import NotificationEnum

# Output array should look like:
# output = {[r1,r2,r3,r4,r5],[g1,g2,g3,g4,g5],[]}


class EffectService:
    def start(self, device):
        """Start the effect service process.

        You can change the effect by adding a new effect enum inside the enum_queue.
        """
        self._device = device
        logger.info(f'Starting Effect Service component from device: {self._device.device_config["device_name"]}')

        self.ten_seconds_counter = time()
        self.start_time = time()

        self._fps_limiter = FPSLimiter(self._device.device_config["fps"])

        self._available_effects = {
            EffectsEnum.effect_off: EffectOff,
            EffectsEnum.effect_single: EffectSingle,
            EffectsEnum.effect_gradient: EffectGradient,
            EffectsEnum.effect_fade: EffectFade,
            EffectsEnum.effect_sync_fade: EffectSyncFade,
            EffectsEnum.effect_slide: EffectSlide,
            EffectsEnum.effect_bubble: EffectBubble,
            EffectsEnum.effect_twinkle: EffectTwinkle,
            EffectsEnum.effect_pendulum: EffectPendulum,
            EffectsEnum.effect_rods: EffectRods,
            EffectsEnum.effect_segment_color: EffectSegmentColor,
            EffectsEnum.effect_fireplace: EffectFireplace,
            EffectsEnum.effect_strobe: EffectStrobe,
            EffectsEnum.effect_scroll: EffectScroll,
            EffectsEnum.effect_advanced_scroll: EffectAdvancedScroll,
            EffectsEnum.effect_energy: EffectEnergy,
            EffectsEnum.effect_wavelength: EffectWavelength,
            EffectsEnum.effect_bars: EffectBars,
            EffectsEnum.effect_power: EffectPower,
            EffectsEnum.effect_beat: EffectBeat,
            EffectsEnum.effect_beat_twinkle: EffectBeatTwinkle,
            EffectsEnum.effect_beat_slide: EffectBeatSlide,
            EffectsEnum.effect_wave: EffectWave,
            EffectsEnum.effect_wiggle: EffectWiggle,
            EffectsEnum.effect_vu_meter: EffectVuMeter,
            EffectsEnum.effect_spectrum_analyzer: EffectSpectrumAnalyzer,
            EffectsEnum.effect_direction_changer: EffectDirectionChanger,
            EffectsEnum.effect_border: EffectBorder
        }

        self._initialized_effects = {}
        self._current_effect = {}

        try:
            # Get the last effect and set it.
            last_effect_string = self._device.device_config["effects"]["last_effect"]
            self._current_effect = EffectsEnum[last_effect_string]
        except Exception:
            logger.exception("Could not parse last effect. Set effect to off.")
            self._current_effect = EffectsEnum.effect_off

        # A token to cancel the while loop.
        self._cancel_token = False
        self._skip_effect = False
        logger.info(f'Effects component started. Device: {self._device.device_config["device_name"]}')

        try:
            while not self._cancel_token:
                self.effect_routine()
        except KeyboardInterrupt:
            sys.exit()

        logger.info(f'Effects component stopped. Device: {self._device.device_config["device_name"]}')

    def effect_routine(self):
        # Limit the fps to decrease lags caused by 100 percent CPU.
        self._fps_limiter.fps_limiter()

        # Check the notification queue.
        if not self._device.device_notification_queue_in.empty():
            self._current_notification_in = self._device.device_notification_queue_in.get_blocking()
            logger.debug(f'Effects Service has a new notification in. Notification: {self._current_notification_in} | Device: {self._device.device_config["device_name"]}')

        if hasattr(self, "_current_notification_in"):
            if self._current_notification_in is NotificationEnum.config_refresh:
                self.refresh()
            elif self._current_notification_in is NotificationEnum.process_continue:
                self._skip_effect = False
            elif self._current_notification_in is NotificationEnum.process_pause:
                self._skip_effect = True
            elif self._current_notification_in is NotificationEnum.process_stop:
                self.stop()

        # Reset the current in notification, to do it only one time.
        self._current_notification_in = None

        # Skip the effect sequence, for example, to "pause" the process.
        if self._skip_effect:
            return

        # Check if the effect changed.
        if not self._device.effect_queue.empty():
            new_effect_item = self._device.effect_queue.get_blocking()
            self._current_effect = new_effect_item.effect_enum
            logger.debug(f"New effect found: {new_effect_item.effect_enum}")

        # Something is wrong here, no effect set. So skip until we get new information.
        if self._current_effect is None:
            logger.error("Effect Service | Could not find effect.")
            return

        if (self._current_effect not in self._initialized_effects):
            if self._current_effect in self._available_effects:
                self._initialized_effects[self._current_effect] = self._available_effects[self._current_effect](self._device)
            else:
                logger.error(f"Could not find effect: {self._current_effect}")

        self.end_time = time()
        if time() - self.ten_seconds_counter > 10:
            self.ten_seconds_counter = time()
            self.time_dif = self.end_time - self.start_time
            self.fps = 1 / self.time_dif
            logger.info(f'FPS: {self.fps:.2f} | Device: {self._device.device_config["device_name"]}')

        self.start_time = time()

        self._initialized_effects[self._current_effect].run()

    def stop(self):
        logger.info("Stopping effect component...")
        self.cancel_token = True

    def refresh(self):
        logger.debug("Refreshing effects...")
        self._initialized_effects = {}

        self._fps_limiter = FPSLimiter(self._device.device_config["fps"])

        # Notify the master component, that I'm finished.
        self._device.device_notification_queue_out.put_blocking(
            NotificationEnum.config_refresh_finished)
        logger.debug("Effects refreshed.")
