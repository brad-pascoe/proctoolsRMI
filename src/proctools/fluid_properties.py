# Thermodynamic fluid properties, stability-limited time steps, and isentropic updates
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

UNIVERSAL_GAS_CONSTANT = 8.314462618  # J/(mol*K)


class ViscosityLaw(ABC):
    @abstractmethod
    def get_viscosity(self, temperature: float) -> float:
        ...


class Inviscid(ViscosityLaw):
    def get_viscosity(self, temperature: float) -> float:
        return 0.0


@dataclass
class ConstantViscosity(ViscosityLaw):
    mu_ref: float

    def get_viscosity(self, temperature: float) -> float:
        return self.mu_ref


@dataclass
class PowerLawViscosity(ViscosityLaw):
    """mu(T) = mu_ref * (T/T_ref)**n"""

    mu_ref: float
    T_ref: float
    n: float

    def get_viscosity(self, temperature: float) -> float:
        return self.mu_ref * (temperature / self.T_ref) ** self.n


@dataclass
class FluidProperties:
    density: float
    pressure: float
    gamma: float
    molar_mass: float  # kg/mol
    viscosity: ViscosityLaw

    @property
    def specific_gas_constant(self) -> float:
        return UNIVERSAL_GAS_CONSTANT / self.molar_mass

    @property
    def temperature(self) -> float:
        return self.pressure / (self.density * self.specific_gas_constant)

    @property
    def sound_speed(self) -> float:
        return math.sqrt(self.gamma * self.pressure / self.density)

    @property
    def dynamic_viscosity(self) -> float:
        return self.viscosity.get_viscosity(self.temperature)

    @property
    def kinematic_viscosity(self) -> float:
        return self.dynamic_viscosity / self.density

    def get_inviscid_time_step(self, dx: float, velocity: float, CFL: float = 1.0) -> float:
        return CFL * dx / (abs(velocity) + self.sound_speed)

    def get_viscous_time_step(self, dx: float, n_dims: int = 3, CFL: float = 1.0) -> float:
        nu = self.kinematic_viscosity
        if nu == 0.0:
            return math.inf
        return CFL * dx ** 2 / (2 * n_dims * nu)


def isentropic_expansion(fluid: FluidProperties, expansion_factor: float) -> FluidProperties:
    """New FluidProperties after an isentropic volume change.

    expansion_factor is the linear length-scale ratio L/L0 (as returned by
    StrainRateInfo.get_expansion). Density follows mass conservation over the
    resulting volume ratio (L/L0)**3; pressure follows p/rho**gamma = const.
    The viscosity law is carried over unchanged, but since temperature is
    derived from density/pressure, a temperature-dependent law (e.g.
    PowerLawViscosity) will still report an updated viscosity value.
    """
    density_ratio = 1.0 / expansion_factor ** 3

    return FluidProperties(
        density=fluid.density * density_ratio,
        pressure=fluid.pressure * density_ratio ** fluid.gamma,
        gamma=fluid.gamma,
        molar_mass=fluid.molar_mass,
        viscosity=fluid.viscosity,
    )
