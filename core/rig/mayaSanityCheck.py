"""@package grid.libs.maya.tactic.checkinSystem
Part of the checkin system related to maya

@package grid.libs.maya.tactic.checkinSystem.checkClasses
Check classes to perform check related to maya before checkin to tactic
"""
import re
import os
import itertools


import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.mel as mayaMel


# import tank


# import gNodes


from checkClasses import CheckAbstract



class CheckMayaAbstract(CheckAbstract):
    """@brief Abstract class for all maya the check
    """
    _asSelection = False
    _asFix = False

    def __init__(self, *args):
        super(CheckMayaAbstract, self).__init__(*args)
        self._errorNodes = list()

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

        @return errorNodes The list of the nodes that fails the check. (list of pm.node)
        """
        return self._errorNodes

    def _setErrorNodes(self, errorNodes):
        """@brief Set the error nodes.

        @param errorNodes list of nodes that fails the check. (list of pm.node)
        """
        self._errorNodes = errorNodes

    errorNodes = property(_getErrorNodes, _setErrorNodes)

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




#==============================================================================================================================================================
# Scene
#==============================================================================================================================================================

#=======================================
# Unknown nodes
#=======================================
class CheckUnknownNodes(CheckMayaAbstract):
    """@brief Check for unknown nodes.
    """
    _name = "Studio unknown nodes"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check for unknown node and add them to errors node.
        """
        unknownNodes = pm.ls(type="unknown")
        if not unknownNodes :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = unknownNodes
            for unknownNode in unknownNodes :
                self.addError("%s is a unknown node" % unknownNode)
            self.errorMessage = "%s Unknown node(s)" % (len(unknownNodes))

    def fix(self):
        """@brief Delete the unknown nodes.
        """
        pm.delete(self.errorNodes)
        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Duplicates names
#=======================================
class CheckDuplicateName(CheckMayaAbstract):
    """@brief Check for Duplicate name.
    """
    _name = "Duplicate nodes name"
    _category = "Scene"

    _asSelection = True
    _asFix = False

    def check(self):
        """@brief Check for nodes with duplicate name and add them to errors node.
        """
        duplicateNames = list()
        for node in pm.ls() :
            if "|" in str(node) :
                if not node.isInstanced():
                    duplicateNames.append(node)
                else :
                    if len(pm.ls(node)) > 1 :
                        duplicateNames.append(node)
        if not duplicateNames :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = duplicateNames
            for duplicateName in duplicateNames :
                self.addError("%s as a non unique name" % duplicateName)
            self.errorMessage = "%s Non unique names" % (len(duplicateNames))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)



#=======================================
# File Name
#=======================================
class CheckFilePathAsset(CheckMayaAbstract):
    """@brief Check if the filename is valid for the maya_asset_work template.
    """
    _name = "File name"
    _category = "Scene"

    _asSelection = False
    _asFix = False

    def check(self):
        """@brief Check if the filename contains a version number in the right format.
        """
        mayaAssetWorkTemplate = self.parent.app.get_template_by_name("maya_asset_work")
        if mayaAssetWorkTemplate.validate(pm.sceneName()) :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorMessage = "File name is not legal"


#=======================================
# Images planes
#=======================================
class CheckImagesPlanes(CheckMayaAbstract):
    """@brief Check for images planes on scene
    """
    _name = "Cameras images planes"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check for images planes on the scene
        """
        imagesP = pm.ls(type="imagePlane")
        if not imagesP :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = imagesP
            for imageP in imagesP :
                self.addError("%s is an image plane" % imageP)
            self.errorMessage = "%s Non vaitertools.chainlid image plane(s)" % (len(imagesP))

    def fix(self):
        """@brief Delete all images planes.
        """
        pm.delete(self.errorNodes)
        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Default cameras
#=======================================
class CheckCameras(CheckMayaAbstract):
    """@brief Check for other existing cameras on scene besides defaults
    """
    _name = "Default cameras"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check cameras on scene
        """
        cams = pm.ls(type="camera")

        for defaultCam in ("frontShape", "perspShape", "sideShape", "topShape"):
            cams.remove(defaultCam)

        if not cams :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = cams
            for cam in cams :
                self.addError("%s is an extra camera" % cam)
            self.errorMessage = "%s Non default camera(s)" % (len(cams))

    def fix(self):
        """@brief Delete all non default cameras
        """
        for cam in self.errorNodes :
            pm.delete(cam.getParent())
        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Unused nodes
#=======================================
class CheckUnusedNodes(CheckMayaAbstract):
    """@brief Check for unused nodes inside Maya.
    """
    _name = "Unused maya nodes"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check for nodes inside Maya that are not used.
        """

        # # Source default check script
        mayaMel.eval("source MLdeleteUnused")

        fullShadeList = list()
        objects = list()

        # # List all kind of nodes in Maya
        for shadeNode in ("utility", "texture", "shader"):
            temp = pm.listNodeTypes(shadeNode)
            fullShadeList.append(temp)

        # # List what kind of objects exits on scene
        for shadeNode in fullShadeList:
            typeOfNode = pm.ls(type=shadeNode)
            if not type:
                pass
            else:
                objects.append(typeOfNode)

        # # Flatten the listitertools.chain
        collObjects = list(itertools.chain(*objects))

        # # Exclude default objects inside Maya
        collObjects.remove('lambert1')
        collObjects.remove('particleCloud1')


        # # Check for connections
        objectsWithoutConnections = list()

        for collObject in collObjects:
            utilities = pm.listNodeTypes("utility")
            textures = pm.listNodeTypes("texture")
            shader = pm.listNodeTypes("shader")
            typeNode = pm.nodeType(collObject)
            # # Checks for Shader nodes
            if typeNode in shader:
                conn = pm.listConnections(collObject)
                if "defaultShaderList1" in conn:
                    conn.remove("defaultShaderList1")
                for node in conn:
                    nt = pm.nodeType(node)
                    if nt == "shadingEngine":
                        pyNodes = str(node)
                        engine = mayaMel.eval('shadingGroupUnused "%s"' % pyNodes)
                        if engine == 1:
                            objectsWithoutConnections.append(collObject)
                        else:
                            pass
            # # Checks for Utility nodes
            if typeNode in utilities:
                conn = pm.listConnections(collObject)
                if "defaultRenderUtilityList1" in conn:
                    conn.remove("defaultRenderUtilityList1")
                if not conn:
                    objectsWithoutConnections.append(collObject)
                else:
                    pass
            # # Checks for textures nodes
            if typeNode in textures:
                conn = pm.listConnections(collObject)
                conn.remove("defaultTextureList1")
                for typeOF in conn:
                    place2D = pm.nodeType(typeOF)
                    if place2D == "place2dTexture":
                        conn.remove(typeOF)
                if not conn:
                    objectsWithoutConnections.append(collObject)
                else:
                    pass

        if not objectsWithoutConnections :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objectsWithoutConnections
            for node in objectsWithoutConnections :
                self.addError("%s is unused" % node)
            self.errorMessage = "%s None used nodes(s)" % (len(objectsWithoutConnections))

    def fix(self):
        """@brief Delete all non used nodes
        """
        mayaMel.eval("MLdeleteUnused()")

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Check lights
#=======================================
class CheckLights(CheckMayaAbstract):
    """@brief Check for lights on the scene
    """
    _name = "Unused lights"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check for Maya lights in scene
        """
        lights = pm.ls(type="light")
        if not lights :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = lights
            for light in lights :
                self.addError("%s light on scene" % light)
            self.errorMessage = "%s None used light(s)" % (len(lights))

    def fix(self):
        """@brief Delete all lights
        """
        objects = []
        for light in self.errorNodes:
            father = light.getParent()
            objects.append(father)

        pm.delete(objects)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        objects = []
        for light in self.errorNodes:
            father = light.getParent()
            objects.append(father)

        pm.select(objects)




