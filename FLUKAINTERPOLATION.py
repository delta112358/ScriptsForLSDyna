import numpy as np
import time
from scipy.interpolate import RegularGridInterpolator
from Parameterfile import *

def main():
    time.clock()
    fileNames=[coordinateFileName,flukaFileName,KFileName,coordinateFileName,outputKFileName]
    IOTypes=['r','r','r','r','w']
    fileAccessInfo = (i for i in zip(fileNames,IOTypes))
    maximumDepositedEnergy = generateLoadApplicationFile(fileAccessInfo,scaleFactor,thresholdFactor,zOffet,ElementType,partNumber)
    printMaximumEnergyDeposition(maximumDepositedEnergy)
    printDuration(int(time.clock()))


def generateLoadApplicationFile(fileAccessInfo,scaleFactor,thresholdFactor,zOffet,ElementType,partNumber):
    maximumDepositedEnergy=[0,0]
    fileList = [open(fileName,IOType) for (fileName,IOType) in fileAccessInfo]
    print('reading FLUKA ...')
    flukaCoordinateAxes, flukaDataArray, dimension = getDataFromFlukaFile(fileList[1],scaleFactor,thresholdFactor)
    timeVector = generateTimeVector(fileList[0],endtime = 1)
    print('reading KFile ...')
    firstElementNumber, meshInformationArray = getMeshInformationArray(fileList[2],partNumber,dimension)
    coordinates = getSweepCoordinates(fileList[3],zOffet,dimension)
    print('interpolate ...')
    maximumEnergyDepostion = interpolateOnMeshAndWriteFile(fileList[4],flukaCoordinateAxes,flukaDataArray,firstElementNumber,meshInformationArray,timeVector,coordinates)
    for file in fileList:
        file.close()
    return maximumEnergyDepostion


def generateTimeVector(coordinateFile,endtime):
    next(coordinateFile)
    times = (float(line.strip().split(',')[1]) for line in coordinateFile)
    firstEntry = next(times)
    rampTime = firstEntry/10000
    offsets = [0,rampTime]
    timeVector = [0,rampTime,firstEntry,firstEntry+rampTime]
    return timeVector + [time+offset for time in times for offset in offsets] + [endtime]



def getDataFromFlukaFile(flukaFile,scaleFactor,thresholdFactor):
    headerRaw = (next(flukaFile).strip().split() for x in range(8))
    headerData = processHeaderData(headerRaw)
    xmax=headerData[0][2]
    ymax=headerData[1][2]
    zmax=headerData[2][2]

    lines = [line.strip().split() for line in flukaFile]
    energyDepositionDensities=(float(energyDepositionDensityString) for line in lines[:lines.index([])] for energyDepositionDensityString in line)

    flukaDataArray=np.zeros((int(headerData[0][2]),int(headerData[1][2]),int(headerData[2][2])),dtype=np.float64)
    for z in range(zmax):
         for y in range(ymax):
            for x in range(xmax):
                flukaDataArray[x,y,z]=next(energyDepositionDensities)
    threshold = float(np.amax(flukaDataArray)) * thresholdFactor
    flukaDataArray[flukaDataArray < threshold] = 0
    dimension = '3D'
    if flukaDataArray.shape[2]==1:
        dimension = '2D'
        flukaDataArray=np.squeeze(flukaDataArray,axis=(2,))
    flukaCoordinateAxes = makeFlukaCoordinateAxes(headerData,dimension)
    flukaDataArray = scaleFactor * flukaDataArray
    return flukaCoordinateAxes, flukaDataArray, dimension


def processHeaderData(headerRaw):
    tempHead=[]
    for line in headerRaw:
        tempLine=[]
        for value in line:
            try:
                tempLine.append(float(value))
            except Exception:
                continue
        tempHead.append(tempLine)
    headerData=tempHead[2:5]
    for index,line in enumerate(headerData):
        headerData[index]=[entry/100. for entry in line]
        headerData[index][2]=int(line[2])
    return headerData


