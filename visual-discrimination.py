from psychopy import visual, core, event, gui, data
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
used_trial_signatures = set()
filename = ''
header = []
image_array = []

# category = ''

# function for image selection and permutation
def permute_images():
    cats = [1, 2, 4, 5]
    # stimulus = []

    # for number of repetitions
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

                    # create the stimuli for the trial
                    # create 3 similar images and one odd image
                    sim_stims = [visual.ImageStim(win, image=mid_img, size=(900, 900), units='pix') for _ in range(3)]
                    odd_stim = visual.ImageStim(win, image=odd_img_path, size=(900, 900), units='pix')
                    image_array.append((sim_stims, odd_stim, mid_img, odd_img_path, category))


# Function to set up the data for the experiment
def setupData(expInfo, dataDir=None):
    permute_images()
    # duplicate loop
    LIMIT = 3
    # Updated vector combination logic
    for set in range(LIMIT):
        # Append 400 images to the preloaded trials
        random.shuffle(image_array)
        preloaded_trials.extend(image_array)
        # append 1200 images into preloaded_trials
        # permute_images()

    # shuffle the preloaded trials to randomize the order
    # random.shuffle(preloaded_trials)

    if dataDir is None:
        dataDir = _thisDir
    global filename
    # create a filename based on participant, experiment name, and date
    
    filename = os.path.join(dataDir, f"data/{expInfo['participant']}_{expName}_{expInfo['date']}.csv")

    header = ['participant', 'name', 'start_time', 'end_time',
              'category', 'selected_image', 'image_position',
              'jitter_var', 'correct', 'reaction_time', 'sim_img_path', 'odd_img_path']

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    # return filename

setupData(expInfo)

# create fixation and welcome message
fixation = visual.TextStim(win=win, text='+', color='white', height=40)
welcome_msg = visual.TextStim(
    win=win,
    text="Welcome to the visual discrimination experiment. Move your mouse to the center to begin...",
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

for trial in range(n_trials):
    # display fixation for brief moment before showing images
    fixation.draw()
    win.flip()
    core.wait(0.5)

    similar_imgs, odd_img, sim_path, odd_path, category = preloaded_trials[trial]

    # mix the similar and odd images together and randomize them
    images = similar_imgs + [odd_img]
    random.shuffle(images)
    correct_index = images.index(odd_img)

    clicked = False
    selected_index = None
    rt_clock = core.Clock()
    rt_clock.reset()

    jitter_info = []

    # Apply random jitter to size and orientation
    for img in images:
        scale_factor = random.uniform(0.8, 1.2)
        angle = random.choice([0, 10, -10, 5, -5])  # this is in degrees
        img.size = (300 * scale_factor, 300 * scale_factor)
        img.ori = angle
        jitter_info.append((round(scale_factor, 2), angle))

    # Display the stimuli until a click is registered
    while not clicked:
        fixation.draw()
        for stim, pos in zip(images, positions):
            stim.pos = pos
            stim.draw()
        win.flip()

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

    # check correctness
    if random.choice(similar_imgs) == odd_img:
        is_correct = True
    else:
        is_correct = selected_index == correct_index

    # log trial result
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            expInfo['participant'],
            expInfo['name'],
            round(rt_clock.getTime(), 3),
            round(response_time, 3),
            category,
            selected_index,
            positions[selected_index],
            jitter_info,
            is_correct,
            round(response_time, 3),
            sim_path,
            odd_path
        ])

    # provide feedback based on response
    if is_correct:
        win.flip()
        core.wait(0.5)
    else:
        msg = visual.TextStim(win=win, text='Incorrect choice', color='red')
        msg.draw()
        win.flip()
        core.wait(pause_duration)

    mouse.clickReset()

# wrap up with final message
final_msg = visual.TextStim(win=win, text="Thank you for your participation", pos=(0, -150), color='white', height=70)
final_msg.draw()
win.flip()
core.wait(2)
win.close()
core.quit()
