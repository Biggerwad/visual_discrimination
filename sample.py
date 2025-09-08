from psychopy import visual, core, event, gui, data, sound
from pypixxlib import tracker
import numpy as np
import random
import csv
import os
from glob import glob

# Next fix: Reaction time = End time - Start time
            # Give location of target and distractor images
            
# updates 
            #  setup function for gaze calculatin to call regularly
            # 
# === CONSTANTS ===

# PRIMARY MONITOR 
PRIMARY_MONITOR_X = 1920
PRIMARY_MONITOR_Y = 1080

# SECONDARY MONITOR
SECONDARY_MONITOR_X = 1280
SECONDARY_MONITOR_Y = 1024

# OFFSET = -6
OFFSET = (0,0)

# FRAME DURATION
DURATION = 3
# === Setup ===
win = visual.Window(size=[1280, 1024],fullscr=True, monitor='secondMonitor', screen=1, units='pix', winType='pyglet', allowStencil=False, blendMode='avg', useFBO=True)

mouse = event.Mouse(visible=True, win=win)

mini = tracker.TRACKPixxMini()
mini.open()

# set variable for generic radius

positions = [
    (-300, 300), (300, 300),
    (-300, -300), (300, -300)
]

psychopyVersion = '2025.1.0dev137'
expName = 'vis_discrimination'
expVersion = ''

_thisDir = os.path.dirname(os.path.abspath(__file__))
runAtExit = []

expInfo = {
    'participant': f"{np.random.randint(0, 999999):06.0f}",
    'name': '',
    'session': '001',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'expVersion|hid': expVersion,
}

dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True)
if dlg.OK == False:
    core.quit()

for key, val in expInfo.copy().items():
    newKey, _ = data.utils.parsePipeSyntax(key)
    expInfo[newKey] = expInfo.pop(key)

# Preload trials and set up the filename and header for data saving
preloaded_trials = []
response_time = 0
used_trial_signatures = set()
filename = ''
header = []
image_array = []