#=======================================
# Check Empty groups
#=======================================
class CheckEmptyGroups(CheckMayaAbstract):
    """@brief Check for empty group on the scene. This check don't look for connections with the groups. Note to use with rigging
    """
    _name = "Empty Groups"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check for empty groups on scene.
        """
        emptyGroup = list()
        
        for group in pm.ls(exactType="transform") :
            if not group.getShapes() and not group.listRelatives() :
                emptyGroup.append(group)
        
        if not emptyGroup :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = emptyGroup
            for group in emptyGroup :
                self.addError("%s empty group on scene" % group)
            self.errorMessage = "%s None used groups(s)" % (len(emptyGroup))

    def fix(self):
        """@brief Delete all empty groups
        """
        pm.delete(self.errorNodes)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Check Render Layers Delete
#=======================================
class CheckRenderLayersDelete(CheckMayaAbstract):
    """@brief Deletes all renders layers present in scene.
    """
    _name = "Render Layers"
    _category = "Scene"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check for render layers on scene besides the default one.
        """
        rndLayers = pm.ls(type="renderLayer", leaf=True)
        rndLayers.remove("defaultRenderLayer")

        for layer in rndLayers:
            if layer.isReferenced():
                rndLayers.remove(layer)

        if not rndLayers :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = rndLayers
            for rndLayer in rndLayers :
                self.addError("%s is a non valid render layer" % rndLayer)
            self.errorMessage = "%s None valid render layer(s)" % (len(rndLayers))

    def fix(self):
        """@brief Delete all render layers.
        """
        pm.delete(self.errorNodes)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        

class CheckCleanHierarchy(CheckMayaAbstract):
    """@brief Check that the root hierarchy is clean.
    """
    _name = "Root hierarchy"
    _category = "Scene"

    _asSelection = False
    _asFix = False

    def check(self):
        """@brief Check there is only 5 nodes at the root of the hierarchy.
        """


        if len(pm.ls(assemblies=True)) < 6 :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.addError("To many nodes at the root of the hiearchy")
            self.errorMessage = "To many nodes at the root of the hiearchy"
            
            
# class CheckSubGNodesGroupLock(CheckMayaAbstract):
#     """@brief Check that group directly below the gNodes node are locked.
#     """
#     _name = "Sub gNodes group lock"
#     _category = "Scene"

#     _asSelection = True
#     _asFix = True


#     def check(self):
#         """@brief Check that group directly below the gNodes node are locked.
#         """
#         unlockGroup = list()
        
#         attributesToCheck = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        
#         for assetNode in pm.ls(type="gAsset") :
#             if not assetNode.isReferenced() :
#                 assetNodeTransform = assetNode.getParent()
#                 for group in assetNodeTransform.listRelatives(shapes=False) :
#                     if group.nodeType() == "transform" and not group.getShapes():
#                         for attributes in attributesToCheck :
#                             if not group.attr(attributes).isLocked() :
#                                 unlockGroup.append(group)
#                                 break
            
#         for shotNode in pm.ls(type="gShot") :
#             for group in shotNode.listRelatives() :
#                 if group.nodeType() == "transform" and not group.getShapes():
#                     for attributes in attributesToCheck :
#                         if not group.attr(attributes).isLocked() :
#                             unlockGroup.append(group)
#                             break
                    
#         for sequenceNode in pm.ls(type="gSequence") :
#             for group in sequenceNode.listRelatives() :
#                 if group.nodeType() == "transform" and not group.getShapes():
#                     for attributes in attributesToCheck :
#                         if not group.attr(attributes).isLocked() :
#                             unlockGroup.append(group)
#                             break

#         if not unlockGroup :
#             self.status = "OK"
#         else :
#             self.status = self.errorMode
#             self.errorNodes = unlockGroup
#             for group in unlockGroup :
#                 self.addError("Transformation is not locked on %s" % group)
#             self.errorMessage = "%s unlock sub gNodes group" % (len(unlockGroup))


#     def select(self):
#         """@brief Select the error nodes.
#         """
#         pm.select(self.errorNodes)


#     def fix(self):
#         """@brief Deletes the useless constrains.
#         """
#         attributeToLock = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
#         for group in self.errorNodes :
#             for attribute in attributeToLock :
#                 group.attr(attribute).lock()
        
#         self.run()


#==============================================================================================================================================================
# Modeling
#==============================================================================================================================================================

#=======================================
# Default render States
#=======================================
class CheckRenderStats(CheckMayaAbstract):
    """@brief Check if all geometry has default render stats.
    """
    _name = "Default render stats"
    _category = "Modeling"

    _asSelection = True
    _asFix = True

    def check(self):
        """@brief Check if the geometries in scene have default render stats values.
        """
        lib = dict()
        lib["castsShadows"] = True
        lib["receiveShadows"] = True
        lib["motionBlur"] = True
        lib["primaryVisibility"] = True
        lib["smoothShading"] = True
        lib["visibleInReflections"] = True
        lib["visibleInRefractions"] = True
        lib["doubleSided"] = False
        lib["opposite"] = False
        geometries = pm.ls(type="mesh")
        checkValue = "OK"
        meshes = []
        for geo in geometries:
            for state in lib:
                value = geo.attr(state).get()
                if value != lib[state]:
                    meshes.append(geo)
                    checkValue = "ERROR"
                    break

        if checkValue == "OK":
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = meshes
            for mesh in meshes:
                self.addError("%s has wrong render states" % mesh)
            self.errorMessage = "%s Non default render states" % (len(meshes))

    def fix(self):
        """@brief Set the correct default renderStates
        """
        for mesh in self.errorNodes :
            mesh.castsShadows.set(True)
            mesh.receiveShadows.set(True)
            mesh.motionBlur.set(True)
            mesh.primaryVisibility.set(True)
            mesh.smoothShading.set(True)
            mesh.visibleInReflections.set(True)
            mesh.visibleInRefractions.set(True)
            mesh.doubleSided.set(False)
            mesh.opposite.set(False)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Default Lambert shader
#=======================================
class CheckDefaultShader(CheckMayaAbstract):
    """@brief Check if all geometry have the default Lambert shader applied
    """
    _name = "Default shader"
    _category = "Modeling"

    _asSelection = True
    _asFix = True


    def check(self):
        """@brief Check if the geometry have the default Lambert shader applied to them
        """
        meshes = pm.ls(type="mesh")
        objects = list()
        self.shaders = list()

        shader = pm.listNodeTypes("shader")

        for mesh in meshes :
            shadingEngines = mesh.listConnections(type="shadingEngine")
            for shadingEngine in shadingEngines :
                if shadingEngine != "initialShadingGroup" :
                    # # Finds the shader to delete afterwards
                    shaderConn = pm.listConnections(shadingEngine)
                    for connection in shaderConn:
                        connType = pm.nodeType(connection)
                        if connType in shader:
                            self.shaders.append(connection)
                    objects.append(mesh)
                    break


        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s dont have default shader" % obj)
            self.errorMessage = "%s dont have default shader" % (len(objects))


    def fix(self):
        """@brief Apply default Lambert shader on objects
        """
        for obj in self.errorNodes:
            pm.select(obj)
            pm.hyperShade(a="lambert1")
        pm.select(cl=True)
        pm.delete(self.shaders)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        nodesToSelect = []
        for geo in self.errorNodes:
            parentNode = geo.getParent()
            nodesToSelect.append(parentNode)
        pm.select(nodesToSelect)



