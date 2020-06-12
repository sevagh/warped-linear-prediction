from wlpac import wlpac_encode, wlpac_decode
from .compare import wlpac_compare
import scipy.io, scipy.io.wavfile
import argparse
import uuid


def encode():
    parser = argparse.ArgumentParser(
        prog="wlpac_encode", description="create a wlpac file from a wav file",
    )
    parser.add_argument("infile", help="Path to input file")

    args = parser.parse_args()

    fname = (args.infile.split("/")[-1]).split(".")[0]
    out_fname = "{0}-out-{1}.wlp.flac".format(fname, str(uuid.uuid4())[:8])

    wlpac_encode(args.infile, out_fname, container="flac")


def decode():
    parser = argparse.ArgumentParser(
        prog="wlpac_decode", description="recreate a wav file from a wlpac file",
    )
    parser.add_argument("infile", help="Path to input file")

    args = parser.parse_args()
    fname = (args.infile.split("/")[-1]).split(".")[0]
    out_fname = "{0}-out-{1}.wav".format(fname, str(uuid.uuid4())[:8])

    wlpac_decode(args.infile, out_fname)


def compare():
    parser = argparse.ArgumentParser(
        prog="wlpac_compare",
        description="compare original uncompressed wav file to wlp.flac file (PESQ + spectrogram)",
    )
    parser.add_argument("infile_wav", help="Path to input wav file")
    parser.add_argument("infile_wlpac", help="Path to input wlpac file")

    args = parser.parse_args()

    wlpac_compare(args.infile_wav, args.infile_wlpac)
