import numpy
import scipy
import scipy.signal
import scipy.io
import scipy.io.wavfile
import os
import collections
import soundfile


class WLPACInfo(object):
    def __init__(self, sampling_frequency, residual):
        self.sampling_frequency = sampling_frequency
        self.residual = residual

    def save_to_file(self, path):
        soundfile.write(path, self.residual, self.sampling_frequency)

    @classmethod
    def load_from_file(cls, path):
        residual, samplerate = soundfile.read(path)
        wlpac_obj = WLPACInfo(samplerate, residual)
        return wlpac_obj


def wlpac_encode(in_wav_file, out_wlpac_file, quantization_ratio=1.0, container="wav"):
    x, fs = soundfile.read(in_wav_file)
    r = wfir(x, fs, 1)

    wlpac_obj = WLPACInfo(fs, r)
    wlpac_obj.save_to_file(out_wlpac_file)
    orig_size = os.path.getsize(in_wav_file)
    new_size = os.path.getsize(out_wlpac_file)
    print("orig size: {0}".format(orig_size))
    print("new size: {0}".format(new_size))
    print(
        "Wrote {0} with quantization ratio {1}, container {2}, {3:.2f}% compressed".format(
            out_wlpac_file,
            quantization_ratio,
            container,
            100.0 - ((orig_size - new_size) / orig_size) * 100.0,
        )
    )


def wlpac_decode(in_wlpac_file, out_fname):
    w = WLPACInfo.load_from_file(in_wlpac_file)
    x_prime = wfir_reconstruct(w.residual, w.sampling_frequency, 1)
    soundfile.write(out_fname, x_prime, w.sampling_frequency)


def bark_warp_coef(fs):
    return (
        1.0674 * numpy.sqrt((2.0 / numpy.pi) * numpy.arctan(0.06583 * fs / 1000.0))
        - 0.1916
    )


def warped_remez_coefs(fs, order):
    l = 20
    r = min(20000, fs / 2 - 1)
    t = 1

    c = scipy.signal.remez(
        order + 1, [0, l - t, l, r, r + t, 0.5 * fs], [0, 1, 0], fs=fs
    )
    return c.tolist()


def wfir(x: numpy.ndarray, fs: float, order: int) -> numpy.ndarray:
    a = bark_warp_coef(fs)

    B = [-a.conjugate(), 1]
    A = [1, -a]
    ys = [0] * order

    ys[0] = scipy.signal.lfilter(B, A, x)
    for i in range(1, len(ys)):
        ys[i] = scipy.signal.lfilter(B, A, ys[i - 1])

    c = warped_remez_coefs(fs, order)

    x_hat = c[0] * x
    for i in range(order):
        x_hat += c[i + 1] * ys[i]

    r = x - x_hat
    return r


def wfir_reconstruct(r: numpy.ndarray, fs: float, order: int) -> numpy.ndarray:
    def wfir_reconstruct_numerator(a, M):
        n = (numpy.poly1d([1, -a])) ** M
        return n.c

    def wfir_reconstruct_denominator(a, M, c):
        if len(c) != M + 1:
            raise ValueError("len filter coefficient array must be order+1")
        expr1 = (numpy.poly1d([1, -a])) ** M
        i = 0
        expr2 = c[i] * (numpy.poly1d([-a, 1]) ** 0) * (numpy.poly1d([1, -a])) ** (M - 0)
        for i in range(1, len(c)):
            expr2 += (
                c[i] * (numpy.poly1d([-a, 1]) ** i) * (numpy.poly1d([1, -a])) ** (M - i)
            )
        den = expr1 - expr2
        return den.c

    a = bark_warp_coef(fs)
    c = warped_remez_coefs(fs, order)

    B = wfir_reconstruct_numerator(a, order)
    A = wfir_reconstruct_denominator(a, order, c)

    x = scipy.signal.lfilter(B, A, r)
    return x
