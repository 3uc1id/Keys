import threading
import queue
import numpy as np
import pyaudio
import dataclasses
from keys.constants import *


@dataclasses.dataclass(slots=True)
class ToneData:
    freq: float
    phase: float
    amplitude: float
    phase_inc: float


class SoundSynthesizer(threading.Thread):
    def __init__(self, buffer_size=BUFFLEN, sampling_rate=F_SAMPLE):
        super().__init__()
        self.bufflen = buffer_size
        self.sampling_rate = sampling_rate
        self.bufflen_t = buffer_size / sampling_rate
        self.queue = queue.Queue()
        self.active_notes: dict[str, ToneData] = {}
        self.active_notes_lock = threading.Lock()
        self.running = True
        # Create a list for command lookup, adjusting for zero-based indexing
        self.command_lookup = [
            self.handle_start_note,
            self.handle_stop_note,
            self.update_buffer_size,
            self.update_sampling_rate,
            self.stop
        ]
        self.pa: pyaudio.PyAudio = None
        self.stream: pyaudio.Stream = None

    def _make_audio_callback(self):
        t_buf = np.linspace(0, self.bufflen_t, num=self.bufflen, dtype=np.float32)
        wave_buf = np.zeros(self.bufflen, dtype=np.float32)

        def audio_callback(in_data, frame_count, time_info, status):
            nonlocal wave_buf
            if not self.running:
                return b'\x00', pyaudio.paContinue
            
            wave_buf[:] = 0.0
            self.active_notes_lock.acquire()
            for td in self.active_notes.values():
                wave_buf += td.amplitude * np.sin(TAU * td.freq * t_buf + td.phase)
                td.phase += td.phase_inc
                td.phase %= TAU
            self.active_notes_lock.release()
            return wave_buf.tobytes(), pyaudio.paContinue
        
        return audio_callback

    def run(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.sampling_rate,
            channels=1,
            format=pyaudio.paFloat32,
            output=True,
            stream_callback=self._make_audio_callback(),
            frames_per_buffer=self.bufflen
        )

        while self.running:
            try:
                command, args = self.queue.get(timeout=0.1)
            except queue.Empty:
                pass
            else:
                self.active_notes_lock.acquire()
                self.command_lookup[command](*args)
                self.active_notes_lock.release()

        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def stop(self):
        self.running = False

    def handle_start_note(self, note: str, frequency: float, amplitude: float):
        self.active_notes[note] = ToneData(frequency, 0.0, amplitude, TAU*frequency*self.bufflen_t)

    def handle_stop_note(self, note):
        if note in self.active_notes:
            self.active_notes.pop(note)

    def update_buffer_size(self, new_buffer_size):
        if new_buffer_size != self.buffer_size:
            self.bufflen = new_buffer_size
            self.bufflen_t = new_buffer_size / self.sampling_rate
            self.stream.stop_stream()
            self.stream.close()
            self.stream = self.p.open(format=pyaudio.paFloat32,
                                       channels=1,
                                       rate=self.sampling_rate,
                                       output=True,
                                       frames_per_buffer=new_buffer_size)

    def update_sampling_rate(self, new_sampling_rate):
        if new_sampling_rate != self.sampling_rate:
            self.sampling_rate = new_sampling_rate
            self.bufflen_t
            self.stream.stop_stream()
            self.stream.close()
            self.stream = self.p.open(format=pyaudio.paFloat32,
                                       channels=1,
                                       rate=self.sampling_rate,
                                       output=True,
                                       frames_per_buffer=self.bufflen)