# function for image selection and permutation
def permute_images():
    cats = [1, 2, 4, 5]

    # Generate 1200 combinations based on the new algorithm
    for cat in cats:
        for i in range(1, 11):
            for j in range(1, 11):
                order = (cat, i, j)
                category = order[0]

                base_path = os.path.join(_thisDir, f"image_folder/cat{category}")
                similar_path = os.path.join(base_path, f"img{str(order[1])}")
                odd_path = os.path.join(base_path, f"img{str(order[2])}")

                # create array of sorted similar and odd images
                similar_images = sorted(glob(os.path.join(similar_path, '*.png')))
                odd_images = sorted(glob(os.path.join(odd_path, '*.png')))

                if len(similar_images) >= 5 and len(odd_images) >= 5:
                    mid_img = similar_images[len(similar_images) // 2]

                    odd_img_path = odd_images[len(odd_images) // 2]

                    # ensure the mid_img and odd_img_path are not the same
                    trial_signature = tuple(sorted([mid_img, odd_img_path]))
                    # if trial_signature in used_trial_signatures:
                    #     continue

                    used_trial_signatures.add(trial_signature)

                    # create 3 similar images and one odd image
                    # set variable for dynamic size factor
                    sim_stims = [visual.ImageStim(win, image=mid_img, size=(2000, 2000), units='pix') for _ in range(3)]
                    odd_stim = visual.ImageStim(win, image=odd_img_path, size=(2000, 2000), units='pix')
                    image_array.append((sim_stims, odd_stim, mid_img, odd_img_path, category))
                # print(f"Category: {category}, Folder i: {i}, Folder j: {j}")
                # print(f"Similar images: {len(similar_images)}, Odd images: {len(odd_images)}")

# Function to set up the data for the experiment
def setupData(expInfo, dataDir=None):
    permute_images()
    LIMIT = 3  # number of repetitions of the image array

    for _ in range(LIMIT):
        random.shuffle(image_array)
        preloaded_trials.extend(image_array)

    print(len(preloaded_trials))

    if dataDir is None:
        dataDir = _thisDir

    global filename
    filename = os.path.join(dataDir, f"data/{expInfo['participant']}_{expInfo['name']}_{expInfo['date']}.csv")

    global header
    header = ['start_time', 'end_time',
              'category', 'selected_image',
              'jitter_var', 'correct', 'target', 'distractor']

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

setupData(expInfo)
# create fixation and welcome message
fixation = visual.Circle(win,radius=40, fillColor=None)
cross = visual.TextStim(win=win, text='+', color='white', height=50)
welcome_msg = visual.TextStim(
    win=win,
    text="Welcome to the visual discrimination experiment. Fixate on the cross to begin...",
    pos=(0, -150),
    color='white'
)

left_eye = visual.Circle(win,radius=10, fillColor='red')
right_eye = visual.Circle(win, radius=10, fillColor='blue')

def split_path(path):
    path = path.split("\\")
    return path[-2]

# Get screen resolution function
def getScreenRelativity(Lx, Ly, Rx, Ry)->list:
    Lx = Lx / PRIMARY_MONITOR_X * SECONDARY_MONITOR_X - OFFSET[0]
    Rx = Rx / PRIMARY_MONITOR_X * SECONDARY_MONITOR_X  - OFFSET[0]
    Ly = Ly / PRIMARY_MONITOR_Y * SECONDARY_MONITOR_Y - OFFSET[1]
    Ry = Ry / PRIMARY_MONITOR_Y * SECONDARY_MONITOR_Y - OFFSET[1]

    return [Lx, Rx, Ly, Ry]

# Welcome screen loop
while True:
    Lx, Ly, Rx, Ry = mini.getEyePosition()

    Lx, Rx, Ly, Ry = getScreenRelativity(Lx, Ly, Rx, Ry)

    left_eye.pos = (Lx, Ly)
    right_eye.pos = (Rx, Ry)
    left_eye.draw()
    right_eye.draw()    

    try:
        gaze_x = (Lx + Rx) / 2
        gaze_y = (Ly + Ry) / 2
        gaze_point = (gaze_x, gaze_y)
    except Exception:
        gaze_point = (0, 0)

    fixation.draw()
    cross.draw()
    welcome_msg.draw()
    win.flip()

    if 'escape' in event.getKeys():
        win.close()
        core.quit()

    # Gaze near fixation OR mouse click
    if fixation.contains(gaze_point):
        break

core.wait(0.3)

n_trials = len(preloaded_trials)

pause_duration = 1.5
correct_sound = sound.Sound("beep-02.wav")

# begin major clock
rt_clock = core.Clock()

# LOAD IMAGES
for trial in range(n_trials):
    fixation.draw()
    cross.draw()
    Lx, Ly, Rx, Ry = mini.getEyePosition()

    Lx, Rx, Ly, Ry = getScreenRelativity(Lx, Ly, Rx, Ry)

    left_eye.pos = (Lx, Ly)
    right_eye.pos = (Rx, Ry)
    win.flip()

    similar_imgs, odd_img, sim_path, odd_path, category = preloaded_trials[trial]

    images = similar_imgs + [odd_img]
    random.shuffle(images)
    correct_index = images.index(odd_img)

    fixed = False
    # selected_index = -1
    
    jitter_info = []

    for img in images:
        scale_factor = random.uniform(0.8, 1.2)
        angle = random.choice([0, 10, -10, 5, -5])
        # give variable for dynamic scale factor
        img.size = (500 * scale_factor, 500 * scale_factor)
        img.ori = angle
        jitter_info.append((round(scale_factor, 2), angle))

    # Fixate before drawing the stimuli
    while not fixed:
        fixation.draw()
        cross.draw()
        Lx, Ly, Rx, Ry = mini.getEyePosition() 
        
        Lx, Rx, Ly, Ry = getScreenRelativity(Lx, Ly, Rx, Ry)

        
        left_eye.pos = (Lx, Ly)
        right_eye.pos = (Rx, Ry)
        left_eye.draw()
        right_eye.draw()
        
        win.flip()
        
        
        try:
            gaze_x = (Lx + Rx) / 2
            gaze_y = (Ly + Ry) / 2
            gaze_point = (gaze_x, gaze_y)
        except Exception:
            gaze_point = (0, 0)

        if 'escape' in event.getKeys():
            win.close()
            core.quit()

        if fixation.contains(gaze_point):
                fixed = True

        # if fixation.contains(mouse):
        #    if mouse.getPressed()[0]:
        #        while mouse.getPressed()[0]:  
        #            pass
        #        mouse.clickReset()  
        #        break

    # rt_clock.reset()

    # Display the stimuli images until a fixation is acquired or there is a time out
    # fixed = False
    stim_time = core.Clock()
    # rt_clock = core.Clock()
    selected_index = -1
    response_time = None
    start_time = rt_clock.getTime()

    while stim_time.getTime() <= DURATION and selected_index == -1:

        try:  
            Lx, Ly, Rx, Ry = mini.getEyePosition()
        
            Lx, Rx, Ly, Ry = getScreenRelativity(Lx, Ly, Rx, Ry)


            gaze_x = (Lx + Rx) / 2
            gaze_y = (Ly + Ry) / 2
            gaze_point = (gaze_x, gaze_y)
        except Exception:
            gaze_point = None

        # Draw fixation and eye indicators
        left_eye.pos = (Lx, Ly)
        right_eye.pos = (Rx, Ry)

        # Draw all images
        for stim, pos in zip(images, positions):
            stim.pos = pos
            stim.draw()

        fixation.draw()
        cross.draw()
        left_eye.draw()
        right_eye.draw()
        # Get gaze point

        win.flip()

        if 'escape' in event.getKeys():
            win.close()
            core.quit()

        # Gaze-based selection
        if gaze_point:
            for idx, stim in enumerate(images):
                if stim.contains(gaze_point):
                    selected_index = idx
                    response_time = rt_clock.getTime()
                    break
    
    end_time = rt_clock.getTime()
    # Mouse-based fallback (optional)
    # if mouse.getPressed()[0]:
    #     for idx, stim in enumerate(images):
    #         if stim.contains(mouse):
    #             selected_index = idx
    #             response_time = rt_clock.getTime()
    #             break

    # if there is a no click 
    #  if selected_index == -1, set is_correct = false
    if selected_index == -1:
        is_correct = False
        msg = visual.TextStim(win=win, text='Incorrect choice', color='red')
        msg.draw()
        win.flip()
        core.wait(pause_duration)
    elif sim_path == odd_path:
        is_correct = True
        correct_sound.play()
        win.flip()
        core.wait(0.5)
    else:
        is_correct = selected_index == correct_index
        if is_correct:
            correct_sound.play()
            win.flip()
            core.wait(0.5)
        else: 
            msg = visual.TextStim(win=win, text='Incorrect choice', color='red')
            msg.draw()
            win.flip()
            core.wait(pause_duration)

        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                # expInfo['participant'],
                # expInfo['name'],
                round(start_time, 3),
                round(end_time, 3),
                category,
                selected_index,
                # positions[selected_index],
                jitter_info,
                is_correct,
                # round(end_time - start_time, 3),
                split_path(sim_path),
                split_path(odd_path)
            ])

        if stim_time.getTime() >= DURATION:
            fixed = False

final_msg = visual.TextStim(win=win, text="Thank you for your participation", pos=(0, -150), color='white', height=70)
final_msg.draw()
win.flip()
core.wait(2)
win.close()
core.quit()
