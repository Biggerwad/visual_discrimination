from psychopy import visual, core, event, gui, data, sound
import numpy as np
import random
import csv
import os
from glob import glob

# === task outline ===
# 1. Display a welcome message and wait for the participant to click the mouse.
# 2. create vector combination of images to be preloaded
# 3. Randomly select images from the preloaded trials.
# 4. Display the fixation cross and wait till it is focused on.
# 5. After fixation, display the images in random positions.
# 6. If the click is on the odd image, record the response as correct (with a ding sound); otherwise, record it as incorrect(show incorrect selection).
# 7. show blank screen and wait for another fixation before the next trial.

# === Setup ===
# Draw the monitor size and mouse
win = visual.Window(size=[1000, 800], color="grey", units="pix")
mouse = event.Mouse(visible=True, win=win)

positions = [(-200, 200), (200, 200), (-200, -200), (200, -200)]

psychopyVersion = '2025.1.0dev137'
expName = 'vis_discrimination'
expVersion = ''

# Get the current directory and set up the run at exit
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

# Create a dialog box to collect participant information
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True)
if dlg.OK == False:
    core.quit()

# Parse the experiment info keys to remove pipe syntax
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
                    if trial_signature in used_trial_signatures:
                        continue

                    used_trial_signatures.add(trial_signature)

                    # create 3 similar images and one odd image
                    sim_stims = [visual.ImageStim(win, image=mid_img, size=(900, 900), units='pix') for _ in range(3)]
                    odd_stim = visual.ImageStim(win, image=odd_img_path, size=(900, 900), units='pix')
                    image_array.append((sim_stims, odd_stim, mid_img, odd_img_path, category))

# Function to set up the data for the experiment
def setupData(expInfo, dataDir=None):
    permute_images()
    LIMIT = 3  # number of repetitions of the image array

    for _ in range(LIMIT):
        random.shuffle(image_array)
        preloaded_trials.extend(image_array)

    if dataDir is None:
        dataDir = _thisDir

    global filename
    filename = os.path.join(dataDir, f"data/{expInfo['participant']}_{expName}_{expInfo['date']}.csv")

    global header
    header = ['participant', 'name', 'start_time', 'end_time',
              'category', 'selected_image', 'image_position',
              'jitter_var', 'correct', 'reaction_time', 'sim_img_path', 'odd_img_path']

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

setupData(expInfo)

# create fixation and welcome message
fixation = visual.TextStim(win=win, text='+', color='white', height=50)
welcome_msg = visual.TextStim(
    win=win,
    text="Welcome to the visual discrimination experiment. Fixate on the cross to begin...",
    pos=(0, -150),
    color='white'
)

# Wait until mouse is within central fixation
while True:
    fixation.draw()
    welcome_msg.draw()
    win.flip()
    if 'escape' in event.getKeys():
        win.close()
        core.quit()
    if fixation.contains(mouse):
        if mouse.getPressed()[0]:
            break

core.wait(0.3)
mouse.clickReset()

n_trials = len(preloaded_trials)
pause_duration = 1.5
correct_sound = sound.Sound("beep-02.wav")

for trial in range(n_trials):
    # display fixation for brief moment before showing images
    fixation.draw()
    win.flip()
    core.wait(0.5)

    similar_imgs, odd_img, sim_path, odd_path, category = preloaded_trials[trial]

    images = similar_imgs + [odd_img]
    random.shuffle(images)
    correct_index = images.index(odd_img)

    clicked = False
    selected_index = -1
    rt_clock = core.Clock()

    jitter_info = []

    # Apply random jitter to size and orientation
    for img in images:
        scale_factor = random.uniform(0.8, 1.2)
        angle = random.choice([0, 10, -10, 5, -5])  # this is in degrees
        img.size = (300 * scale_factor, 300 * scale_factor)
        img.ori = angle
        jitter_info.append((round(scale_factor, 2), angle))

    # Fixate before drawing the stimuli
    while True:
        fixation.draw()
        win.flip()
        if 'escape' in event.getKeys():
            win.close()
            core.quit()
        if fixation.contains(mouse):
            if mouse.getPressed()[0]:
                while mouse.getPressed()[0]:  
                    pass
                mouse.clickReset()  
                break

    rt_clock.reset()

    # Display the stimuli until a click is registered
    while not clicked:
        fixation.draw()
        for stim, pos in zip(images, positions):
            stim.pos = pos
            stim.draw()

        win.flip()
        if rt_clock.getTime() >= 2.0:
            break

        if 'escape' in event.getKeys():
            win.close()
            core.quit()

        if mouse.getPressed()[0]:
            for idx, stim in enumerate(images):
                if stim.contains(mouse):
                    selected_index = idx
                    response_time = rt_clock.getTime()
                    clicked = True
                    break
            
            # if there is a no mouse click 
            if selected_index == -1:
                mouse.clickReset()
                break

    if sim_path == odd_path:
        is_correct = True
    else:
        is_correct = selected_index == correct_index

    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            expInfo['participant'],
            expInfo['name'],
            round(rt_clock.getTime(), 3),
            round(response_time, 3),
            category,
            selected_index,
            positions[selected_index] if selected_index != -1 else None,
            jitter_info,
            is_correct,
            round(response_time, 3),
            sim_path,
            odd_path
        ])

    if selected_index != -1 and is_correct:
        correct_sound.play()
        win.flip()
        core.wait(0.5)
    elif selected_index != -1 and not is_correct:
        msg = visual.TextStim(win=win, text='Incorrect choice', color='red')
        msg.draw()
        win.flip()
        core.wait(pause_duration)
    else:
        pass

    mouse.clickReset()

# wrap up with final message
final_msg = visual.TextStim(win=win, text="Thank you for your participation", pos=(0, -150), color='white', height=70)
final_msg.draw()
win.flip()
core.wait(2)
win.close()
core.quit()
