"""@package grid.libs.maya.tactic.checkinSystem
Part of the checkin system related to maya

@package grid.libs.maya.tactic.checkinSystem.checkClasses Check classes to
perform check related to maya before checkin
#SMSH is in check mesh name for modeling stage and rigging stage needs to be
#removed after MDR.
"""
import logging
import os
import re

import maya.cmds as cmds
import pymel.core as pm

import checkClasses

reload(checkClasses)
from checkClasses import CheckAbstract

SHOW = None

if 'SHOW_NAME' in os.environ:
    SHOW = os.environ['SHOW_NAME']

# if SHOW == 'ZIGGY':
#     TYPE = 'SINGLE'
# else:
#     TYPE = 'MULTI'


from source.Validations.core.Validations import path_generator
from source.Validations.core.Validations import Validations

class CheckMayaAbstract(CheckAbstract):
    """@brief Abstract class for all maya the check
    """
    _asSelection = False
    _asFix = False

    def __init__(self, parent=None, errorMode=False):
        super(CheckMayaAbstract, self).__init__(parent, errorMode=errorMode)
        self._errorNodes = list()
        self._meshNodes = list()
        self._errorDict = {}

    def _getAsSelection(self):
        """@brief Return if the Check can select the error nodes.

        @return asSelection If the nodes can select the error nodes. (bool)
        """
        return self._asSelection

    asSelection = property(_getAsSelection)

    def _getAsFix(self):
        """@brief Return if the check as some autofix.

        @return asFix If the check as autofix mecanisme. (bool)
        """
        return self._asFix

    asFix = property(_getAsFix)

    def _getErrorNodes(self):
        """@brief Return the error nodes.

        @return errorNodes The list of the nodes that fails the check. (list of
        pm.node)
        """
        return self._errorNodes

    def _setErrorNodes(self, errorNodes):
        """@brief Set the error nodes.

        @param errorNodes list of nodes that fails the check. (list of pm.node)
        """
        self._errorNodes = errorNodes

    errorNodes = property(_getErrorNodes, _setErrorNodes)

    def _getErrorNodesDict(self):
        """@brief Return the error nodes.

        @return errorNodes The list of the nodes that fails the check. (list of
        pm.node)
        """
        return self._errorDict

    def _setErrorNodesDict(self, errorDict):
        """@brief Set the error nodes.

        @param errorNodes list of nodes that fails the check. (list of pm.node)
        """
        self._errorDict = errorDict

    errorDict = property(_getErrorNodesDict, _setErrorNodesDict)

    def addErrorNodesDict(self, errorDict):
        """@brief Add a error node to errorNodes.

        @param errorNode A node that fails the check. (pm.node)
        """
        self.errorDict.update(errorDict)

    def addErrorNodes(self, errorNode):
        """@brief Add a error node to errorNodes.

        @param errorNode A node that fails the check. (pm.node)
        """
        self.errorNodes.append(errorNode)

    def selectErrorNodes(self):
        """@brief select the nodes that fails the check.
        """
        pm.select(self.errorNodes)

    def fix(self):
        """@brief Run the fix.
        """
        raise NotImplemented

    def reset(self):
        """@brief Reset the instance.

        Reset the status to WAITING and empty the error log
        and empty the list of the error nodes
        """
        super(CheckMayaAbstract, self).reset()
        self.errorNodes = list()
        self._errorDict = {}


# ==============================================================================
# Rigging
# ==============================================================================


class CheckMasterCtrl(Validations.Validations):
    """@brief Check for the master controler.

    Check if there is a node with the name top_C_001_CTRL.
    """
    _name = "Top CTRL"
    _category = "Rigging"

    _asSelection = False
    _asFix = False

    def check(self):
        """@brief Check if a node with the name top_C_001_CTRL exist.
        """
        if pm.objExists("top_C_001_CTRL"):
            self.status = "OK"
        else:
            self.status = "ERROR"
            self.addError("No node with the name top_C_001_CTRL")
            self.errorMessage = "No top Controler"


