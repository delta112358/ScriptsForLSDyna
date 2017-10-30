import math
import matplotlib.pyplot as plt

def frange(fromValue, toValue, timeStep):
  while fromValue <= toValue:
    yield float(fromValue)
    fromValue += float(timeStep)


def getInputs():
    displacement=float(input('Enter desired displacement:'))
    startTime=float(input('Enter start time of displacement:'))
    endTime=float(input('Enter end time of displacement:'))
    timeStep=float(input('Enter desired resulution in seconds:'))
    return [displacement,startTime,endTime,timeStep]


def generateDataZip(generateTimeList,generateValueList,inputs):
    TimeList=generateTimeList(0,inputs[2]-inputs[1],inputs[3])
    TimeListForOutput=[time+inputs[1] for time in TimeList]
    return zip(TimeListForOutput,generateValueList(inputs[0],inputs[2]-inputs[1],TimeList))


def generateTimeList(startTime,endTime,timeStep):
    return list(frange(startTime,endTime+timeStep,timeStep))


def generateAccelerationValueList(maximumDisplacement,endTime,TimeList):
    return[round(8*maximumDisplacement*(math.sin(2*t*math.pi/endTime))**2/endTime**2,10) if t<=endTime/2 else round(-8*maximumDisplacement*(math.sin(2*t*math.pi/endTime))**2/endTime**2,10) for t in TimeList]

def generateDisplacementValueList(maximumDisplacement,endTime,TimeList):
    return[round(maximumDisplacement*(2*(t/endTime)**2+(math.cos((4*t*math.pi)/endTime)-1)/(4*(math.pi)**2)),10) if t<=endTime/2 else -round(maximumDisplacement*(2*(t/endTime)**2+(math.cos((4*t*math.pi)/endTime)-1)/(4*math.pi**2)+(1-4*t/endTime)),10) for t in TimeList]


def plotDataZip(DataZip):
    x,y=zip(*DataZip)
    plt.plot(x,y,'r')
    plt.xlabel('time in s')
    plt.ylabel('displacement in m')
    plt.show()


def writeLoadCurve(DataZip,OutputFile):
    with open(OutputFile, 'w') as OutputFile:
        OutputFile.write("*DEFINE_CURVE\n%10.0f%10.0f%10.0f%10.0f%10.0f%10.0f\n" % (2,0,1,1,0,0))
        for time, displacement in DataZip:
            OutputFile.write("%20.7E%20.7E\n" % (time,displacement))


def main():
    inputs=getInputs()
    writeLoadCurve(generateDataZip(generateTimeList,generateAccelerationValueList,inputs),"Accel.k")
    plotDataZip(generateDataZip(generateTimeList,generateDisplacementValueList,inputs))
    print('The Loadcurve for *LOAD_BODY_GENERALIZED was saved as Accel.k.')
if __name__ == '__main__':
  main()


