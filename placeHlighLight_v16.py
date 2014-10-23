#/// place hlighlight v016 ///#

### Description ###
'''place hlighlight v016
This function is to place a light according to
the position of highlight which is defined by user over mesh object
Tehre are 4 required input node/ object(
just select their transform node one by one, and then
press click'''


### bugs fix ###


### add ###
#01. support arnold light


import pymel.core as pm
import maya.OpenMaya as OM
import maya.OpenMayaUI as omui

from math import *
import pymel.core.datatypes as dt

ui_layout = {}
UI_name = []
item_list = []


pos_hLitPt = dt.Vector([0,0,0])

#// initilize
pm.scriptJob(ka=True)
pm.makeLive(none=True)
script_job_id = -1

def getActiveCam(*args):
    #// get active camera dag path
    dPath_cam = OM.MDagPath()
    omui.M3dView.active3dView().getCamera( dPath_cam )
    activeViewCamera = str(pm.PyNode(dPath_cam.fullPathName()).getParent())
    #print dPath_cam.Path_cam.partialPathName()
    
    return activeViewCamera


def placeHighLight(*args):
    ### UI setup 
    global UI_name
    UI_name = [ 'txtBtn_light', 'txtBtn_camera', 'txtBtn_object', 'txtBtn_HLitPoint', 'btn_placeHLit', 'chk_interaction' ]
    
    if pm.window( 'winPlaceHLit', exists=True ):
        pm.deleteUI( 'winPlaceHLit', window=True )
        
    ui_layout['window'] = pm.window( 'winPlaceHLit', title='Place Highlight', sizeable=False, h=100, w=250 )
    ui_layout['mainLayout'] = pm.columnLayout( columnAlign='left', columnAttach=['left', 0] )
    
    #// get active camera
    activeViewCamera = getActiveCam()
    
    '''loc_light_probe = pm.createNode('locator', name='light_probe')
    pm.lockNode(loc_light_probe, lock=False)'''

    #// sub layout
    #// sub1
    ui_layout['ui_sub1'] = pm.rowLayout(nc=2, cw=[(1, 210), (2, 40)], p=ui_layout['mainLayout'] )
    pm.textFieldButtonGrp( UI_name[0], label='Light: ', text='', buttonLabel='Pick',editable=False, buttonCommand='pickLit()', cw=[(1,50), (2,120), (3,40)], p=ui_layout['ui_sub1'] )
    pm.button( 'btn_sel_light' ,label='Sel', command=pm.Callback( doSelItem, UI_name[0] ), p=ui_layout['ui_sub1'] )
    
    #// sub2
    ui_layout['ui_sub2'] = pm.rowLayout(nc=2, cw=[(1, 210), (2, 40)], p=ui_layout['mainLayout'] )
    pm.textFieldButtonGrp( UI_name[1], label='Camera: ', text=activeViewCamera, buttonLabel='Pick', editable=False, buttonCommand='pickCam()', cw=[(1,50), (2,120), (3,40)], p=ui_layout['ui_sub2'] )
    pm.button( 'btn_sel_camera' ,label='Sel', command=pm.Callback( doSelItem, UI_name[1] ), p=ui_layout['ui_sub2'] )
    
    #// sub3
    ui_layout['ui_sub3'] = pm.rowLayout(nc=2, cw=[(1, 210), (2, 40)], p=ui_layout['mainLayout'] )
    pm.textFieldButtonGrp( UI_name[2], label='Object: ', text='', buttonLabel='Pick', editable=False, buttonCommand='pickTgtObj()', cw=[(1,50), (2,120), (3,40)], p=ui_layout['ui_sub3'] )
    pm.button( 'btn_sel_obj' ,label='Sel', command=pm.Callback( doSelItem, UI_name[2] ), p=ui_layout['ui_sub3'] )
    
    #// sub4
    ui_layout['ui_sub4'] = pm.rowLayout(nc=2, cw=[(1, 210), (2, 40)], p=ui_layout['mainLayout'] )    
    pm.textFieldButtonGrp( UI_name[3], label='Point: ', text='', buttonLabel='Pick', editable=False, buttonCommand='pickHLitPt()', cw=[(1,50), (2,120), (3,40)], p=ui_layout['ui_sub4'] )
    pm.button( 'btn_sel_point' ,label='Sel', command=pm.Callback( doSelItem, UI_name[3] ), p=ui_layout['ui_sub4'] )
    
    #// sub5
    ui_layout['ui_sub5'] = pm.rowLayout(nc=2, cw=[(1, 70), (2, 50)], p=ui_layout['mainLayout'] )
    pm.button( UI_name[4] ,label='Place Light!', command='doPlaceHLight()', p=ui_layout['ui_sub5'] )    
    pm.checkBox( UI_name[5], label='interactive mode', onCommand=pm.Callback( doInteractionON ), offCommand=pm.Callback( doInteractionOFF ), p=ui_layout['ui_sub5'] )
    
    
    pm.showWindow( ui_layout['window'] )
    
    pm.spaceLocator( name='light_probe' )
    pm.lockNode( 'light_probe', lock=True )
    pm.textFieldButtonGrp( 'txtBtn_HLitPoint', edit=True, text='light_probe' )
    
    #// clean make live and scriptJob after exit script
    pm.scriptJob( uiDeleted=[ ui_layout['window'], pm.Callback( flushScript ) ] )


