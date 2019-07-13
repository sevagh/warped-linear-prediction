import numpy
import scipy
import scipy.signal
import scipy.io
import scipy.io.wavfile
import pickle
import lzma
import os


class WLPACInfo(object):
    def __init__(self, fs, q, l_, r_, lb):
        self.fs = fs
        self.q = q
        self.l_ = l_
        self.r_ = r_
        self.lb = lb


    def save_to_file(self, path):
        with lzma.open(path, 'wb') as f:
            pickle.dump(self, f)


    @classmethod
    def load_from_file(cls, path):
        with lzma.open(path, 'rb') as f:
            wlpac_obj = pickle.load(f)
            return wlpac_obj



def wlpac_encode(in_wav_file, out_wlpac_file, quality=0.5):
    fs, x = scipy.io.wavfile.read(in_wav_file)              
    r = wfir(x, fs, 1)
    q, l_, r_, lb = quantize(r, quality)
    wlpac_obj = WLPACInfo(fs, q, l_, r_, lb)
    wlpac_obj.save_to_file(out_wlpac_file)
    orig_size = os.path.getsize(in_wav_file)
    new_size = os.path.getsize(out_wlpac_file)
    print('Wrote {0} with quality {1}, {2:.2f}% smaller'.format(out_wlpac_file, quality, ((orig_size-new_size)/orig_size)*100.0))


def wlpac_decode(in_wlpac_file, out_wav_file):
    w = WLPACInfo.load_from_file(in_wlpac_file)
    r_prime = unquantize(w.q, w.l_, w.r_, w.lb)
    x_prime = wfir_reconstruct(r_prime, w.fs, 1)
    scipy.io.wavfile.write(out_wav_file, w.fs, x_prime)


def quantize(x, ratio: float):
    min_x = min(x)
    max_x = max(x)
    len_b = int(ratio*float(len(x)))
    bins = numpy.linspace(min_x, max_x, len_b)
    inds = numpy.digitize(x, bins)
    return inds, min_x, max_x, len_b


def unquantize(binned, l, r, lb):
    bins = numpy.linspace(l, r, lb)
    ret = []
    for b in binned:
        ret.append(bins[b-1])
    return numpy.asarray(ret)


def bark_warp_coef(fs):
        return 1.0674 * numpy.sqrt((2.0 / numpy.pi) * numpy.arctan(0.06583 * fs / 1000.0)) - 0.1916
    
    
def warped_remez_coefs(fs, order):
    l = 20
    r = min(20000, fs/2 - 1)
    t = 1
      
    c = scipy.signal.remez(order+1, [0, l-t, l, r, r+t, 0.5*fs], [0, 1, 0], fs=fs)
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
        x_hat += c[i+1] * ys[i]

    r = x - x_hat
    return r

def wfir_reconstruct(r: numpy.ndarray, fs: float, order: int) -> numpy.ndarray:
    def wfir_reconstruct_numerator(a, M):
        n = (numpy.poly1d([1, -a]))**M
        return n.c
    
    
    def wfir_reconstruct_denominator(a, M, c):
        if len(c) != M+1:
            raise ValueError('len filter coefficient array must be order+1')
        expr1 = (numpy.poly1d([1, -a]))**M
        i = 0
        expr2 = c[i]*(numpy.poly1d([-a, 1])**0)*(numpy.poly1d([1, -a]))**(M-0)
        for i in range(1, len(c)):
            expr2 += c[i]*(numpy.poly1d([-a, 1])**i)*(numpy.poly1d([1, -a]))**(M-i)
        den = expr1 - expr2
        return den.c
    
    
    a = bark_warp_coef(fs)
    c = warped_remez_coefs(fs, order)
    
    B = wfir_reconstruct_numerator(a, order)
    A = wfir_reconstruct_denominator(a, order, c)
    
    x = scipy.signal.lfilter(B, A, r)
    return x