#=======================================
# More than 4 sides faces
#=======================================
class CheckNgons(CheckMayaAbstract):
    """@brief Check if all geometries faces don't have more than 4 vertices.
    """
    _name = "Ngons"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def checkNgons(self, dagName):
        """@brief Return all the face with more that 4 vertices on dagName.
        
        @param dagName The name of the object that need to be checked. (string)
        
        @return badFaces Face with more that 4 vertices. (list of string)
        """
        cmds.select('{0}.f[*]'.format(dagName))
        cmds.polySelectConstraint(type=8, size=3, mode=2)
        cmds.polySelectConstraint(disable=True)
        return cmds.ls(sl=True)


    def check(self):
        """@brief Check if the geometry has more than 4 vertices per face
        """
        badFaces = list()

        for mesh in pm.ls(type="mesh"):
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                badFaces.extend(self.checkNgons(mesh))

        if not badFaces :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badFaces
            for obj in badFaces :
                self.addError("%s faces have more than 4 vertex" % obj)
            self.errorMessage = "%s faces have more than 4 vertex" % (len(badFaces))
        

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        
#===============================================================================
# Concave Face
#===============================================================================
class CheckConcaveFaces(CheckMayaAbstract):
    """@brief Check for concave faces.
    """
    _name = "Concave face"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def checkConcaveFaces(self, dagName):
        """@brief Return all the concave face.
        
        @param dagName The name of the object that need to be checked. (string)
        
        @return badFaces Concave face. (list of string)
        """
        cmds.select('{0}.f[*]'.format(dagName))
        cmds.polySelectConstraint(type=8, convexity=1, mode=2)
        cmds.polySelectConstraint(disable=True)
        return cmds.ls(sl=True)


    def check(self):
        """@brief Check if the geometry contains concave face.
        """
        badFaces = list()

        for mesh in pm.ls(type="mesh"):
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                badFaces.extend(self.checkConcaveFaces(mesh))

        if not badFaces :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badFaces
            for obj in badFaces :
                self.addError("%s is concave" % obj)
            self.errorMessage = "%s concave face(s)" % (len(badFaces))
        

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        
#===============================================================================
# Lone vertex
#===============================================================================
class CheckLoneVertex(CheckMayaAbstract):
    """@brief Check for lone vertex.
    """
    _name = "Lone vertex"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def checkLoneVertex(self, dagName):
        """@brief Return all the lone vertex.
        
        @param dagName The name of the object that need to be checked. (string)
        
        @return loneVertex Lone vertexs. (list of string)
        """
        cmds.select('{0}.vtx[*]'.format(dagName))
        cmds.polySelectConstraint(type=1, angle=True, anglebound=[0, 180], mode=2, w=2)
        cmds.polySelectConstraint(disable=True)
        return cmds.ls(sl=True)


    def check(self):
        """@brief Check if the geometry contains lone vertex.
        """
        loneVertexs = list()

        for mesh in pm.ls(type="mesh"):
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                loneVertexs.extend(self.checkLoneVertex(mesh))

        if not loneVertexs :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = loneVertexs
            for obj in loneVertexs :
                self.addError("%s is a lone vertex" % obj)
            self.errorMessage = "%s lone vertex(s)" % (len(loneVertexs))
        

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        
# #===============================================================================
# # Non manifold
# #===============================================================================
# class CheckNonManifold(CheckMayaAbstract):
#     """@brief Check for non manifold face.
#     """
#     _name = "Non manifold"
#     _category = "Modeling"
# 
#     _asSelection = True
#     _asFix = False
#     
#     def checkNonManifold(self, dagName):
#         """@brief Check for non manifold face.
#         
#         @param dagName The name of the object that need to be checked. (string)
#         
#         @return nonManifold Non Manifold face. (list of string)
#         """
#         cmds.select('{0}.vtx[*]'.format(dagName))
#         cmds.polySelectConstraint(type=1, nonmanifold=1, mode=2)
#         cmds.polySelectConstraint(disable=True)
#         faces = cmds.polyListComponentConversion(fromVertex=True, toFace=True)
#         cmds.select(faces)
# 
# 
#     def check(self):
#         """@brief Check if the geometry non manifold face.
#         """
#         nonManifold = list()
# 
#         for mesh in pm.ls(type="mesh"):
#             nonManifold.extend(self.checkNonManifold(mesh))
# 
#         if not nonManifold :
#             self.status = "OK"
#         else :
#             self.status = self.errorMode
#             self.errorNodes = nonManifold
#             for obj in nonManifold :
#                 self.addError("%s is non manifold face" % obj)
#             self.errorMessage = "%s non manifold faces's" % (len(nonManifold))
#         
# 
#     def select(self):
#         """@brief Select the error nodes.
#         """
#         pm.select(self.errorNodes)
        
#===============================================================================
# Non merged open borders
#===============================================================================
class CheckNonMergedOpenBorders(CheckMayaAbstract):
    """@brief Check Non merged open borders.
    """
    _name = "Non merged open borders"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def checkNonMergedOpenBorders(self, dagName):
        """@brief Check for non merged open borders.
        
        @param dagName The name of the object that need to be checked. (string)
        
        @return edges Non merged edges. (list of string)
        """
        node = pm.polyCloseBorder(dagName, constructionHistory=True)[0]
        cmds.select('{0}.f[*]'.format(dagName))
        cmds.polySelectConstraint(type=8, geometricarea=True, geometricareabound=[0, 0.000001], mode=2)
        cmds.polySelectConstraint(disable=True)
        edges = cmds.polyListComponentConversion(fromFace=True, toEdge=True)
        pm.delete(node)
        pm.delete(dagName, ch=True)
        return edges



    def check(self):
        """@brief Check Non merged open borders.
        """
        nonMerged = list()

        for mesh in pm.ls(type="mesh"):
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                nonMerged.extend(self.checkNonMergedOpenBorders(mesh.getParent().name()))

        if not nonMerged :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = nonMerged
            for obj in nonMerged :
                self.addError("%s is a non merged edge" % obj)
            self.errorMessage = "%s Non merged open border(s)" % (len(nonMerged))
        

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Attributes limits
#=======================================
class CheckAttrsLimits(CheckMayaAbstract):
    """@brief Check if all geometry don't have attribute limits
    """
    _name = "Attribute limits"
    _category = "Modeling"

    _asSelection = True
    _asFix = True


    def check(self):
        """@brief Check if all transform nodes have no limits on them
        """
        transformNodes = pm.ls(type="transform")
        objects = []

        checkValue = "OK"
        self.listOfLimits = "mtxe", "mtye", "mtze", "xtxe", "xtye", "xtze", "mrxe", "mrye", "mrze", "xrxe", "xrye", "xrze", "msxe", "msye", "msze", "xsxe", "xsye", "xsze"

        for obj in transformNodes:
            limitState = []
            for state in self.listOfLimits:
                value = obj.attr(state).get()
                limitState.append(value)
            if limitState != [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]:
                objects.append(obj)
                checkValue = "ERROR"

        if checkValue == "OK":
            self.status = "OK"

        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects:
                self.addError("%s has attribute limits" % obj)
            self.errorMessage = "%s Have attributes limits" % (len(objects))

    def fix(self):
        """@brief Set the attributes limits to OFF
        """
        for obj in self.errorNodes:
            for state in self.listOfLimits:
                obj.attr(state).set(False)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)




#=======================================
# Freezed transformations
#=======================================
class CheckTransforms(CheckMayaAbstract):
    """@brief Check if all geometries have their transform values freezed (0,0,0)
    """
    _name = "Freeze transformations"
    _category = "Modeling"

    _asSelection = True
    _asFix = True


    def check(self):
        """@brief Check if the geometry have values on translate, rotate or scale
        """
        meshes = pm.ls(type="mesh")
        objects = []

        attributesToCheck = "translate", "rotate"

        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck"):
                father = mesh.getParent()
                for attr in attributesToCheck:
                    values = father.attr(attr).get()
                    for i in values:
                        if i != 0:
                            objects.append(father)
                            break
                values = father.getScale()
                for i in values:
                    if i != 1:
                        objects.append(father)
                        break

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s are not freezed" % obj)
            self.errorMessage = "%s dont have freezed values" % (len(objects))


    def fix(self):
        """@brief Freeze transform values on errorNodes
        """
        for obj in self.errorNodes:
            pm.makeIdentity(obj, t=True, r=True, s=True, a=True)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Reset Pivot
#=======================================
class CheckPivots(CheckMayaAbstract):
    """@brief Check if all geometries have their pivots at Maya origin.
    """
    _name = "Reset Pivots"
    _category = "Modeling"

    _asSelection = True
    _asFix = True


    def check(self):
        """@brief Check if the geometry has the pivot on a different place than Maya's origin
        """
        meshes = pm.ls(type="mesh")
        objects = []

        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck"):
                father = mesh.getParent()
                pivot = father.getRotatePivot()
                for i in pivot:
                    if i != 0:
                        objects.append(father)
                        break

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s mesh(es) have wrong pivot" % obj)
            self.errorMessage = "%s have wrong pivot" % (len(objects))


    def fix(self):
        """@brief Reset pivot to Maya's origin
        """
        for obj in self.errorNodes:
            obj.setPivots((0, 0, 0), worldSpace=True)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)