### UI function
###

## select light and return its name

def pickLit(*args):
    light = pm.ls( sl=True )
    if ( len( light ) != 1 ):
        pm.confirmDialog( t='Error', message= 'Selct only One light!' , button = 'OK' )
        return 0

    if( light[0].getShape().nodeType() != 'aiAreaLight' ):
        if ( light[0].getShape().classification()[-1] != 'light' ):
            pm.confirmDialog( t='Error', message= 'Not a valid light!' , button = 'OK' )
            return 0
            
    pm.textFieldButtonGrp( 'txtBtn_light', edit=True, text=str( light[0] ) ) 
    return 1
    

## select Camera and return its name
def pickCam(*args):
    cam = []  
    cam = pm.ls( sl=True )
    if ( len( cam ) == 0 ):
        cam.append( getActiveCam() )
    
    else:
        if ( len( cam ) > 1 ):
            pm.confirmDialog( t='Error', message= 'Selct only One Camera!' , button = 'OK' )
            return 0;
        
        if ( pm.nodeType( cam[0].getShape() ) != 'camera' ):
            pm.confirmDialog( t='Error', message= 'Selct object is NOT Camera!' , button = 'OK' )
            return 0
       
    pm.textFieldButtonGrp( 'txtBtn_camera', edit=True, text=str( cam[0] ) )
    return 1
    

## select Target Object and return its name
def pickTgtObj(*args):
    tgtObj = pm.ls( sl=True )
    
    if ( len( tgtObj) != 1 ):
        pm.confirmDialog( t='Error', message= 'Selct only One Mesh Object!' , button = 'OK' )
        return 0
    
    if ( pm.nodeType( tgtObj[0].getShape() ) != 'mesh' ):
        pm.confirmDialog( t='Error', message= 'Selct object is NOT Mesh' , button = 'OK' )
        return 0
       
    pm.textFieldButtonGrp( 'txtBtn_object', edit=True, text=str( tgtObj[0] ) )
    
    #// initialize make live objet
    pm.makeLive( none=True )
    pm.makeLive( str(tgtObj[0]) )
    
    return 1
    
    
## select reference point and return its name
def pickHLitPt(*args):
    hLitPt = pm.ls( sl=True )
    
    if ( len( hLitPt) != 1 ):
        pm.confirmDialog( t='Error', message= 'Selct one reference point!' , button = 'OK' )
        return 0;
       
    pm.textFieldButtonGrp( 'txtBtn_HLitPoint', edit=True, text=str( hLitPt[0] ) )
    
    #// store the initial point position
    global pos_hLitPt
    pos_hLitPt = pm.ls(sl=True)[0].getTranslation(space='world')
    
    return 1
    
    
def doSelItem( name ):
    _obj = pm.textFieldButtonGrp( name, query=True, text=True )
    if( pm.ls(_obj) == [] ):
        print 'no object selected!'
        return 0
        
    pm.select(_obj, r=True )
    return 1


