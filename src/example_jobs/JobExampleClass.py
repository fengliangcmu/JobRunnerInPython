import datetime
import json

class JobExampleClass:
    def __init__(self):
        print('JobService instance')
    
    def __str__(self):
        return 'JobService'
    
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
    
    if __name__ == "__main__":
        printSomething()
        exportJsonFile()