#=======================================
# No default display layers
#=======================================
class CheckDisplayLayers(CheckMayaAbstract):
    """@brief Check if scene has more than default display layer
    """
    _name = "Display layers"
    _category = "Modeling"

    _asSelection = True
    _asFix = True


    def check(self):
        """@brief Check if the Maya scene has more than 1 display layers
        """
        layers = pm.ls(type="displayLayer")
        layers.remove("defaultLayer")

        if not layers :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = layers
            for lay in layers :
                self.addError("%s layer in scene" % lay)
            self.errorMessage = "%s non valid display layers" % (len(layers))

    def fix(self):
        """@brief Delete all layers
        """
        pm.delete(self.errorNodes)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Objects with locked attributes
#=======================================
class CheckLockAttrs(CheckMayaAbstract):
    """@brief Check if objects on scene have locked attributes
    """
    _name = "Locked Attributes"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if any object has any locked attribute
        """
        transformNode = pm.ls(type="transform")
        if pm.objExists("*GAST"):
            transformNode.remove("*GAST")
        objects = []

        for tNode in transformNode:
            if tNode.getShapes():
                attributes = tNode.listAttr(l=True)
                if not attributes:
                    pass
                else:
                    objects.append(tNode)

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s has locked attributes" % obj)
            self.errorMessage = "%s have locked attributes" % (len(objects))

    def fix(self):
        """@brief Unlock All attributes
        """
        from grid.libs.maya.utils.common import unlockAndUnhide
        unlockAndUnhide(self.errorNodes)
        pm.select(cl=True)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# Keyframes
#=======================================
class CheckKeyframes(CheckMayaAbstract):
    """@brief Check if scene has keyframes
    """
    _name = "Delete Keyframes"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if scene has keyframes
        """
        keys = pm.ls(type="animCurve")

        if not keys :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = keys
            self.errorMessage = "%s Non valid keyframes" % (len(keys))

    def fix(self):
        """@brief Delete all keyframing on scene
        """
        pm.delete(self.errorNodes)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#=======================================
# PolySmooths nodes
#=======================================
class CheckPolySmooth(CheckMayaAbstract):
    """@brief Check if objects on scene have a polySmooth node applied
    """
    _name = "Delete PolySmooths"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if polySmooth nodes exists on scene
        """
        polySmoothNode = pm.ls(type="polySmoothFace")

        if not polySmoothNode :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = polySmoothNode
            self.errorMessage = "%s PolySmooths on scene" % (len(polySmoothNode))

    def fix(self):
        """@brief Delete all polySmooths
        """
        pm.delete(self.errorNodes)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        listOfObj = list()
        for smooth in self.errorNodes:
            parent = pm.listConnections(smooth)
            listOfObj.append(parent[0])
        pm.select(listOfObj, tgl=True)



#=======================================
# Smooth preview value
#=======================================
class CheckSmooth(CheckMayaAbstract):
    """@brief Check if objects on scene are been display as smooth objects
    """
    _name = "Smooth object preview"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if geometries are been displayed with smooth on viewport
        """
        meshes = pm.ls(type="mesh")
        objects = []

        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck"):
                smoothLevel = pm.displaySmoothness(mesh, q=True, po=True)
                if smoothLevel == None:
                    pass
                elif smoothLevel != [0]:
                    father = mesh.getParent()
                    objects.append(father)

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s has smooth preview" % obj)
            self.errorMessage = "%s Have smooth preview" % (len(objects))

    def fix(self):
        """@brief Set display smooth to 0
        """
        for obj in self.errorNodes:
            pm.displaySmoothness(obj, po=0)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)



#=======================================
# Delete history
#=======================================
class CheckHistory(CheckMayaAbstract):
    """@brief Check if objects on scene have construction history
    """
    _name = "Construction history"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if geometries have construction history (besides shape)
        """
        meshes = pm.listTransforms(type="mesh")
        shadersList = pm.listNodeTypes('shader')
        utilitiesList = pm.listNodeTypes('utility')
        texturesList = pm.listNodeTypes('texture')
        objects = []

        for mesh in meshes:
            ref = mesh.isReferenced()
            if ref == False:
                historyNodes = pm.listHistory(mesh, ac=True)
                historyNodes.remove(historyNodes[0])
                realHistory = list()
                
                for hisObj in historyNodes:
                    nodeInHistory = pm.nodeType(hisObj)
                    for typeOfShader in shadersList:
                        if nodeInHistory == typeOfShader:
                            realHistory.append(hisObj)
                    for typeOfUtil in utilitiesList:
                        if nodeInHistory == typeOfUtil:
                            realHistory.append(hisObj)
                    for typeOfUtil in texturesList:
                        if nodeInHistory == typeOfUtil:
                            realHistory.append(hisObj)
                    if nodeInHistory == "shadingEngine":
                        realHistory.append(hisObj)

                for hisObj in realHistory:
                    historyNodes.remove(hisObj)
                
                if len(historyNodes) > 0 :
                    objects.append(mesh)
         
        # # Checks if objects have shader           
        sel = pm.ls(type='mesh')
        shaderObjects = list()
        
        for obj in sel:
            history = pm.listHistory(obj)
            listOfNodes = list()
            
            for item in history:
                typeOfNode = pm.nodeType(item)
                if typeOfNode == 'groupId':
                    listOfNodes.append(item)
                    
            for node in listOfNodes:
                conn = pm.listConnections(node)
                for connection in conn:
                    typeOfNode = pm.nodeType(connection)
                    if typeOfNode == 'shadingEngine':
                        shaderObjects.append(obj)
                break
        
        if len(shaderObjects) > 0:
            for item in shaderObjects:
                father = item.getParent()
                if not father:
                    pass
                else:
                    if not father in objects:
                        pass
                    else:
                        objects.remove(father)

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s has construction history" % obj)
            self.errorMessage = "%s Have construction history" % (len(objects))

    def fix(self):
        """@brief Delete all history
        """
        for obj in self.errorNodes:
            pm.delete(obj, ch=True)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)




#=======================================
# Face normals
#=======================================
class CheckFaceNormals(CheckMayaAbstract):
    """@brief Check if objects have flipped face normals
    """
    _name = "Face normals"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if geometries have flipped face normals.
        """
        meshes = pm.ls(type="mesh")
        objects = []
        normals = []

        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                father = mesh.getParent()
                normalsTool = pm.polyNormal(father, nm=2, ch=True)
                flippedFaces = pm.selected()
                
                if flippedFaces:
                    normals.append(flippedFaces)
                    objects.append(father)
                
                pm.delete(normalsTool)
                pm.delete(father, ch=True)
                pm.select(cl=True)

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            self.objectNormals = normals
            for obj in objects :
                self.addError("%s has flipped face normals" % obj)
            self.errorMessage = "%s objects have face normals flipped." % (len(objects))

    def fix(self):
        """@brief Flips the normals that are inverted
        """
        for obj in self.errorNodes:
            pm.polyNormal(obj, nm=2, ch=True)
            pm.delete(obj, ch=True)
            pm.select(cl=True)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(cl=True)
        pm.select(self.errorNodes)
        pm.select(self.objectNormals, add=True)


#=======================================
# Non Manifold edges and vertexs
#=======================================
class CheckNonManifold(CheckMayaAbstract):
    """@brief Check if objects have non manifold components
    """
    _name = "Non manifold edge, faces"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    _deactivatable = True


    def check(self):
        """@brief Check if geometries have non manifold components.
        """
        meshes = pm.listTransforms(type="mesh")
        objects = []
        components = []

        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                nonManifoldVert = pm.polyInfo(mesh, nmv=True, nme=True)
                if nonManifoldVert == None:
                    pass
                else:
                    components.append(nonManifoldVert)
                    objects.append(mesh)
                
                pm.select(cl=True)

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = components
            for obj in objects :
                self.addError("%s has non manifold components." % obj)
            self.errorMessage = "%s objects have non manifold components." % (len(objects))



    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(cl=True)
        pm.select(self.errorNodes)