class CheckPluginNodes(CheckMayaAbstract):
    """Check for nodes created by plugins that are not needed."""

    _name = "Plugin Nodes"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """Scan the scene for "unsupported" plugin nodes."""

        # TODO: Make this a setting that can be configured in the environment
        #       yml file
        plugins_to_kill = ['ngSkinTools', 'Turtle', 'Mayatomr']

        self.errorNodes = []
        self.errorPlugins = []

        for plugin in plugins_to_kill:
            if plugin not in cmds.pluginInfo(q=True, pluginsInUse=True):
                continue
            nodetypes = cmds.pluginInfo(plugin, q=True, dependNode=True)
            self.errorNodes.extend(cmds.ls(type=nodetypes))
            self.errorPlugins.append(plugin)

        if self.errorNodes:
            self.status = self.errorMode
            self.errorMessage = "%s nodes from unsupported plugins" % (
                len(self.errorNodes))
        else:
            self.status = "OK"

    def select(self):
        """Select the error nodes."""
        pm.select(self.errorNodes)

    def fix(self):
        """Remove all "unsupported" plugin nodes and unload plugins."""

        cmds.lockNode(self.errorNodes, l=False)
        cmds.delete(self.errorNodes)
        cmds.flushUndo()
        for plugin in self.errorPlugins:
            cmds.unloadPlugin(plugin)

        self.run()

# TODO : NEED TO WORK ON THIS.....
class CheckLatestModel(CheckMayaAbstract):
    """Check if the referenced model is up to date."""

    _name = "Latest Model"
    _category = "Rigging"

    _asSelection = True
    _asFix = True

    def _make_platform_dependent(self, path):
        path = path.replace('/', os.path.sep)
        path = os.path.expandvars(path)
        path = path.replace('$GRID_PROJECT_PATH', 'P:/projects')
        return path

    def _make_platform_independent(self, path):
        grid_project_path = 'P:/projects'
        if os.environ['GRID_PROJECT_PATH']:
            grid_project_path = os.environ['GRID_PROJECT_PATH']

        path = path.replace(grid_project_path, '$GRID_PROJECT_PATH')
        return path

    def check(self,):
        # engine = tank.platform.current_engine()
        # tk = engine.tank

        path_gen = path_generator.pathGenerator()

        for x in pm.listReferences():
            node_name = x.refNode.longName()
            # get the path and make it platform dependent
            # (maya uses C:/style/paths)
            print x.path, '<--------------------------------'
            path = self._make_platform_dependent(x.path)

            path_template = tk.template_from_path(path)
            fields = path_template.get_fields(path)
            all_versions = tk.paths_from_template(
                path_template, fields, skip_keys='version')
            latest = max(all_versions)
            if path != latest:
                self.errorNodes.append({"node": node_name, "path": latest})

        if self.errorNodes:
            self.status = self.errorMode
            self.errorMessage = "%s models need to be updated" % (
                len(self.errorNodes))
        else:
            self.status = "OK"

    def select(self):
        """Select the referece nodes that are not up to date."""
        pm.select([x['node'] for x in self.errorNodes])

    def fix(self):
        """Update the references."""

        for each in self.errorNodes:
            path = self._make_platform_independent(each['path'])
            ref = pm.FileReference(each['node'])
            try:
                ref.load(path)
            except RuntimeError as e:
                # A RuntimeError gets raised when the reference has nodes
                # from a plugin that is not currently loaded. We can safely
                # ignore this (But we still want to print out the message
                # in case anything goes wrong.
                print e.message

        self.run()


class CheckUselessConstrains(CheckMayaAbstract):
    """@brief Check for non used constrains in scene.
    """
    _name = "Useless constrains"
    _category = "Rigging"

    _asSelection = True
    _asFix = True

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
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = uselessConstrains
            for obj in uselessConstrains:
                self.addError("%s doesn't have outgoing connections." % obj)
            self.errorMessage = "%s useless constrains" % (
                len(uselessConstrains))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)

    def fix(self):
        """@brief Deletes the useless constrains.
        """

        pm.delete(self.errorNodes)

        self.run()

