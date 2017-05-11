"""
This is the main module responsible for the RigValidations, which use the sub-class Validation for the Validation
process.
"""
# General Imports.
import ConfigParser
import os
import re

import pymel.core as pm

from Validations.core import validations

reload(validations)


class MayaValidations(validations.Validations):
    """
    This is the Class responsible for the maya related validation overrides.
    """
    @staticmethod
    def normalize(x):
        """
        This is to normalize the exponential values sometimes we get from maya.
        :param x:
        :type x:
        :return:
        :rtype: float
        """
        return float('{0:.5f}'.format(x))

    @property
    def get_config(self):
        """
        This will return the config file for the project.
        :return:
        :rtype:
        """
        root_folder = os.path.dirname(os.path.dirname(__file__)).replace('core', 'config')
        proj_config = os.path.join(root_folder, self.project.lower()).replace('\\', '/')
        if not os.path.isfile(proj_config):
            proj_config = os.path.join(root_folder, 'default').replace('\\', '/')
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

    def fix(self):
        """
        Fixes the Errors by deleting the errorNodes.
        :return:
        :rtype:
        """
        print 'Can\'t be auto fixed, please select to check and fix it manually.'
        # pm.delete(self.errorNodes)


class CheckMasterCtrl(MayaValidations):
    """@brief Check for the master controler.

    Check if there is a node with the name top_C_001_CTRL.
    """
    _name = "Top CTRL check"
    _category = "Rigging Validations"

    def check(self):
        """@brief Check if a node with the name top_C_001_CTRL exist.
        """
        top_node_name = self.get_parser.get('MASTERCTRL', 'main_ctrl')
        print top_node_name
        if pm.objExists(top_node_name):
            self.setStatus('OK')
        else:
            self.setStatus('ERROR')
            self.setErrorMessage('No Top Node Found in the scene.')
        self.isNodes = False
        self.isFixable = False


class CheckUselessConstrains(MayaValidations):
    """@brief Check for non used constrains in scene.
    """
    _name = "Useless constrainscheck"
    _category = "Rigging Validations"

    def check(self):
        """@brief Check if they are constrains without output connections
        """

        constrains = pm.ls(type='constraint')
        uselessConstrains = []

        for const in constrains:
            connections = const.listConnections(scn=True, s=False, d=True)
            if const in connections:
                connections.remove(const)

            if len(connections) == 0:
                uselessConstrains.append(const)

        if not uselessConstrains:
            self.setStatus('OK')
        else:
            self.setStatus('ERROR')
            self.setErrorNodes(uselessConstrains)
            self.setErrorMessage('%s number of useless constraints found in the scene.' % len(uselessConstrains))

        self.isNodes = True
        self.isFixable = False


class CheckCtrlTransform(MayaValidations):
    """@brief Check for the master controler.

    Check if there is a node with the name top_C_001_CTRL.
    """
    _name = "CTRL Transform check"
    _category = "Rigging Validations"

    def check(self):
        """@brief Check if a node with the name top_C_001_CTRL exist.
        """
        errorCTRLs = list()
        # warningNodes = list()
        for each in pm.ls('*CTRL'):
            translate_chk = each.t.get() == pm.datatypes.Vector([0.0, 0.0, 0.0])
            rotate_chk = each.r.get() == pm.datatypes.Vector([0.0, 0.0, 0.0])
            scale_chk = each.s.get() == pm.datatypes.Vector([1.0, 1.0, 1.0])
            if not translate_chk or not rotate_chk or not scale_chk:
                errorCTRLs.append(each)
        self.setStatus('OK')
        if errorCTRLs:
            self.setStatus('ERROR')
            self.setErrorNodes(errorCTRLs)
            self.setErrorMessage('%s CTRLS has non ZERO values' % len(errorCTRLs))

        self.isFixable = True
        self.isNodes = True

    def fix(self):
        """
        This is the fix override for this class. This will set the transforms set to default.
        :return:
        :rtype:
        """
        if pm.objExists('errorTransformSet'):
            pm.delete('errorTransformSet')
        errorTransformSet = pm.sets(name='errorTransformSet')
        errorTransformSet.union(self.errorNodes)
        self.errorLog = 'All invalid transform nodes are stored in a set named "errorTransformSet".' \
                        '\nPleas check them manuall.'
        # errorTransformSet = pm.sets(node_name='errorTransformSet')
        # errorTransformSet.union(self.errorNodes)

        # for node_name in self.errorNodes:
        #     for each in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
        #         node_attr = pm.PyNode('%s.%s' % (node_name, each))
        #         if str(node_attr.isFreeToChange()) == 'freeToChange':
        #             if node_attr.get() < 0.0001:
        #                 node_attr.set(0)
        #     for each in ['sx', 'sy', 'sz']:
        #         node_attr = pm.PyNode('%s.%s' % (node_name, each))
        #         if str(node_attr.isFreeToChange()) == 'freeToChange':
        #
        #             node_attr.set(1)