#=======================================
# Locked Vertex Normals
#=======================================

# TODO : to slow
class CheckVertexNormals(CheckMayaAbstract):
    """@brief Check if objects have locked normals
    """
    _name = "Locked normals"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if geometries have locked normals.
        """
        meshes = pm.ls(type="mesh")
        objects = []

        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                numsOfVertex = pm.polyEvaluate(mesh, v=True)
                for vertex in range(0, numsOfVertex, 1):
                    normals = pm.polyNormalPerVertex('%s.vtx[%s]' % (mesh, vertex), q=True, fn=True)
                    if True in normals:
                        father = mesh.getParent()
                        objects.append(father)
                        break

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s has locked  normals" % obj)
            self.errorMessage = "%s objects have locked normals." % (len(objects))

    def fix(self):
        """@brief Unlock all normals on object
        """
        for obj in self.errorNodes:
            pm.polyNormalPerVertex(obj, ufn=True)
            pm.delete(obj, ch=True)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(cl=True)
        pm.select(self.errorNodes)

#=======================================
# Vertex Transform
#=======================================

# TODO : to slow

class CheckVertexTransform(CheckMayaAbstract):
    """@brief Check if objects have vertex with transforms normals
    """
    _name = "Vertex transform"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if geometries have vertex with transform values.
        """
        meshes = pm.ls(type="mesh")
        objects = []

        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                numsOfVertex = pm.polyEvaluate(mesh, v=True)
                for vertex in range(0, numsOfVertex, 1):
                    values = mesh.attr('pnts[%s]' % vertex).get()
                    if values != (0.0, 0.0, 0.0):
                        father = mesh.getParent()
                        objects.append(father)
                        break

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s have vertex transformations" % obj)
            self.errorMessage = "%s objects have vertex transformation." % (len(objects))

    def fix(self):
        """@brief Freeze vertex transforms
        """
        for obj in self.errorNodes:
            simplePlane = pm.polyPlane(n='tempPlane', sx=1, sy=1)
            combine = pm.polyUnite(obj, simplePlane, ch=False)
            obj = pm.rename(combine, obj)
            lastFace = pm.polyEvaluate(obj, f=True)
            pm.delete('%s.f[%s]' % (obj, lastFace))
            conn = pm.listHistory(obj, ac=True, type='shadingEngine')
        
            shadersList = pm.listNodeTypes('shader')
        
            for shaderVal in range(0, len(shadersList), 1):
                shader = pm.listConnections(conn[0], type=shadersList[shaderVal])
                if shader != []:
                    pm.select(obj)
                    pm.hyperShade(a=shader[0])
                    pm.select(cl=True)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(cl=True)
        pm.select(self.errorNodes)



#=======================================
# Objects visibility
#=======================================
class CheckVisibility(CheckMayaAbstract):
    """@brief Check if objects on scene are hidden.
    """
    _name = "Objects visibility"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    _deactivatable = True


    def check(self):
        """@brief Check if geometries are hidden on scene.
        """
        meshes = pm.listTransforms(type=("mesh", "subdiv", "nurbsSurface", "nurbsCurve"))
        objects = []

        for mesh in meshes:
            vis = mesh.visibility.get()
            if vis == False:
                objects.append(mesh)

        if not objects :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = objects
            for obj in objects :
                self.addError("%s is hidden in scene" % obj)
            self.errorMessage = "%s Hidden objects" % (len(objects))

    def fix(self):
        """@brief Set objects visibility
        """
        for obj in self.errorNodes:
            if obj.visibility.get(l=True) == True:
                obj.visibility.set(l=False)
            obj.visibility.set(1)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)

#===============================================================================
# Duplicate textures
#===============================================================================
class CheckDuplicateTextures(CheckMayaAbstract):
    """@brief Check if there is multiple file nodes pointing to the same texture.
    """
    _name = "Duplicate file nodes"
    _category = "Texturing"

    _asSelection = True
    _asFix = True
    _deactivatable = True

    def _getDuplicateFileNode(self):
        """@brief return the file nodes that are pointing to the same textures.

        @return texturesPaths Dictionary with the texturePath a key and the the file nodes as value. (dict)
        """
        texturesPaths = dict()
        # get all the file nodes that are not referenced
        fileNodes = [fileNode for fileNode in pm.ls(type="file") if not fileNode.isReferenced()]
        for fileNode in fileNodes :
            texturePath = fileNode.fileTextureName.get()
            try :
                texturesPaths[texturePath].append(fileNode)
            except KeyError :
                texturesPaths[texturePath] = [fileNode]

        return texturesPaths

    def _deleteFileNode(self, fileNode):
        """@brief Delete a file node and the place2dTexture where it is connected
        if the the place2dTexture is not connected to another file node.
        """
        place2dText = fileNode.uvCoord.inputs()[0]
        # check that the place2dText is not connected to another file node
        # if not delete it
        if not [node for node in place2dText.outputs(type="file") if node != fileNode] :
            pm.delete(place2dText)
        pm.delete(fileNode)



    def check(self):
        """@brief Check if there is multiple file nodes pointing to the same texture.
        """
        for texturesPath, fileNodes in self._getDuplicateFileNode().items() :
            if len(fileNodes) > 1 :
                self.errorNodes.extend(fileNodes)
                self.addError("multiple file nodes point to %s" % texturesPath)

        if self.errorNodes :
            self.status = self.errorMode
            self.errorMessage = "%s FileNodes are duplicate" % (len(self.errorNodes))
        else :
            self.status = "OK"

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)

    def fix(self):
        """@brief Get a list of the files node that point to the same textures
        leave only one and reconnect it where the deleted one where connected.
        """
        texturesPaths = self._getDuplicateFileNode()
        for texturesPath, fileNodes in texturesPaths.items() :
            # if there is more that one fileNode pointing to the same
            # texture get the attributes where are connected the duplicate fileNode
            # connect the first file node and delete the duplicate one.
            if len(fileNodes) > 1 :
                for duplicateFileNode in fileNodes[1:] :
                    attributes = duplicateFileNode.outputs(connections=True, plugs=True)
                    for outAttribute, inAttribute in attributes :
                        if not inAttribute.startswith("defaultTextureList") :
                            outAttributeName = str(outAttribute).split(".")[-1]
                            fileNodes[0].attr(outAttributeName).connect(inAttribute, f=True)
                    self._deleteFileNode(duplicateFileNode)

        self.run()



#=======================================
# Ghost Shapes
#=======================================
class CheckGhostShapes(CheckMayaAbstract):
    """@brief Check if objects on scene have ghost shapes.
    """
    _name = "Ghost Shapes"
    _category = "Modeling"

    _asSelection = True
    _asFix = True


    def check(self):
        """@brief Check for shapes without any connection
        """
        
        meshes = pm.ls(type="mesh")
        ghostShapes = []


        for mesh in meshes:
            if not pm.objExists(mesh.name() + ".grid_noCheck"):
                connections = mesh.listConnections()
                if len(connections) == 0:
                    ghostShapes.append(mesh)

        if not ghostShapes :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = ghostShapes
            for obj in ghostShapes :
                self.addError("%s is a ghost shape." % obj)
            self.errorMessage = "%s Ghost shapes on scene." % (len(ghostShapes))

    def fix(self):
        """@brief Deletes the ghost shapes
        """
        
        pm.delete(self.errorNodes)

        self.run()

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        

