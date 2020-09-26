from Serial import *

def txtComportsAvailable():
    FILE = open( "../comportList.txt",'w' )

    comportList = serialPorts()

    for num, comport enumerate(comportList):
        FILE.write(str(comport) + ' , ' + str(num) )
    
    FILE.close()