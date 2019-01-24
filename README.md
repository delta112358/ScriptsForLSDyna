# ScriptsForLSDyna
Collection of Python3 Scripts useful for Simulations with LS-Dyna.
## GenerateHeatLoadcurves.py
Generates an internal heat generation rate in W/m^3 of a body, for each finite element over time (*LOAD_HEAT_GENERATION_%).
- The load has to be defined in text files (Hgen1.txt, Hgen2.txt, ...).
- Each file stores a constant heat generation rate for each finite element, sorted by the finite element number.
- The number of files defines the number of load steps to discetize a variable heat generation rate over time.
- The end times of the load steps have to be stored in a time.txt file.

## FLUKAINTERPOLATION.py
Generates an internal heat generation rate in W/m^3 of a body, for each finite element over time (*LOAD_HEAT_GENERATION_%).
- The load is defined by a sweep movement of discrete impact locations of a single bunch.
- As input for the single bunch, a FLUKA output file is used (single bunch, kinetic energy per bin per proton in GeV/cm^3).
- The sweep is described in a csv file with the impact locations as (impact time,x,y) coordinates.
- All inputs to the script are defined in a Parameter.py file.

## GenerateTemperatureLoadcurves.py
Generates a change of temperature in a body, defined node wise (*LOAD_THERMAL_VARIABLE).
- The load has to be defined in text files (Temp1.txt, Temp2.txt, ...), where each file describes a new Temperature field.
- Temp1.txt describes the field after the first impact of the beam.
- the timing, when the temperature fields are imposed has to be given in the main function in the list 'pulseTimes' and the last field is kept till 'endTime'.

## GenerateTemperatureLoadcurvesWithDynamicRelaxation.py
Generates a change of temperature in a body, defined node wise (*LOAD_THERMAL_VARIABLE).
- The load has to be defined in text files (Temp1.txt, Temp2.txt, ...), where each file describes a new Temperature field
- Temp1.txt describes the intitialisation field and the following files the temperatures after the beam impacts.
- the timing, when the temperature fields are imposed has to be given in the main function in the list 'pulseTimes' and the last field is kept till 'endTime'

## GenerateSmoothDisplacement.py
Generates a Loadcurve for LS-Dyna to use with \*LOAD_BODY_GENERALIZED. The curve describes an acceleration profile over time with a sin(t)^2 like profile to prevent higher order excitations of the structure. 