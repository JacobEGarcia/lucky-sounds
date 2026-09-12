import numpy as np, wave, os
SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wav')

def t(dur): return np.arange(int(SR * dur)) / SR
def env_exp(n, tau):
    x = np.arange(n) / SR
    return np.exp(-x / tau)
def bell(freq, dur, tau=None, bright=1.0):
    n = int(SR * dur); x = np.arange(n) / SR
    tau = tau or dur / 3.5
    y = np.sin(2*np.pi*freq*x) * np.exp(-x/tau)
    y += 0.4*bright*np.sin(2*np.pi*freq*2.76*x) * np.exp(-x/(tau*0.45))
    y += 0.18*bright*np.sin(2*np.pi*freq*5.40*x) * np.exp(-x/(tau*0.2))
    return y / max(1e-9, np.abs(y).max())
def mallet(freq, dur, tau=None):
    n = int(SR * dur); x = np.arange(n) / SR
    tau = tau or dur / 4
    y = np.sin(2*np.pi*freq*x) + 0.3*np.sin(2*np.pi*freq*2.01*x)
    return y * np.exp(-x/tau) / 1.3
def chirp(f0, f1, dur, tau=None):
    n = int(SR * dur); x = np.arange(n) / SR
    k = (f1 - f0) / dur
    ph = 2*np.pi*(f0*x + 0.5*k*x*x)
    tau = tau or dur / 2.5
    return np.sin(ph) * np.exp(-x/tau)
def noise(n, seed=7): return np.random.default_rng(seed).standard_normal(n)
def bandpass(x, fc, bw):
    from numpy.fft import rfft, irfft, rfftfreq
    X = rfft(x); f = rfftfreq(len(x), 1/SR)
    H = np.exp(-0.5*((f-fc)/(bw/2))**2)
    return irfft(X*H, len(x))
def trem(x, rate, depth=0.6):
    x = x.copy(); n = len(x); xx = np.arange(n)/SR
    return x * (1 - depth*0.5*(1+np.sin(2*np.pi*rate*xx)))
def stereo(y, detune_cents=3):
    """two slightly detuned renders -> decorrelated L/R (cheap width)"""
    yL = y; yR = np.roll(y, 0)
    if detune_cents:
        # resample-shift trick: tiny linear interp shift ~= few cents at hf, fine for sfx
        idx = np.arange(len(y))
        r = 2**(detune_cents/1200)
        yR = np.interp(idx*r, idx, y, left=0, right=0)[:len(y)]
    m = np.vstack([yL, yR]).T
    return m / max(1e-9, np.abs(m).max()) * 0.85
def place(dur_total, events):
    """events: list of (start_sec, mono_array)"""
    n = int(SR*dur_total); mix = np.zeros(n)
    for st, y in events:
        i0 = int(st*SR); i1 = min(n, i0+len(y))
        mix[i0:i1] += y[:i1-i0]
    return mix
