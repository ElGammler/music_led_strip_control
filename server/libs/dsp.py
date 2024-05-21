from math import log

import numpy as np
from scipy.ndimage import gaussian_filter1d


class DSP:
    def __init__(self, config, device_config=None) -> None:
        self._config = config
        self._device_config = device_config

        # Initialise filters etc. I've no idea what most of these are for but I imagine I won't be getting rid of them soon.
        n_fft_bins = self._config["general_settings"]["n_fft_bins"]
        min_volume_threshold = self._config["general_settings"]["min_volume_threshold"]
        frames_per_buffer = self._config["general_settings"]["frames_per_buffer"]
        n_rolling_history = self._config["general_settings"]["n_rolling_history"]

        led_count = 200 if device_config is None else self._device_config["led_count"]

        self.fft_plot_filter = ExpFilter(np.tile(1e-1, n_fft_bins), alpha_decay=0.5, alpha_rise=0.99)
        self.mel_gain = ExpFilter(np.tile(1e-1, n_fft_bins), alpha_decay=0.01, alpha_rise=0.99)
        self.mel_smoothing = ExpFilter(np.tile(1e-1, n_fft_bins), alpha_decay=0.5, alpha_rise=0.99)
        self.gain = ExpFilter(np.tile(0.01, n_fft_bins), alpha_decay=0.001, alpha_rise=0.99)
        self.r_filt = ExpFilter(np.tile(0.01, led_count // 2), alpha_decay=0.2, alpha_rise=0.99)
        self.g_filt = ExpFilter(np.tile(0.01, led_count // 2), alpha_decay=0.05, alpha_rise=0.3)
        self.b_filt = ExpFilter(np.tile(0.01, led_count // 2), alpha_decay=0.1, alpha_rise=0.5)
        self.common_mode = ExpFilter(np.tile(0.01, led_count // 2), alpha_decay=0.99, alpha_rise=0.01)
        self.p_filt = ExpFilter(np.tile(1, (3, led_count // 2)), alpha_decay=0.1, alpha_rise=0.99)
        self.volume = ExpFilter(min_volume_threshold, alpha_decay=0.02, alpha_rise=0.02)
        self.p = np.tile(1.0, (3, led_count // 2))
        # Number of audio samples to read every time frame.
        # self.samples_per_frame = int(default_sample_rate / fps)
        self.samples_per_frame = int(frames_per_buffer)
        # Array containing the rolling audio sample window.
        rng = np.random.default_rng()
        self.y_roll = rng.random((n_rolling_history, self.samples_per_frame)) / 1e16
        self.fft_window = np.hamming(int(frames_per_buffer) * n_rolling_history)

        self.samples = None
        self.mel_y = None
        self.mel_x = None
        self.melbank = Melbank()
        self.create_mel_bank()

    def update(self, audio_samples):
        """Return processed audio data.

        Returns mel curve, x/y data.
        This method is called every time there is a microphone update.

        Returns
        -------
        audio_data: dict
            Dict containing "mel", "vol", "x", and "y".

        """
        min_frequency = self._config["general_settings"]["min_frequency"]
        max_frequency = self._config["general_settings"]["max_frequency"]

        audio_data = {}
        # Normalize samples between 0 and 1.
        y = audio_samples / 2.0**15
        # Construct a rolling window of audio samples.
        self.y_roll[:-1] = self.y_roll[1:]
        self.y_roll[-1, :] = np.copy(y)
        y_data = np.concatenate(self.y_roll, axis=0).astype(np.float32)
        vol = np.max(np.abs(y_data))
        # Transform audio input into the frequency domain.
        N = len(y_data)  # noqa: N806
        N_zeros = 2**int(np.ceil(np.log2(N))) - N  # noqa: N806
        # Pad with zeros until the next power of two.
        y_data *= self.fft_window
        y_padded = np.pad(y_data, (0, N_zeros), mode="constant")
        YS = np.abs(np.fft.rfft(y_padded))  # noqa: N806
        # Construct a Mel filterbank from the FFT data.
        mel = np.atleast_2d(YS).T * self.mel_y.T
        # Scale data to values more suitable for visualization.
        mel = np.sum(mel, axis=0)
        mel **= 2.0
        # Gain normalization.
        self.mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= self.mel_gain.value
        mel = self.mel_smoothing.update(mel)
        x = np.linspace(min_frequency, max_frequency, len(mel))
        y = self.fft_plot_filter.update(mel)

        audio_data["mel"] = mel
        audio_data["vol"] = vol
        audio_data["x"] = x
        audio_data["y"] = y
        return audio_data

    def rfft(self, data, window=None):
        default_sample_rate = self._config["general_settings"]["default_sample_rate"]

        window = 1.0 if window is None else window(len(data))
        ys = np.abs(np.fft.rfft(data * window))
        xs = np.fft.rfftfreq(len(data), 1.0 / default_sample_rate)
        return xs, ys

    def fft(self, data, window=None):
        default_sample_rate = self._config["general_settings"]["default_sample_rate"]

        window = 1.0 if window is None else window(len(data))
        ys = np.fft.fft(data * window)
        xs = np.fft.fftfreq(len(data), 1.0 / default_sample_rate)
        return xs, ys

    def create_mel_bank(self):
        default_sample_rate = self._config["general_settings"]["default_sample_rate"]
        min_frequency = self._config["general_settings"]["min_frequency"]
        max_frequency = self._config["general_settings"]["max_frequency"]
        frames_per_buffer = self._config["general_settings"]["frames_per_buffer"]
        n_rolling_history = self._config["general_settings"]["n_rolling_history"]
        n_fft_bins = self._config["general_settings"]["n_fft_bins"]

        samples = (2**int(np.ceil(np.log2(frames_per_buffer * n_rolling_history)))) // 2 + 1

        self.mel_y, (_, self.mel_x) = self.melbank.compute_melmat(
            num_mel_bands=n_fft_bins,
            freq_min=min_frequency,
            freq_max=max_frequency,
            num_fft_bands=samples,
            sample_rate=default_sample_rate
        )


class ExpFilter:
    """Simple exponential smoothing filter."""

    def __init__(self, val=0.0, alpha_decay=0.5, alpha_rise=0.5) -> None:
        """Small rise/decay factors = more smoothing."""
        assert 0.0 < alpha_decay < 1.0, "Invalid decay smoothing factor."  # noqa: S101
        assert 0.0 < alpha_rise < 1.0, "Invalid rise smoothing factor."  # noqa: S101
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):
        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value


class Melbank:
    """Implement a Mel Filter Bank.

    In other words it is a filter bank with triangular shaped bands
    arranged on the mel frequency scale.
    An example is shown in the following figure:
    .. plot::
        from pylab import plt
        import melbank
        f1, f2 = 1000, 8000
        melmat, (melfreq, fftfreq) = melbank.compute_melmat(6, f1, f2, num_fft_bands=4097)
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(fftfreq, melmat.T)
        ax.grid(True)
        ax.set_ylabel('Weight')
        ax.set_xlabel('Frequency / Hz')
        ax.set_xlim((f1, f2))
        ax2 = ax.twiny()
        ax2.xaxis.set_ticks_position('top')
        ax2.set_xlim((f1, f2))
        ax2.xaxis.set_ticks(melbank.mel_to_hertz(melfreq))
        ax2.xaxis.set_ticklabels(['{:.0f}'.format(mf) for mf in melfreq])
        ax2.set_xlabel('Frequency / mel')
        plt.tight_layout()
        fig, ax = plt.subplots()
        ax.matshow(melmat)
        plt.axis('equal')
        plt.axis('tight')
        plt.title('Mel Matrix')
        plt.tight_layout()
    Functions
    ---------.
    """

    @staticmethod
    def hertz_to_mel(freq):
        """Return mel-frequency from linear frequency input.

        Parameter
        ---------
        freq : scalar or ndarray
            Frequency value or array in Hz.

        Returns
        -------
        mel : scalar or ndarray
            Mel-frequency value or ndarray in Mel.

        """
        return 3340.0 * log(1 + (freq / 250.0), 9)

    @staticmethod
    def mel_to_hertz(mel):
        """Return frequency from mel-frequency input.

        Parameter
        ---------
        mel : scalar or ndarray
            Mel-frequency value or ndarray in Mel

        Returns
        -------
        freq : scalar or ndarray
            Frequency value or array in Hz.

        """
        # return 700.0 * (10**(mel / 2595.0)) - 700.0
        return 250.0 * (9**(mel / 3340.0)) - 250.0

    def melfrequencies_mel_filterbank(self, num_bands, freq_min, freq_max, num_fft_bands):
        """Return centerfrequencies and band edges for a mel filter bank.

        Parameters
        ----------
        num_bands : int
            Number of mel bands.
        freq_min : scalar
            Minimum frequency for the first band.
        freq_max : scalar
            Maximum frequency for the last band.
        num_fft_bands : int
            Number of fft bands.

        Returns
        -------
        center_frequencies_mel : ndarray
        lower_edges_mel : ndarray
        upper_edges_mel : ndarray.

        """
        mel_max = self.hertz_to_mel(freq_max)
        mel_min = self.hertz_to_mel(freq_min)
        delta_mel = np.abs(mel_max - mel_min) / (num_bands + 1.0)
        frequencies_mel = mel_min + delta_mel * np.arange(0, num_bands + 2)
        lower_edges_mel = frequencies_mel[:-2]
        upper_edges_mel = frequencies_mel[2:]
        center_frequencies_mel = frequencies_mel[1:-1]
        return center_frequencies_mel, lower_edges_mel, upper_edges_mel

    def compute_melmat(self, num_mel_bands=12, freq_min=64, freq_max=8000,
                       num_fft_bands=513, sample_rate=16000):
        """Return tranformation matrix for mel spectrum.

        Parameters
        ----------
        num_mel_bands : int
            Number of mel bands. Number of rows in melmat.
            Default: 24
        freq_min : scalar
            Minimum frequency for the first band.
            Default: 64
        freq_max : scalar
            Maximum frequency for the last band.
            Default: 8000
        num_fft_bands : int
            Number of fft-frequenc bands. This ist NFFT/2+1 !
            number of columns in melmat.
            Default: 513   (this means NFFT=1024)
        sample_rate : scalar
            Sample rate for the signals that will be used.
            Default: 44100

        Returns
        -------
        melmat : ndarray
            Transformation matrix for the mel spectrum.
            Use this with fft spectra of num_fft_bands_bands length
            and multiply the spectrum with the melmat
            this will tranform your fft-spectrum
            to a mel-spectrum.
        frequencies : tuple (ndarray <num_mel_bands>, ndarray <num_fft_bands>)
            Center frequencies of the mel bands, center frequencies of fft spectrum.

        """
        center_frequencies_mel, lower_edges_mel, upper_edges_mel = self.melfrequencies_mel_filterbank(
            num_mel_bands,
            freq_min,
            freq_max,
            num_fft_bands
        )

        center_frequencies_hz = self.mel_to_hertz(center_frequencies_mel)
        lower_edges_hz = self.mel_to_hertz(lower_edges_mel)
        upper_edges_hz = self.mel_to_hertz(upper_edges_mel)
        freqs = np.linspace(0.0, sample_rate / 2.0, num_fft_bands)
        melmat = np.zeros((num_mel_bands, num_fft_bands))

        for imelband, (center, lower, upper) in enumerate(zip(
                center_frequencies_hz, lower_edges_hz, upper_edges_hz)):

            left_slope = (freqs >= lower) == (freqs <= center)
            melmat[imelband, left_slope] = (
                (freqs[left_slope] - lower) / (center - lower)
            )

            right_slope = (freqs >= center) == (freqs <= upper)
            melmat[imelband, right_slope] = (
                (upper - freqs[right_slope]) / (upper - center)
            )
        return melmat, (center_frequencies_mel, freqs)
