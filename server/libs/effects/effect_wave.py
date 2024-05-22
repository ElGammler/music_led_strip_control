import numpy as np

from libs.effects.effect import Effect


class EffectWave(Effect):
    def run(self):
        """Effect that flashes to the beat with scrolling coloured bits."""
        effect_config = self.get_effect_config("effect_wave")
        led_count = self._device.device_config["led_count"]

        audio_data = self.get_audio_data()
        y = self.get_mel(audio_data)

        if y is None:
            return

        self.update_freq_channels(y)
        self.detect_freqs()

        if self.current_freq_detects["beat"]:
            output = np.zeros((3, led_count))
            output[0][:] = self._color_service.colour(effect_config["color_flash"])[0]
            output[1][:] = self._color_service.colour(effect_config["color_flash"])[1]
            output[2][:] = self._color_service.colour(effect_config["color_flash"])[2]
            self.wave_wipe_count = min(effect_config["wipe_len"], led_count)
        else:
            output = np.copy(self.prev_output)
            # for i in range(len(self.prev_output)):
            #     output[i] = np.hsplit(self.prev_output[i],2)[0]
            output = np.multiply(self.prev_output, effect_config["decay"])
            for i in range(self.wave_wipe_count):
                output[0][i] = self._color_service.colour(effect_config["color_wave"])[0]
                output[0][-i] = self._color_service.colour(effect_config["color_wave"])[0]
                output[1][i] = self._color_service.colour(effect_config["color_wave"])[1]
                output[1][-i] = self._color_service.colour(effect_config["color_wave"])[1]
                output[2][i] = self._color_service.colour(effect_config["color_wave"])[2]
                output[2][-i] = self._color_service.colour(effect_config["color_wave"])[2]
            # output = np.concatenate([output,np.fliplr(output)], axis=1)
            self.wave_wipe_count = min(self.wave_wipe_count, led_count // 2)

            # Calculate how many steps the array will roll.
            steps = self.get_roll_steps(effect_config["wipe_speed"])

            self.wave_wipe_count += steps

        self.queue_output_array_noneblocking(output)

        self.prev_output = output
