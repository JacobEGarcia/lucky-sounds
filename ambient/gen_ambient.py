import numpy as np, wave, os
SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wav2')
def noise(n, seed): return np.random.default_rng(seed).standard_normal(n)
def bandpass(x, fc, bw):
    from numpy.fft import rfft, irfft, rfftfreq
    X = rfft(x); f = rfftfreq(len(x), 1/SR)
    H = np.exp(-0.5*((f-fc)/(bw/2))**2)
    return irfft(X*H, len(x))
def lowpass(x, fc):
    from numpy.fft import rfft, irfft, rfftfreq
    X = rfft(x); f = rfftfreq(len(x), 1/SR)
    H = 1/(1+(f/fc)**4)
    return irfft(X*H, len(x))
def loopify(y, cut_L=None):
    """wrap-correct seamless loop: out[i] = y[i]*a + y[i+L]*(1-a) over the first
    xf samples; out[L-1]=y[L-1] wraps into out[0]=y[L], consecutive in source.
    The cut L is chosen at a low-energy point to keep the wrap delta small."""
    n = len(y); xf = min(SR*4, n//4)
    L = cut_L if cut_L is not None else n - xf
    out = y[:L].copy()
    a = 0.5 - 0.5*np.cos(np.pi*np.arange(xf)/xf)
    out[:xf] = y[:xf]*a + y[L:L+xf]*(1-a)
    return out
def mallet(freq, dur, tau=None):
    n = int(SR*dur); x = np.arange(n)/SR
    tau = tau or dur/4
    y = np.sin(2*np.pi*freq*x) + 0.3*np.sin(2*np.pi*freq*2.01*x)
    return y*np.exp(-x/tau)/1.3
def bell(freq, dur, tau=None, bright=1.0):
    n = int(SR*dur); x = np.arange(n)/SR
    tau = tau or dur/3.5
    y = np.sin(2*np.pi*freq*x)*np.exp(-x/tau)
    y += 0.4*bright*np.sin(2*np.pi*freq*2.76*x)*np.exp(-x/(tau*0.45))
    return y/max(1e-9, np.abs(y).max())
def detune(y):
    # 3-cent circular resample for width; any wrap artifact sits at the very
    # end of the long source and is cut/blended away by loopify afterwards
    idx = np.arange(len(y)); r = 2**(3/1200)
    pad = int(len(y)*(r-1)) + 64
    yext = np.concatenate([y, y[:pad]])
    return np.interp(idx*r, np.arange(len(yext)), yext)[:len(y)]
def stereo_pair(y, cut_L=None):
    # detune first, then loopify BOTH channels with the same cut L so each
    # channel is individually seamless at the identical loop point
    n = len(y); xf = min(SR*4, n//4)
    L = cut_L if cut_L is not None else n - xf
    chans = []
    for ch in (y, detune(y)):
        out = ch[:L].copy()
        a = 0.5 - 0.5*np.cos(np.pi*np.arange(xf)/xf)
        out[:xf] = ch[:xf]*a + ch[L:L+xf]*(1-a)
        chans.append(out)
    m = np.vstack(chans).T
    return m/max(1e-9, np.abs(m).max())*0.8
def save(name, m):
    m = np.clip(m, -1, 1)
    with wave.open(os.path.join(OUT, name+'.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((m*32767).astype(np.int16).tobytes())
    print('rendered', name)

DUR = 40  # seconds, pre-loopify
N = SR*DUR
PENT = [220.0, 246.94, 277.18, 329.63, 369.99, 440.0, 493.88, 554.37, 659.25]  # A maj pent spread

# 1. room_day: warm airy tone + soft random mallet plinks + distant purr swells
base = 0.05*lowpass(noise(N, 101), 500)
x = np.arange(N)/SR
base *= (1 + 0.15*np.sin(2*np.pi*0.05*x))  # slow breathing
mix = base.copy()
rng = np.random.default_rng(7)
for _ in range(26):  # sparse plinks
    st = rng.uniform(0, DUR-1)
    f = PENT[rng.integers(0, len(PENT))]*2
    i0 = int(st*SR); y = 0.16*mallet(f, 0.5)
    i1 = min(N, i0+len(y)); mix[i0:i1] += y[:i1-i0]
for st in [6, 21, 33]:  # purr swells
    n2 = int(SR*2.5); x2 = np.arange(n2)/SR
    p = bandpass(noise(n2, int(st)), 110, 90)*(0.5+0.5*np.sin(2*np.pi*22*x2))*np.exp(-x2/1.6)
    i0 = int(st*SR); mix[i0:i0+n2] += 0.25*p
save('room_day', stereo_pair(mix))

# 2. room_night: darker air + sparse low bells + cricket-ish high ticks
base = 0.04*lowpass(noise(N, 202), 300)
mix = base.copy()
rng = np.random.default_rng(11)
for _ in range(10):
    st = rng.uniform(0, DUR-1.2)
    f = PENT[rng.integers(0, 5)]  # low register only
    i0 = int(st*SR); y = 0.12*bell(f, 1.2, bright=0.4)
    i1 = min(N, i0+len(y)); mix[i0:i1] += y[:i1-i0]
for _ in range(40):  # crickets
    st = rng.uniform(0, DUR-0.1)
    n3 = int(SR*0.06); x3 = np.arange(n3)/SR
    c = np.sin(2*np.pi*4200*x3)*np.exp(-x3/0.02)
    i0 = int(st*SR); mix[i0:i0+n3] += 0.05*c
save('room_night', stereo_pair(mix))

# 3. room_rain: steady rain bed + occasional low mallet
rain = bandpass(noise(N, 303), 1800, 2600)*0.35 + lowpass(noise(N, 304), 400)*0.5
rain *= (1 + 0.1*np.sin(2*np.pi*0.07*np.arange(N)/SR))
mix = rain.copy()
rng = np.random.default_rng(13)
for _ in range(14):
    st = rng.uniform(0, DUR-0.8)
    f = PENT[rng.integers(0, len(PENT))]
    i0 = int(st*SR); y = 0.10*mallet(f, 0.7)
    i1 = min(N, i0+len(y)); mix[i0:i1] += y[:i1-i0]
save('room_rain', stereo_pair(mix))

# 4. music_pet_theme: gentle 8-bar pentatonic loop, music-box feel
bpm = 84; beat = 60/bpm; bars = 8; dur_m = bars*4*beat
Nm = int(SR*dur_m); mix = np.zeros(Nm + SR*4)
melody = [  # (beat_position, note) - simple lullaby-ish line, A maj pent
    (0,440),(1,554.37),(2,659.25),(3,554.37),
    (4,493.88),(5,659.25),(6,739.99),(7,659.25),
    (8,440),(9,554.37),(10,659.25),(11,880),
    (12,739.99),(13,659.25),(14,554.37),(15,493.88),
    (16,440),(17,554.37),(18,659.25),(19,554.37),
    (20,493.88),(21,440),(22,369.99),(23,329.63),
    (24,440),(25,554.37),(26,659.25),(27,880),
    (28,739.99),(29,659.25),(30,554.37),(31,440),
]
for b, f in melody:
    st = int(b*beat*SR); y = 0.5*bell(f, 0.9, bright=0.7)
    i1 = min(len(mix), st+len(y)); mix[st:i1] += y[:i1-st]
for bar in range(bars):  # soft low root each bar
    st = int(bar*4*beat*SR); y = 0.3*mallet(110, 1.4, tau=0.6)
    i1 = min(len(mix), st+len(y)); mix[st:i1] += y[:i1-st]
pad = lowpass(noise(len(mix), 404), 250)*0.03
mix += pad
save('music_pet_theme', stereo_pair(mix, cut_L=Nm))
print('AMBIENT DONE')
