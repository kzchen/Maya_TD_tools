'''
   Module 6
   This script is to reduce mesh by distance from camera 
'''

import maya.cmds as mc
from math import sqrt

def sortByValue(inDict):        # sort Dict items by value
    _items = inDict.items()
    _rotateItems = [ [i[1],i[0]] for i in _items ]        # rotate key and values for each item
    _rotateItems.sort()        # sort by value
    return [ _rotateItems[i][1] for i in range(0, len(_rotateItems)) ]        #returen key

selObjVal = {}
camPos = mc.getAttr("camera1.translate")

for i in mc.ls(sl=True):
    objPos = mc.getAttr( i + ".translate" )
    
    # assign the value of distance form camera for each obj to key in selObjSel{}
    selObjVal[i] = sqrt((objPos[0][0]-camPos[0][0])**2 + (objPos[0][1]-camPos[0][1])**2 + (objPos[0][2]-camPos[0][2])**2)

mc.select(cl=True)
sortedKey = sortByValue(selObjVal)
# distance from min-dist obj to max-dist-obj 
distMinMax = ( selObjVal[sortedKey[-1]] - selObjVal[sortedKey[0]] )

for key in selObjVal.keys():
    # caculate the distant ratio for each object
    _distRatio = 1 - (selObjVal[sortedKey[-1]] - selObjVal[key]) / distMinMax 
    # add polyReduce() fed parameter by _distRatio
    mc.polyReduce( key, compactness = 0.5, percentage = _distRatio * 90 )
