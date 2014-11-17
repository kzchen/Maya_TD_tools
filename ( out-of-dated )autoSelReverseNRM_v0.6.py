'''
UPDATE --This is tool is obsolete. Maya has had a built-in tool to do the same thing more efficiently--

auto select reversed face beta 0.6
This is a script to find and select face with invert noraml
by Kenzie Chen | kenzie@gmail.com
'''



import pymel.core as pm
import maya.OpenMaya as OM
import math
import pymel.core.datatypes as dt

uiLayout = {}

## get face center function from maya station ##
def getFaceCenter():
    faceCenter = []

    selection = OM.MSelectionList()
    OM.MGlobal.getActiveSelectionList(selection)

    iter = OM.MItSelectionList (selection, OM.MFn.kMeshPolygonComponent)

    while not iter.isDone():
        
        dagPath = OM.MDagPath()
        component = OM.MObject()

        iter.getDagPath(dagPath, component)

        polyIter = OM.MItMeshPolygon(dagPath, component)
        
        while not polyIter.isDone():
            
            i = 0
            i = polyIter.index()

            center = OM.MPoint
            center = polyIter.center(OM.MSpace.kWorld)
            point = [0.0,0.0,0.0]
            point[0] = center.x
            point[1] = center.y
            point[2] = center.z
            faceCenter += point
            
            polyIter.next()
            
        iter.next()
       
    return dt.Vector(faceCenter)


# test if an input point is inside an object by usibg allIntersections
# the argument "shape" must be a shape node     
def isPointInsdeObject( shape, point, rayDir=( 0.0, 0.0, 1.0 ) ):
    OM.MGlobal.selectByName(shape,OM.MGlobal.kReplaceList)
    sList = OM.MSelectionList()
    OM.MGlobal.getActiveSelectionList( sList )
        
    dagPath = OM.MDagPath()
    sList.getDagPath( 0, dagPath )
   
    fnMesh = OM.MFnMesh( dagPath )
    
    raySource = OM.MFloatPoint( *point )
    rayDirection = OM.MFloatVector( *rayDir )
    faceIds = None
    triIds = None
    idsSorted = False
    space = OM.MSpace.kWorld
    maxParam = 99999
    testBothDirections = False
    accelParams = None
    sortHits = True
    hitPoints = OM.MFloatPointArray()
    hitRayParams = OM.MFloatArray()
    hitFaces = OM.MIntArray()
    hitTris = None
    hitBarys1 = None
    hitBarys2 = None
    tolerance = 1e-4
    
    # original API function
    '''
    bool MFnMesh::allIntersections 	( 	const MFloatPoint &  	raySource,
		const MFloatVector &  	rayDirection,
		const MIntArray *  	faceIds,
		const MIntArray *  	triIds,
		bool  	idsSorted,
		MSpace::Space  	space,
		float  	maxParam,
		bool  	testBothDirections,
		MMeshIsectAccelParams *  	accelParams,
		bool  	sortHits,
		MFloatPointArray &  	hitPoints,
		MFloatArray *  	hitRayParams,
		MIntArray *  	hitFaces,
		MIntArray *  	hitTriangles,
		MFloatArray *  	hitBary1s,
		MFloatArray *  	hitBary2s,
		float  	tolerance = 1e-6,
		MStatus *  	ReturnStatus = NULL	 
	)''' 	
   
    isHit = fnMesh.allIntersections(raySource, rayDirection, faceIds, triIds, idsSorted, space, maxParam, testBothDirections, accelParams, sortHits, hitPoints, hitRayParams, hitFaces, hitTris, hitBarys1, hitBarys2, tolerance)
    result = len(hitFaces) % 2
    
    return result
    