# TODO : NEED TO FIX THIS....
class CheckGNodesPresent(CheckMayaAbstract):
    """@brief Check if there is only one gNodes at the top of the hierarchie.
    """
    _name = "GNodes Present"
    _category = "GNodes"

    _asSelection = False
    _asFix = False

    def check(self):
        """@brief Check if there is only one gNodes at the top of the hierarchie.
        """
        try:
            gNodes.getTopGNode()
        except gNodes.NoGNodesError:
            self.status = self.errorMode
            self.addError("No GNodes at the top of the hieararchy")
            self.errorMessage = "No gNodes at the top of the hierarchy"
        except gNodes.MultipleGNodesError:
            self.status = self.errorMode
            self.addError("Multiple gNodes at the top of the  hierarchy")
            self.errorMessage = "Multiple gNodes at the top of the  hierarchy"
        else:
            self.status = "OK"

# TODO : NEED TO FIX THIS....
class CheckRenderGeo(CheckMayaAbstract):
    """@brief Check if there at least one geo tagged as render geo.
    """
    _name = "Render geo"
    _category = "GNodes"

    _asSelection = False
    _asFix = True

    def check(self):
        """@brief Check if there at least one geo tagged as render geo.
        """
        gAsset = cmds.ls(type='gAsset')

        render_geo = []
        if gAsset:
            trans = cmds.listRelatives(gAsset[0], p=True, f=True)
            meshes = cmds.listRelatives(trans, ad=True, type='mesh', f=True)
            if meshes:
                render_geo.extend(meshes)
            # for item in meshes:
            #    trans = cmds.listRelatives(item, p=True, f=True)
            #    render_geo.extend(trans)

            if not pm.ls("*.grid_renderGeo"):
                self.status = self.errorMode
                self.addError("No geometry's are tagged as render geo")
                self.errorMessage = "No geometry is tagged as render geo"
            elif not len(set(cmds.ls("*.grid_renderGeo"))) == len(render_geo):
                self.status = self.errorMode
                self.addError("Not all Geo tags under gasset")
                self.errorMessage = "Not all Geo tags under gasset"
            else:
                self.status = "OK"
        else:
            self.addError("No Gasset found")
            self.errorMessage = "No gasset found"

    def fix(self):
        """@brief Delete the namespace in the scene.
        """
        gAsset = cmds.ls(type='gAsset')

        trans = cmds.listRelatives(gAsset[0], p=True)
        meshes = cmds.listRelatives(trans, ad=True, type='mesh')
        for mesh in meshes:
            if mesh:
                try:
                    cmds.addAttr(mesh, ln="grid_renderGeo", at='double', dv=1)
                    cmds.setAttr(
                        '{0}.grid_renderGeo'.format(mesh), e=False, keyable=False, lock=True)
                except:
                    pass

        self.run()


