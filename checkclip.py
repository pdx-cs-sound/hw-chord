#!/usr/bin/python3
import argparse
import numpy as np
import sys, soundfile

ap = argparse.ArgumentParser()
ap.add_argument(
    "-t", "--test",
    help="Test WAV.",
)
ap.add_argument(
    "-r", "--ref",
    help="Reference WAV.",
)
args = ap.parse_args()

def approx(n1, n2, delta):
    return abs(n1 - n2) <= delta

def fail(msg):
    print(msg)
    exit(1)

# Read a tone from a wave file.
def read_reference(filename):
    fref = soundfile.SoundFile(filename)
    data = fref.read(dtype=np.int16)
    return (fref, data)

def compare_test(fref, filename):
    with soundfile.SoundFile(filename) as f:
        if f.format != fref.format:
            fail(f"wrong file format {f.format}")
        if f.subtype != fref.subtype:
            fail(f"wrong file subtype {f.subtype}")
        if f.channels != fref.channels:
            fail(f"wrong number {f.channels} of channels")
        if f.samplerate != fref.samplerate:
            fail(f"wrong sample rate {f.samplerate}")
        data = f.read(dtype=np.int16)
        if f.frames != fref.frames:
            dframe = f.frames - fref.frames
            print(f"warning: length {dframe:+} frames")
            if not approx(f.frames, fref.frames, 100):
                tframe = f.frames / f.samplerate
                fail(f"wrong clip length {tframe} secs")
            data = np.resize(data, fref.frames)
    return data

fref, refwav = read_reference(args.ref)
wav = compare_test(fref, args.test)

signal = (wav.astype(np.float64) - refwav.astype(np.float64)) / 32768.0
rms = np.sqrt(np.mean(np.square(signal)))
if rms >= 0.1:
    fail(f"rms error {rms}")
