import tkinter as tk
from itertools import cycle
from .constants import SynthCommand, NOTE_TABLE
from .synthesizer import SoundSynthesizer


class App:
    def __init__(self,
                 title: str = 'Keys',
                 key_count: int = 7,
                 octave_count: int = 2,
                 width: int = 700,
                 height: int = 300):
        key_width = width // (key_count * octave_count)
        self.root = tk.Tk()
        self.root.title(title)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_offset = (screen_width - width) // 2
        y_offset = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x_offset}+{y_offset}')
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            highlightthickness=0,
            background='black')

        self.white_keys = []
        note_letters = 'CDEFGAB'
        for note_i, (pixel_i, letter_i) in enumerate(zip(range(0, width, key_width), cycle(note_letters))):
            white_key_i = self.canvas.create_rectangle(
                pixel_i+1, 0,
                pixel_i+key_width-1, height,
                fill='white',
                outline='black',
                tags=(f'{letter_i}{note_i//7 + 4}',)
            )
            self.white_keys.append(white_key_i)
            self.canvas.tag_bind(white_key_i,
                                 '<ButtonPress-1>',
                                 self.on_key_press)
            self.canvas.tag_bind(white_key_i,
                                 '<ButtonRelease-1>',
                                 self.on_key_release)

        self.black_keys = []
        for offset in range(octave_count):
            k = 7*offset
            for i in (1+k,2+k,4+k,5+k,6+k):
                black_key_i = self.canvas.create_rectangle(
                    (i-1/3)*key_width, 0,
                    (i+1/3)*key_width, 7/12*height,
                    fill='black',
                    tags=(f'{note_letters[i%7-1]}{i//7+4}#',
                          f'{note_letters[i%7]}{i//7+4}b')
                )
                self.black_keys.append(black_key_i)
                self.canvas.tag_bind(black_key_i,
                                     '<ButtonPress-1>',
                                     self.on_key_press)
                self.canvas.tag_bind(black_key_i,
                                     '<ButtonRelease-1>',
                                     self.on_key_release)

        self.canvas.pack()
        self.synth_thread = SoundSynthesizer()
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.synth_thread.stop() or self.synth_thread.join() or self.root.destroy())

    def on_key_press(self, event):
        key_id = event.widget.find_withtag('current')[0]
        self.canvas.itemconfigure(key_id, outline='red')
        note = self.canvas.gettags(key_id)[0]
        print('starting', note)
        self.synth_thread.queue.put((SynthCommand.START_NOTE,
                                    (note,
                                     NOTE_TABLE[note],
                                     0.1)))
        

    def on_key_release(self, event):
        key_id = event.widget.find_withtag('current')[0]
        self.canvas.itemconfigure(key_id, outline='black')
        note = self.canvas.gettags(key_id)[0]
        print('ending', note)
        self.synth_thread.queue.put((SynthCommand.STOP_NOTE,
                                    (note,)))

    def run(self):
        self.synth_thread.start()
        self.root.mainloop()
