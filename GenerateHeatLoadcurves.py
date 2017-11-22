import sys
import time
plonk=(time.clock())
# Print iterations progress
def printProgressBar (iteration, total):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    prefix = 'Generating Load Curves:'
    suffix = 'Complete'
    length = 25
    decimals = 1
    fill = 'X'
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('%s |%s| %s%% %s\r' % (prefix, bar, percent, suffix), end = '\r')
    sys.stdout.flush()
    if iteration == total: 
        print()

def printDuration(durationInSeconds, StringFormat='\nIt took %i:%i:%i to finish.'):
    RestTime = durationInSeconds
    Hours = int(durationInSeconds / 3600)
    RestTime = durationInSeconds - Hours * 3600
    Minutes = int(RestTime / 60)
    RestTime = RestTime - Minutes * 60
    Seconds = int(RestTime)
    print(StringFormat % (Hours , Minutes , Seconds))

def generateTimeVector(timeFileName,endtime):
    with open(str(timeFileName),"r") as timeFile:
        firstEntry=float(timeFile.readline().strip())
        rampTime=firstEntry/10000
        timeVector=[]
        timeVector.append(0)
        timeVector.append(rampTime)
        timeVector.append(firstEntry)
        timeVector.append(firstEntry+rampTime)
        for line in timeFile:
            timeVector.append(float(line))
            timeVector.append(float(line)+rampTime)
        timeVector.append(endtime)
        return timeVector

def writeLoadCurve(KFile, ElementType, HeatGenerationCurve, FiniteElementNumber, timeVector):
    HeatGenerationCurve = [0] + [element for element in HeatGenerationCurve for _ in range(2)] + [0, 0]
    KFile.write('*DEFINE_CURVE\n% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f% 10.0f' % (FiniteElementNumber,0,1,1,0,0))
    for BunchNumber,time in enumerate(timeVector):
        try:
            cond1=HeatGenerationCurve[BunchNumber-1]>0
            cond2=HeatGenerationCurve[BunchNumber+1]>0
            cond3=time==0
            if cond1 or cond2 or cond3:
                KFile.write('\n%20.7E%20.6E' % (time, HeatGenerationCurve[BunchNumber]))
        except IndexError:
            KFile.write('\n%20.7E%20.6E' % (time, HeatGenerationCurve[BunchNumber]))
    KFile.write('\n*LOAD_HEAT_GENERATION_'+ElementType+'\n% 10.0f% 10.0f% 10.0f\n' % (FiniteElementNumber, FiniteElementNumber,1))

def getNumberOfFiniteElements():
    with open("Hgen1.txt","r") as FiniteElementFile:
        return sum(1 for line in FiniteElementFile)

def iterateOverFiniteElements(NumberOfBunches):
    heatFiles = [open("Hgen"+str(i)+".txt","r") for i in range(1, NumberOfBunches+1)]

    for FiniteElement in zip(*heatFiles):
        yield [float(entry) for entry in FiniteElement]

    for heatFile in heatFiles:
        heatFile.close()

def writeLoadCurves(KFileName,ElementType):
    timeVector=generateTimeVector("time.txt",endtime)        
    NumberOfBunches=int(len(timeVector)/2-1)
    numberOfFiniteElements = getNumberOfFiniteElements()
    printedPercentage=0
    with open(KFileName,"w") as KFile:
        KFile.write('$\n$\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n')
        KFile.write('$                               LOAD DEFINITIONS                               $\n')
        KFile.write('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n$\n')
        for FiniteElementNumber, HeatGenerationCurve in enumerate(iterateOverFiniteElements(NumberOfBunches), start=1):
            if max(HeatGenerationCurve)>0:
                writeLoadCurve(KFile, ElementType, HeatGenerationCurve, FiniteElementNumber, timeVector)
            if (FiniteElementNumber)-(printedPercentage)*(numberOfFiniteElements/100)=0:
                printProgressBar(FiniteElementNumber, numberOfFiniteElements)
                printedPercentage=printedPercentage+1

def main():
    endtime=1e-3
    ElementType='SOLID'
    writeLoadCurves("Load.k",ElementType)
    printDuration(int(time.clock()))

if __name__ == '__main__':
    main()