class CheckGAssetName(CheckMayaAbstract):
    """@brief Check if the name of asset node match with the naming convention.
    """
    _name = "Asset node name"
    _category = "GNodes"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if the name of asset node match with the naming convention.
        """
        badNamedAssetNode = list()

        # prog = re.compile("^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_GAST[0-9]{2}Shape$")
        prog = re.compile("^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_G[A-Z]{3}[0-9]{2}Shape$")
        progFx = re.compile(
            "^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_G[A-Z]{2}[0-9]{2}Shape$")

        for assetNode in pm.ls(type="gAsset"):
            nodename = assetNode.nodeName(stripNamespace=True)
            if not prog.match(nodename):
                if not progFx.match(nodename):
                    badNamedAssetNode.append(assetNode)

        if not badNamedAssetNode:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = badNamedAssetNode
            for mesh in badNamedAssetNode:
                self.addError("%s is not a legal asset node name" % mesh)
            self.errorMessage = "%s illegal asset node name(s)" % (
                len(badNamedAssetNode))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckGAssetTransformName(CheckMayaAbstract):
    """@brief Check if the name of the parent of the asset node match with the naming convention.
    """
    _name = "GAsset transform name"
    _category = "GNodes"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if the name of the parent of the asset node match with the naming convention.
        """
        badTransformName = list()

        # prog = re.compile("^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_GAST$")
        prog = re.compile("^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_G[A-Z]{3}$")
        progFx = re.compile("^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_G[A-Z]{2}$")

        for assetTransform in pm.ls(type="gAsset"):
            nodename = assetTransform.getParent().nodeName(stripNamespace=True)
            if not prog.match(nodename):
                if not progFx.match(nodename):
                    badTransformName.append(assetTransform)

        if not badTransformName:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = badTransformName
            for mesh in badTransformName:
                self.addError(
                    "%s is not a legal asset node transform name" % mesh)
            self.errorMessage = "%s illegal asset node transform name(s)" % (
                len(badTransformName))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckAssetNodeDataContextMatch(CheckMayaAbstract):
    """@brief Check if the data in the asset node and the one from the tank context match.
    """
    _name = "Asset Metadata tank context match"
    _category = "GNodes"

    _asSelection = False
    _asFix = False

    def check(self):
        """@brief Check if the data in the asset node and the one from the tank context match.
        """
        # get the data from shotgun
        app = self.parent.app
        context = app.context
        # get asset type
        filters = [["id", "is", context.entity["id"]]]
        fields = ["sg_asset_type"]
        assetType = app.shotgun.find_one(
            "Asset", filters=filters, fields=fields)["sg_asset_type"]
        # get step short name
        filters = [["id", "is", context.step["id"]]]
        fields = ["short_name"]
        stepShortName = app.shotgun.find_one(
            "Step", filters=filters, fields=fields)["short_name"]

        try:
            assetNode = gNodes.getTopGNode()
        except:
            assetNode = None

        if assetNode:
            metadataCode = assetNode.grid_code.get()
            metadataAssetType = assetNode.grid_type.get(asString=True)
            metadataPipeStep = assetNode.grid_pipeStep.get(asString=True)
            if not (assetType == metadataAssetType and
                    stepShortName == metadataPipeStep and
                    context.entity["name"] == metadataCode):
                self.status = self.errorMode
                self.addError("Context and asset node metadata don't match")
                self.errorMessage = "Context and asset node metadata don't match"
            else:
                self.status = "OK"
        else:
            self.status = "OK"


class CheckSequenceNodeDataContextMatch(CheckMayaAbstract):
    """@brief Check if the data in the sequence node and the one from the tank context match.
    """
    _name = "Sequence Metadata tank context match"
    _category = "GNodes"

    _asSelection = False
    _asFix = False

    def check(self):
        """@brief Check if the data in the sequence node and the one from the tank context match.
        """
        # get the data from shotgun
        app = self.parent.app
        context = app.context

        # get step short name
        filters = [["id", "is", context.step["id"]]]
        fields = ["short_name"]
        stepShortName = app.shotgun.find_one(
            "Step", filters=filters, fields=fields)["short_name"]

        try:
            sequenceNode = gNodes.getTopGNode()
        except:
            sequenceNode = None

        if sequenceNode:
            metadataCode = sequenceNode.grid_code.get()
            metadataPipeStep = sequenceNode.grid_pipeStep.get(asString=True)
            if not (stepShortName == metadataPipeStep and
                    context.entity["name"] == metadataCode):
                self.status = self.errorMode
                self.addError("Context and sequence node metadata don't match")
                self.errorMessage = "Context and sequence node metadata don't match"
            else:
                self.status = "OK"
        else:
            self.status = "OK"


class CheckShotNodeDataContextMatch(CheckMayaAbstract):
    """@brief Check if the data in the sequence node and the one from the tank context match.
    """
    _name = "Shot Metadata tank context match"
    _category = "GNodes"

    _asSelection = False
    _asFix = False

    def check(self):
        """@brief Check if the data in the sequence node and the one from the tank context match.
        """
        # get the data from shotgun
        app = self.parent.app
        context = app.context

        # get step short name
        filters = [["id", "is", context.step["id"]]]
        fields = ["short_name"]
        stepShortName = app.shotgun.find_one(
            "Step", filters=filters, fields=fields)["short_name"]

        try:
            shotNode = gNodes.getTopGNode()
        except:
            shotNode = None

        if shotNode:
            metadataCode = shotNode.grid_code.get()
            metadataPipeStep = shotNode.grid_pipeStep.get(asString=True)
            if not (stepShortName == metadataPipeStep and
                    context.entity["name"] == metadataCode):
                self.status = self.errorMode
                self.addError("Context and shot node metadata don't match")
                self.errorMessage = "Context and shot node metadata don't match"
            else:
                self.status = "OK"
        else:
            self.status = "OK"


