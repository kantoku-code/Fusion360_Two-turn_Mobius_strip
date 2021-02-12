#Author-kantoku
#Description-Two-turn Mobius strip
#Fusion360API Python

import adsk.core
import adsk.fusion
import traceback
import math
from typing import List

_debug = False

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        MobiusStripFactry.unitTest()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MobiusStripFactry:

    @staticmethod
    def createMobiusStrip(
        center :adsk.fusion.SketchPoint,
        twistCount :int,
        holeCount :int,
        thick :float
        ) -> adsk.fusion.BRepBody:

        # numerical calculation
        rotations = [0, 240, 480]

        # base point
        basePnt = adsk.core.Point3D.create(holeCount * 0.25, 0, 0)

        # sweep
        sweeps = [MobiusStripFactry._initSweep(basePnt, twistCount, ang) for ang in rotations]

        if _debug:
            trims = sweeps
        else:
            # sphere
            spheres = [MobiusStripFactry._initSphere(basePnt, ang, holeCount) for ang in rotations]

            # trim
            trims = [MobiusStripFactry._initTrim(sw,sps) for sw, sps in zip(sweeps, spheres)]

        # create BaseFeature
        baseBodies = MobiusStripFactry._createBaseFeature(trims)

        # get Matrix
        sktMat :adsk.core.Matrix3D = MobiusStripFactry._getSketchPointMatrix(center)
        mat :adsk.core.Matrix3D = sktMat.copy()

        # create occurrence
        app :adsk.core.Application = adsk.core.Application.get()
        des :adsk.fusion.Design = app.activeProduct
        root :adsk.fusion.Component = des.rootComponent
        occ :adsk.fusion.Occurrence = root.occurrences.addNewComponent(
            adsk.core.Matrix3D.create())
        occ.component.name = 'Two-turn Mobius strip'

        # thickenBody
        MobiusStripFactry._createThickenBody(
            baseBodies,
            adsk.core.ValueInput.createByReal(thick * 0.5),
            occ.component,
            mat)

        # body rename
        bodies :adsk.fusion.BRepBodies = occ.component.bRepBodies
        if bodies.count > 0:
            bodies[0].name = f'twist{twistCount}_hole{holeCount}'
            return bodies[0]
        else:
            return None

    @staticmethod
    def previewMobiusStrip(
        center :adsk.fusion.SketchPoint,
        twistCount :int,
        holeCount :int,
        ) -> List[adsk.fusion.BRepBody]:

        # numerical calculation
        rotations = [0, 240, 480]

        # base point
        basePnt = adsk.core.Point3D.create(holeCount * 0.25, 0, 0)

        # sweep
        sweeps = [MobiusStripFactry._initSweep(basePnt, twistCount, ang) for ang in rotations]

        # get mat
        sktMat :adsk.core.Matrix3D = MobiusStripFactry._getSketchPointMatrix(center)
        mat :adsk.core.Matrix3D = sktMat.copy()

        # create BaseFeature
        baseBodies = MobiusStripFactry._createBaseFeature(sweeps, mat)

        return baseBodies


    # sweep
    @staticmethod
    def _initSweep(
        basePnt :adsk.core.Point3D,
        twistCount :int,
        posAng :float
        ) -> adsk.fusion.BRepBody:

        app = adsk.core.Application.get()
        des :adsk.fusion.Design = app.activeProduct
        root :adsk.fusion.Component = des.rootComponent

        pnt3D = adsk.core.Point3D
        vec3D = adsk.core.Vector3D

        width = 4.0
        twistAllAng = 180 * twistCount
        twistStartAng = twistAllAng * (1/3) * (posAng / 240)
        twistAngle = twistAllAng * (1/3)

        dustBox = []

        mat :adsk.core.Matrix3D = adsk.core.Matrix3D.create()
        mat.setToRotation(
            math.radians(posAng),
            vec3D.create(0,0,1),
            pnt3D.create(0,0,0))

        # prof coordinate
        profMin :adsk.core.Point3D = pnt3D.create(
            basePnt.x + (-width * 0.5 * math.cos(math.radians(-twistStartAng))),
            0,
            -width * 0.5 * math.sin(math.radians(-twistStartAng)))
        profMin.transformBy(mat)

        profMax :adsk.core.Point3D = pnt3D.create(
            basePnt.x + (width * 0.5 * math.cos(math.radians(-twistStartAng))),
            0,
            width * 0.5 * math.sin(math.radians(-twistStartAng)))
        profMax.transformBy(mat)

        # sketch
        skt :adsk.fusion.Sketch = root.sketches.addWithoutEdges(
            root.xYConstructionPlane)
        dustBox.append(skt)
        skt.isLightBulbOn = False

        # prof
        lines :adsk.fusion.SketchLines = skt.sketchCurves.sketchLines
        line = lines.addByTwoPoints(profMin, profMax)

        prof :adsk.fusion.Profile = root.createOpenProfile(line)

        # path
        pathPnt :adsk.core.Point3D = basePnt.copy()
        pathPnt.transformBy(mat)
        arcs :adsk.fusion.sketchArcs = skt.sketchCurves.sketchArcs
        guide :adsk.fusion.SketchArc = arcs.addByCenterStartSweep(
            pnt3D.create(0,0,0),
            pathPnt,
            math.radians(240))

        NOCHAINED = adsk.fusion.ChainedCurveOptions.noChainedCurves
        path = adsk.fusion.Path.create(guide, NOCHAINED)

        # sweep
        swpFeats :adsk.fusion.SweepFeatures = root.features.sweepFeatures
        NEWBODY = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        valIpt = adsk.core.ValueInput

        twistVal = valIpt.createByReal(math.radians(twistAngle))

        swpIpt :adsk.fusion.SweepFeatureInput = swpFeats.createInput(prof, path, NEWBODY)
        swpIpt.twistAngle = twistVal
        swpIpt.isSolid = False

        swpFeat :adsk.fusion.SweepFeature = swpFeats.add(swpIpt)
        dustBox.append(swpFeat)

        tmpMgr = adsk.fusion.TemporaryBRepManager.get()
        clone :adsk.fusion.BRepBody = tmpMgr.copy(swpFeat.bodies[0])

        # delete skt,sweep
        [d.deleteMe() for d in dustBox[::-1]]

        return clone


    # sphere
    @staticmethod
    def _initSphere(
        basePnt :adsk.core.Point3D,
        posAng :float,
        holeCount :int,
        radius :float = 1.4
        ) -> List[adsk.fusion.BRepBody]:

        pnt3D = adsk.core.Point3D
        vec3D = adsk.core.Vector3D
        mat3D = adsk.core.Matrix3D

        unitAng = 720 / holeCount
        spCount = int(240 // unitAng) + 2
        vecZ = vec3D.create(0,0,1)
        pntZero = pnt3D.create(0,0,0)
        startAng = int(posAng / unitAng) * unitAng

        tmpMgr = adsk.fusion.TemporaryBRepManager.get()
        baseSp = tmpMgr.createSphere(basePnt, radius)
        spheres = []
        for idx in range(spCount):
            clone = tmpMgr.copy(baseSp)
            mat = mat3D.create()
            mat.setToRotation(math.radians(unitAng * idx + startAng), vecZ, pntZero)
            tmpMgr.transform(clone, mat)
            spheres.append(clone)

        return spheres


    # trim
    @staticmethod
    def _initTrim(
        sw :adsk.fusion.BRepBody,
        sps :List[adsk.fusion.BRepBody]
        ) -> adsk.fusion.BRepBody:

        tmpMgr = adsk.fusion.TemporaryBRepManager.get()

        clone = tmpMgr.copy(sw)
        boolDiff = adsk.fusion.BooleanTypes.DifferenceBooleanType
        for sp in sps:
            tool = tmpMgr.copy(sp.faces[0])
            tmpMgr.booleanOperation(clone,tool,boolDiff)

        return clone


    # insert Bodies
    @staticmethod
    def _createBaseFeature(
        surfs :List[adsk.fusion.BRepBody],
        mat :adsk.core.Matrix3D = None
        ) -> List[adsk.fusion.BRepBody]:

        app = adsk.core.Application.get()
        des :adsk.fusion.Design = app.activeProduct
        comp :adsk.fusion.Component = des.rootComponent



        matZero :adsk.core.Matrix3D = adsk.core.Matrix3D.create()
        if not mat:
            mat = matZero.copy()

        # transform
        if not matZero.isEqualTo(mat):
            tmpMgr = adsk.fusion.TemporaryBRepManager.get()
            [tmpMgr.transform(surf, mat) for surf in surfs]

        # BaseFeature
        baseFeats :adsk.fusion.BaseFeatures = comp.features.baseFeatures
        baseFeat = adsk.fusion.BaseFeature.cast(None)
        bodyLst = []
        try:
            baseFeat = baseFeats.add()
            baseFeat.startEdit()
            for surf in surfs:
                bodyLst.append(comp.bRepBodies.add(surf, baseFeat))
        except:
            pass
        finally:
            baseFeat.finishEdit()

        return bodyLst

    # get Matrix
    @staticmethod
    def _getSketchPointMatrix(
        sketchPnt :adsk.fusion.SketchPoint
        ) -> adsk.core.Matrix3D:

        try:
            # sketch point
            skt :adsk.fusion.Sketch = sketchPnt.parentSketch
            mat :adsk.core.Matrix3D = skt.transform
            _, xAxis, yAxis, zAxis = mat.getAsCoordinateSystem()
            mat.setWithCoordinateSystem(sketchPnt.worldGeometry, xAxis, yAxis, zAxis)

            if _debug :
                dumpMsg(f'skt_mat:{mat.asArray()}' )

            return mat
        except:
            # root
            return adsk.core.Matrix3D.create()

    # get Matrix -non use
    @staticmethod
    def _getOccMatrixFromSketchPoint(
        sketchPnt :adsk.fusion.SketchPoint
        ) -> adsk.core.Matrix3D:

        try:
            # occ
            skt :adsk.fusion.Sketch = sketchPnt.parentSketch
            occ :adsk.fusion.Occurrence = skt.assemblyContext
            des = adsk.fusion.Design.cast(occ.component.parentDesign)
            root = des.rootComponent

            mat = adsk.core.Matrix3D.create()
            occ_names = occ.fullPathName.split('+')
            if _debug:
                dumpMsg(f'occ_name:{occ.fullPathName}' )
            occs = [root.allOccurrences.itemByName(name) 
                        for name in occ_names]
            mat3ds = [occ.transform for occ in occs]
            mat3ds.reverse() #important!!
            for mat3d in mat3ds:
                mat.transformBy(mat3d)

            if _debug :
                dumpMsg(f'occ_mat:{mat.asArray()}' )

            return mat
        except:
            # root
            return adsk.core.Matrix3D.create()


    @staticmethod
    def _createThickenBody(
        bodyList :List[adsk.fusion.BRepBody],
        value :adsk.core.ValueInput,
        comp :adsk.fusion.Component,
        mat :adsk.core.Matrix3D = None
        ) -> adsk.fusion.BRepBody:

        # ObjectCollection
        objs = adsk.core.ObjectCollection.create()
        [objs.add(body.faces[0]) for body in bodyList]

        # thickenFeature
        thickFeats :adsk.fusion.ThickenFeatures  = comp.features.thickenFeatures
        NEWBODY = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        thickFeat = thickFeats.add(thickFeats.createInput(objs, value, True, NEWBODY))

        # clone
        tmpMgr = adsk.fusion.TemporaryBRepManager.get()
        clone :adsk.fusion.BRepBody = tmpMgr.copy(thickFeat.bodies[0])

        # get Matrix & transform
        matZero :adsk.core.Matrix3D = adsk.core.Matrix3D.create()
        if not mat:
            mat = matZero.copy()

        if not matZero.isEqualTo(mat):
            tmpMgr.transform(clone, mat)

        # BaseFeature
        baseFeats :adsk.fusion.BaseFeatures = comp.features.baseFeatures
        baseFeat = adsk.fusion.BaseFeature.cast(None)
        body = adsk.fusion.BRepBody.cast(None)

        try:
            baseFeat = baseFeats.add()
            baseFeat.startEdit()
            body = comp.bRepBodies.add(clone, baseFeat)
        except:
            pass
        finally:
            baseFeat.finishEdit()

        bodyList[0].baseFeature.deleteMe()
        thickFeat.deleteMe()

        return body


    @staticmethod
    def unitTest():
        import random
        ui = None

        try:
            app = adsk.core.Application.get()
            app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            ui = app.userInterface
            des :adsk.fusion.Design = app.activeProduct
            root :adsk.fusion.Component = des.rootComponent

            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            comps = [root, occ.component]

            pnt3D = adsk.core.Point3D

            for comp in comps:
                skt :adsk.fusion.Sketch = comp.sketches.add(comp.xYConstructionPlane)
                pnts :adsk.fusion.SketchPoints = skt.sketchPoints
                
                pntLst = []
                for _ in range(2):
                    pntLst.append(
                        pnts.add(
                            pnt3D.create(random.uniform(50, -50), random.uniform(50, -50), 0)))

                MobiusStripFactry.previewMobiusStrip(pntLst[0], 5, 23)
                app.activeViewport.refresh()
                adsk.doEvents()

                MobiusStripFactry.createMobiusStrip(pntLst[1], 1, 17, 0.05)
                app.activeViewport.refresh()
                adsk.doEvents()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def dumpMsg(msg :str):
    adsk.core.Application.get().userInterface.palettes.itemById('TextCommands').writeText(str(msg))