class CheckTopNodes(MayaValidations):
    """@brief Check for the master controler.

    Check if there is a node with the name top_C_001_CTRL.
    """
    _name = "Number of Top Node check"
    _category = "Rigging Validations"

    def check(self):
        """@brief Check if a node with the name top_C_001_CTRL exist.
        """
        defaults = ['persp', 'top', 'front', 'side']

        wrong_names = list()
        for each in pm.ls(assemblies=1):
            if str(each) in defaults:
                continue
            wrong_names.append(str(each))
        self.setStatus('OK')
        if len(wrong_names)-1:
            self.setStatus('ERROR')
            self.setErrorNodes(wrong_names)
            self.setErrorMessage('%s number of top nodes found in the scene, allowed only 1.' % len(wrong_names))

        self.isFixable = False
        self.isNodes = True

    def fix(self):
        """
        This Error can't be fixed automatically, so just print.
        :return:
        :rtype:
        """
        print 'Can\'t be auto fixed, please select to check and fix it manually.'


class CheckCTRLNaming(MayaValidations):
    """@brief Check for the master controler.

    Check if there is a node with the name top_C_001_CTRL.
    """
    _name = "CTRL Naming check"
    _category = "Rigging Validations"

    def check(self):
        """@brief Check if a node with the name top_C_001_CTRL exist.
        """
        regex = re.compile('[0-9]+')
        has_numerics = list()
        node_name_mismatch = list()
        transform_node = None
        for each in pm.ls(r=1):
            if str(each).endswith('CTRL'):
                continue

            if not transform_node:
                continue
            tmp = transform_node[0].split('_')
            if len(tmp) == 4:
                regex_ret = regex.search(tmp[-1])
                if regex_ret:
                    has_numerics.append(str(transform_node[0]))
                if not regex_ret:
                    if len(tmp[-1]) != 4:
                        node_name_mismatch.append(str(transform_node[0]))

        has_numerics = list(set(has_numerics))
        node_name_mismatch = list(set(node_name_mismatch))

        self.setStatus('OK')
        if has_numerics or node_name_mismatch:
            self.setStatus('ERROR')
            tmp = has_numerics
            tmp.extend(node_name_mismatch)
            self.setErrorNodes(tmp)
            self.setErrorMessage('%s CTRL names are not valid.' % len(tmp))

        self.isNodes = True
        self.isFixable = False


class CheckUtilityNodeNaming(MayaValidations):
    """@brief Check for the master controler.

    Check if there is a node with the name top_C_001_CTRL.
    """
    _name = "CTRL Transform check"
    _category = "Rigging Validations"

    def check(self):
        """@brief Check if a node with the name top_C_001_CTRL exist.
        """
        regex = re.compile('[0-9]+')
        has_numeric = list()
        node_name_mismatch = list()
        # transform_node = None
        utilityNodeTypes = ['addDoubleLinear', 'clamp', 'condition', 'multiplyDivide', 'plusMinusAverage', 'reverse',
                            'setRange', 'vectorProduct', 'unitConversion']
        for each in pm.ls(type=utilityNodeTypes):
            tmp = each.split('_')
            # print tmp
            if len(tmp) == 4:
                regex_ret = regex.search(tmp[-1])
                if regex_ret:
                    has_numeric.append(str(each))
                if not regex_ret:
                    if len(tmp[-1]) != 4:
                        node_name_mismatch.append(str(each))
            else:
                node_name_mismatch.append(str(each))

        has_numeric = list(set(has_numeric))
        node_name_mismatch = list(set(node_name_mismatch))

        self.setStatus('OK')
        if has_numeric or node_name_mismatch:
            self.setStatus('ERROR')
            tmp = has_numeric
            tmp.extend(node_name_mismatch)
            self.setErrorNodes(tmp)
            self.setErrorMessage('%s utility names are not valid.\n\t%s' % (len(tmp), '\n'.join(tmp)))

        self.isFixable = True
        self.isNodes = True

    def fix(self):
        """
        This Error can't be fixed automatically, so just print.
        :return:
        :rtype:
        """
        if pm.objExists('errorUtilitySet'):
            pm.delete('errorUtilitySet')
        errorTransformSet = pm.sets(name='errorUtilitySet')
        errorTransformSet.union(self.errorNodes)
        self.errorLog = 'All invalid transform nodes are stored in a set named "errorUtilitySet".' \
                        '\nPleas check them manuall.'


