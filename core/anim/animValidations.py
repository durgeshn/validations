"""
This is the main module responsible for the RigValidations, which use the sub-class Validation for the Validation
process.
"""
# General Imports.
import ConfigParser
import os
import re

# maya related imports.
import pymel.core as pm

# custom imports.
from Validations.core import validations
reload(validations)


class MayaValidations(validations.Validations):
    """
    This is the Class responsible for the maya related validation overrides.
    """
    @property
    def get_config(self):
        """
        This will return the config file for the project.
        :return:
        :rtype:
        """
        root_folder = os.path.dirname(os.path.dirname(__file__)).replace('\\', '/')
        root_folder = root_folder.replace('/core', '/config')
        # print root_folder, '<----------------------------------------'
        proj_config = os.path.join(root_folder, self.project.lower()).replace('\\', '/')
        # print proj_config, '============================================='
        if not os.path.isfile(proj_config):
            proj_config = os.path.join(root_folder, 'default').replace('\\', '/')
        # print proj_config, '<========================================'
        return proj_config

    @property
    def get_parser(self):
        """
        Make the parser here.
        :return:
        :rtype:
        """
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(self.get_config)
        return config_parser

    def selectErrorNodes(self):
        """
        Selects the ErrorNodes in the Class.
        :return:
        :rtype:
        """
        pm.select(self.errorNodes)

    if __name__ == '__main__':
        def fix(self):
            """
            Fixes the Errors by deleting the errorNodes.
            :return:
            :rtype:
            """
            print 'Can\'t be auto fixed, please select to check and fix it manually.'
            # pm.delete(self.errorNodes)

# Unassociated refrence nodes ERROR
# Latest version. ASSET ERROR/ SHOT WARNING


class CheckUnknownNodes(MayaValidations):
    """
    This will check the scene for any unknown nodes.
    """
    _name = "Unknow node check"
    _category = "Animation Validations"

    def check(self):
        """
        List out the unknown nodes in the errorNodes.
        :return:
        :rtype:
        """
        self.isNodes = True
        self.isFixable = True
        errorNodes = list()
        for each in pm.ls(type='unknown'):
            errorNodes.append(each)
        self.status = 'OK'
        if len(errorNodes):
            self.setErrorNodes(errorNodes)
            self.setStatus('ERROR')

    def fix(self):
        """
        delete the error nodes.
        :return:
        :rtype:
        """
        exceptionError = ''
        for each in self.errorNodes:
            try:
                pm.delete(each)
            except exceptionError:
                print exceptionError


# root hiearchy check. WARNING
class CheckRootHiearchy(MayaValidations):
    """
    This will check the scene for the settings info node which is in shotgun's case is "shot" node.
    """
    _name = "Root Hiearchy check"
    _category = "Animation Validations"

    def check(self):
        """
        Check for the settings info node. IF not found then take it as Warning and if more than 1 found then take it as
        Error.
        :return:
        :rtype:
        """
        self.isNodes = True
        self.isFixable = False
        defaults = ['persp', 'top', 'front', 'side']
        project_defaults = ['__SUBSET__', '__SET__', '__CAMERA__', '__CHARS__', '__PROPS__']

        errorNodes = list()
        for each in pm.ls(assemblies=1):
            if str(each) in defaults:
                continue
            if str(each) in project_defaults:
                continue
            errorNodes.append(str(each))
        self.setStatus('OK')
        if len(errorNodes) > 0:
            self.setStatus('WARNING')
            self.errorNodes = errorNodes
            self.errorMessage = '%s numbers of extra root nodes found in the scene.' % str(len(self.errorNodes))


# namespace. ERRROR
# render resolution. ERROR



# check for the settings info node(shot node).
class CheckSettingsInfoNode(MayaValidations):
    """
    This will check the scene for the settings info node which is in shotgun's case is "shot" node.
    """
    _name = "Shot node check"
    _category = "Animation utility Validations"

    def check(self):
        """
        Check for the settings info node. IF not found then take it as Warning and if more than 1 found then take it as
        Error.
        :return:
        :rtype:
        """
        self.isNodes = False
        self.isFixable = False
        nodeType = self.get_parser.get('SETTINGS', 'settingsinfonode')
        self.setStatus('OK')
        if not len(pm.ls(type=nodeType)):
            self.setStatus('WARNING')
            self.setErrorMessage('No %s node found in the scene.' % nodeType)
            return False, ''
        elif len(pm.ls(type=nodeType)) > 1:
            self.setStatus('ERROR')
            self.setErrorMessage('More than 1 %s node found in the scene.' % nodeType)
            return False, ''
        return True, pm.ls(type=nodeType)[0]

class CheckFrameLength(MayaValidations):
    """
    This will check the start and end frame for the scene.
    This will first look for the settings info node(shot node) and if not found then will revert to the database for
    those info.
    """
    _name = "Start and End frame check"
    _category = "Animation Validations"
    _startFrame = ''
    _endFrame = ''

    def check(self):
        """

        :return:
        :rtype:
        """
        self.isNodes = False
        self.isFixable = True
        start_frame = ''
        end_frame = ''

        checkInfo = CheckSettingsInfoNode(self.project)
        nodeCheck = checkInfo.check()
        if nodeCheck[0]:
            # print 'Settings info node found not refering to the database.'
            shotNode = pm.PyNode(nodeCheck[1])
            start_frame = shotNode.startFrame.get()
            end_frame = shotNode.endFrame.get()
        else:
            print 'No settings info node found, reverting to the database.'
            raise RuntimeError('No settings info node found, reverting to the database.')

        scene_start_frame = pm.playbackOptions(q=1, min=1)
        scene_end_frame = pm.playbackOptions(q=1, max=1)
        self._startFrame = start_frame
        self._endFrame = end_frame

        self.setStatus('OK')
        if start_frame != scene_start_frame or end_frame != scene_end_frame:
            self.setStatus('ERROR')
            self.setErrorMessage = 'Start and End frame mismatch.'

    def fix(self):
        """
        set the start and end frame.
        :return:
        :rtype:
        """
        pm.playbackOptions(min=self._startFrame)
        pm.playbackOptions(max=self._endFrame)



# sound related checks. WARNING
class CheckAudio(MayaValidations):
    """
    This will check the start and end frame for the scene.
    This will first look for the settings info node(shot node) and if not found then will revert to the database for
    those info.
    """
    _name = "Audio check"
    _category = "Animation Validations"

    def check(self):
        """

        :return:
        :rtype:
        """
        self.isNodes = True
        self.isFixable = False
        self.setStatus('OK')
        checkInfo = CheckSettingsInfoNode(self.project)
        nodeCheck = checkInfo.check()

        shot_audio = ''
        if not nodeCheck[0]:
            raise RuntimeError('Settings info node not found, invalid scene.')

        shotNode = pm.PyNode(nodeCheck[1])
        for each in shotNode.listConnections():
            if pm.nodeType(each) == 'audio':
                shot_audio = each

        scene_audio = pm.ls(type='audio')
        if not len(scene_audio):
            self.errorMessage = 'No audio in the scene.'
            self.setStatus('WARNING')
            self.isNodes = False
            return False
        if len(scene_audio)>1:
            self.errorNodes = [str(x) for x in scene_audio]
            self.errorMessage = 'More than 1 audio present in the scene.'
            self.setStatus('ERROR')
            return False
        if scene_audio[0] != shot_audio:
            self.errorNodes.append(scene_audio[0])
            self.errorMessage = 'Audio not matching with the shotNode audio.'
            self.setStatus('ERROR')
            return False
        return True
