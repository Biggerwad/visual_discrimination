from psychopy import visual, core, event, gui, data
from pypixxlib import tracker
import numpy as np
import random
import csv
import os
from glob import glob

# === Setup ===
win = visual.Window(size=[1000, 800], color="grey", units="pix")
mouse = event.Mouse(visible=True, win=win)

mini = tracker.TRACKPixxMini()
mini.open()

positions = [
    (-200, 200), (200, 200),
    (-200, -200), (200, -200)
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

preloaded_trials = []
used_trial_signatures = set()
filename = ''
header = []
category = ''

DESIRED_TRIALS = 60

def setupData(expInfo, dataDir=None):
    global preloaded_trials, filename, header, category

    cats = [1, 2, 4, 5]
    category = f'cat{np.random.choice(cats)}'
    base_path = os.path.join(_thisDir, f"psycho_pilot_jf16_08122024/{category}")
    all_subfolders = sorted([f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))])

    combinations = [(s, o) for s in all_subfolders for o in all_subfolders if s != o]
    random.shuffle(combinations)

    for similar_folder, odd_folder in combinations:
        if len(preloaded_trials) >= DESIRED_TRIALS:
            break

        similar_path = os.path.join(base_path, similar_folder)
        odd_path = os.path.join(base_path, odd_folder)

        similar_images = sorted(glob(os.path.join(similar_path, '*.png')))
        odd_candidates = sorted(glob(os.path.join(odd_path, '*.png')))

        if len(similar_images) >= 5 and odd_candidates:
            mid_img = similar_images[len(similar_images) // 2]
            odd_img_path = random.choice(odd_candidates)

            trial_signature = tuple(sorted([mid_img, odd_img_path]))
            if trial_signature in used_trial_signatures:
                continue

            used_trial_signatures.add(trial_signature)

            sim_stims = [visual.ImageStim(win, image=mid_img, size=(600, 600), units='pix') for _ in range(3)]
            odd_stim = visual.ImageStim(win, image=odd_img_path, size=(600, 600), units='pix')

            preloaded_trials.append((sim_stims, odd_stim, mid_img, odd_img_path))

    if dataDir is None:
        dataDir = _thisDir

    filename = os.path.join(dataDir, f"data/{expInfo['participant']}_{expName}_{expInfo['date']}.csv")

    header = ['participant', 'name', 'start_time', 'end_time',
              'category', 'selected_image', 'image_position',
              'jitter_var', 'correct', 'reaction_time', 'sim_img_path', 'odd_img_path']

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

setupData(expInfo)
fixation = visual.TextStim(win=win, text='+', color='white', height=40)
welcome_msg = visual.TextStim(win=win, text="Welcome to the visual discrimination experiment. Move your gaze to the center or click to begin...", pos=(0, -150), color='white')

# Welcome screen loop
while True:
    try:
        Lx, Ly, Rx, Ry = mini.getEyePosition()
        gaze_x = (Lx + Rx) / 2
        gaze_y = (Ly + Ry) / 2
        gaze_point = (gaze_x, gaze_y)
    except Exception:
        gaze_point = (0, 0)

    fixation.draw()
    welcome_msg.draw()
    win.flip()

    if 'escape' in event.getKeys():
        win.close()
        core.quit()

    # Gaze near fixation OR mouse click
    if fixation.contains(gaze_point) or mouse.getPressed()[0]:
        break

core.wait(0.3)
mouse.clickReset()

n_trials = len(preloaded_trials)
pause_duration = 1.5

for trial in range(n_trials):
    fixation.draw()
    win.flip()
    core.wait(0.5)

    similar_imgs, odd_img, sim_path, odd_path = preloaded_trials[trial]

    images = similar_imgs + [odd_img]
    random.shuffle(images)
    correct_index = images.index(odd_img)

    clicked = False
    selected_index = None
    rt_clock = core.Clock()
    rt_clock.reset()

    jitter_info = []

    for img in images:
        scale_factor = random.uniform(0.8, 1.2)
        angle = random.choice([0, 10, -10, 5, -5])
        img.size = (300 * scale_factor, 300 * scale_factor)
        img.ori = angle
        jitter_info.append((round(scale_factor, 2), angle))

    while not clicked:
        fixation.draw()
        for stim, pos in zip(images, positions):
            stim.pos = pos
            stim.draw()

        try:
            Lx, Ly, Rx, Ry = mini.getEyePosition()
            gaze_x = (Lx + Rx) / 2
            gaze_y = (Ly + Ry) / 2
            gaze_point = (gaze_x, gaze_y)
        except Exception:
            gaze_point = None

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
                    clicked = True
                    break

        # Fallback: mouse click selection
        if not clicked and mouse.getPressed()[0]:
            for idx, stim in enumerate(images):
                if stim.contains(mouse):
                    selected_index = idx
                    response_time = rt_clock.getTime()
                    clicked = True
                    break

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
            positions[selected_index],
            jitter_info,
            is_correct,
            round(response_time, 3),
            sim_path,
            odd_path
        ])

    if is_correct:
        win.flip()
        core.wait(0.5)
    else:
        msg = visual.TextStim(win=win, text='Incorrect choice', color='red')
        msg.draw()
        win.flip()
        core.wait(pause_duration)

    mouse.clickReset()

final_msg = visual.TextStim(win=win, text="Thank you for your participation", pos=(0, -150), color='white', height=70)
final_msg.draw()
win.flip()
core.wait(2)
win.close()
core.quit()
