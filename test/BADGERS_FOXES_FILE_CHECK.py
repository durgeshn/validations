import os
import sys
import time


def get_oldest_file(main_folder):
    oldest_file = None
    for each in os.listdir(main_folder):
        if not each.endswith('.ma'):
            continue
        file_path = os.path.join(main_folder, each).replace('\\', '/')
        file_time = os.path.getmtime(file_path)
        if not oldest_file:
            oldest_file = file_path
            continue
        old_time = os.path.getmtime(oldest_file)
        if old_time > file_time:
            oldest_file = file_path
    # print oldest_file
    return oldest_file

# a = r'P:\badgers_and_foxes\01_SAISON_1\13_PRODUCTION\04_EPISODES\02_Fabrication_3D\BDG101\%s\lay\maya\work'
a = r'B:\01_SAISON_1\13_PRODUCTION\04_EPISODES\02_Fabrication_3D\BDG101\%s\lay\maya\work'
error = dict()
# for each in os.listdir(r'p:\badgers_and_foxes\01_SAISON_1\13_PRODUCTION\04_EPISODES\02_Fabrication_3D\BDG101'):
for each in os.listdir(r'B:\01_SAISON_1\13_PRODUCTION\04_EPISODES\02_Fabrication_3D\BDG101'):
    if each == 'animatic':
        continue
    shot_loc = a % each
    oldest_file = get_oldest_file(shot_loc)
    if not oldest_file:
        continue
    if oldest_file.endswith('_001.ma'):
        continue
    # print shot_loc
    # print oldest_file
    print each, ':\t\t', shot_loc
    error[each] = shot_loc

print len(error.keys())
