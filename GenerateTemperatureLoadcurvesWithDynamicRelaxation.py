def generateTimeVector(relaxationTime,pulseTimes,endTime):
	timeVector=[0]+[i for i in pulseTimes]+[endTime]
	return timeVector

def getNumberOfNodes():
    with open("Temp1.txt","r") as NodeFile:
        return sum(1 for line in NodeFile)

def iterateOverNodes(NumberOfTempFiles,roomTemperature):
    tempFiles = [open("Temp"+str(i+1)+".txt","r") for i in range(NumberOfTempFiles)]

    for Node in zip(*tempFiles):
        yield [float(entry)-roomTemperature for entry in Node]

    for tempFile in tempFiles:
        tempFile.close()

def writeLoadCurves(loadFileName, pulseTimes, roomTemperature, endTime):
    timeVector=generateTimeVector(relaxationTime,pulseTimes,endTime)        
    NumberOfTempFiles=int(len(pulseTimes)+1)
    with open(loadFileName,"w") as loadFile:
        loadFile.write('$\n$\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
        loadFile.write('$                       Additions for Dynamic Relaxation                       $\n')
        loadFile.write('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n$')
        loadFile.write('\n*CONTROL_DYNAMIC_RELAXATION\n% 10.0f% 10.3f% 10.3f% 10.0E% 10.0f% 10.0f% 10.2f% 10.0f' % (250,0.001,0.995,1e-9,0,0,0.04,5))
        loadFile.write('\n*CONTROL_IMPLICIT_GENERAL\n% 10.0f% 10.0E\n' % (0,1E-10))
        loadFile.write('$\n$\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
        loadFile.write('$                               LOAD DEFINITIONS                               $\n')
        loadFile.write('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n$\n')
        for NodeNumber, temperatureDifferenceCurve in enumerate(iterateOverNodes(NumberOfTempFiles,roomTemperature), start=1):
            if max(temperatureDifferenceCurve)>0:
                writeLoadCurve(loadFile, temperatureDifferenceCurve, roomTemperature, NodeNumber, timeVector)

def writeLoadCurve(loadFile, temperatureDifferenceCurve, roomTemperature, NodeNumber, timeVector):
    temperatureDifferenceCurve =[temperatureDifference for temperatureDifference in temperatureDifferenceCurve] + [temperatureDifferenceCurve[-1]]
    loadFile.write('*DEFINE_CURVE\n% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f' % (NodeNumber,2,1,1,0,0))
    for timeIndex,time in enumerate(timeVector):
        try:
            cond1=temperatureDifferenceCurve[timeIndex-1]>0
            cond2=temperatureDifferenceCurve[timeIndex+1]>0
            cond3=time==0
            if cond1 or cond2 or cond3:
                loadFile.write('\n%20.7E%20.6E' % (time, temperatureDifferenceCurve[timeIndex]))
        except IndexError:
            loadFile.write('\n%20.7E%20.6E' % (time, temperatureDifferenceCurve[timeIndex]))
    loadFile.write('*SET_NODE_LIST\n% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f\n% 10.0f' % (NodeNumber+10,0,0,0,0,NodeNumber))
    loadFile.write('\n*LOAD_THERMAL_VARIABLE\n% 10.0f\n% 10.0f% 10.0f% 10.0f\n' % (NodeNumber+10,1,roomTemperature,NodeNumber))

def main():
    # Temp1.txt contains the temperatures for the preload sorted by node number
    # Temp2.txt contains the temperatures after the first beam impact
    # Temp3.txt after the second beam impact and so on
    roomTemperature = 22
    pulseTimes = [2.1E-6]
    endTime = 5e-5
    loadFileName='Load.k'
    writeLoadCurves(loadFileName, pulseTimes, roomTemperature, endTime)

if __name__ == '__main__':
    main()