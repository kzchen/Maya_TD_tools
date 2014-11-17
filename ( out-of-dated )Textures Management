import maya.cmds as cmds;
import os.path as os;
import shutil;
import random as rand;
from math import *;

'''
This script is to deal with several MAPS management, including
To find missing maps
To relink all missing maps to an specified directory
To copy/move all scene maps to an specified directory
To relink all scene maps to an specified directory
'''

def mapExplorerUI():
    if cmds.window("mapExplorer", exists = True): cmds.deleteUI("mapExplorer", window = True);
    
    winName = cmds.window("mapExplorer", title = "Maps Explorer");
    form = cmds.formLayout(numberOfDivisions=50);
    
    cmds.textScrollList( "mapsField", numberOfRows=8, allowMultiSelection=True  )
    cmds.button("btnListAllMap", width= 150, height = 25,\
                label = "Show All maps", command = "showAllMap()");
    cmds.button("btnListMissMap", width= 150, height = 25,\
                label = "Show missing maps", command = "showMissMap()");
    cmds.button("btnRelinkMissMap",  width= 150, height = 25,\
                label = "Relink missing maps", command = "relinkMissingMap()");
    cmds.button("btnCollectMap",  width= 150, height = 25,\
                label = "Collect scene maps", command = "collectMap()");
    cmds.checkBox( "chkRelink", label="relocate" );
    cmds.checkBox( "chkMove", label="move" );
    
    cmds.formLayout( form, edit=True,\
                     attachForm = [("mapsField", "top", 1),\
                                   ("mapsField", "bottom", 100),\
                                   ("mapsField", "left", 1),\
                                   ("mapsField", "right", 1),\
                                   ("btnListMissMap", "right", 1),\
                                   ("btnRelinkMissMap", "left", 1),\
                                   ("btnCollectMap", "left", 1)],\
                    attachControl = [("btnListAllMap", "top", 5, "mapsField"),\
                                     ("btnListMissMap", "top", 5, "mapsField"),\
                                     ("btnListMissMap", "left", 1, "btnListAllMap"),\
                                     ("btnRelinkMissMap", "top", 5, "btnListAllMap"),\
                                     ("btnCollectMap", "top", 5, "btnRelinkMissMap"),\
                                     ("chkRelink","top", 15, "btnRelinkMissMap"),\
                                     ("chkRelink","left", 5, "btnCollectMap"),\
                                     ("chkMove", "top", 1, "btnRelinkMissMap"),\
                                     ("chkMove", "left", 5, "btnCollectMap")] );       
    cmds.showWindow(winName);
    initialize();

## to intilize required variables and process    
def initialize():
    global _mapFiles;
    global _mapPath;
    global _missMapFiles;
    global _missMapPath;
    
    ## clean up cintents
    _mapFiles = [];
    _mapPath = []; 
    _missMapFiles = [];
    _missMapPath = [];
    
    ## to get all map paths in scene
    _mapFiles = cmds.ls( type="file" );
    for i in range( 0, len(_mapFiles) ):
        _mapPath[len(_mapPath):] = [ cmds.getAttr( str(_mapFiles[i])+".fileTextureName" ) ];
      
    ## clean textfield content    
    cmds.textScrollList( "mapsField", edit=True, removeAll=True );

## To list all maps' paths     
def showAllMap():
    initialize();
    cmds.textScrollList( "mapsField", edit=True,\
                         append=[ _mapPath[j] for j in range(0, len(_mapPath)) ] );

## To list all missing maps                         
def showMissMap():    
    initialize();
    ## check if each map is existing or not
    for i in range(0, len(_mapPath)):
        if( os.exists(_mapPath[i])!=True ):
            _missMapFiles[len(_missMapFiles):] = [ _mapFiles[i] ];
            _missMapPath[len(_missMapPath):] = [ _mapPath[i] ];
    
    if ( len(_missMapPath)==0 ):
        cmds.confirmDialog( t="Warning", message= "No missing maps in scene!" , button = "OK" );
        return;
    else:
        cmds.textScrollList( "mapsField", edit=True,\
                             append=[ _missMapPath[j] for j in range(0, len(_missMapPath)) ] );
                             
## re-assign all missing maps to a new path                         
def relinkMissingMap(): 
    if( len(_missMapPath)==0):
        cmds.confirmDialog( t="Warning", message= "No missing maps in lists!" , button = "OK" );
        return;
        
    ## return the user defined path to the callback function "setMissMapPat"
    cmds.fileBrowserDialog( mode=4, dialogStyle = 2, fileCommand=setMissMapPath,\
                            actionName="Set new directory" );

def collectMap(): 
    initialize();
    _newMapPath = "";   
    ## return the user defined path to the callback function "transMapsToDict"
    cmds.fileBrowserDialog( mode=4, dialogStyle = 2, fileCommand=transMapsToDict,\
                            actionName="Select new path" );

def setMissMapPath( _path, _type):
    _missMapName = [];      
    for i in range(0, len(_missMapPath)):
        ##retrieve file name ONLY
        _missMapName[len(_missMapName):] = [ _missMapPath[i].split("/")[-1] ];
        cmds.setAttr( str(_missMapFiles[i])+".fileTextureName",\
                    (_path + "/" + _missMapName[i]), type="string" );
                    
    cmds.confirmDialog( t="Relink missing maps", message= "Done!" , button = "OK" );

def transMapsToDict( _path, _type):
    print len(_mapPath);
    _isMove = cmds.checkBox( "chkMove", query=True, value=True );     
    _isRelink = cmds.checkBox( "chkRelink", query=True, value=True );

    for i in range(0, len(_mapPath)):
        if(_isMove): shutil.move( _mapPath[i], _path );     ## move files to new path  
        else: shutil.copy2( _mapPath[i], _path );       ## copy files to new path  
    
    _mapName = [];
    if(_isRelink):
        for j in range(0, len(_mapPath)):
            ##retrieve file name ONLY
            _mapName[len(_mapName):] = [ _mapPath[j].split("/")[-1] ];
            print (_path + "/" + _mapName[j]);
            cmds.setAttr( str(_mapFiles[j])+".fileTextureName",\
                        (_path + "/" + _mapName[j]), type="string" );
    
    cmds.confirmDialog( t="Copy all maps", message= "Complete!" , button = "OK" );
    
mapExplorerUI();