class CheckTextureLowInLibrary(CheckMayaAbstract):
    """@brief Check if all the texture in the scene are low res texture in the library.
    """
    _name = "Texture low in lib"
    _category = "Textures"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if all the texture in the scene are low res texture in the library.
        """
        badTextures = list()

        textLowPublishTemplate = self.parent.app.get_template_by_name(
            "textureLow_publish")

        for fileNode in pm.ls(type="file"):
            filePath = os.path.abspath(fileNode.fileTextureName.get())
            if not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(fileNode)

        for aiImageNode in pm.ls(type="aiImage"):
            filePath = os.path.abspath(aiImageNode.filename.get())
            if not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(aiImageNode)

        if not badTextures:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = badTextures
            for node in badTextures:
                nodeType = node.type()
                if nodeType == "file":
                    self.addError("%s is not in the library" %
                                  node.fileTextureName.get())
                elif nodeType == "aiImage":
                    self.addError("%s is not in the library" %
                                  node.filename.get())
                else:
                    raise "%s from nodeType %s is not supported by this check" % (
                        node, node.type())
            self.errorMessage = "%s texture not in library" % (
                len(badTextures))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckTextureInLibrary(CheckMayaAbstract):
    """@brief Check if all the textures in the scene are texture in the library.
    """
    _name = "Texture in lib"
    _category = "Textures"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if all the textures in the scene are texture in the library.
        """
        badTextures = list()

        if not TYPE == 'MULTI':
            textPublishTemplate = self.parent.app.get_template_by_name(
                "texture_publish_seq")
        else:
            textPublishTemplate = self.parent.app.get_template_by_name(
                "texture_publish_multi_seq")

        for fileNode in pm.ls(type="file"):
            print fileNode
            filePath = os.path.abspath(fileNode.fileTextureName.get())
            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(fileNode)

        for aiImageNode in pm.ls(type="aiImage"):
            print aiImageNode
            filePath = os.path.abspath(aiImageNode.filename.get())
            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(aiImageNode)

        if not badTextures:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = badTextures
            for node in badTextures:
                nodeType = node.type()
                if nodeType == "file":
                    self.addError("%s is not in the library" %
                                  node.fileTextureName.get())
                elif nodeType == "aiImage":
                    self.addError("%s is not in the library" %
                                  node.filename.get())
                else:
                    raise "%s from nodeType %s is not supported by this check" % (
                        node, node.type())
            self.errorMessage = "%s texture(s) not in library" % (
                len(badTextures))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckTextureInAnyLibrary(CheckMayaAbstract):
    """@brief Check if all the textures or texture low in the scene are texture in the library.
    """
    _name = "Texture in any lib"
    _category = "Textures"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if all the textures or texture low in the scene are texture in the library.
        """
        badTextures = list()

        if not TYPE == 'MULTI':
            textPublishTemplate = self.parent.app.get_template_by_name(
                "texture_publish_seq")
            textLowPublishTemplate = self.parent.app.get_template_by_name(
                "textureLow_publish")
        else:
            textPublishTemplate = self.parent.app.get_template_by_name(
                "texture_publish_multi_seq")
            textLowPublishTemplate = self.parent.app.get_template_by_name(
                "textureLow_publish_multi")

        for fileNode in pm.ls(type="file"):
            filePath = os.path.abspath(fileNode.fileTextureName.get())

            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]) and not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(fileNode)

        for aiImageNode in pm.ls(type="aiImage"):
            filePath = os.path.abspath(aiImageNode.filename.get())
            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]) and not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(aiImageNode)

        if not badTextures:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = badTextures
            for node in badTextures:
                nodeType = node.type()
                if nodeType == "file":
                    self.addError(
                        "%s is not in the library will be published" % node.fileTextureName.get())
                elif nodeType == "aiImage":
                    self.addError(
                        "%s is not in the library will be published" % node.filename.get())
                else:
                    raise "%s from nodeType %s is not supported by this check" % (
                        node, node.type())
            self.errorMessage = "%s texture(s) not in library will be published" % (
                len(badTextures))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckCacheInLibrary(CheckMayaAbstract):
    """@brief Check if all the cache in the scene are in the Library.
    """
    _name = "Cache in lib"
    _category = "FX"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if all the cache in the scene are in the Library.
        """
        badCachePath = list()
        badCacheNode = list()
        cacheIn = getCacheInfoFromMaya()
        cacheInScene = cacheIn.getCacheFromScene()
        # get the templates

        if not TYPE == 'MULTI':
            cachePublishTemplate = self.parent.app.get_template_by_name(
                'fx_cacheseq_shot_publish')
            mayaCachePublishTemplate = self.parent.app.get_template_by_name(
                'maya_fx_cacheseq_shot_publish')
        else:
            cachePublishTemplate = self.parent.app.get_template_by_name(
                'fx_cacheseq_shot_publish')
            mayaCachePublishTemplate = self.parent.app.get_template_by_name(
                'maya_fx_cacheseq_shot_publish')

        for cacheFrom, cacheVal in cacheInScene.iteritems():
            fileNode = cacheVal
            for nodes, nodeVal in cacheVal.iteritems():
                for cacheNumber, cacheVal in nodeVal.iteritems():
                    filePath = cacheVal['path']

                    if cachePublishTemplate.validate(filePath, skip_keys=["SEQ"]):
                        continue

                    elif mayaCachePublishTemplate.validate(filePath, skip_keys=["SEQ"]):
                        continue

                    else:
                        badCachePath.append(pm.Path(filePath))
                        badCacheNode.append(nodes)
                        continue

        if not badCachePath:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = badCacheNode
            for node in badCachePath:
                self.addError("%s is not in the library" % node)

            self.errorMessage = "%s Cache not in library" % (len(badCachePath))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckCacheInWork(CheckMayaAbstract):
    """@brief Check if all the cache in the scene are in the work.
    """
    _name = "Cache in Work"
    _category = "FX"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if all the cache in the scene are in the work.
        """
        badCachePath = list()
        badCacheNode = list()
        cacheIn = getCacheInfoFromMaya()
        cacheInScene = cacheIn.getCacheFromScene()
        # get the templates

        if not TYPE == 'MULTI':
            cacheWorkTemplate = self.parent.app.get_template_by_name(
                'fx_cacheseq_shot_work')
            cachePublishTemplate = self.parent.app.get_template_by_name(
                'fx_cacheseq_shot_publish')
            mayaCachePublishTemplate = self.parent.app.get_template_by_name(
                'maya_asset_publish_cache_multi')
            mayaCacheWorkTemplate = self.parent.app.get_template_by_name(
                'maya_asset_work_cache_multi')
        else:
            cacheWorkTemplate = self.parent.app.get_template_by_name(
                'fx_cacheseq_shot_work')
            cachePublishTemplate = self.parent.app.get_template_by_name(
                'fx_cacheseq_shot_publish')
            mayaCachePublishTemplate = self.parent.app.get_template_by_name(
                'maya_asset_publish_cache')
            mayaCacheWorkTemplate = self.parent.app.get_template_by_name(
                'maya_asset_work_cache')

        for cacheFrom, cacheVal in cacheInScene.iteritems():

            fileNode = cacheVal
            for nodes, nodeVal in cacheVal.iteritems():
                for cacheNumber, cacheVal in nodeVal.iteritems():
                    filePath = cacheVal['path']

                    if cacheWorkTemplate.validate(filePath, skip_keys=["SEQ"]):
                        continue

                    elif mayaCacheWorkTemplate.validate(filePath, skip_keys=["SEQ"]):
                        continue

                    elif cachePublishTemplate.validate(filePath, skip_keys=["SEQ"]):
                        continue

                    elif mayaCachePublishTemplate.validate(filePath, skip_keys=["SEQ"]):
                        continue

                    else:
                        badCachePath.append(pm.Path(filePath))
                        badCacheNode.append(nodes)
                        continue

        if not badCachePath:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = badCacheNode
            for node in badCachePath:
                self.addError("%s is not in the library" % node)

            self.errorMessage = "%s Cache not in library" % (len(badCachePath))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class getCacheInfoFromMaya(object):

    def getCacheFromScene(self):
        cacheInfo = {}

        alembicNode = cmds.ls(type='AlembicNode')
        alembicFile = {}
        alembicFileInfo = {}
        alembicFileNode = {}
        for item in alembicNode:
            if cmds.getAttr('{0}.abc_File'.format(item)):
                alembicFile['path'] = cmds.getAttr('{0}.abc_File'.format(item))
                alembicFile['type'] = cmds.getAttr('{0}.abc_File'.format(item))
                alembicFileInfo['assetName'] = alembicFile
                alembicFileNode[item] = alembicFileInfo

        if alembicFileNode:
            cacheInfo['alembic'] = alembicFileNode

        mayaNCacheNode = cmds.ls(type='cacheFile')

        mayaCacheInfo = {}
        for cacheNode in mayaNCacheNode:
            cachesMayaMC = self.getMayaCachePath(cacheNode)
            if cachesMayaMC:
                mayaCacheInfo[cacheNode] = cachesMayaMC
                cacheInfo['nMaya'] = mayaCacheInfo

        return cacheInfo

    def getMayaCachePath(self, mayaCacheFileNode):
        mayaCacheInfo = {}
        mayaCaches = {}
        mayaNCache = cmds.cacheFile(mayaCacheFileNode, query=True, f=True)
        for cache in mayaNCache:
            if cache.endswith('mc'):
                if os.path.exists(cache):
                    mayaCacheInfo['path'] = cache
                    mayaCacheInfo['type'] = 'mc'
                    mayaCaches['cacheFile'] = mayaCacheInfo
                    return mayaCaches
        return None


class CheckMeshReferenced(CheckMayaAbstract):
    """@brief Check if all the meshes in the scene are referenced.
    """
    _name = "Meshes referenced"
    _category = "Reference"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if all the meshes in the scene are referenced.
        """
        nonReferencedMesh = list()

        for mesh in pm.ls(type="mesh"):
            if not pm.objExists(mesh.name() + ".grid_noCheck"):
                if not mesh.isReferenced():
                    nonReferencedMesh.append(mesh)

        if not nonReferencedMesh:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = nonReferencedMesh
            for mesh in nonReferencedMesh:
                self.addError("%s is not referenced" % mesh.name())
            self.errorMessage = "%s non referenced mesh(es)" % (
                len(nonReferencedMesh))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckModLowMeshTransform(CheckMayaAbstract):
    """@brief Check if the meshes of the referenced modLowAsset don't have any transformation.
    """
    _name = "Mod low mesh transform"
    _category = "Reference"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if the meshes of the referenced modLowAsset don't have any transformation.
        """
        transformedMesh = list()

        for assetNode in pm.ls(type="gAsset"):
            if assetNode.grid_pipeStep.get(asString=True) == "modLow":
                assetNodeTransform = assetNode.getParent()
                for mesh in assetNodeTransform.listRelatives(ad=True, type="mesh"):
                    meshTransform = mesh.getParent()
                    if meshTransform.getTranslation() != pm.dt.Vector([0, 0, 0]):
                        transformedMesh.append(meshTransform)
                        continue
                    elif meshTransform.getRotation() != pm.dt.EulerRotation([0, 0, 0]):
                        transformedMesh.append(meshTransform)
                        continue
                    elif meshTransform.getScale() != [1, 1, 1]:
                        transformedMesh.append(meshTransform)

        if not transformedMesh:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = transformedMesh
            for meshTransform in transformedMesh:
                self.addError("%s as some transformation" % mesh.name())
            self.errorMessage = "%s mesh(es) with transformation" % (
                len(transformedMesh))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckAssetNodeNamespace(CheckMayaAbstract):
    """@brief Check if the namespace on the asset node are legal.
    """
    _name = "Asset node namespace"
    _category = "Reference"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if the meshes of the referenced modLowAsset don't have any transformation.
        """
        illegalNamespaces = list()

        prog = re.compile("^[A-Z]{4}[0-9]{2}_[0-9]{3}:$")

        for assetNode in pm.ls(type="gAsset"):
            if assetNode.isReferenced() and not prog.match(assetNode.namespace()):
                illegalNamespaces.append(assetNode)

        if not illegalNamespaces:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = illegalNamespaces
            for illegalNamespace in illegalNamespaces:
                self.addError("%s has a illegal namespace" % illegalNamespace)
            self.errorMessage = "%s asset(s) have a illegal namespace" % (
                len(illegalNamespaces))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


