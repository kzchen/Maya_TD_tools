## A small tool with a button UI in the Hpershade window to grah selected objects' material in hypershade without break current shading-network layout.
## Kenzie Chen | kzchen@gmail.com

import pymel.core as pm
import maya.mel as mel


panel_hyperShd = []
#// graph & add selected material
def addMaterialinGraph(*args):
    
    sel_shapes = pm.ls( sl=True, dag=True, type='shape' )
    
    global panel_hyperShd
    for shape in sel_shapes:
        if( not( pm.nodeType(shape) == 'mesh' or pm.nodeType(shape) == 'nurbsSurface' ) ):
            pm.confirmDialog( t="Error", message= " selected objects are not mesh or nurbsSurface", icon='critical' )
            
        shdGrp = shape.outputs(type='shadingEngine')
        for sg in shdGrp:
            shader = pm.ls( sg.inputs(), materials=1 )
            pm.select(shader)
            mel.eval( "hyperShadePanelGraphCommand( \"%s\", \"addSelected\" )"  % str(panel_hyperShd) )
            
            pm.select(shape.getParent())
            
            
def main():
    global panel_hyperShd
    
    #// collect hyperShade Window
    win_hyperShd = [ win for win in pm.lsUI( type='window' ) if win.find('hyperShade') != -1 ]
    
    #// test if hyershade is open
    if len(win_hyperShd) == 0:
        pm.runtime.HypershadeWindow()
    
    panel_hyperShd = pm.getPanel( scriptType='hyperShadePanel' )[0]
    print panel_hyperShd
    
    #// add button in hyperShade 
    pm.setParent( panel_hyperShd + '|mainForm|hyperShadeToolbarForm' )
    if( not(pm.button( 'grab', exists=True )) ):
         pm.button('grab', bgc=[0.5,0.5,0], c=pm.Callback( addMaterialinGraph ),  width=50 )
         
main()
