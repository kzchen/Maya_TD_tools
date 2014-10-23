import pymel.core as pm
import maya.OpenMaya as OM
import pymel.core.datatypes as dt

UI_name = []
ui_layout = {}

def main(*args):
    ### UI setup
    global UI_name 
    UI_name = [ 'txtBtn_object', 'txtBtn_mesh', 'ray_dir', 'txtBtn_run' ]

    if pm.window( 'obj_deform', exists=True ):
        pm.deleteUI( 'obj_deform', window=True )
        
    ui_layout['window'] = pm.window( 'obj_deform', title='Object Deform on Mesh', sizeable=False, h=150, w=200 )
    ui_layout['mainLayout'] = pm.columnLayout( columnAlign='left', columnAttach=['left', 0] )

    pm.textFieldButtonGrp( UI_name[0], label='object: ', text='', buttonLabel='  Pick  ', buttonCommand=pm.Callback( doPickObj, UI_name[0] ), cw=[(1,50), (2,150), (3,50)], p=ui_layout['mainLayout'] )
    pm.textFieldButtonGrp( UI_name[1], label='mesh: ', text='', buttonLabel='  Pick  ', buttonCommand=pm.Callback( doPickObj, UI_name[1] ), cw=[(1,50), (2,150), (3,50)], p=ui_layout['mainLayout'] )
    
    pm.floatFieldGrp( UI_name[2], numberOfFields=3, label='project direction:', value1=0.0, value2=-1.0, value3=0.0, cw=[(1,90), (2,50), (3,50), (4,50)], parent=ui_layout['mainLayout'] )


    ui_layout['ui_sub1'] = pm.rowLayout(nc=1, p=ui_layout['mainLayout'] )
    pm.button( UI_name[3] ,label=' Deform Object !', command=pm.Callback( doDeform ), align='center', p=ui_layout['ui_sub1'] )
    
    pm.showWindow( ui_layout['window'] )
    

def doPickObj( ui_name ):
    obj = pm.ls( sl=True )
    if ( len( obj ) != 1 ):
        pm.confirmDialog( t='Error', message= 'Selct only One object!' , button = 'OK' )
        return 0
                
    if ( pm.nodeType( obj[0].getShape() ) != 'mesh' ):
        pm.confirmDialog( t='Error', message= 'Selct object type is NOT MESH!' , button = 'OK' )
        return 0;

    pm.textFieldButtonGrp( ui_name, edit=True, text=str( obj[0] ) )
    return 1
    
       
    
def getClosetPointAndNormal( src_point, mesh, rayDir=( 0.0, -1.0, 0.0 ) ):
    ## in order to get the dagPath to MFnMesh, we need to get MSelectionList first...
    ## MGlobal::getActiveSelectionList()
    pm.select(clear=True)
    OM.MGlobal.selectByName( mesh, OM.MGlobal.kReplaceList );
    sList_mesh = OM.MSelectionList();
    OM.MGlobal.getActiveSelectionList( sList_mesh );
    
    ## get dagPath
    dPath_mesh = OM.MDagPath();
    sList_mesh.getDagPath( 0, dPath_mesh );
    #dPath_mesh.extendToShape();

    
    ## get closet face ID to the highlight point
    ##
    meshFn = OM.MFnMesh(dPath_mesh)
    #point = OM.MPoint()
    #ray = OM.MPoint()
   
    #point = dt.Vector( src_point )
    #ray = dt.Vector(rayDir)
    
    ## parameters for getClosestPointAndNormal()
    print "start!"
    raySource = OM.MFloatPoint( *src_point )
    rayDirection = OM.MFloatVector( *rayDir )
    faceIds = None
    triIds = None
    idsSorted = False
    space = OM.MSpace.kWorld
    maxParam = 99999
    testBothDirections = False
    accelParams = None
    hitPoint = OM.MFloatPoint()
    hitRayParams = None
    hitFaces = OM.MScriptUtil().asIntPtr()
    hitTris = None
    hitBarys1 = None
    hitBarys2 = None
    tolerance = 1e-4
    print "end!"
    '''
    bool MFnMesh::closestIntersection(	     const MFloatPoint & 	raySource,
                                            const MFloatVector & 	rayDirection,
                                            const MIntArray * 	faceIds,
                                            const MIntArray * 	triIds,
                                            bool 	idsSorted,
                                            MSpace::Space 	space,
                                            float 	maxParam,
                                            bool 	testBothDirections,
                                            MMeshIsectAccelParams * 	accelParams,
                                            MFloatPoint & 	hitPoint,
                                            float * 	hitRayParam,
                                            int * 	hitFace,
                                            int * 	hitTriangle,
                                            float * 	hitBary1,
                                            float * 	hitBary2,
                                            float 	tolerance = 1e-6,
                                            MStatus * 	ReturnStatus = NULL	 )
    '''           		                         		 
    isHit = meshFn.closestIntersection(raySource, rayDirection, faceIds, triIds, idsSorted, space, maxParam, testBothDirections, accelParams, hitPoint, hitRayParams, hitFaces, hitTris, hitBarys1, hitBarys2, tolerance )
    if( isHit ):
        return ( hitPoint.x, hitPoint.y, hitPoint.z )
    else:
        return src_point
    
def doDeform(*args):
    global UI_name
    deform_obj = pm.textFieldButtonGrp( UI_name[0], query=True, text=True )
    target_mesh = pm.textFieldButtonGrp( UI_name[1], query=True, text=True )
    
    if( len(deform_obj) == 0 or len(target_mesh) == 0 ):
        pm.confirmDialog( t='Error', message= 'some input field is empty!' , button = 'OK' )
    
    deform_obj_shp = pm.PyNode(deform_obj).getShape()
    target_mesh_shp = pm.PyNode(target_mesh).getShape()
    
    _x = pm.floatFieldGrp( UI_name[2], q=True, value1=True )
    _y = pm.floatFieldGrp( UI_name[2], q=True, value2=True )
    _z = pm.floatFieldGrp( UI_name[2], q=True, value3=True )
    ray_dir = dt.Vector(_x, _y, _z)
    
    print ray_dir
    
    for vtx in deform_obj_shp.vtx:
       v_pos = vtx.getPosition(space='world')
       ray_pos = getClosetPointAndNormal( v_pos, target_mesh_shp, ray_dir )
       vtx.setPosition( ray_pos,space='world' )
        
main()
    
