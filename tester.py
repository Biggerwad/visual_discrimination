# Task
# Return eye tracker position for debugging
# Display two dots at top left and bottom right corners

from psychopy import visual, core, event, gui, data, sound
from pypixxlib import tracker

win = visual.Window(size=[1280, 1024],fullscr=True, monitor='secondMonitor', screen=1, units='pix', winType='pyglet', allowStencil=False, blendMode='avg', useFBO=True)

mouse = event.Mouse(visible=True, win=win)

mini = tracker.TRACKPixxMini()

mini.open()

# show both dots at corners
while True:
    left_eye = visual.Circle(win,radius=10, fillColor='red')
    right_eye = visual.Circle(win, radius=10, fillColor='blue')

    Lx, Ly, Rx, Ry = mini.getEyePosition()

    Lx = Lx / 1920 * 1280 
    Rx = Rx / 1920 * 1280 
    Ly = Ly / 1080 * 1024 - 50
    Ry = Ry / 1080 * 1024 - 50

    left_eye.pos = (Lx, Ly)
    right_eye.pos = (Rx, Ry)

    measurement = visual.TextStim(
        win=win,
        text=f'Left: ({Lx:.1f}, {Ly:.1f}), Right: ({Rx:.1f}, {Ry:.1f})',
        pos=(0, 0),
        color='white'
    )

    top_left = visual.Circle(win,radius=30, fillColor='yellow', pos=(-640, +520))
    bottom_right = visual.Circle(win,radius=30, fillColor='yellow', pos=(640, -520))


    # Draw everything

    left_eye.draw()
    right_eye.draw()
    measurement.draw()
    top_left.draw()
    bottom_right.draw()

    win.flip()

    # Exit on key press
    if event.getKeys():
        break

win.close()
core.quit()