#===============================================================================
# reverse uv
#===============================================================================
class CheckReverseUv(CheckMayaAbstract):
    """@brief Check for object with reverse uv.
    """
    _name = "Reverse uv"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def checkReversedUVs(self, dagName):
        """@brief Return the uv that a reverse.
        
        @param dagName The name of the object that need to be checked. (string)
        
        @return reversedUv
        """
        inversedUv = list()
        selection = om.MSelectionList()
        selection.add(dagName)
        if not selection.isEmpty() :
            mesh = om.MFnMesh(selection.getDagPath(0))
            for polyIndex in xrange(mesh.numPolygons):
                try :
                    pointList = []
                    for pointIndex in xrange(3):
                        pointList.append(mesh.getPolygonUV(polyIndex, pointIndex))
                    edges = (
                        (pointList[1][0] - pointList[0][0], pointList[1][1] - pointList[0][1]),
                        (pointList[2][0] - pointList[1][0], pointList[2][1] - pointList[1][1]))
                    if (edges[0][0] * edges[1][1]) - (edges[0][1] * edges[1][0]) < 0 :
                        inversedUv.append("%s.map[%s]" % (dagName, polyIndex))
                except RuntimeError :
                    inversedUv.append(dagName)
        
        if len(inversedUv) > 3 :
            return inversedUv
        else :
            return []


    def check(self):
        """@brief Check for inversed uv.
        """
        inversedUvs = list()
        
        for mesh in pm.ls(type="mesh") :
            if not pm.objExists(mesh.name() + ".grid_noCheck") and pm.objExists(mesh.name() + ".grid_renderGeo"):
                inversedUvs.extend(self.checkReversedUVs(mesh.getParent().name()))
            

        if not inversedUvs :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = inversedUvs
            for uv in inversedUvs :
                self.addError("%s is inversed." % uv)
            self.errorMessage = "%s inversed uv's." % (len(inversedUvs))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)

class CheckMeshName(CheckMayaAbstract):
    """@brief Check if the name of the meshes match with the naming convention.
    """
    _name = "Meshes name"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if the name of the meshes match with the naming convention.
        """
        badNamedMeshes = list()
        
        prog = re.compile("^[a-z][a-zA-Z]+_[C|L|R|F|B|U|D]_[0-9]{3}_DMSH[0-9]{2}Shape$")
        
        for mesh in pm.ls(type="mesh") :
            # get only the last part of the name to avoid the problems when geometry are instanced
            if not prog.match(mesh.shortName().split("|")[-1]) :
                badNamedMeshes.append(mesh)
            

        if not badNamedMeshes :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badNamedMeshes
            for mesh in badNamedMeshes :
                self.addError("%s is not a legal mesh name" % mesh)
            self.errorMessage = "%s illegal mesh name(s)" % (len(badNamedMeshes))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        
        
class CheckMeshTransformName(CheckMayaAbstract):
    """@brief Check if the name of the parent of the meshes match with the naming convention.
    """
    _name = "Meshes transform name"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if the name of the parent of the meshes match with the naming convention.
        """
        badTransformName = list()
        
        prog = re.compile("^[a-z][a-zA-Z]+_[C|L|R|F|B|U|D]_[0-9]{3}_DMSH$")
        
        for mesh in pm.ls(type="mesh") :
            transform = mesh.getParent()
            # get only the last part of the name to avoid the problem with the instance
            # TODO : check for a cleaner way to get the real shortname
            if not prog.match(transform.shortName().split("|")[-1]) :
                badTransformName.append(transform)
            

        if not badTransformName :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badTransformName
            for mesh in badTransformName :
                self.addError("%s is not a legal mesh transform name" % mesh)
            self.errorMessage = "%s illegal mesh transform name(s)" % (len(badTransformName))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        
class CheckGroupName(CheckMayaAbstract):
    """@brief Check if the name of the group (transform without shape) match with the naming convention.
    """
    _name = "Group name"
    _category = "Modeling"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if the name of the group (transform without shape) match with the naming convention.
        """
        badGroupName = list()
        
        prog = re.compile("^[a-z][a-zA-Z]+_[C|L|R|F|B|U|D]_[0-9]{3}_GRUP$")
        
        for group in pm.ls(exactType="transform") :
            if not group.isReferenced() :
                if not pm.objExists(group.name() + ".grid_noCheck") :
                    if not group.getShapes():
                        if not prog.match(group.name()) :
                            badGroupName.append(group)
            

        if not badGroupName :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badGroupName
            for group in badGroupName :
                self.addError("%s is not a legal group name" % group)
            self.errorMessage = "%s illegal group name(s)" % (len(badGroupName))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        
class CheckMeshLockedTransform(CheckMayaAbstract):
    """@brief Check if the transform attributes of the mesh are locked.
    """
    _name = "Mesh Lock Transform"
    _category = "Modeling"

    _asSelection = True
    _asFix = True
    
    def check(self):
        """@brief Check if the transform attributes of the mesh are locked.
        """
        unlockedTransforms = list()
        
        for mesh in pm.ls(type="mesh") :
            meshTransform = mesh.getParent()
            for attribute in ["tx", "ty", "tz",
                               "rx", "ry", "rz",
                               "sx", "sy", "sz"] :
                if not meshTransform.attr(attribute).isLocked() :
                    unlockedTransforms.append(meshTransform)
                    break
            

        if not unlockedTransforms :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = unlockedTransforms
            for transform in unlockedTransforms :
                self.addError("%s as unlocked transform attributes" % transform)
            self.errorMessage = "%s unlocked mesh transform" % (len(unlockedTransforms))
            
    def fix(self):
        """@brief Lock the transform of the meshes.
        """
        for transform in self.errorNodes:
            for attribute in ["tx", "ty", "tz",
                               "rx", "ry", "rz",
                               "sx", "sy", "sz"] :
                transform.attr(attribute).lock()
        self.run()
            

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)

#==============================================================================================================================================================
# Rigging
#==============================================================================================================================================================

#=======================================
# Master Control
#=======================================
class CheckMasterCtrl(CheckMayaAbstract):
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
        if pm.objExists("top_C_001_CTRL") :
            self.status = "OK"
        else :
            self.status = "ERROR"
            self.addError("No node with the name top_C_001_CTRL")
            self.errorMessage = "No top Controler"


#=======================================
# Useless constrains
#=======================================
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

        if not uselessConstrains :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = uselessConstrains
            for obj in uselessConstrains :
                self.addError("%s doesn't have outgoing connections." % obj)
            self.errorMessage = "%s useless constrains" % (len(uselessConstrains))


    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


    def fix(self):
        """@brief Deletes the useless constrains.
        """
        
        pm.delete(self.errorNodes)
        
        self.run()

#===============================================================================
# gNodes
#===============================================================================

# class CheckGNodesPresent(CheckMayaAbstract):
#     """@brief Check if there is only one gNodes at the top of the hierarchie.
#     """
#     _name = "GNodes Present"
#     _category = "GNodes"

#     _asSelection = False
#     _asFix = False


#     def check(self):
#         """@brief Check if there is only one gNodes at the top of the hierarchie.
#         """
#         try :
#             gNodes.getTopGNode()
#         except gNodes.NoGNodesError:
#             self.status = self.errorMode
#             self.addError("No GNodes at the top of the hieararchy")
#             self.errorMessage = "No gNodes at the top of the hierarchy"
#         except gNodes.MultipleGNodesError:
#             self.status = self.errorMode
#             self.addError("Multiple gNodes at the top of the  hierarchy")
#             self.errorMessage = "Multiple gNodes at the top of the  hierarchy"
#         else :
#             self.status = "OK"
            
# class CheckRenderGeo(CheckMayaAbstract):
#     """@brief Check if there at least one geo tagged as render geo.
#     """
#     _name = "Render geo"
#     _category = "GNodes"

#     _asSelection = False
#     _asFix = False


#     def check(self):
#         """@brief Check if there at least one geo tagged as render geo.
#         """
#         if not pm.ls("*.grid_renderGeo") :
#             self.status = self.errorMode
#             self.addError("No geometry's are tagged as render geo")
#             self.errorMessage = "No geometry is tagged as render geo"
#         else :
#             self.status = "OK"

# class CheckGAssetName(CheckMayaAbstract):
#     """@brief Check if the name of asset node match with the naming convention.
#     """
#     _name = "Asset node name"
#     _category = "GNodes"

#     _asSelection = True
#     _asFix = False
    
#     def check(self):
#         """@brief Check if the name of asset node match with the naming convention.
#         """
#         badNamedAssetNode = list()
        
#         prog = re.compile("^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_GAST[0-9]{2}Shape$")
        
#         for assetNode in pm.ls(type="gAsset") :
#             if not prog.match(assetNode.name()) and not assetNode.isReferenced() :
#                 badNamedAssetNode.append(assetNode)