def makeFlukaCoordinateAxes(headerData,dimension):
    flukaCoordinateAxes=[]
    for i in range(3):
        flukaCoordinateAxes.append(np.linspace(headerData[i][0]+0.5*headerData[i][3],headerData[i][1]-0.5*headerData[i][3],num=headerData[i][2]))
    if dimension == '2D':
        filteredFlukaCoordinateAxes=(flukaCoordinateAxes[0], flukaCoordinateAxes[1])
    else:
        filteredFlukaCoordinateAxes=(flukaCoordinateAxes[0], flukaCoordinateAxes[1], flukaCoordinateAxes[2])
    return filteredFlukaCoordinateAxes


def getMeshInformationArray(KFile,partNumber,dimension):
    firstElementNumber,meshInformationArray = getElementCoordinates(KFile,partNumber)
    if dimension == '2D':
        meshInformationArray=meshInformationArray[:,:2]
    return firstElementNumber,meshInformationArray


def getElementCoordinates(KFile,partNumber):
    locstr = str
    locfloat = float
    locint = int
    goTo(KFile,"*NODE")
    nodeDict=makeLineDict(KFile,16,0,3,locfloat)
    goTo(KFile,"*ELEMENT")
    elementNodesIterator = makeLineIterator(KFile,8,0,-1,locint)
    elementCentroids = []
    elementNumbers = []
    for finiteElement in elementNodesIterator:
        if finiteElement[1] == partNumber:
            elementNumbers.append(finiteElement[0])
            elementCentroids.append(np.mean(np.array([nodeDict[locstr(locint(i))] for i in finiteElement[2:]]),axis=0))
    return elementNumbers[0],np.array(elementCentroids)

def goTo(file,signal):
    for line in giveLine(file):
        if signal in line:
            return

def giveLine(file):
    for line in file:
        yield line

def makeLineDict(KFile,chunkSize,start,end,variableType):
    dictionary={}
    for line in giveLineOfBlock(KFile,['$','*']):
        dictionary[line[:8].strip()]=[element for element in chunks(line[8:],chunkSize)]
    for key,value in dictionary.items():
        dictionary[key]=[variableType(element) for element in value[start:end]]
    return dictionary


def makeLineIterator(KFile,chunkSize,start,end,variableType):
    return (([variableType(entry) for entry in [element for element in chunks(line,chunkSize)][:-1]]) for line in giveLineOfBlock(KFile,['$','*']))

def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start+n]

def giveLineOfBlock(file,signal):
    for line in file:
        if signal[0] in line:
            return
        elif signal[1] in line:
            return
        yield line



def getSweepCoordinates(coordinateFile,zOffet,dimension):
    next(coordinateFile)
    coordinates=(line.strip().split(',')[2:] for line in coordinateFile)
    if dimension == '3D':
        return [np.array([float(value) for value in line]+[zOffet]) for line in coordinates]
    else:
        return [np.array([float(value) for value in line]) for line in coordinates]



# def interpolateOnMeshAndWriteFile(outputKFile,flukaCoordinateAxes,flukaDataArray,firstElementNumber,meshInformationArray,timeVector,coordinates):
#     maximumDepositedEnergy = [0,0]
#     outputKFile.write('$\n$\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
#     outputKFile.write('$                               LOAD DEFINITIONS                               $\n')
#     outputKFile.write('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n$\n')

#     interpolationFunction = RegularGridInterpolator(flukaCoordinateAxes, flukaDataArray, bounds_error=False, fill_value=None)

#     previousElementNumber = firstElementNumber - 1
#     for localFiniteElementNumber, heatGenerationCurve in enumerate(iterateOverFiniteElements(meshInformationArray, coordinates, interpolationFunction), start=1):
#         finiteElementNumber = localFiniteElementNumber + previousElementNumber
#         heatGenerationCurve = np.array(heatGenerationCurve)
#         heatGenerationCurve[heatGenerationCurve < 0] = 0
#         if np.amax(heatGenerationCurve) > 0:
#             depositedEnergy = writeLoadCurve(outputKFile, [ElementType, heatGenerationCurve, finiteElementNumber, timeVector])
#             if depositedEnergy > maximumDepositedEnergy[1]:
#                 maximumDepositedEnergy = [finiteElementNumber,depositedEnergy]
#     previousElementNumber = previousElementNumber + meshInformationArray.shape[0]
#     return maximumDepositedEnergy

