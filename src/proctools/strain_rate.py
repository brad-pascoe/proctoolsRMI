# Strain-rate profiles and the resulting strain/expansion/time-remap math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

import numpy as np


class StrainProfile(StrEnum):
    NoStrain = "NoStrain"
    ConstantVelocity = "ConstantVelocity"
    ConstantStrain = "ConstantStrain"

    def suffix(self) -> str:
        if self is StrainProfile.ConstantStrain:
            return "_CS"
        elif self is StrainProfile.ConstantVelocity:
            return "_CV"
        return ""

    def abbrv(self) -> str:
        if self is StrainProfile.ConstantStrain:
            return "CS"
        elif self is StrainProfile.ConstantVelocity:
            return "CV"
        return ""

    def strain_label(self, nondim_strain: float, precision: int = 2) -> str:
        if self is StrainProfile.ConstantStrain:
            return rf"$\widehat{{S}}={nondim_strain:.{precision}f}$"
        elif self is StrainProfile.ConstantVelocity:
            return rf"$\widehat{{S}}_0={nondim_strain:.{precision}f}$"
        return ""


@dataclass
class StrainRateInfo(ABC):
    strain_rate: float
    initial_strain_time: float = 0.0

    profile: ClassVar[StrainProfile]

    def _active(self, t):
        return t >= self.initial_strain_time

    def get_strain(self, t):
        t = np.asarray(t, dtype=float)
        result = np.where(
            self._active(t), self._strain(t - self.initial_strain_time), 0.0
        )
        return result if result.ndim else result.item()

    def get_strain_drag(self, t):
        return 0.0

    def get_expansion(self, t: float | np.ndarray) -> float | np.ndarray:
        t = np.asarray(t, dtype=float)
        result = np.where(
            self._active(t), self._expansion(t - self.initial_strain_time), 1.0
        )
        return result if result.ndim else result.item()

    @abstractmethod
    def _strain(self, dt): ...

    @abstractmethod
    def _expansion(self, dt): ...


class NoStrainRate(StrainRateInfo):
    profile: ClassVar[StrainProfile] = StrainProfile.NoStrain

    def _strain(self, dt):
        return 0.0

    def _expansion(self, dt):
        return 1.0


class ConstantStrainRate(StrainRateInfo):
    """Strain rate held fixed: S(t) = S0."""

    profile: ClassVar[StrainProfile] = StrainProfile.ConstantStrain

    def _strain(self, dt):
        return self.strain_rate

    def _expansion(self, dt):
        return np.exp(self.strain_rate * dt)


class ConstantVelocity(StrainRateInfo):
    """Strain velocity held fixed: S(t) = S0 / (1 + S0*t)."""

    profile: ClassVar[StrainProfile] = StrainProfile.ConstantVelocity

    def _strain(self, dt):
        return self.strain_rate / (1 + self.strain_rate * dt)

    def get_strain_drag(self, t):
        return -(self.get_strain(t) ** 2)

    def _expansion(self, dt):
        return 1 + self.strain_rate * dt