class CheckNamespace(CheckMayaAbstract):
    """@brief Check if the namespaces are legal.
    """
    _name = "Namespace"
    _category = "Reference"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check if the namespaces are legal.
        """
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
            self.status = self.errorMode
            self.errorNodes = illegalNamespaces
            for illegalNamespace in illegalNamespaces:
                self.addError("%s is a illegal namespace" % illegalNamespace)
            self.errorMessage = "%s  illegal namespace" % (
                len(illegalNamespaces))

    def select(self):
        """@brief Select the error nodes.
        """
        for elem in self.errorLog:
            print elem


class CheckNoNamespace(CheckMayaAbstract):
    """@brief Check if there is some namespace in the scene.
    """
    _name = "No namespace"
    _category = "Reference"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check if there is some namespace in the scene.
        """
        BadNamespaces = list()

        for namespace in pm.listNamespaces():
            BadNamespaces.append(namespace)

        if not BadNamespaces:
            self.status = "OK"
        else:
            self.status = self.errorMode
            self.errorNodes = namespace
            for namespace in BadNamespaces:
                self.addError("namespace %s exist" % namespace)
            self.errorMessage = "%s namespace" % (len(BadNamespaces))

    def select(self):
        """@brief Select the error nodes.
        """
        for elem in self.errorLog:
            print elem

    def fix(self):
        """@brief Delete the namespace in the scene.
        """
        for namespace in pm.listNamespaces():
            for elem in namespace.ls():
                elem.rename(elem.split(":")[-1])
            namespace.remove()

        self.run()


