import re

string_list = ['cam', 'Cam', 'CAM']
input_string = 'bdg_am_ccd_sfddfd.ma'

print re.findall(r"(?=("+'|'.join(string_list)+r"))", input_string)
