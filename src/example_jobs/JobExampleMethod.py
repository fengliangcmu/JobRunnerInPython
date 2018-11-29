import datetime
import json

def printSomething():
    print('this is from printSomething method, at :' + datetime.datetime.utcnow().isoformat(' ', 'seconds'))

def printParameters(p1, p2):
    print('this is from printParameters, p1 is: ' + p1 + ' p2 is: ' + p2)
def exportJsonFile():
    tempJsonObj = {
        'attributeA': 'attributeA_value',
        'attributeB': ['a','b','c'],
        'attributeC': {'subAttri': 2}
    }
    fileName = 'tempJsonObj_' + datetime.datetime.utcnow().isoformat(' ', 'seconds') +'.json'
    with open(fileName, 'w') as outfile:
        json.dump(tempJsonObj, outfile)
