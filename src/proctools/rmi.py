# Key functions and values for quarterscale analysis
import math
import numpy as np
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Self


class RMI_Cases(StrEnum):
    StandardTheta = "StandardTheta"
    QuarterTheta = "QuarterTheta"
    WalchliSingleMode = "WalchliSingleMode"
    PascoeSingleMode = "PascoeSingleMode"
    StandardThetaDNS697 = "StandardThetaDNS697"


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
    deltaU: float = 0.0
    Us: float = 0.0
    C: float = 0.0
    CAlt: float = 0.0
    sigma0Plus: float = 0.0
    # RMI
    U0: float = 0.0
    time2tau: float = 0.0

    @classmethod
    def from_case(cls, case: RMI_Cases) -> Self:
        try:
            builder = _CASE_BUILDERS[case]
        except KeyError:
            raise NotImplementedError(f"RMI parameters not implemented for {case}") from None
        return cls(**builder())


def _standard_fluid_pair(n_min: float) -> dict:
    """Shared setup for the cases built on the standard rho=1.80/5.22 fluid pair.

    n_min is the number of smallest wavelengths across the domain width L
    (e.g. 8 for StandardTheta, 32 for QuarterTheta).
    """
    L = 2.0 * math.pi
    lambda_min = L / n_min
    lambda_bar = np.sqrt(12.0 / 7.0) * lambda_min
    kbar = 2.0 * math.pi / lambda_bar
    sigma0 = 0.1 * lambda_min

    Atwood = (5.22 - 1.80) / (5.22 + 1.80)
    rhoplus_bar = 0.5 * (1.80 + 5.22)
    deltaU = 291.575
    Us = 434.6
    C = 1 - deltaU / Us
    CAlt = 0.576
    # Equation 11
    sigma0Plus = C * sigma0
    U0 = 0.564 * sigma0Plus * kbar * deltaU * Atwood
    time2tau = U0 / lambda_bar

    return dict(
        L=L, lambda_bar=lambda_bar, kbar=kbar, sigma0=sigma0,
        Atwood=Atwood, rhoplus_bar=rhoplus_bar, deltaU=deltaU, Us=Us,
        C=C, CAlt=CAlt, sigma0Plus=sigma0Plus, U0=U0, time2tau=time2tau,
    )


def _build_standard_theta() -> dict:
    return _standard_fluid_pair(n_min=8.0)


def _build_quarter_theta() -> dict:
    return _standard_fluid_pair(n_min=32.0)


def _build_standard_theta_dns697() -> dict:
    params = _standard_fluid_pair(n_min=8.0)

    lambda_min = params["L"] / 8.0
    rhoMinus_bar = 0.5 * (3.0 + 1.0)
    delta0 = lambda_min / (4.0 * math.sqrt(math.pi))
    D = 0.1 / rhoMinus_bar
    ts = 0.0011
    deltaMinus = math.sqrt(4.0 * D * ts + delta0 ** 2)
    deltaPlus = deltaMinus * rhoMinus_bar / params["rhoplus_bar"]
    psi = 1 + math.sqrt(2.0 / math.pi) * params["kbar"] * deltaPlus

    params["U0"] = 0.564 * params["sigma0Plus"] * params["kbar"] * params["deltaU"] * params["Atwood"] / psi
    params["time2tau"] = params["U0"] / params["lambda_bar"]
    return params


def _build_pascoe_single_mode() -> dict:
    L = 0.2
    lambda_bar = L
    kbar = 2.0 * math.pi / lambda_bar
    sigma0 = 0.0
    Atwood = 0.5
    rhoplus_bar = 2
    U0 = 1
    time2tau = U0 / lambda_bar

    return dict(
        L=L, lambda_bar=lambda_bar, kbar=kbar, sigma0=sigma0,
        Atwood=Atwood, rhoplus_bar=rhoplus_bar, U0=U0, time2tau=time2tau,
    )


_CASE_BUILDERS: dict[RMI_Cases, Callable[[], dict]] = {
    RMI_Cases.StandardTheta: _build_standard_theta,
    RMI_Cases.QuarterTheta: _build_quarter_theta,
    RMI_Cases.PascoeSingleMode: _build_pascoe_single_mode,
    RMI_Cases.StandardThetaDNS697: _build_standard_theta_dns697,
}
