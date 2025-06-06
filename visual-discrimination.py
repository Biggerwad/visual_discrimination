from psychopy import visual, core, event, gui, data
import numpy as np
import random
import csv
import os
from glob import glob
# from datetime import datetime

# === Setup ===
# window settings
win = visual.Window(size=[800, 600], color="grey", units="pix")
mouse = event.Mouse(visible=True, win=win)

# 4-corner positions
positions = [
    (-200, 200),   # top-left
    (200, 200),    # top-right
    (-200, -200),  # bottom-left
    (200, -200)    # bottom-right
]

# == experiment Info ==

psychopyVersion = '2025.1.0dev137'
expName = 'vis_discrimination'  # from the Builder filename that created this script
expVersion = ''

# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))

# a list of functions to run when the experiment ends (starts off blank)
runAtExit = []

# information about this experiment
expInfo = {
    'participant': f"{np.random.randint(0, 999999):06.0f}",
    'name':'',
    'session': '001',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'expVersion|hid': expVersion,
    # 'psychopyVersion|hid': psychopyVersion,
}

# show participant info dialog
dlg = gui.DlgFromDict(
    dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
)
if dlg.OK == False:
    core.quit()  # user pressed cancel
    # return expInfo

# remove dialog-specific syntax from expInfo
for key, val in expInfo.copy().items():
    newKey, _ = data.utils.parsePipeSyntax(key)
    expInfo[newKey] = expInfo.pop(key)

# == DATA CONFIG ==

# Data file setup
# store preloaded images
preloaded_images = []

def setupData(expInfo, dataDir=None):
    
    # Category selection logic
    cats = [1, 2, 4, 5]
    imgs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # random folder name 
    category = f'cat{np.random.choice(cats)}'
    two_random_ints = random.sample(imgs, 2)

    # choose 2 image folders under selected category [odd_image_folder, even_image_folder]
    img_folder = [f'img{two_random_ints[0]}', f'img{two_random_ints[1]}']

    # PRELOAD IMAGES
    image_folder = os.path.join(
        _thisDir,
        f"psycho_pilot_jf16_08122024/{category}/{img_folder[1]}"
    )

    odd_folder = os.path.join(
        _thisDir,
        f"psycho_pilot_jf16_08122024/{category}/{img_folder[0]}"
    )    
    
    # Load similar image sets (must have at least 3)    
    # for main_dir in os.listdir(image_folder):
    #     path_main = os.path.join(image_folder, main_dir)
    #     if not os.path.isdir(path_main):
    #         continue

    #     for sub_dir in os.listdir(path_main):
    #         path_sub = os.path.join(path_main, sub_dir)
    #         if not os.path.isdir(path_sub):
    #             continue
        
    image_files = glob(os.path.join(image_folder, '*.png'))
    if len(image_files) >= 3:
        image_stims = [visual.ImageStim(win, image=img, size=(0.5, 0.5)) for img in image_files]
        preloaded_images.append(image_stims)
            
    # load ODD images
    global odd_images
    
    odd_images = [visual.ImageStim(win, image=img, size=(0.5, 0.5)) 
    for img in glob(os.path.join(odd_folder, '*.png'))]

    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    
    global filename 
    
    # make sure filename is relative to dataDir
    # if os.path.isabs(filename):
    #     dataDir = os.path.commonprefix([dataDir, filename])
    #     filename = os.path.relpath(filename, dataDir)
    
    filename = u'data/%s_%s_%s.csv' % (expInfo['participant'], expName, expInfo['date'])
    
    # filename = os.path.commonprefix()
    global header
    header = ['participant', 'name', 'start_time', 'end_time',
              'category', 'selected_image','image_position', 
              'jitter_var', 'correct', 'reaction_time']

    # QUESTION:
    # should image position be one all images configuration or just the odd one?
    # Write header only if file doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

# === Welcome Screen ===
setupData(expInfo)
fixation = visual.TextStim(win=win, text='+', color='white', height=40)
welcome_msg = visual.TextStim(win=win, text="Welcome to the visual discrimination experiment. Click anywhere to begin...", pos=(0, -150), color='white')

fixation.draw()
welcome_msg.draw()
win.flip()

# Wait for click to begin
event.clearEvents()
while not mouse.getPressed()[0]:
    if 'escape' in event.getKeys():
        win.close()
        core.quit()
core.wait(0.3)
mouse.clickReset()

# === Experiment Loop ===

# Trial configuration
n_trials = 5
pause_duration = 1.5  # seconds

for trial in range(n_trials):
    # Show fixation cross before trial
    fixation.draw()
    win.flip()
    core.wait(0.5)

    # Choose a valid set
    
    # setupData(expInfo)
    valid_sets = [img_set for img_set in preloaded_images if len(img_set) >= 3]
    
    if not valid_sets:
        print("Not enough valid similar image sets.")
        break

    sim_set = random.choice(valid_sets)
    similar_imgs = random.sample(sim_set, 3)
    odd_img = random.choice(odd_images)
    
    # Combine and shuffle
    images = similar_imgs + [odd_img]
    random.shuffle(images)
    correct_index = images.index(odd_img)
    
    # Assign 3 same colors and 1 odd color, then shuffle
    # colors = [same_color] * 3 + [odd_color]
    # # random.shuffle(colors)
    # shuffled_colors = random.sample(colors, len(colors))

    # # Create stimuli
    # stimuli = []
    # for pos, color in zip(positions, shuffled_colors):
    #     rect = visual.Rect(win=win, width=300, height=300, fillColor=color_values[color], pos=pos)
    #     stimuli.append((rect, color))

    clicked = False
    selected_img = None
    rt_clock = core.Clock()
    rt_clock.reset()

    while not clicked:
        for rect, _ in images:
            rect.draw()
        win.flip()

        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            core.quit()

        if mouse.getPressed()[0]:  # Left-click
            for rect, quadrant in images:
                if rect.contains(mouse):
                    selected_quad = quadrant
                    response_time = rt_clock.getTime()
                    clicked = True
                    break

    is_correct = selected_quad == correct_index
    
    # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # filename = os.path.commonprefix()
    global header
    header = ['participant', 'name', 'start_time', 'end_time',
              'category', 'selected_image','image_position', 
              'jitter_var', 'correct', 'reaction_time']
    
    # Save result to CSV immediately
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([expInfo['participant'], expInfo['name'], rt_clock, round(response_time, 3)] , selected_quad, is_correct)
        writer.writerow(header)

    # Feedback
    if is_correct:
        win.flip()  # Blank screen
        core.wait(0.5)
    else:
        msg = visual.TextStim(win=win, text='Incorrect choice', color='red')
        msg.draw()
        win.flip()
        core.wait(pause_duration)

    mouse.clickReset()


# == File storage ==



# === End Screen ===
final_msg = visual.TextStim(win=win, text="Thank you for your participation",  pos=(0, -150), color='white', height=70)
msg_duration = 2

final_msg.draw()
win.flip()
core.wait(msg_duration)

# === Cleanup ===
win.close()
core.quit()