def interpolateOnMeshAndWriteFile(outputKFile,flukaCoordinateAxes,flukaDataArray,firstElementNumber,meshInformationArray,timeVector,coordinates):
    maximumDepositedEnergy = [0,0]
    outputKFile.write('$\n$\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
    outputKFile.write('$                               LOAD DEFINITIONS                               $\n')
    outputKFile.write('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n$\n')

    interpolationFunction = RegularGridInterpolator(flukaCoordinateAxes, flukaDataArray, bounds_error=False, fill_value=None)

    previousElementNumber = firstElementNumber - 1
    sections = int(meshInformationArray.shape[0] / 300000)
    if sections == 0: sections = 1
    for i,array in enumerate(iter(np.array_split(meshInformationArray, sections, axis=0))):
        for localFiniteElementNumber, heatGenerationCurve in enumerate(iterateOverFiniteElements(array, coordinates, interpolationFunction), start=1):
            finiteElementNumber = localFiniteElementNumber + previousElementNumber
            heatGenerationCurve = np.array(heatGenerationCurve)
            heatGenerationCurve[heatGenerationCurve < 0] = 0
            if np.amax(heatGenerationCurve) > 0:
                depositedEnergy = writeLoadCurve(outputKFile, [ElementType, heatGenerationCurve, finiteElementNumber, timeVector])
                if depositedEnergy > maximumDepositedEnergy[1]:
                    maximumDepositedEnergy = [finiteElementNumber,depositedEnergy]
        previousElementNumber = previousElementNumber + array.shape[0]
    return maximumDepositedEnergy



def iterateOverFiniteElements(meshInformationArray, coordinates, interpolationFunction):
    meshDataIterator = (np.nditer(interpolationFunction(np.subtract(meshInformationArray,coordinateSystem))) for coordinateSystem in coordinates)
    for heatGenerationCurve in zip(*meshDataIterator):
        yield heatGenerationCurve

def writeLoadCurve(outputKFile, parameters):
    ElementType, heatGenerationCurve, finiteElementNumber, timeVector = parameters
    heatGenerationCurve = [0] + [element for element in heatGenerationCurve for _ in range(2)] + [0, 0]
    outputKFile.write('*DEFINE_CURVE\n% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f' % (finiteElementNumber,0,1,1,0,0))
    energyDeposition = []
    for BunchNumber,time in enumerate(timeVector):
        try:
            cond1 = heatGenerationCurve[BunchNumber-1]>0
            cond2 = heatGenerationCurve[BunchNumber+1]>0
            cond3 = time == 0
            if cond1 or cond2 or cond3:
                outputKFile.write('\n%20.7E%20.6E' % (time, heatGenerationCurve[BunchNumber]))
                energyDeposition.append([time, heatGenerationCurve[BunchNumber]])
        except IndexError:
            outputKFile.write('\n%20.7E%20.6E' % (time, heatGenerationCurve[BunchNumber]))
            energyDeposition.append([time, heatGenerationCurve[BunchNumber]])
    outputKFile.write('\n*LOAD_HEAT_GENERATION_'+ElementType+'\n% 10.0f% 10.0f% 10.0f\n' % (finiteElementNumber, finiteElementNumber,1))
    energy = 0
    for index,line in enumerate(energyDeposition[1:],start = 1):
        energy = energy+((line[1]+energyDeposition[index-1][1])/2)*(line[0]-energyDeposition[index-1][0])
    return energy


def printMaximumEnergyDeposition(maximumDepositedEnergy):
    print("Maximum deposited Energy in Element "+ str(maximumDepositedEnergy[0]) +":\n" + str(maximumDepositedEnergy[1]/1000000) + " J/cm3.")
    with open('EnergyDeposition2.txt','w') as file:
        file.write("\nMaximum deposited Energy in Element "+ str(maximumDepositedEnergy[0]) +":\n" + str(maximumDepositedEnergy[1]/1000000) + " J/cm3.")

def printDuration(durationInSeconds, StringFormat = '\nIt took %i:%i:%i to finish.'):
    RestTime = durationInSeconds
    Hours = int(durationInSeconds / 3600)
    RestTime = durationInSeconds - Hours * 3600
    Minutes = int(RestTime / 60)
    RestTime = RestTime - Minutes * 60
    Seconds = int(RestTime)
    print(StringFormat % (Hours , Minutes , Seconds))

if __name__ == '__main__':
    main()