#         if not badNamedAssetNode :
#             self.status = "OK"
#         else :
#             self.status = self.errorMode
#             self.errorNodes = badNamedAssetNode
#             for mesh in badNamedAssetNode :
#                 self.addError("%s is not a legal asset node name" % mesh)
#             self.errorMessage = "%s illegal asset node name(s)" % (len(badNamedAssetNode))

#     def select(self):
#         """@brief Select the error nodes.
#         """
#         pm.select(self.errorNodes)
        
        
# class CheckGAssetTransformName(CheckMayaAbstract):
#     """@brief Check if the name of the parent of the asset node match with the naming convention.
#     """
#     _name = "GAsset transform name"
#     _category = "GNodes"

#     _asSelection = True
#     _asFix = False
    
#     def check(self):
#         """@brief Check if the name of the parent of the asset node match with the naming convention.
#         """
#         badTransformName = list()
        
#         prog = re.compile("^[A-Z]{4}[0-9]{2}_C_[0-9]{3}_GAST$")
        
#         for assetTransform in pm.ls(type="gAsset") :
#             if not prog.match(assetTransform.getParent().name()) and not assetTransform.isReferenced():
#                 badTransformName.append(assetTransform)
            

#         if not badTransformName :
#             self.status = "OK"
#         else :
#             self.status = self.errorMode
#             self.errorNodes = badTransformName
#             for mesh in badTransformName :
#                 self.addError("%s is not a legal asset node transform name" % mesh)
#             self.errorMessage = "%s illegal asset node transform name(s)" % (len(badTransformName))

#     def select(self):
#         """@brief Select the error nodes.
#         """
#         pm.select(self.errorNodes)
        

# class CheckAssetNodeDataContextMatch(CheckMayaAbstract):
#     """@brief Check if the data in the asset node and the one from the tank context match.
#     """
#     _name = "Asset Metadata tank context match"
#     _category = "GNodes"

#     _asSelection = False
#     _asFix = False
    
#     def check(self):
#         """@brief Check if the data in the asset node and the one from the tank context match.
#         """
#         # get the data from shotgun
#         app = self.parent.app
#         context = app.context
#         # get asset type
#         filters = [["id", "is", context.entity["id"]]]
#         fields = ["sg_asset_type"]
#         assetType = app.shotgun.find_one("Asset", filters=filters, fields=fields)["sg_asset_type"]
#         # get step short name
#         filters = [["id", "is", context.step["id"]]]
#         fields = ["short_name"]
#         stepShortName = app.shotgun.find_one("Step", filters=filters, fields=fields)["short_name"]
        
#         try :
#             assetNode = gNodes.getTopGNode()
#         except :
#             assetNode = None
            
#         if assetNode :
#             metadataCode = assetNode.grid_code.get()
#             metadataAssetType = assetNode.grid_type.get(asString=True)
#             metadataPipeStep = assetNode.grid_pipeStep.get(asString=True)
#             if not (assetType == metadataAssetType \
#                     and stepShortName == metadataPipeStep\
#                     and context.entity["name"] == metadataCode) :
#                 self.status = self.errorMode
#                 self.addError("Context and asset node metadata don't match")
#                 self.errorMessage = "Context and asset node metadata don't match"
#             else :
#                 self.status = "OK"
#         else :
#             self.status = "OK"
            
# class CheckSequenceNodeDataContextMatch(CheckMayaAbstract):
#     """@brief Check if the data in the sequence node and the one from the tank context match.
#     """
#     _name = "Sequence Metadata tank context match"
#     _category = "GNodes"

#     _asSelection = False
#     _asFix = False
    
#     def check(self):
#         """@brief Check if the data in the sequence node and the one from the tank context match.
#         """
#         # get the data from shotgun
#         app = self.parent.app
#         context = app.context

#         # get step short name
#         filters = [["id", "is", context.step["id"]]]
#         fields = ["short_name"]
#         stepShortName = app.shotgun.find_one("Step", filters=filters, fields=fields)["short_name"]
        
#         try :
#             sequenceNode = gNodes.getTopGNode()
#         except :
#             sequenceNode = None
            
#         if sequenceNode :
#             metadataCode = sequenceNode.grid_code.get()
#             metadataPipeStep = sequenceNode.grid_pipeStep.get(asString=True)
#             if not (stepShortName == metadataPipeStep\
#                     and context.entity["name"] == metadataCode) :
#                 self.status = self.errorMode
#                 self.addError("Context and sequence node metadata don't match")
#                 self.errorMessage = "Context and sequence node metadata don't match"
#             else :
#                 self.status = "OK"
#         else :
#             self.status = "OK"
        
#===============================================================================
# Texture
#===============================================================================

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
        
        
        textLowPublishTemplate = self.parent.app.get_template_by_name("textureLow_publish")
        
        for fileNode in pm.ls(type="file") :
            filePath = os.path.abspath(fileNode.fileTextureName.get())
            if not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]) :
                badTextures.append(fileNode)
                
        for aiImageNode in pm.ls(type="aiImage") :
            filePath = os.path.abspath(aiImageNode.filename.get())
            if not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]) :
                badTextures.append(aiImageNode)
                
        if not badTextures :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badTextures
            for node in badTextures :
                nodeType = node.type()
                if nodeType == "file" :
                    self.addError("%s is not in the library" % node.fileTextureName.get())
                elif nodeType == "aiImage" :
                    self.addError("%s is not in the library" % node.filename.get())
                else :
                    raise "%s from nodeType %s is not supported by this check" % (node, node.type())
            self.errorMessage = "%s texture not in library" % (len(badTextures))

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
        
        
        textPublishTemplate = self.parent.app.get_template_by_name("texture_publish")
        
        for fileNode in pm.ls(type="file") :
            print fileNode
            filePath = os.path.abspath(fileNode.fileTextureName.get())
            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]) :
                badTextures.append(fileNode)
                
        for aiImageNode in pm.ls(type="aiImage") :
            print aiImageNode
            filePath = os.path.abspath(aiImageNode.filename.get())
            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]) :
                badTextures.append(aiImageNode)
                
        if not badTextures :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badTextures
            for node in badTextures :
                nodeType = node.type()
                if nodeType == "file" :
                    self.addError("%s is not in the library" % node.fileTextureName.get())
                elif nodeType == "aiImage" :
                    self.addError("%s is not in the library" % node.filename.get())
                else :
                    raise "%s from nodeType %s is not supported by this check" % (node, node.type())
            self.errorMessage = "%s texture(s) not in library" % (len(badTextures))

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
        
        
        textPublishTemplate = self.parent.app.get_template_by_name("texture_publish")
        textLowPublishTemplate = self.parent.app.get_template_by_name("textureLow_publish")
        
        for fileNode in pm.ls(type="file") :
            filePath = os.path.abspath(fileNode.fileTextureName.get())
            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]) and not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(fileNode)
                
        for aiImageNode in pm.ls(type="aiImage") :
            filePath = os.path.abspath(aiImageNode.filename.get())
            if not textPublishTemplate.validate(filePath, skip_keys=["udim"]) and not textLowPublishTemplate.validate(filePath, skip_keys=["udim"]):
                badTextures.append(aiImageNode)
            
                
        if not badTextures :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badTextures
            for node in badTextures :
                nodeType = node.type()
                if nodeType == "file" :
                    self.addError("%s is not in the library" % node.fileTextureName.get())
                elif nodeType == "aiImage" :
                    self.addError("%s is not in the library" % node.filename.get())
                else :
                    raise "%s from nodeType %s is not supported by this check" % (node, node.type())
            self.errorMessage = "%s texture(s) not in library" % (len(badTextures))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)

