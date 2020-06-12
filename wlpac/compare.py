import matplotlib.pyplot as plt
import soundfile
from pesq import pesq
import os


def wlpac_compare(file1, file2):
    reference, fs = soundfile.read(file1)
    result, fs = soundfile.read(file2)

    print("PESQ: {0}".format(pesq(fs, reference, result, "nb")))

    plt.figure()
    _, _, _, im = plt.specgram(reference, Fs=fs, NFFT=1024, noverlap=256)
    fname = os.path.basename(file1)
    plt.title(file1)
    plt.savefig("{0}-specgram.png".format(fname))
    plt.close()

    plt.figure()
    _, _, _, im = plt.specgram(result, Fs=fs, NFFT=1024, noverlap=256)
    fname = os.path.basename(file2)
    plt.title(file2)
    plt.savefig("{0}-specgram.png".format(fname))
    plt.close()
