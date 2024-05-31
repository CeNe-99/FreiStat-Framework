"""
Module implementing the behavior of the setup function for running cyclic
voltammetery.

"""

__author__ = "Mark Jasper"
__contact__ = "University of Freiburg, IMTEK, Jochen Kieninger"
__credits__ = "Mark Jasper"

__version__ = "1.0.0"
__maintainer__ = "Mark Jasper"
__email__ = "mark.jasper@imtek.uni-freiburg.de, kieninger@imtek.uni-freiburg.de"

# Import dependencies

# Import internal dependencies
from ...data_storage.constants import *
from .setup_behavior import SetupBehavior


class SetupCV(SetupBehavior):
    """
    Description
    -----------
    Behavior class implementing the functionality of the setup function when
    running cyclic voltammetry.

    """

    def setup(self, listExperimentParameters: list) -> int:
        """
        Description
        -----------
        Setup method for cyclic voltammetry

        List of required parameters
        ----------
        StartVoltage : float
            Potential at which FreiStat should start to ramp up

        FirstVertex : float
            Potential of the first vertex in mV

        SecondVertex : float
            Potential of the second vertex in mV

        Stepsize : float
            In mV

        Scanrate : float
            In mV/s

        Cycle : int
            Amount of cycles the CV should run

        FixedWEPotential : int
            Defines if the we electrode potential should be fixed to the middle
            of the dynamic range (1.3 V) or not.

        LPTIA_Resistor : int
            Size of the low power transimpendance amplifier resistor which is
            used to measure the current. Range 200 - 512000 ohm.

        MainsFilter: bool
            Enable/ Disable 50 Hz/ 60 Hz mains filter.
            If enabled `Sinc2_Oversampling` must be defiend (Default: 667)

        Sinc2_Oversampling : int
            Oversampling rate of the Sinc 2 filter
            Defiend OSR rates: [22, 44, 89, 178, 267, 533,
            640, 667, 800, 889, 1067, 1333]

        Sinc3_Oversampling : int
            Oversampling rate of the Sinc 3 filter
            Defiend OSR rates: [0 (Disabled), 2, 4, 5]
            Oversampling rate of 5 is not recommanded

        Parameters
        ----------
        `listExperimentParameters`: list
            List which needs to include all required parameters for CV in the
            above stated order.

        Return
        ------
        `iErrorCode` : int
            Error code encoded as integer

        -----------------------------------------------------------------------

        Error Codes
        -----------
        The following table shows all error codes

        iErrorCode  :   Description
        0           :   No error occured, setup successful
        11001       :   List contains wrong amount of parameters
        11002       :   Scan range exceeded by given parameters
        11003       :   Amount of potential steps don't match amount of pulse lengths
        11004       :   To many parameters in list
        11100       :   StartVoltage named wrong or not found as 1 entry
        11101       :   FirstVertex named wrong or not found as 2 entry
        11102       :   SecondVertex named wrong or not found as 3 entry
        11103       :   Stepsize named wrong or not found as 4 enty
        11104       :   Scanrate named wrong or not found as 5 entry
        11105       :   Cycle named wrong or not found as 6 entry
        11106       :   LPTIA Rtia size named wrong or not found as 7 entry
        11107       :   FixedWEPotential named wrong or not found as 8 entry
        11108       :   Mains filter named wrong or not found as 9 entry
        11109       :   Sinc2 oversampling rate named wrong or not found as 10 entry
        11110       :   Sinc3 oversampling rate named wrong or not found as 11 entry
        11200       :   StartVoltage out of bounds
        11201       :   FirstVertex out of bounds
        11202       :   SecondVertex out of bounds
        11203       :   Stepsize out of bounds
        11204       :   Scanrate out of bounds
        11205       :   Cycle out of bounds
        11206       :   LPTIA Rtia size out of bounds
        11207       :   FixedWEPotential out of bounds
        11208       :   Mains filter out of bounds
        11209       :   Sinc2 oversampling rate out of bounds
        11210       :   Sinc3 oversampling rate out of bounds

        """
        # Initialize variables
        iErrorCode: int = EC_NO_ERROR

        fStartPotentialLB: float = 0
        fStartPotentialUB: float = 0

        # Check which vertex is higher
        if listExperimentParameters[1][1] > listExperimentParameters[2][1]:
            # First vertex is higher
            fStartPotentialLB = listExperimentParameters[2][1]
            fStartPotentialUB = listExperimentParameters[1][1]

        else:
            # Second vertex is higher
            fStartPotentialLB = listExperimentParameters[1][1]
            fStartPotentialUB = listExperimentParameters[2][1]

        # Scan range is limited to 2.1 V / 4.0 V (Depending on the mode)
        fRange = abs(listExperimentParameters[2][1] - listExperimentParameters[1][1])

        # Check if potential of the working electrode is fixed or not
        if listExperimentParameters[7][1] == 1:
            fVoltageRange = VOLTAGE_RANGE_FWP
        else:
            fVoltageRange = VOLTAGE_RANGE * 2

        # Initialize reference list
        listReferenceList = [
            [START_POTENTIAL, fStartPotentialLB, fStartPotentialUB],
            [
                LOWER_POTENTIAL,
                fStartPotentialUB - fVoltageRange,
                fStartPotentialLB + fVoltageRange,
            ],
            [
                UPPER_POTENTIAL,
                fStartPotentialUB - fVoltageRange,
                fStartPotentialLB + fVoltageRange,
            ],
            [STEP_SIZE, MIN_STEP_SIZE, MAX_STEP_SIZE],
            [SCAN_RATE, MIN_SCAN_RATE, MAX_SCAN_RATE],
            [CYCLE, MIN_CYCLE, MAX_CYCLE],
            [LPTIA_RTIA_SIZE, LPTIARTIA_OPEN, LPTIARTIA_512K],
            [FIXED_WE_POTENTIAL, 0, 1],
            [MAINS_FILTER, 0, 1],
            [SINC2_OVERSAMPLING, ADCSINC2OSR_DISABLED, ADCSINC2OSR_1333],
            [SINC3_OVERSAMPLING, ADCSINC3OSR_DISABLED, ADCSINC3OSR_2],
        ]

        # Check if list of Parameters is in correct format
        if len(listExperimentParameters) != CV_NUM_PARAMETER:
            # Not enough Parameters
            iErrorCode = EC_SETUP + EC_SE_AMOUNT_PARAMETER
            return iErrorCode

        # Check individual entries
        for iEntry in range(len(listExperimentParameters)):
            # Check if parameter is named correct and at the right position
            if listExperimentParameters[iEntry][0] != listReferenceList[iEntry][0]:
                iErrorCode = EC_SETUP + EC_SE_PARAM_NOT_FOUND + iEntry
                return iErrorCode

            # Check if the parameters are in the boundaries
            if (
                listExperimentParameters[iEntry][1] < listReferenceList[iEntry][1]
                or listExperimentParameters[iEntry][1] > listReferenceList[iEntry][2]
            ):
                iErrorCode = EC_SETUP + EC_SE_PARAM_OUT_OF_BOUND + iEntry
                return iErrorCode

        # Check if scan range is not exceeded
        if fRange >= fVoltageRange:
            iErrorCode = EC_SETUP + EC_SE_SCAN_RANGE_ERROR
            return iErrorCode

        # Safe experiment parameters
        self._dataHandling.save_ExperimentType(CV)
        self._dataHandling.save_ExperimentParmeters(listExperimentParameters)

        # Setup CSV export for the chosen experiment
        self._dataSoftwareStorage._dataHandling.setup_ExportFiles()

        # Return error code
        return iErrorCode
