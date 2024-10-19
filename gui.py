from tkinter import *
from tkinter.ttk import *
from math import sqrt
import pygame.midi
import tkinter.font as tkfont


root = Tk()
root.geometry('1024x800')
root.title('Bastard Beat')

pygame.midi.init()
output_id = pygame.midi.get_default_output_id()
output = pygame.midi.Output(output_id)
print(pygame.midi.get_device_info(output_id))

base_offset = 21

time_step = 1000 // 120
#print(time_step)

background_colour = '#222'

cell_size = 40

num_cells_x = 16
num_cells_y = 16

font_spec = tkfont.Font(family="Georgia", size=20)
font_metrics = font_spec.metrics()

colours = {
    'Black': '#333',
    'Dark-Gray': '#5f574f',
    'Light-Grey': '#c2c3c7',
    'White': '#eee',
    'Yellow': '#ffd817',
    'Orange': '#ff4f00',
    'Red': '#e33',
    'Green': '#8BEF88',
    'Cyan': '#A8FDE8',
    'Blue': '#88f',
    'Purple': '#A349A4',
}



frame = Frame(root)
frame.pack(fill=BOTH, expand=YES, padx=0, pady=0)

hscrollbar = Scrollbar(frame, orient=HORIZONTAL)
hscrollbar.pack(side=BOTTOM, fill=X)

vscrollbar = Scrollbar(frame, orient=VERTICAL)
vscrollbar.pack(side=RIGHT, fill=Y)

canvas = Canvas(frame, bd=0, bg=background_colour)
canvas.pack(side=LEFT, fill=BOTH, expand=YES)

hscrollbar.config(command=canvas.xview)
vscrollbar.config(command=canvas.yview)


def get_visible_ids(tag_name=None, ignore_tags=None):
    ignore_list = []
    #ignore_list.extend(canvas.find_withtag('colours'))
    #ignore_list.extend(canvas.find_withtag('info'))

    #visible_ids = set(canvas.find_all()) - set(ignore_list)
    all_items = canvas.find_all() if tag_name is None else canvas.find_withtag(tag_name)
    visible_ids = {item for item in all_items if canvas.itemcget(item, 'state') != 'hidden'} - set(ignore_list)
    return visible_ids


def get_live_ids(tag_name=None):
    all_items = canvas.find_all() if tag_name is None else canvas.find_withtag(tag_name)
    deleted_ids = canvas.find_withtag('deleted')
    live_layer_ids = tuple(set(all_items) - set(deleted_ids))
    return live_layer_ids


def on_canvas_resize(event=None):
    #print('resize')
    bbox = canvas.bbox('all')
    #print(f'{bbox=}')
    window_width, window_height = canvas.winfo_width(), canvas.winfo_height()

    if bbox is None:
        x1 = -window_width
        y1 = -window_height
        x2 = window_width * 2
        y2 = window_height * 2
    else:
        #print(bbox)
        x1 = bbox[0] - bbox[2] - window_width
        y1 = bbox[1] - bbox[3] - window_height
        x2 = bbox[2] + bbox[2] + window_width
        y2 = bbox[3] + bbox[3] + window_width

    scroll_region = canvas.cget("scrollregion")
    if scroll_region == '':
        #print('not set')
        pass
    else:
        old_x1, old_y1, old_x2, old_y2 = (float(n) for n in scroll_region.split(' '))
        #print(('old', old_x1, old_y1, old_x2, old_y2))
        x1 = min(x1, old_x1)
        y1 = min(y1, old_y1)
        x2 = max(x2, old_x2)
        y2 = max(y2, old_y2)

    #print(('new', x1, y1, x2, y2))

    canvas.config(scrollregion=(x1, y1, x2, y2))

    canvas.config(
        xscrollcommand=hscrollbar.set,
        yscrollcommand=vscrollbar.set)


def echo_event(event):
    #print(event)
    return "break"


canvas.bind('<Configure>', on_canvas_resize)


def start_panning(event):
    x, y = event.x, event.y
    canvas.scan_mark(x, y)

