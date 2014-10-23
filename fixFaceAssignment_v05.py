#/// fix face assignment v05 ///#

### Description ###
## This script can fix face assignment( component shader ) to avoid render layer broken.
##It can automatically repair and restore objects' shader assignment for each render layer.

## feel free to mail me if you have any comments and suggestions
## Thanks! :)
## Kenzie Chen | kenziec@themill.com  


import pymel.core as pm

UI_name = []
ui_layout = {}

def ui_fixComponentShading(*args):
    ### UI setup
    global UI_name

    UI_name = [ 'chk_find', 'chk_fix', 'chk_layer', 'btn_run' ]

    if pm.window( 'fix_component_shading', exists=True ):
        pm.deleteUI( 'fix_component_shading', window=True )
        
    ui_layout['window'] = pm.window( 'fix_component_shading', title='Fix Component Shading', sizeable=False, h=200, w=200 )
    ui_layout['mainLayout'] = pm.columnLayout( columnAlign='left', columnAttach=['left', 0] )

    pm.checkBox( UI_name[0], label=' Find Component Shading Object', value=1, w=200, p=ui_layout['mainLayout'] )
    pm.checkBox( UI_name[1], label=' Fix Component Shading Object', w=200, p=ui_layout['mainLayout'] )
    pm.checkBox( UI_name[2], label=' Fix Ecah Render Layer', w=200, p=ui_layout['mainLayout'] )

    ui_layout['ui_sub1'] = pm.formLayout(p=ui_layout['mainLayout'] )
    btn = pm.button( UI_name[3] ,label=' Execute !', command=pm.Callback( doExecution ), w=100, p=ui_layout['ui_sub1'] )
    pm.formLayout( ui_layout['ui_sub1'], e=True, attachForm=[ (btn, 'left', 50 ) ] )
    
    pm.separator( h=8, w=200, style='single', p=ui_layout['mainLayout'] )
    
    ui_layout['ui_sub2'] = pm.columnLayout(p=ui_layout['mainLayout'] )
    pm.text(label=' --- This script will keep the material \n in the CURRENT render layer, so \n it better to run it in MASTER layer! --- ', bgc=[0.05, 0.05, 0.05], align='left', p=ui_layout['ui_sub2'] )
    
    pm.showWindow( ui_layout['window'] )
    


#// select object with component shading
def findErrorShape(*args):
    error_shape = []
    sel = pm.ls(sl=True, dag=True, type='mesh')
    for shp in sel:
        SG_list = pm.listConnections(shp, type='shadingEngine')  
        #// print SG_list
        #// test if shape has a SG
        if( SG_list != None ):
            #// test if it's a component shading !
            if( len(SG_list) > 1 ):
                error_shape.append(shp)
    print error_shape
    
    pm.select(cl=True)
    pm.select(error_shape)
    
    return 1


#// automatically remove domponent shading
#// NOTE!!!..this way is to assign the FIRST shadingEngine as a main shader
def fixComponentShading(*args):
    sel = pm.ls(sl=True, dag=True, type='mesh')        
    for shp in sel:
        SG_list = pm.listConnections(shp, t='shadingEngine')
        #print SG_list
        
        if( SG_list == None ):
            continue
         
        if( len(SG_list) < 1 ):
            SG_list.append('initialShadingGroup')
        
        main_SG = SG_list[0]
        #print main_SG
        all_connections = pm.listConnections( shp, c=1, p=1, type='shadingEngine' )
        for connection in all_connections:
            pm.delete( connection, icn=True)
        
        pm.sets( main_SG,edit=True, forceElement=shp )
        
    return 1


def collectShaderInfoInLayer():
    sel = pm.ls(sl=True, dag=True, type='mesh')        
       
    shader_info_all_layers = []
    
    for renderlayer in pm.ls(type='renderLayer'):
        pm.editRenderLayerGlobals( currentRenderLayer=renderlayer )
        
        #// shader_info_layer stores the info for each seleted objs in CURRENT layer
        #// flush content of shader_info_layer 
        shader_info_layer = []
        for mesh in sel:
            SG_list = pm.listConnections(mesh, t='shadingEngine')
            #print SG_list
            
            if( SG_list == None ):
                continue
             
            if( len(SG_list) < 1 ):
                SG_list.append('initialShadingGroup')
            
            #// store mesh & material in CURRENT layer
            shader_info_layer.append( ( mesh, SG_list[0] ) )
            
        shader_info_all_layers.append( ( renderlayer, shader_info_layer ) )
        
    pm.editRenderLayerGlobals( currentRenderLayer='defaultRenderLayer' )          
    return shader_info_all_layers


#// if you want to find and select objects with component shading, run the findErrorShape() ONLY and remark fixComponentShading() with ## ahead
#// if you want to fix the shading network, run both findErrorShape() and fixComponentShading()
def doExecution(*args):
    is_find = pm.checkBox( UI_name[0], q=True, value=True )
    is_fix = pm.checkBox( UI_name[1], q=True, value=True )
    is_fixLayer = pm.checkBox( UI_name[2], q=True, value=True )
    
    shader_info_all_layers = []   
    
    if( is_find ):
        findErrorShape()
    
    if( is_fixLayer ):
        #// collect shaders info in each layer
        shader_info_all_layers = collectShaderInfoInLayer()                        

    if( is_fix ):
        fixComponentShading()
        
        if( is_fixLayer ):
            for shd_layer in shader_info_all_layers:
                
                #// switch to a specified layer
                curr_layer = shd_layer[0]
                pm.editRenderLayerGlobals( currentRenderLayer=curr_layer )
                
                #// parsing string for mesh & shader from list
                #// assign shader to mesh from list
                for shd in shd_layer[1]:                 
                    obj = shd[0]
                    SG = shd[1]
                    pm.sets( SG, edit=True, forceElement=obj )
                    
    pm.editRenderLayerGlobals( currentRenderLayer='defaultRenderLayer' )                          
    return 1

def main(*args):
    ui_fixComponentShading(*args)

        
main()



    