#===============================================================================
# Reference
#===============================================================================
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
        
        
        for mesh in pm.ls(type="mesh") :
            if not pm.objExists(mesh.name() + ".grid_noCheck") :
                if not mesh.isReferenced() :
                    nonReferencedMesh.append(mesh)
                
        if not nonReferencedMesh :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = nonReferencedMesh
            for mesh in nonReferencedMesh :
                self.addError("%s is not referenced" % mesh.name())
            self.errorMessage = "%s non referenced mesh(es)" % (len(nonReferencedMesh))

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
        
        for assetNode in pm.ls(type="gAsset") :
            if assetNode.grid_pipeStep.get(asString=True) == "modLow" :
                assetNodeTransform = assetNode.getParent()
                for mesh in assetNodeTransform.listRelatives(ad=True, type="mesh") :
                    meshTransform = mesh.getParent()
                    if meshTransform.getTranslation() != pm.dt.Vector([0, 0, 0]) :
                        transformedMesh.append(meshTransform)
                        continue
                    elif meshTransform.getRotation() != pm.dt.EulerRotation([0, 0, 0]) :
                        transformedMesh.append(meshTransform)
                        continue
                    elif meshTransform.getScale() != [1, 1, 1] :
                        transformedMesh.append(meshTransform)
                
        if not transformedMesh :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = transformedMesh
            for meshTransform in transformedMesh :
                self.addError("%s as some transformation" % mesh.name())
            self.errorMessage = "%s mesh(es) with transformation" % (len(transformedMesh))

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
        
        for assetNode in pm.ls(type="gAsset") :
            if assetNode.isReferenced() and not prog.match(assetNode.namespace()) :
                illegalNamespaces.append(assetNode)
                
        if not illegalNamespaces :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = illegalNamespaces
            for illegalNamespace in illegalNamespaces :
                self.addError("%s has a illegal namespace" % illegalNamespace)
            self.errorMessage = "%s asset(s) have a illegal namespace" % (len(illegalNamespaces))

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
        
        for namespaces in pm.namespaceInfo(listOnlyNamespaces=True, internal=False, recurse=True) :
            for namespace in namespaces.split(":") :
                if not progStandard.match(namespace) and not progShot.match(namespace) not in ["UI", "shared"] :
                    illegalNamespaces.append(namespace)
        
                
        if not illegalNamespaces :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = illegalNamespaces
            for illegalNamespace in illegalNamespaces :
                self.addError("%s is a illegal namespace" % illegalNamespace)
            self.errorMessage = "%s  illegal namespace" % (len(illegalNamespaces))

    def select(self):
        """@brief Select the error nodes.
        """
        for elem in self.errorLog :
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
        
        for namespace in pm.listNamespaces() :
            BadNamespaces.append(namespace)
        
                
        if not BadNamespaces :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = namespace
            for namespace in BadNamespaces :
                self.addError("namespace %s exist" % namespace)
            self.errorMessage = "%s namespace" % (len(BadNamespaces))

    def select(self):
        """@brief Select the error nodes.
        """
        for elem in self.errorLog :
            print elem
            
    def fix(self):
        """@brief Delete the namespace in the scene.
        """
        for namespace in pm.listNamespaces() :
            for elem in namespace.ls() :
                elem.rename(elem.split(":")[-1])
            namespace.remove()
            
        self.run()
        
#===============================================================================
# Shots
#===============================================================================

class CheckShotsStartEnd(CheckMayaAbstract):
    """@brief Check if the start and end frame of the shots match with the start and end frame of sequences.
    """
    _name = "Shots start end match sequences"
    _category = "Shots"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if the start and end frame of the shots match with the start and end frame of sequences.
        """
        badShots = list()
        
        for shot in pm.ls(type="shot") :
            if not shot.startFrame.get() == shot.sequenceStartFrame.get() :
                badShots.append(shot)
                continue
            elif not shot.endFrame.get() == shot.sequenceEndFrame.get() :
                badShots.append(shot)
        
                
        if not badShots :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = badShots
            for shot in badShots :
                self.addError("shot start or end frame don't match sequence start or end on %s" % shot)
            self.errorMessage = "%s shots where start or end frame don't match sequence start or end frame" % (len(badShots))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
        for elem in self.errorLog :
            print elem
            
        
class CheckOverlappingShots(CheckMayaAbstract):
    """@brief Check if there is no overlaping shot in the sequencer.
    """
    _name = "Overlapping shot"
    _category = "Shots"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if there is no overlaping shot in the sequencer.
        """
        overlappingShots = list()
        
        shots = pm.ls(type="shot")
        
        for i, shot in enumerate(shots) :
            start = shot.startFrame.get()
            end = shot.endFrame.get()
            for shotB in shots[i + 1:] :
                if (start >= shotB.startFrame.get() and start <= shotB.endFrame.get()) \
                or end >= shotB.startFrame.get() and end <= shotB.endFrame.get() :
                    overlappingShots.append(shotB)
                    break

        
                
        if not overlappingShots :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = overlappingShots
            for shot in overlappingShots :
                self.addError("shot %s overlap with some other shots" % shot)
            self.errorMessage = "%s overlapping with some other shots" % (len(overlappingShots))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)


#===============================================================================
# Look dev
#===============================================================================
class CheckShadingId(CheckMayaAbstract):
    """@brief Check if all the shading groups are linked to at least one if.
    """
    _name = "Shading group in id"
    _category = "LookDev"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if all the shading groups are linked to at least one if.
        """
        shadingGroupNoId = list()
        
        excludedShadingEngine = ["initialParticleSE",
                                 "initialShadingGroup"]
        
        for shadingGroup in pm.ls(type="shadingEngine") :
            if not shadingGroup.name() in excludedShadingEngine :
                if not pm.objExists("%s.grid_noCheck" % shadingGroup.name()) :
                    # check if there is at least one connection to the aiCustomAOVs input array
                    if not shadingGroup.aiCustomAOVs.inputs() :
                        shadingGroupNoId.append(shadingGroup)

        
        if not shadingGroupNoId :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = shadingGroupNoId
            for shadingGroup in shadingGroupNoId :
                self.addError("shading group %s don't have any input in aiCustomAOVs" % shadingGroup)
            self.errorMessage = "%s shading group are not in any id" % (len(shadingGroupNoId))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes, noExpand=True)
        
        
class CheckShadingGroupName(CheckMayaAbstract):
    """@brief Check if the name of the shading groups are legal.
    """
    _name = "Shading group name"
    _category = "LookDev"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if the name of the shading groups are legal.
        """
        shadingGroupBadName = list()
        
        prog = re.compile("^[a-z][a-zA-Z]+_(C|L|R|F|B|U|D)_[0-9]{3}_SHAD$")
        
        excludedShadingEngine = ["initialParticleSE",
                                 "initialShadingGroup"]
        
        for shadingGroup in pm.ls(type="shadingEngine") :
            if not pm.objExists("%s.grid_noCheck" % shadingGroup.name()) :
                if not shadingGroup.name() in excludedShadingEngine :
                    if not prog.match(shadingGroup.name()) :
                        shadingGroupBadName.append(shadingGroup)


        if not shadingGroupBadName :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = shadingGroupBadName
            for shadingGroup in shadingGroupBadName :
                self.addError("%s is not a legal name for a shading group" % shadingGroup)
            self.errorMessage = "%s shading groups with illegal name" % (len(shadingGroupBadName))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes, noExpand=True)
        

class CheckShaderName(CheckMayaAbstract):
    """@brief Check if the name of the shaders are legal.
    """
    _name = "Shader name"
    _category = "LookDev"

    _asSelection = True
    _asFix = False
    
    def check(self):
        """@brief Check if the name of the shaders are legal.
        """
        shaderBadName = list()
        
        prog = re.compile("^[a-z][a-zA-Z]+_(C|L|R|F|B|U|D)_[0-9]{3}_AIST$")
        
        # TODO: add support for the other shader 
        for aiStandard in pm.ls(type="aiStandard") :
            if not pm.objExists("%s.grid_noCheck" % aiStandard.name()) :
                if not prog.match(aiStandard.name()) :
                    shaderBadName.append(aiStandard)


        if not shaderBadName :
            self.status = "OK"
        else :
            self.status = self.errorMode
            self.errorNodes = shaderBadName
            for shadingGroup in shaderBadName :
                self.addError("%s is not a legal name for a shader" % shadingGroup)
            self.errorMessage = "%s shader with illegal name" % (len(shaderBadName))

    def select(self):
        """@brief Select the error nodes.
        """
        pm.select(self.errorNodes)
