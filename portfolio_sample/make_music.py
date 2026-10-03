"""Synthesize a ~60s light ambient pad and mux it onto the silent medical-billing video."""
import numpy as np
import wave
import subprocess
import imageio_ffmpeg

OUTDIR = "C:/Users/M Bilal/Desktop/medical.bill/portfolio_sample"
SR = 44100

progression = [
    [261.63, 329.63, 392.00, 493.88],   # Cmaj7
    [220.00, 261.63, 329.63, 392.00],   # Am7
    [174.61, 220.00, 261.63, 329.63],   # Fmaj7
    [196.00, 246.94, 293.66, 329.63],   # G6
]
chords = progression * 2  # loop the progression twice over the full minute

TOTAL_DUR = 60.0
CROSSFADE = 0.6
n_chords = len(chords)
chord_dur = TOTAL_DUR / n_chords + CROSSFADE / n_chords

def render_chord(freqs, dur, sr=SR):
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    sig = np.zeros_like(t)
    for i, fq in enumerate(freqs):
        amp = 1.0 / (i + 1.4)
        vibrato = 1 + 0.0015 * np.sin(2 * np.pi * 0.15 * t)
        sig += amp * np.sin(2 * np.pi * fq * vibrato * t)
        sig += 0.18 * amp * np.sin(2 * np.pi * fq * 2 * vibrato * t)
    sig /= len(freqs)
    return sig

segments = [render_chord(c, chord_dur) for c in chords]

fade_len = int(CROSSFADE * SR)
total_len = int(TOTAL_DUR * SR)
out = np.zeros(total_len + fade_len)
pos = 0
for seg in segments:
    seg = seg.copy()
    n = len(seg)
    fl = min(fade_len, n // 2)
    seg[:fl] *= np.linspace(0, 1, fl)
    seg[-fl:] *= np.linspace(1, 0, fl)
    end = pos + n
    if end > len(out):
        out = np.pad(out, (0, end - len(out)))
    out[pos:end] += seg
    pos += n - fl

out = out[:total_len]
kernel = np.ones(6) / 6
out = np.convolve(out, kernel, mode="same")

env = np.ones_like(out)
fi = int(1.2 * SR)
fo = int(2.0 * SR)
env[:fi] = np.linspace(0, 1, fi)
env[-fo:] = np.linspace(1, 0, fo)
out *= env
peak = np.max(np.abs(out))
out = out / peak * 0.22

stereo = np.stack([out, out * 0.985], axis=1)
pcm = (stereo * 32767).astype(np.int16)

wav_path = f"{OUTDIR}/_bg_music.wav"
with wave.open(wav_path, "w") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
print("wrote", wav_path, TOTAL_DUR, "s")

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
video_in = f"{OUTDIR}/Project_Video_MedicalBilling_silent.mp4"
video_out = f"{OUTDIR}/Project_Video_MedicalBilling.mp4"

cmd = [
    ffmpeg, "-y",
    "-i", video_in,
    "-i", wav_path,
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "128k",
    "-shortest",
    "-map", "0:v:0", "-map", "1:a:0",
    video_out,
]
subprocess.run(cmd, check=True)
print("wrote", video_out)