### function declaration
###
## get the closet WORLD-Space Closet point and Normal
def getClosetPointAndNormal( refPt, mesh ):
    ## in order to get the dagPath to MFnMesh, we need to get MSelectionList first...
    ## MGlobal::getActiveSelectionList()
    pm.select(clear=True)
    OM.MGlobal.selectByName( mesh );
    sList_mesh = OM.MSelectionList();
    OM.MGlobal.getActiveSelectionList( sList_mesh );
    
    ## get dagPath
    dPath_mesh = OM.MDagPath();
    sList_mesh.getDagPath( 0, dPath_mesh );
    dPath_mesh.extendToShape();

    
    ## get closet face ID to the highlight point
    ##
    meshFn = OM.MFnMesh(dPath_mesh);
    pos_refPt = dt.Vector( pm.PyNode( refPt ).getTranslation( space='world' ) );
    
    ## parameters for getClosestPointAndNormal()
    toThisPoint = OM.MPoint( pos_refPt[0], pos_refPt[1], pos_refPt[2], 1.0 );
    theClosestPoint = OM.MPoint();
    theNormal = OM.MVector();
    space = OM.MSpace.kWorld;
    
    util = OM.MScriptUtil();
    ptr_FaceID = util.asIntPtr();
    
    meshFn.getClosestPointAndNormal( toThisPoint,
                            		 theClosestPoint,
                            		 theNormal,
                            		 space,
                            		 ptr_FaceID )
                            		                         		 
    ## return util.getInt( ptr_FaceID );
    out = [ theClosestPoint, theNormal, util.getInt( ptr_FaceID ) ]
    
    return out;


## get Reflective vector from Vector( camera-->face center )
def getReflectVector(incidentVec, axisNormal):   
    #// R = V - 2(d dot n )*n
    vec_refl = incidentVec - 2 * ( incidentVec.dot(axisNormal) ) * axisNormal
    vec_refl.normalize()
    return vec_refl


## To create a World Matrix by an input vector and pivot
def vecToWorldMatrix( pivot, reflectVec):
    ## conver the face normal from local to Wrold
    ## Z-axis should be mul -1.0 to follow the right-hand coordinate rule
	## switch Y-axis and Z-axis because the light node is Z-up
	
    axis_X = dt.Vector(1, 1, -1*( reflectVec[0] + reflectVec[1]) / reflectVec[2] )
    axis_X.normalize()
    axis_Y = reflectVec
    axis_Z = axis_X.cross(axis_Y)
    axis_Z.normalize()
    
    #// w-space face TM
    new_face_TM = dt.TransformationMatrix( axis_X, -1 * axis_Z, axis_Y, pivot )
    
    #// o-space lgiht TM  
    currlit_local_TM = dt.TransformationMatrix( pm.PyNode( item_list[0]).getTransformation() )
    
    #// if object has a parent, get the inverse PARENT-space TM of light
    if( pm.PyNode( item_list[0]).getParent() != None ):
        print 'YES'
        currlit_parent_local_inv_TM = dt.TransformationMatrix( pm.PyNode( item_list[0]).getParent().getTransformation() ).asMatrixInverse()
    
        #// convert w-space face TM to PARENT-space TM of light
        result_wroldTM = new_face_TM * currlit_parent_local_inv_TM
    
    else:
        result_wroldTM = new_face_TM
    
    #// PARENT-space TM of light      
    return result_wroldTM
    