def motion_panning(event):
    x, y = event.x, event.y
    canvas.scan_dragto(x, y, gain=1)

canvas.bind('<ButtonPress-3>', start_panning)
canvas.bind('<B3-Motion>', motion_panning)


root.bind('<Alt_L>', lambda x: "break") # ignore key press


note_map = {
        220: 0, # \
        90: 1, # Z
        88: 2, # X
        67: 3, # C
        86: 4, # V
        66: 5, # B
        78: 6, # N
        77: 7, # M
        188: 8, # ,
        190: 9, # .
        191: 10, # /

        65: 11, # A
        83: 12, # S
        68: 13, # D
        70: 14, # F
        71: 15, # G
        72: 16, # H
        74: 17, # J
        75: 18, # K
        76: 19, # L
        186: 20, # ;
        192: 21, # '
        222: 22, # #

        81: 23, # Q
        87: 24, # W
        69: 25, # E
        82: 26, # R
        84: 27, # T
        89: 28, # Y
        85: 29, # U
        73: 30, # I
        79: 31, # O
        80: 32, # P
        219: 33, # [
        221: 34, # ]

        49: 35, # 1
        50: 36, # 2
        51: 37, # 3
        52: 38, # 4
        53: 39, # 5
        54: 40, # 6
        55: 41, # 7
        56: 42, # 8
        57: 43, # 9
        48: 44, # 0
        189: 45, # -
        187: 46, # =

        8:  0, # backspace
        13: 0, # enter
        16: 0, # shift
        17: 0, # ctrl
        27: 0, # escape
        33: 0, # page up
        34: 0, # page down
        35: 0, # end
        36: 0, # home
        38: 0, # del
        45: 0, # insert
        37: 0, # left
        38: 0, # up
        39: 0, # right
        40: 0, # down
        }

def on_key_press(event):
    #print(event)

    char = event.char
    keysym = event.keysym
    #print(f'{char=}, {keysym=}')

    match keysym:
        case 'Up':
            move_cursor(delta_y=-1)
            return 'break'
        case 'Down':
            move_cursor(delta_y=1)
            return 'break'
        case 'Left':
            move_cursor(delta_x=-1)
            return 'break'
        case 'Right':
            move_cursor(delta_x=1)
            return 'break'
        case 'space':
            move_cursor(delta_x=1)
            return 'break'


    #print(event.keycode)
    note = base_offset + note_map.get(event.keycode, event.keycode)

    set_note(note, input_cursor_x, input_cursor_y)

    output.write_short(0x90, note, 100)  # Note on, channel 0, note 60, velocity 100

    move_cursor(delta_x=1)

    return 'break'

def set_note(note, cell_x, cell_y):
    note_name = pygame.midi.midi_to_ansi_note(note)
    print(note_name)

    if '#' in note_name:
        cell_colour = 'black'
    else:
        cell_colour = 'white'

    canvas.create_rectangle(
        cell_x * cell_size,
        cell_y * cell_size,
        (cell_x + 1) * cell_size,
        (cell_y + 1) * cell_size,
        fill=cell_colour,
        #outline='black',
    )


cursor_colour = 'white'
cursor_height = font_metrics["ascent"] + 2

input_cursor_id = None
music_cursor_id = None

input_cursor_x = 0
input_cursor_y = 0

def create_input_cursor(x, y):
    global input_cursor_id
    input_cursor_id = canvas.create_rectangle(
            x,
            y,
            x+cell_size,
            y+cell_size,
            tags='cell',
            fill=cursor_colour)


