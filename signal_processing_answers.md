# Signal Processing – Answers

**A. What is the difference between these graphs?**

Graph 1 is in the **time domain**: amplitude [G] vs. time. It shows how the
vibration evolves moment to moment. Graph 2 is in the **frequency domain**
(a spectrum): amplitude [G] vs. frequency [Hz]. It shows which frequency
components a signal contains and how strong each one is. The two views are
connected by the Fourier transform (FFT), so one signal can be shown in
both forms.

**B. How would I determine whether they come from the same data set?**

The task does not state that both graphs come from the same signal, so I
would not assume it. I would look for evidence of consistency or
inconsistency:

1. **FFT check:** run an FFT on the raw samples behind Graph 1 and compare
   the peak frequencies and amplitudes with Graph 2. A match supports the
   same-capture hypothesis.
2. **Metadata:** compare sampling rate, duration, sensor ID, timestamp,
   measurement axis and units. Graph 2's frequency axis ends near 5 kHz,
   which would imply a sampling rate of about 10 kHz (Nyquist) for the
   measurement behind Graph 2. This says nothing about Graph 1 unless the
   two are confirmed to be the same capture.
3. **Amplitude sanity check:** two components of ~1 G each would sum to
   peaks of up to ~2 G in the time domain, while Graph 1 stays within
   about ±1 G. This suggests different captures or filtering, but it is
   not proof, since values are read from an image.


**C. What can be learned from Graph 2 that cannot be learned from Graph 1?**

In the time domain the signal is a dense waveform whose composition is
hard to read. The spectrum shows directly that it contains only two
dominant components: one at a very low frequency (near 0 Hz, I estimate
the order of tens of Hz) and one at about 4000 Hz, each with an amplitude
of roughly 1 G. The exact frequency of each component, which is not
readable from the time plot, is what matters in machine condition
monitoring: different faults appear at characteristic frequencies, so the spectrum
shows what is vibrating and at which frequency. It also separates a real disturbance from background noise.