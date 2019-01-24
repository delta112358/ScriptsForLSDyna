# Modification of FLUKA file
# 
#  Scaling of Energy Deposition from GeV/cm^3/p+ to J/m^3:
numberOfProtons       = 1.3E11
protonCharge          = 1E6*1E9*1.602176487e-19
bunchLength           = 25E-9
scaleFactor           = numberOfProtons*protonCharge/bunchLength

# Definition of Directories:
# 
#  Input and Output for LS-Dyna files:
# KFileName             = "TestSmall.k"
KFileName             = "TestShell.k"
outputDirectory       = ''
# outputKFileName       = 'LoadSmall.k'
outputKFileName       = 'LoadSmallShell.k'

#  Directory of FLUKA file:
# flukaDirectory        = 'G:\\Projects\\BID\\Run3\\HL_LHC\\lhc_TDE_7TeV\\downstreamwindow\\R3STD_2pt08emittance_single_bunch\\'
# flukaFileName         = flukaDirectory + "res_ascii_merged.51"
flukaDirectory        = 'G:\\Projects\\BID\\Run3\\HL_LHC\\lhc_TDE_7TeV\\upstreamwindow\\CCwindow_density_1pt5\\BCMS_1pt37emittance_single_bunch\\'
flukaFileName         = flukaDirectory + "res_ascii_merged.72"

#  Directory of Sweep patterns:
patternDirectory      = 'D:\\TDE\\00Sim\\FLUKA\\'
patternDirectory      = ''
coordinateFileName    = patternDirectory + "Single.csv"

# Settings for Interpolation:
interpolationTypeList = ['nodalbased with maximum','nodalbased with mean','centroidbased']
interpolationType     = interpolationTypeList[2]
# zOffet                = -4.1626
zOffet                = 4.205
# partNumber            = 1
partNumber            = 2
# ElementType           = 'SOLID'
ElementType           = 'SHELL'
thresholdFactor       = 0.001