class CheckNamespace(MayaValidations):
    """@brief Check if the namespaces are legal.
    """
    _name = "Namespace"
    _category = "Rigging Validations"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if the namespaces are legal.
        """

        self.isFixable = False
        self.isNodes = True

        illegalNamespaces = list()
        progStandard = re.compile("^[A-Z]{4}[0-9]{2}_[0-9]{3}$")
        progShot = re.compile("^SH[0-9]{4}_[0-9]{3}$")
        for namespaces in pm.namespaceInfo(listOnlyNamespaces=True, internal=False, recurse=True):
            for namespace in namespaces.split(":"):
                if not progStandard.match(namespace) and not progShot.match(namespace) not in ["UI", "shared"]:
                    illegalNamespaces.append(namespace)
        if not illegalNamespaces:
            self.status = "OK"
        else:
            self.setStatus('ERROR')
            self.errorNodes = illegalNamespaces
            self.errorMessage = "%s  illegal namespace" % (len(illegalNamespaces))


class CheckPluginRequired(MayaValidations):
    """@brief Check for the master controler.

    Check if there is a node with the name top_C_001_CTRL.
    """
    _name = "Plugins required check"
    _category = "Rigging Validations"

    def check(self):
        """
        This is to check the Maya file in the ASCII mode for any of the possible plugin imports in it.
        :return:
        :rtype:
        """

        self.isFixable = False
        self.isNodes = True

        problematic_plugins = ['sqtVelvetShader', 'poseReader', 'hairAndFur', 'rpmaya', 'nwPitNodes', 'nwLightingTools',
                               'nwLightingTools']
        sceneFileName = str(pm.sceneName())
        errorPlugins = list()
        with open(sceneFileName, 'r') as readId:
            for each in readId:
                if not each.startswith('requires'):
                    continue
                # print each
                for each_plug in problematic_plugins:
                    if each_plug in each:
                        errorPlugins.append(each_plug)
        self.setStatus('OK')
        if errorPlugins:
            self.setErrorNodes(errorPlugins)
            self.setErrorMessage(
                '%s numbers of unwanted plugins found in the scene in ACSII mode.' % len(self.errorNodes))
            self.setStatus('ERROR')
            print self._name
            print errorPlugins


class CheckRenderSet(MayaValidations):
    """
    This is just a test class to check it with the UI.
    """
    _name = "RenderSet Check"
    _category = "Rigging Validations"

    def check(self):
        """
        This Error can't be fixed automatically, so just print.
        :return:
        :rtype:
        """

        self.isFixable = False
        self.isNodes = True

        parser = self.get_parser
        renderSetName = parser.get('NAME', 'rendersetname')
        geomGroupName = parser.get('NAME', 'geomgroupname')

        self.setStatus('OK')
        renderSets = pm.ls(renderSetName, type='objectSet')
        if not renderSets:
            self.setStatus('ERROR')
            self.setErrorMessage('There is no RenderSet in the scene.')
            return False
        renderSet = renderSets[0]
        geomGroup = pm.PyNode(geomGroupName)
        allGeomParts = geomGroup.listRelatives(ad=1)

        errorNodes = list()
        for each in renderSet.members():
            if each not in allGeomParts:
                errorNodes.append(each)

        if len(errorNodes):
            self.setStatus('ERROR')
            self.setErrorNodes(errorNodes)
            self.setErrorMessage('The renderSet contains invalid objects.')
            return False


class TexturePathCheck(MayaValidations):
    """
    This is just a test class to check it with the UI.
    """
    _name = "Texture Path Check"
    _category = "Rigging Validations"

    def check(self):
        """
        This Error can't be fixed automatically, so just print.
        :return:
        :rtype:
        """

        self.isFixable = False
        self.isNodes = True

        errorNodes = list()
        for each in pm.ls(type='file'):
            if not (each.fileTextureName.get()).startswith('$PROD_SERVER'):
                errorNodes.append(each)
        self.setStatus('OK')
        if len(errorNodes):
            self.setStatus('ERROR')
            self.errorNodes.extend(errorNodes)
            self.setErrorMessage('%s file textures are from invalid paths.' % len(errorNodes))
            msg = 'Following file texture paths are not valid : \n'
            msg += '\n'.join([str(x) for x in errorNodes])
            self.setErrorLog(msg)


class ShapeDeformedCheck(MayaValidations):
    """
    This is just a test class to check it with the UI.
    """
    _name = "ShapeDeformed Check"
    _category = "Rigging Validations"

    def check(self):
        """
        This Error can't be fixed automatically, so just print.
        :return:
        :rtype:
        """
        self.isNodes = True
        self.isFixable = False

        to_match = 'ShapeDeformed'
        # to_match = 'ShapeOrig'

        errorNodes = list()
        for each in pm.ls(type='mesh'):
            if to_match in str(each):
                errorNodes.append(str(each))
        self.setStatus('OK')
        if len(errorNodes):
            self.setStatus('ERROR')
            self.errorNodes.extend(errorNodes)
            msg = 'Following Nodes as not valid :\n'
            msg += '\n'.join(errorNodes)
            self.setErrorLog(msg)


class BDGTopGroupCheck(MayaValidations):
    """
    This is just a test class to check it with the UI.
    """
    _name = "BDGTopGroupCheck"
    _category = "Rigging Validations (BDG)"

    def check(self):
        """
        This Error can't be fixed automatically, so just print.
        :return:
        :rtype:
        """

        self.isFixable = False
        self.isNodes = False

        defaults = ['persp', 'top', 'front', 'side']
        top_groups = [str(x) for x in pm.ls(assemblies=1) if str(x) not in defaults]
        self.setStatus('OK')
        if len([str(x) for x in top_groups]) > 1:
            self.setStatus('ERROR')
            self.setErrorMessage('More than 1 top group present in the scene. Allowed only 1')

        top_group = pm.PyNode(top_groups[0])
        # top group name match.
        if top_group != 'rig_group':
            self.setStatus('ERROR')
            self.setErrorMessage('Top group name is invalid. Please chaneg it to a valid name "%s"' % 'rig_group')
        # top group need to have only 2 sub-groups.
        if len(top_group.listRelatives()) > 2:
            self.setStatus('ERROR')
            self.setErrorMessage('Too many groups in main group. Allowed only 2')
        # match the sub-group names.
        if len([x for x in top_group.listRelatives() if str(x) in ['Rig', 'Geometries']]) < 2:
            self.setStatus('ERROR')
            self.setErrorMessage('Not proper naming for the child groups.')


# class TestingTheUI(MayaValidations):
#     """
#     This is just a test class to check it with the UI.
#     """
#     _name = "TestingTheUI"
#     _category = "TestingTheUI"
#
#     def check(self):
#         """
#         This Error can't be fixed automatically, so just print.
#         :return:
#         :rtype:
#         """
#         print 'Testing the UI.'
#         self.errorMode = 'ERROR'
#         self.errorMessage = 'Errors found in this checking.'
#         self.errorNodes = ['a', 'sdf', 'we', 'sdodfm', 'dfgdf', 'dghfhjg', 'tyfbdfb']
#
#     def fix(self):
#         """
#         This Error can't be fixed automatically, so just print.
#         :return:
#         :rtype:
#         """
#         print 'Can\'t be auto fixed, please fix it manually in ACSII mode.'









if __name__ == '__main__':
    a = CheckCTRLNaming('bdg')
    print a.get_parser.get('NAME', 'rendersetname')
