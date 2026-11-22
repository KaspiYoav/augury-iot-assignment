SIGNAL PROCESSING – ANSWERS

A. What is the difference between these graphs?
Graph 1 is the signal in the TIME domain (amplitude vs. time): it shows how
the vibration changes from moment to moment. Graph 2 is the signal in the
FREQUENCY domain (amplitude vs. frequency, a spectrum): it shows which
frequencies the signal is made of and how strong each one is. The two are
different representations of the same kind of data, connected by the Fourier
transform (FFT).

B. How would I determine whether they come from the same data set?
1. Compute the FFT of the time-domain signal (Graph 1) and compare the
   resulting spectrum to Graph 2: same peak frequencies and amplitudes
   suggest the same data.
2. Check consistency of the parameters: sampling rate (Graph 2's axis
   reaches ~5 kHz, so by Nyquist fs would be about 10 kHz), duration, and
   frequency resolution (1 / duration).
3. Optionally do the inverse FFT of Graph 2 and compare to Graph 1
   (only possible if phase information is available).
4. Compare metadata: sensor ID, timestamp, units (G), measurement axis.
Note: a spectrum alone drops phase, so matching magnitudes is strong
evidence but not proof.

C. What can be learned from Graph 2 that cannot be learned from Graph 1?
In the time domain the signal looks like a dense, hard-to-read pattern.
The spectrum shows clearly that it consists of just two components: one
near 0 Hz (a DC offset / very low-frequency component) and one at 4000 Hz,
each with amplitude ~1 G. This lets us identify the vibration source's
characteristic frequencies, which is the basis of machine condition
monitoring: different faults (imbalance, bearing wear, misalignment)
appear at different, specific frequencies.