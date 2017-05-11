import os
import sys
import subprocess


class AppLauncher:
    def __init__(self, project=''):
        self.project = project.upper()
        self.show_wrapper = ''
        self.app_wrapper = ''
        self.env_settings = dict()
        self.config_location = '//stor/data/python_packages/configs'

    def get_show_wrapper(self):
        self.show_wrapper = self.config_location + '/show_config/' + self.project + '/show_wrapper.txt'

    def get_app_wrapper(self, app_name='maya2015'):
        self.app_wrapper = self.config_location + '/app_config/' + app_name.capitalize() + '.txt'

    def configure_settings(self):
        self.get_app_wrapper()
        self.get_show_wrapper()
        app_settings = read_config(self.app_wrapper)
        show_settings = read_config(self.show_wrapper)

        new_dict = show_settings.copy()
        for key in app_settings.keys():
            if key in new_dict.keys():
                new_dict[key].extend(app_settings[key])
        self.env_settings = new_dict.copy()
        return new_dict

    def set_up_env(self):
        self.configure_settings()
        my_env = dict()
        for each_env in self.env_settings.keys():
            print 'setting %s to : %s' % (each_env, ';'.join(self.env_settings[each_env]) if sys.platform == 'win32' else ':'.join(self.env_settings[each_env]))
            os.environ[each_env] = ';'.join(self.env_settings[each_env]) if sys.platform == 'win32' else ':'.join(self.env_settings[each_env])

    def get_app_exe(self, app_name='maya2015', is_batch=False):
        if is_batch:
            return 'C:/Program Files/Autodesk/%s/bin/mayapy.exe' % app_name.capitalize()
        else:
            return 'C:/Program Files/Autodesk/%s/bin/maya.exe' % app_name.capitalize()

    def start_up_commands(self):
        pass

    def launch_app(self, app_to_launch, version='', start_up='', file_to_open='', is_batch=False):
        app_exe = self.get_app_exe(app_name=app_to_launch, is_batch=is_batch)
        self.set_up_env()
        # cmd = [app_exe, '-hideConsole', '-log', 'D:/temp/maya_log.txt', '-noAutoloadPlugins']
        cmd = [app_exe, file_to_open, '-noAutoloadPlugins', '-log', 'D:/temp/maya_log.txt']
        # cmd = [app_exe, '-log', 'D:/temp/maya_log.txt', '-noAutoloadPlugins']
        print cmd
        subprocess.Popen(cmd)
        print os.environ['MAYA_SCRIPT_PATH']


def read_config(config):
    global new_list
    ret_dict = dict()
    stats = 0
    # print config, '<---------------------<<<'
    with open(config, 'r') as fid:
        for each_line in fid:
            each_line = each_line.strip()
            if each_line.startswith('['):
                stats = 1
                new_list = list()
                key = each_line.replace('[', '').replace(']', '')
                ret_dict[key] = new_list
                continue
            if not each_line:
                stats = 0
                continue
            if each_line and stats:
                new_list.append(each_line)
    return ret_dict

    
if __name__ == '__main__':
    os.environ['PROJECT'] = 'bdg'
    app = AppLauncher(project='bdg')
    app.launch_app('maya2015', file_to_open=r"C:\Users\durgesh.n\Desktop\BDG105_004_lay.ma", is_batch=True)