def create_music_cursor(x, y):
    global music_cursor_id
    music_cursor_id = canvas.create_rectangle(
            x,
            y,
            x+(cell_size//8),
            y+(cell_size*num_cells_y),
            tags='cell',
            fill=cursor_colour)


def set_cursor(x, y):
    global input_cursor_x
    global input_cursor_y

    input_cursor_x = min(max(x, 0), num_cells_x)
    input_cursor_y = min(max(y, 0), num_cells_y)

    if input_cursor_x == 16: input_cursor_x = 0
    if input_cursor_y == 16: input_cursor_y = 0

    x = input_cursor_x * cell_size
    y = input_cursor_y * cell_size

    canvas.coords(
            input_cursor_id,
            x, y,
            x + cell_size, y + cell_size,
            )

def move_cursor(delta_x=0, delta_y=0):
    new_x = input_cursor_x + delta_x
    new_y = input_cursor_y + delta_y

    set_cursor(new_x, new_y)


def flash_input_cursor():
    global cursor_colour
    cursor_colour = "red" if cursor_colour == 'white' else "white"
    canvas.itemconfig(input_cursor_id, fill=cursor_colour)
    canvas.after(1000, flash_input_cursor)


def debug_object(obj):
    print(str(obj))
    print(repr(obj))
    for attr_name in [a for a in dir(obj) if not a.startswith('_')]:
        print((attr_name, getattr(obj, attr_name)))


def move_cursor_to_mouse(event):
    x = canvas.canvasx(event.x) // cell_size
    y = canvas.canvasy(event.y) // cell_size
    print((x, y))
    set_cursor(x, y)
    return 'break'

task_id_play = None
played = None


def play_notes(notes):
    if not notes:
        return
    c = notes.pop(0)
    #print((note, notes))

    keycode = ord(c.upper())
    note = base_offset + note_map.get(keycode, keycode)
    #print(f'{c=} {keycode=} {note=}')
    print(pygame.midi.midi_to_ansi_note(note))
    output.write_short(0x90, note, 100)  # Note on, channel 0, note 60, velocity 100

    canvas.after(100, play_notes, notes)


def play_item(item_id):
    played.add(item_id)
    notes = list(canvas.itemcget(item_id, 'text'))
    #print(f'play {item_id=} {notes=}')
    canvas.after(0, play_notes, notes)


def stop_and_rewind(event=None):
    global task_id_play
    task_id_play = None
    x, y, *_ = canvas.coords(music_cursor_id)
    target_x = 0
    delta_x = target_x - x
    canvas.move(music_cursor_id, delta_x, 0)


def step(init=False):
    global task_id_play
    if init:
        pass
    elif task_id_play is None:
        return
    task_id_play = canvas.after(time_step, step)

    coords = canvas.coords(music_cursor_id)

    grid_ids = canvas.find_withtag('grid')

    ignore_list = set((input_cursor_id, music_cursor_id, *grid_ids))

    overlaps = set(canvas.find_overlapping(*coords)) - ignore_list - played
    for item_id in overlaps:
        play_item(item_id)

    canvas.move(music_cursor_id, 1, 0)


def toggle_play(event):
    global task_id_play
    global played
    if task_id_play is None:
        played = set()
        step(init=True)
    else:
        canvas.after_cancel(task_id_play)
        task_id_play = None


def draw_grid(width, height, interval):
    global grid_ids
    # Vertical lines
    for i in range(0, width, interval):
        line_id = canvas.create_line(i, 0, i, height, fill="gray", tags='grid')
    
    # Horizontal lines
    for i in range(0, height, interval):
        canvas.create_line(0, i, width, i, fill="gray", tags='grid')

    canvas.create_line(width-1, 0, width-1, height, fill="gray", tags='grid')
    canvas.create_line(0, height-1, width, height-1, fill="gray", tags='grid')



create_music_cursor(0, 0)

draw_grid(
        width=num_cells_x * cell_size,
        height=num_cells_y * cell_size,
        interval=cell_size,
        )

create_input_cursor(0, 0)
flash_input_cursor()

root.bind('<KeyPress-Escape>', stop_and_rewind)
root.bind('<KeyPress-Return>', toggle_play)
root.bind('<KeyPress-Control_L>', lambda e: None)

root.bind('<KeyPress-Up>', on_key_press)
root.bind('<KeyPress-Down>', on_key_press)
root.bind('<KeyPress-Left>', on_key_press)
root.bind('<KeyPress-Right>', on_key_press)

canvas.bind('<Double-Button-1>', move_cursor_to_mouse)
root.bind('<KeyPress>', on_key_press)

root.mainloop()

del output
pygame.midi.quit()