def save(name, ystereo):
    m = np.clip(ystereo, -1, 1)
    pcm = (m * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('rendered', name)

A3,A4,B4,Cs5,E5,Cs6,E6,Fs5,A5 = 220.0,440.0,493.88,554.37,659.25,1108.7,1318.5,739.99,880.0

# 1. audio logo: A5 -> Cs6 -> E6 bells over a warm A3 pluck + shimmer
logo = place(2.0, [
    (0.00, 0.5*mallet(A3, 1.2, tau=0.5)),
    (0.02, 0.9*bell(A5, 0.9)),
    (0.16, 0.9*bell(Cs6, 0.9)),
    (0.32, 1.0*bell(E6, 1.3)),
    (0.35, 0.25*chirp(3000, 6000, 0.7, tau=0.35)),
])
save('audio_logo', stereo(logo))

# 2. startup chime: soft rising A4 -> E5 + air swell
sw = bandpass(noise(int(SR*0.5), 3), 2500, 2000) * env_exp(int(SR*0.5), 0.4)[::-1]
start = place(1.1, [
    (0.00, 0.15*sw),
    (0.05, 0.8*mallet(A4, 0.6)),
    (0.22, 0.9*mallet(E5, 0.8)),
])
save('startup_chime', stereo(start))

# 3. notify message: soft two-note E5 -> A5
save('notify_message', stereo(place(0.7, [(0.0, 0.7*mallet(E5,0.35)), (0.14, 0.8*mallet(A5,0.5))])))

# 4. notify task done: ascending triad + coin sparkle
done = place(1.0, [
    (0.00, 0.8*mallet(A4,0.3)), (0.09, 0.8*mallet(Cs5,0.3)), (0.18, 0.9*mallet(E5,0.45)),
    (0.20, 0.3*chirp(4500, 8000, 0.35, tau=0.18)), (0.30, 0.2*chirp(6000, 9000, 0.3, tau=0.15)),
])
save('notify_task_done', stereo(done))

# 5. notify alert: two gentle low bell taps
save('notify_alert', stereo(place(0.8, [(0.0, 0.7*bell(A3,0.35,bright=0.5)), (0.28, 0.7*bell(A3,0.4,bright=0.5))])))

# 6. ui tap: short tick
n6 = int(SR*0.12); x6 = np.arange(n6)/SR
tick = 0.6*np.sin(2*np.pi*2000*x6)*np.exp(-x6/0.012) + 0.4*bandpass(noise(n6,5), 4000, 3000)*np.exp(-x6/0.008)
save('ui_tap', stereo(tick, detune_cents=0))

# 7. ui toggle: two-tone click up
save('ui_toggle', stereo(place(0.28, [(0.0, 0.5*chirp(700, 900, 0.08, tau=0.03)), (0.09, 0.5*chirp(1100, 1500, 0.09, tau=0.035))]), detune_cents=0))

# 8. ui success: A5 bell + E6 fifth
save('ui_success', stereo(place(0.55, [(0.0, 0.8*bell(A5,0.3)), (0.08, 0.6*bell(E6,0.4))])))

# 9. ui error: soft low thud, pitch droop
save('ui_error', stereo(0.8*chirp(220, 150, 0.4, tau=0.12), detune_cents=0))

# 10. pet eat: 4 munch bursts
ev = []
for i in range(4):
    nb = bandpass(noise(int(SR*0.09), 11+i), 900+150*i, 900)
    nb *= np.hanning(len(nb))
    ev.append((i*0.16, 0.9*nb))
    ev.append((i*0.16+0.01, 0.25*chirp(300+40*i, 180, 0.08, tau=0.03)))
save('pet_eat', stereo(place(0.75, ev), detune_cents=0))

# 11. pet play: bouncy arpeggio with pitch bounce
ev = []
for i, f in enumerate([A4, Cs5, E5, A5, E5, A5]):
    ev.append((i*0.11, 0.7*chirp(f*0.92, f, 0.14, tau=0.06)))
save('pet_play', stereo(place(0.85, ev)))

# 12. pet sleep: descending lullaby + breath
br = bandpass(noise(int(SR*1.4), 21), 600, 500)
br *= 0.5*(1+np.sin(2*np.pi*0.8*np.arange(len(br))/SR))
sleep = place(1.7, [
    (0.00, 0.06*br),
    (0.05, 0.7*mallet(E5, 0.6, tau=0.35)), (0.5, 0.7*mallet(Cs5, 0.6, tau=0.35)), (0.95, 0.8*mallet(A4, 0.7, tau=0.4)),
])
save('pet_sleep', stereo(sleep))

# 13. pet happy: purr + rising chirp
n13 = int(SR*1.2); x13 = np.arange(n13)/SR
purr = bandpass(noise(n13, 31), 120, 100) * (0.5+0.5*np.sin(2*np.pi*24*x13)) * np.exp(-x13/0.9)
happy = place(1.2, [(0.0, 1.2*purr), (0.25, 0.5*chirp(600, 1400, 0.5, tau=0.3)), (0.7, 0.4*chirp(900, 1800, 0.35, tau=0.2))])
save('pet_happy', stereo(happy, detune_cents=0))

# 14. pet sad: descending minor third E4 -> C4 with vibrato
def vib_tone(f, dur, vib=5.5, depth=6):
    n = int(SR*dur); x = np.arange(n)/SR
    ph = 2*np.pi*(f*x + (depth/(2*np.pi*vib))*np.sin(2*np.pi*vib*x))
    return np.sin(ph)*np.exp(-x/(dur/2.5))
save('pet_sad', stereo(place(1.0, [(0.0, 0.7*vib_tone(329.63, 0.45)), (0.42, 0.8*vib_tone(261.63, 0.55))])))

# 15. pet evolve: sparkle gliss + bright A major bell chord
n15 = int(SR*0.9); x15 = np.arange(n15)/SR
gl = np.sin(2*np.pi*(900*x15 + 0.5*(3400/0.9)*x15*x15)) * (0.5+0.5*np.sin(2*np.pi*18*x15)) * np.exp(-x15/0.5)
evolve = place(1.9, [
    (0.0, 0.5*gl),
    (0.75, 0.8*bell(A4, 1.0)), (0.78, 0.7*bell(Cs5, 1.0)), (0.81, 0.8*bell(E5, 1.1)), (0.85, 0.5*bell(A5, 1.1)),
])
save('pet_evolve', stereo(evolve))
print('ALL RENDERED')
