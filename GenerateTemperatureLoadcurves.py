def generateTimeVector(pulseTimes,endTime):
	timeVector=[0]+[i for i in pulseTimes]+[endTime]
	return timeVector

def iterateOverNodes(NumberOfTempFiles,roomTemperature):
    tempFiles = [open("Temp"+str(i+1)+".txt","r") for i in range(NumberOfTempFiles)]

    for Node in zip(*tempFiles):
        yield [float(entry)-roomTemperature for entry in Node]

    for tempFile in tempFiles:
        tempFile.close()

def writeLoadCurves(loadFileName, pulseTimes, roomTemperature, endTime):
    timeVector=generateTimeVector(pulseTimes,endTime)        
    NumberOfTempFiles=int(len(pulseTimes))
    with open(loadFileName,"w") as loadFile:
        loadFile.write('$\n$\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
        loadFile.write('$                               LOAD DEFINITIONS                               $\n')
        loadFile.write('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n$\n')
        for NodeNumber, temperatureDifferenceCurve in enumerate(iterateOverNodes(NumberOfTempFiles,roomTemperature), start=1):
            if max(temperatureDifferenceCurve)>0:
                writeLoadCurve(loadFile, temperatureDifferenceCurve, roomTemperature, NodeNumber, timeVector)

def writeLoadCurve(loadFile, temperatureDifferenceCurve, roomTemperature, NodeNumber, timeVector):
    temperatureDifferenceCurve = [0] + [temperatureDifference for temperatureDifference in temperatureDifferenceCurve] + [temperatureDifferenceCurve[-1]]
    loadFile.write('*DEFINE_CURVE\n% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f' % (NodeNumber,0,0,1,0,0))
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
    # Temp1.txt contains the temperatures after the first beam impact sorted by node number
    # Temp2.txt after the second beam impact and so on
    roomTemperature = 22
    pulseTimes = [2.1E-6]
    endTime = 5e-5
    loadFileName='Load.k'
    writeLoadCurves(loadFileName, pulseTimes, roomTemperature, endTime)

if __name__ == '__main__':
    main()