# ScriptsForLSDyna
Collection of Python3 Scripts useful for Simulations with LS-Dyna.
## HeatLoadcurves.py
Generates Loadcurves sorted after the FE-number, extracted for each Loadstep from ANSYS. The Loadcorves descibe an internal heat generation in W/m^3 for each SHELL-element over time.
## GenerateSmoothDisplacement.py
Generates a Loadcurve for LS-Dyna to use with \*LOAD_BODY_GENERALIZED. The curve describes an acceleration profile over time with a sin(t)^2 like profile to prevent higher order excitations. 