## select face with invert normal
def doSelInvNRMFace( *args ):
    print "start!"
    # pm.delete( pm.ls(sl=True), ch=1 )
    selShape = pm.ls( sl=True, dag=True, type='shape' )

        
    faceInvertNRM = []
    
    offset = pm.floatFieldGrp( 'valOffset', q=True, value1=True )
    _x = pm.floatFieldGrp( 'valDir', q=True, value1=True )
    _y = pm.floatFieldGrp( 'valDir', q=True, value2=True )
    _z = pm.floatFieldGrp( 'valDir', q=True, value3=True )
    testRayDir = dt.Vector(_x, _y, _z)

    for shape in selShape:
        ## test if selected object type is "mesh"
        if( pm.nodeType(shape) != 'mesh' ):
            pm.confirmDialog( t="Error", message= shape.getParent() + " is not a mesh object! ", icon='critical' )
            return 0
            
        #pm.delete( shape, ch=1 )
        maxValue = float(len(shape.faces))
       
        pm.progressWindow( title='normal test Calculation', progress=0, maxValue=maxValue, isInterruptable=True, status='calculating: 0%' )
        for i, face in enumerate(shape.faces):
            try:
                pm.progressWindow( edit=True, progress=i, status=('calculating: ' + str( math.ceil( 100 * i/ maxValue) ) + '%') )
                
                ## ESC to cancel progress windows
                if pm.progressWindow( query=True, isCancelled=True ):
                    pm.progressWindow(endProgress=1)
                    break
                           
                curr_face = face
                obj_faces = shape.faces
                del_tmp_obj = [] 
                #// Test if face is NGon   
                if face.numTriangles() > 2:
                    tmp_obj = pm.duplicate( selShape, rr=True )[0]
                    del_face_id = [ id for id in range( len(obj_faces) ) if id != i  ]
                    pm.delete( tmp_obj.getShape().f[del_face_id] )
                    
                    #// triangulate N-Gon
                    pm.polyTriangulate( tmp_obj, ch=False )
                    
                    #//
                    curr_face = tmp_obj.getShape().f[0]
                    
                    #//
                    del_tmp_obj.append(tmp_obj)
                    
                    
                    
                pm.select( curr_face, r=1) 
                cenPos = getFaceCenter()
    
                faceNRM = curr_face.getNormal('world')
                offsetPos = cenPos + faceNRM * offset
                #testObj = pm.polySphere( r=5, sx=4, sy=4 )
                #testObj[0].setTranslation(offsetPos)
                
                ## test if point inside object
                testInside = isPointInsdeObject( shape, offsetPos, testRayDir )
                pm.delete(del_tmp_obj)
                
                if( testInside ):
                    faceInvertNRM.append( face )
            except:
                continue
   
    pm.progressWindow(endProgress=1) 
    pm.select( faceInvertNRM, r=1 )    
        
    return 1
  

def main( *args ): 
    if( pm.window('selInvertNormalFace', exists=True) ):
       pm.deleteUI('selInvertNormalFace') 
                  
    uiLayout['window'] = pm.window('selInvertNormalFace', menuBar=True, title='select face with invert normal', sizeable=False, h=60, w=180)
    uiLayout['mainLayout'] = pm.columnLayout(columnAlign='left', columnAttach=['left', 0] )
    
    pm.floatFieldGrp( 'valDir', numberOfFields=3, label='Direction:', value1=0.0, value2=1.0, value3=0.0, cw4=[ 50, 30, 30, 30 ], parent=uiLayout['mainLayout'] )
      
    uiLayout['ui_sub1'] = pm.rowColumnLayout( w=180, nc=2, cw=[(1, 85), ( 2,80 ) ], parent=uiLayout['mainLayout'] )
    pm.floatFieldGrp( 'valOffset', numberOfFields=1, label='Offset:', value1=0.5, cw2=[ 50, 30 ], parent=uiLayout['ui_sub1'] )
    pm.button( label=' Select Face!  ', ebg=True, c=doSelInvNRMFace, parent=uiLayout['ui_sub1'] )   
    
    pm.showWindow( uiLayout['window'] )
 
main()
