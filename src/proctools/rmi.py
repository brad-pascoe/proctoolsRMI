# Key functions and values for quarterscale analysis
import math
import numpy as np
from dataclasses import dataclass
from enum import Enum


class RMI_Cases(Enum):
    StandardTheta = 1
    QuarterTheta = 2
    WalchliSingleMode = 3
    PascoeSingleMode = 4
    StandardThetaDNS697 = 5


@dataclass
class RMI_Parameters:
    # Geometry
    L: float
    lambda_bar: float
    kbar: float
    sigma0: float
    # Fluids
    Atwood: float
    rhoplus_bar: float
    deltaU: float
    Us: float
    C: float
    CAlt: float
    # RMI
    U0: float
    time2tau: float

    def __init__(self, case: RMI_Cases):

        match case:
            case RMI_Cases.StandardTheta:
                # Standard domain width
                self.L = 2.0*math.pi
                # Calculate smallest wavelength
                lambda_min = self.L/8.0
                # Calculate mean wavelength and wavenumber
                self.lambda_bar = np.sqrt(12.0/7.0) * lambda_min
                self.kbar = 2.0 * math.pi / self.lambda_bar
                # Calculate standard deviation of amplitude
                self.sigma0 = 0.1*lambda_min

                self.Atwood = (5.22-1.80)/(5.22+1.80)
                self.rhoplus_bar = 0.5*(1.80+5.22)
                self.deltaU = 291.575
                self.Us = 434.6
                self.C = (1-self.deltaU/self.Us)
                self.CAlt = 0.576
                # Equation 11
                self.sigma0Plus = self.C*self.sigma0
                self.U0 = 0.564*self.sigma0Plus*self.kbar*self.deltaU*self.Atwood
                # Nondimensionalistion for time
                self.time2tau = self.U0/self.lambda_bar

            case RMI_Cases.QuarterTheta:
                # Standard domain width
                self.L = 2.0*math.pi
                # Calculate smallest wavelength
                lambda_min = self.L/32.0
                # Calculate mean wavelength and wavenumber
                self.lambda_bar = np.sqrt(12.0/7.0) * lambda_min
                self.kbar = 2.0 * math.pi / self.lambda_bar
                # Calculate standard deviation of amplitude
                self.sigma0 = 0.1*lambda_min

                self.Atwood = (5.22-1.80)/(5.22+1.80)
                self.rhoplus_bar = 0.5*(1.80+5.22)
                self.deltaU = 291.575
                self.Us = 434.6
                self.C = (1-self.deltaU/self.Us)
                self.CAlt = 0.576
                # self.U0 = 12.649

                # Equation 11
                self.sigma0Plus = self.C*self.sigma0
                self.U0 = 0.564*self.sigma0Plus*self.kbar*self.deltaU*self.Atwood
                # Nondimensionalistion for time
                self.time2tau = self.U0/self.lambda_bar
            case RMI_Cases.PascoeSingleMode:
                self.L = 0.2
                self.lambda_bar = self.L
                self.kbar = 2.0 * math.pi / self.lambda_bar
                self.sigma0 = 0.0
                self.Atwood = 0.5
                self.rhoplus_bar = 2
                self.U0 = 1
                self.time2tau = self.U0/self.lambda_bar

            case RMI_Cases.StandardThetaDNS697:
                # Standard domain width
                self.L = 2.0*math.pi
                # Calculate smallest wavelength
                lambda_min = self.L/8.0
                # Calculate mean wavelength and wavenumber
                self.lambda_bar = np.sqrt(12.0/7.0) * lambda_min
                self.kbar = 2.0 * math.pi / self.lambda_bar
                # Calculate standard deviation of amplitude
                self.sigma0 = 0.1*lambda_min

                self.Atwood = (5.22-1.80)/(5.22+1.80)
                self.rhoplus_bar = 0.5*(1.80+5.22)
                self.deltaU = 291.575
                self.Us = 434.6
                self.C = (1-self.deltaU/self.Us)
                self.CAlt = 0.576
                # Equation 11
                self.sigma0Plus = self.C*self.sigma0
                rhoMinus_bar = 0.5*(3.0+1.0)
                # delta0 = self.L/32.0
                delta0 = lambda_min/(4.0*math.sqrt(math.pi))
                D = 0.1/rhoMinus_bar
                ts = 0.0011
                deltaMinus = math.sqrt(4.0*D*ts+delta0**2)
                deltaPlus = deltaMinus*rhoMinus_bar/self.rhoplus_bar
                psi = 1+math.sqrt(2.0/math.pi)*self.kbar*deltaPlus
                self.U0 = 0.564*self.sigma0Plus*self.kbar*self.deltaU*self.Atwood/psi
                # Nondimensionalistion for time
                self.time2tau = self.U0/self.lambda_bar
            case _:
                print(f"RMI parameters not implemented for {case}")
                raise NotImplementedError
