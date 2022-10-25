import soundfile as sf
import pyloudnorm as pyln
import numpy as np
import pandas as pd
import datetime
import matplotlib.dates as matdates


class AudioFile(object):
    def __init__(self, file_path, data=None, sample_rate=None):
        self.file_path = file_path

        if data is None:
            self.data, self.sample_rate = sf.read(file_path)
        else:
            self.data, self.sample_rate = data, sample_rate

        self.meter = pyln.Meter(self.sample_rate)

    def loudness_integrated(self):
        return self.meter.integrated_loudness(self.data)

    def max_min_loudness_short_term(self, window=3, step=None, plot=None, short_target=None, axes=None):
        '''
        Sliding window loudness calc with 1 second step size

        :param window:
        :return:
        '''
        if step is None:
            step = self.sample_rate // 2

        L = self.data.shape[0]
        ranges = [(x, min(L, (x + self.sample_rate * window))) for x in range(0, L, step)]

        loudness_vals = []
        if plot is not None:
            loudness_df = pd.DataFrame(columns=['LUF-S'])

        for start, end in ranges:
            slice = self.data[start:end]

            if slice.shape[0] < self.sample_rate:
                continue

            start_time = self.samples_to_time(start)
            end_time = self.samples_to_time(end)

            loudness = self.meter.integrated_loudness(slice)
            loudness_vals.append((loudness, f"{start_time.strftime('%M:%S')} - {end_time.strftime('%M:%S')}"))

            if plot is not None:
                loudness_df.loc[end_time] = loudness

        if plot is not None:
            ax1 = loudness_df.plot(title=self.file_path, ylim=(-30, -5), grid=True,
                                   ax=axes[plot] if axes is not None else None)
            if short_target:
                ax1.axhline(y=short_target, color='red')

        return max(loudness_vals), min(loudness_vals)

    def __add__(self, other):
        assert self.sample_rate == other.sample_rate, "Mismatched sample rates!"

        return AudioFile(None, np.concatenate((self.data, other.data)), self.sample_rate)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def samples_to_seconds(self, samples):
        return samples / self.sample_rate

    def samples_to_time(self, samples):
        m, s = divmod(self.samples_to_seconds(samples), 60)
        h, m = divmod(m, 60)
        micro = int((s % 1) * 1e6)
        return datetime.time(hour=int(h), minute=int(m), second=int(s), microsecond=int(micro))

    def __len__(self):
        return self.data.shape[0]

    def length(self):
        return self.samples_to_time(self.__len__())

    @staticmethod
    def to_db(x):
        return 20 * np.log10(x)

    def peak(self, arr):
        return self.to_db(np.max(arr, axis=0))

    def trough(self, arr):
        return self.to_db(np.min(arr, axis=0))

    def peak_sec(self, secs=2):
        ds = pd.DataFrame(self.data).rolling(self.sample_rate * secs).mean().dropna().values
        return self.peak(ds)

    def sample_peak(self):
        return self.peak(self.data)

    def sample_trough(self):
        return self.trough(self.data)

    def calc_row(self, short_target=None, plot=None, axes=None):
        (max_lufs, max_time), (min_lufs, min_time) = self.max_min_loudness_short_term(short_target=short_target,
                                                                                      plot=plot, axes=axes)
        peak_l, peak_r = self.sample_peak()
        lufi = self.loudness_integrated()
        avg_peak = (peak_l + peak_r) / 2
        psr = avg_peak - max_lufs
        plr = avg_peak - lufi

        return [self.sample_rate, self.length().strftime('%M:%S'), lufi, max_lufs, max_time,
                min_lufs, min_time, peak_l, peak_r, plr, psr]

