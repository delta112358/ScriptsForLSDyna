import sys
import time
plonk=(time.clock())
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = 'X'):
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
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    # print ("\n" * 10)
    print('%s |%s| %s%% %s\r' % (prefix, bar, percent, suffix), end = '\r')

    #sys.stdout.write('\r%s |%s| %s%% %s\r' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    # Print New Line on Complete
    if iteration == total: 
        print()

def printDuration(durationInSeconds, StringFormat='\nIt took %i:%i:%i to finish.'):
    RestTime = durationInSeconds # t: seconds left
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

def writeLoadCurve(KFile, HeatGenerationCurvesPerElement, FiniteElementNumber, timeVector):
    HeatGenerationCurvesPerElement = [0] + [element for element in HeatGenerationCurvesPerElement for _ in range(2)] + [0, 0]
    KFile.write("""*DEFINE_CURVE\n% 10.0f         0     1.000     1.000     0.000     0.000""" % (FiniteElementNumber))
    BunchNumber=1
    j=0
    while j+1<len(timeVector):
        if BunchNumber>3:
            if float(HeatGenerationCurvesPerElement[BunchNumber-2])!=0 or float(HeatGenerationCurvesPerElement[BunchNumber])!=0:
                KFile.write("""\n%20.7E%20.6E""" % (float(timeVector[j]), float(HeatGenerationCurvesPerElement[BunchNumber-1])))
        else:
            KFile.write("""\n%20.7E%20.6E""" % (float(timeVector[j]), float(HeatGenerationCurvesPerElement[BunchNumber-1])))
        BunchNumber=BunchNumber+1
        j=j+1
    KFile.write("""\n%20.7E%20.6E""" % (float(timeVector[j]), float(HeatGenerationCurvesPerElement[BunchNumber-1])))
    KFile.write("""\n*LOAD_HEAT_GENERATION_SHELL\n% 10.0f% 10.0f         1\n""" % (FiniteElementNumber, FiniteElementNumber))

def getNumberOfFiniteElements():
    with open("Hgen1.txt","r") as FiniteElementFile:
        return sum(1 for line in FiniteElementFile)

def iterateOverFiniteElements(NumberOfBunches):
    element=0
    heatFiles = [open("Hgen"+str(i)+".txt","r") for i in range(1, NumberOfBunches+1)]

    for FiniteElement in zip(*heatFiles):
        yield [float(entry)*0.9 for entry in FiniteElement]

    for heatFile in heatFiles:
        heatFile.close()

def main():
    endtime=1e-3
    Roomtemp=20
    timeVector=generateTimeVector("time.txt",endtime)        
    NumberOfBunches=int(len(timeVector)/2-1)
    numberOfFiniteElements = getNumberOfFiniteElements()
    c=1
    printProgressBar(0, numberOfFiniteElements, prefix = 'Generating Load Curves:', suffix = 'Complete', length = 25)

    with open("Load.k","a") as KFile:
        KFile.write("$\n$\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")
        KFile.write("$                               LOAD DEFINITIONS                               $\n")
        KFile.write("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")
        KFile.write("$\n")
        for i, HeatGenerationCurvesPerElement in enumerate(iterateOverFiniteElements(NumberOfBunches)):
            if max(HeatGenerationCurvesPerElement)>0:
                writeLoadCurve(KFile, HeatGenerationCurvesPerElement, FiniteElementNumber=i+1, timeVector=timeVector)
            if (i+1)-(numberOfFiniteElements/100)-c*(numberOfFiniteElements/100)>0:
                printProgressBar(i+1, numberOfFiniteElements, prefix = 'Generating Load Curves:', suffix = 'Complete', length = 25)
                c=c+1
    printProgressBar(i+1, numberOfFiniteElements, prefix = 'Generating Load Curves:', suffix = 'Complete', length = 25)
    printDuration(int(time.clock()))

if __name__ == '__main__':
    main()