class CheckReferenceFileTypes(CheckMayaAbstract):

    """@brief Checks reference nodes for the path used, if abc file is found
    error is raised, stop publish

    """
    _name = "Check Reference Paths"
    _category = "Reference"
    _tooltip = "Check file path of reference, if path is pointing to an ABC"

    _asSelection = True
    _asFix = False

    def __init__(self, parent, errorMode=False):
        super(CheckReferenceFileTypes, self).__init__(
            parent, errorMode=errorMode)
        self.abc_references = []

    def _get_referenced_filetype(self, node):

        file_path = cmds.referenceQuery(
            node, filename=True, withoutCopyNumber=True)
        if type(file_path) is not str:
            try:
                file_path = str(file_path)
            except:
                raise TypeError('Data no unicode or string')

        file_type = os.path.splitext(file_path)[-1]

        if file_type == '.abc':
            self.abc_references.append(node)
            msg = 'Found abc reference, {0}'.format(node)
            logging.info(msg)

        elif file_type == '.ma':
            logging.info('Correct reference, continueing...')

    def check(self):

        reference_nodes = cmds.ls(type='reference')
        reference_nodes = [ref for ref in reference_nodes if not cmds.referenceQuery(
            ref, isNodeReferenced=True) and ref != 'sharedReferenceNode']
        for reference in reference_nodes:
            self._get_referenced_filetype(reference)

        if self.abc_references:
            self.status = self.errorMode
            self.errorNodes = self.abc_references
            logging.error('ABC references found! Convert to .MA !')
        else:
            self.status = 'OK'

        return self.status

    def select(self):
        cmds.select(self.errorNodes)