def tweakLightTM( currLit, currCam, tgtObj, hLitPt ):
    ## get the Closet point and Normal
    listVec = []
    listVec = getClosetPointAndNormal( hLitPt, tgtObj )
    
    
    hitFacePoint = dt.Vector( listVec[0] )
    hitFaceNormal = dt.Vector( listVec[1] )
    
    
    ## get Vector from camrea -> face
    camPos = dt.Vector( pm.PyNode( currCam ).getTranslation( space='world' ) )
    v_camToFace = hitFacePoint - camPos
    v_camToFace.normalize()
   
    #// get reflective vector
    reflectVec = getReflectVector( v_camToFace, hitFaceNormal )
    
    #// create a W-matrix
    face_TM = vecToWorldMatrix( hitFacePoint, reflectVec )
        
    #// store original distance between Light and point  
    pos_currLit = pm.PyNode( currLit ).getTranslation( space='world' )

    global pos_hLitPt
    dist_litToPt = dt.Vector( pos_currLit - pos_hLitPt ).length()
    pos_hLitPt = pm.PyNode( hLitPt ).getTranslation( space='world' )
    
    scale_currlit = pm.PyNode( currLit ).getScale()
    #rot_currlit = pm.PyNode( currLit ).getRotation(space='object')
    
    #// apply the W-matrix and offest a distance
    pm.PyNode( currLit ).setTransformation( face_TM )
    
    #// resotre to the original relative position, Z-rot, and scale
    pm.move( currLit, dist_litToPt, z=True, relative=True, objectSpace=True, worldSpaceDistance=True )
    #pm.PyNode( currLit ).rz.set( rot_currlit[2] )
    pm.PyNode( currLit ).setScale( scale_currlit )
    
    ## clear selection
    OM.MGlobal.clearSelectionList();
        

# // check if items are valid
def checkItems( *args ):
    global item_list
    item_list = []
    
    _light = pm.textFieldButtonGrp( 'txtBtn_light', query=True, text=True )
    _camera = pm.textFieldButtonGrp( 'txtBtn_camera', query=True, text=True )
    _object = pm.textFieldButtonGrp( 'txtBtn_object', query=True, text=True )
    _point = pm.textFieldButtonGrp( 'txtBtn_HLitPoint', query=True, text=True )
    item_list = [ _light, _camera, _object, _point ]
    

    for index, item in enumerate(item_list, 1):
        if( item == '' ):
            pm.confirmDialog( t='Error', message= ( 'Please specify item ' + str(index) ) , button = 'OK' )
            return 0
        if( len(pm.ls(item)) == 0 ):
            pm.confirmDialog( t='Error', message= ( '%s is not existing in scene!' % item ) , button = 'OK' )
            return 0
    
    #// all items are valid !
    return 1
            

def doPlaceHLight(*args):
    if( checkItems() == 0 ):
        return 0
        
    #// item_list = [ _light, _camera, _object, _point ]    
    global item_list
    print item_list
    
    hLitPt = item_list[3]
    tweakLightTM( item_list[0], item_list[1], item_list[2], item_list[3] )
    pm.select(hLitPt, replace=True)
    
    return 1

#// UI lock ON/ OFF
def ui_enable( btn=False, status=True ):
    global UI_name
    for ui in UI_name[:-2]:
        pm.textFieldButtonGrp( ui, edit=True, en=status )
    
    #// check if inclde button
    if( btn ):
        pm.button( UI_name[-2], edit=True, en=status )
    
    return 1


def doInteractionON( *args ):
    print 'interaction ON'
    
    #// if cehckItems() is not valid, interactive mode doesn't work 
    if( checkItems() == 0 ):
        pm.checkBox( 'chk_interaction', edit=True, value=False )
        return 0
    
    #// lock UI to grey
    ui_enable( True, False )
    
    global item_list
    hLitPt = item_list[3]
    
    global script_job_id
    script_job_id = pm.scriptJob( attributeChange=[ (hLitPt + '.translate'), pm.Callback( doPlaceHLight ) ] )
    
    return 1
    
    
def doInteractionOFF( *args ):
    print 'interaction OFF'
    
    #// unlock UI
    ui_enable( True, True )
    
    global script_job_id
    if( script_job_id == -1 ):
        return 0
    
    print 'script_job_id:', script_job_id
    pm.scriptJob( kill=script_job_id, force=True )
    print 'delete script_job_id:', script_job_id
    
    script_job_id = -1  
        
    return 1
    

def flushScript( *args ):
    if( script_job_id != -1 ):
        pm.scriptJob( kill=script_job_id, force=True )
        
    pm.lockNode( 'light_probe', lock=False )
    pm.delete('light_probe')
        
    pm.makeLive(none=True)


    
         
placeHighLight()
