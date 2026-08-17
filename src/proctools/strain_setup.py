# Key functions and values for quarterscale analysis
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
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
class StrainInfo(ABC):
    strain_rate: float
    initial_strain_time: float = 0.0
    direction: str | None = None

    profile: ClassVar[StrainProfile]
    _append_initial_subscript: ClassVar[bool] = False

    def get_suffix(self) -> str:
        return self.profile.suffix()

    def get_label(self, nondim_strain: float, precision: int = 2) -> str:
        subscript = {"Axial": "A", "Transverse": "T"}.get(self.direction, "")
        if self._append_initial_subscript:
            subscript = f"{subscript},0" if subscript else "0"
        return rf"$\widehat{{S}}_{{{subscript}}}={nondim_strain:.{precision}f}$"

    def _active(self, t):
        return t >= self.initial_strain_time

    def get_strain(self, t):
        t = np.asarray(t, dtype=float)
        result = np.where(self._active(t), self._strain(t - self.initial_strain_time), 0.0)
        return result if result.ndim else result.item()

    def get_strain_drag(self, t):
        return 0.0

    def get_expansion(self, t):
        t = np.asarray(t, dtype=float)
        result = np.where(self._active(t), self._expansion(t - self.initial_strain_time), 1.0)
        return result if result.ndim else result.item()

    def get_alternate_time(self, t):
        t = np.asarray(t, dtype=float)
        if self.strain_rate == 0.0:
            return t.copy() if t.ndim else t.item()
        dt = t - self.initial_strain_time
        result = np.where(self._active(t), self.initial_strain_time + self._alternate_time(dt), t)
        return result if result.ndim else result.item()

    def get_axial_linear_model(self, t, U0):
        if self.initial_strain_time != 0:
            print("Linear model assumes initial strain time is zero!")
        if self.strain_rate == 0.0:
            return t * U0
        return self._axial_linear_model(t, U0)

    def get_linear_model(self, t, U0):
        if self.initial_strain_time != 0:
            print("Linear model assumes initial strain time is zero!")
        if self.strain_rate == 0.0:
            return t * U0
        return self._linear_model(t, U0)

    @abstractmethod
    def _strain(self, dt):
        ...

    @abstractmethod
    def _expansion(self, dt):
        ...

    @abstractmethod
    def _alternate_time(self, dt):
        ...

    @abstractmethod
    def _axial_linear_model(self, t, U0):
        ...

    @abstractmethod
    def _linear_model(self, t, U0):
        ...


class NoStrainInfo(StrainInfo):
    profile: ClassVar[StrainProfile] = StrainProfile.NoStrain

    def _strain(self, dt):
        return 0.0

    def _expansion(self, dt):
        return 1.0

    def _alternate_time(self, dt):
        return dt

    def _axial_linear_model(self, t, U0):
        return t * U0

    def _linear_model(self, t, U0):
        return t * U0


class ConstantStrainInfo(StrainInfo):
    """Strain rate held fixed: S(t) = S0."""

    profile: ClassVar[StrainProfile] = StrainProfile.ConstantStrain

    def _strain(self, dt):
        return self.strain_rate

    def _expansion(self, dt):
        return np.exp(self.strain_rate * dt)

    def _alternate_time(self, dt):
        return (1.0 - np.exp(-self.strain_rate * dt)) / self.strain_rate

    def _axial_linear_model(self, t, U0):
        return U0 / self.strain_rate * (np.exp(self.strain_rate * t) - 1)

    def _linear_model(self, t, U0):
        return U0 / self.strain_rate * (np.exp(self.strain_rate * t) - 1.0)


class ConstantVelocityStrainInfo(StrainInfo):
    """Strain velocity held fixed: S(t) = S0 / (1 + S0*t)."""

    profile: ClassVar[StrainProfile] = StrainProfile.ConstantVelocity
    _append_initial_subscript: ClassVar[bool] = True

    def _strain(self, dt):
        return self.strain_rate / (1 + self.strain_rate * dt)

    def get_strain_drag(self, t):
        return -self.get_strain(t) ** 2

    def _expansion(self, dt):
        return 1 + self.strain_rate * dt

    def _alternate_time(self, dt):
        return np.log(1 + self.strain_rate * dt) / self.strain_rate

    def _axial_linear_model(self, t, U0):
        expansion = 1 + self.strain_rate * t
        return U0 / self.strain_rate * expansion * np.log(expansion)

    def _linear_model(self, t, U0):
        return U0 / self.strain_rate * (1.0 + self.strain_rate * t) * np.log(1 + self.strain_rate * t)


def get_strain_case_folders(dir: str | Path,
                            strain_filter: float = None,
                            cfl_filter: float = None,
                            cell_filter: int = None,
                            profile_filter: StrainProfile = None) \
        -> list[tuple[Path, StrainProfile | None, float, float | None, int | None]]:
    dir = Path(dir)
    all_cases = [p.name for p in dir.iterdir()]
    desired_cases = []
    for case in all_cases:
        if 'Strain' not in case:
            continue

        # Detect profile
        if '_CS_' in case:
            profile = StrainProfile.ConstantStrain
        elif '_CV_' in case:
            profile = StrainProfile.ConstantVelocity
        else:
            print(f"No profile detected for case: {case}")
            profile = None
        if profile_filter is not None and profile != profile_filter:
            continue

        # Detect strain rate
        strain = re.search(r"(?<=_S)(\+|\-|\d|\.)+",case)
        if strain is None:
            print(f"No strain-rate detected for case: {case}")
            continue
        else:
            strain = float(strain[0])
        if strain_filter is not None and strain != strain_filter:
            continue

        # Detect CFL
        cfl = re.search(r"(?<=CFL)(\d|\.)+",case)
        if cfl is None:
            print(f"No cfl detected for case: {case}")
        else:
            cfl = float(cfl[0])
        if cfl_filter is not None and cfl != cfl_filter:
            continue

        # Detect cells
        cells = re.search(r"(?<=_)\d+(?=Cells)",case)
        if cells is None:
            print(f"No cells detected for case: {case}")
        else:
            cells = int(cells[0])
        if cell_filter is not None and cells != cell_filter:
            continue

        desired_cases.append((dir/case,profile,strain,cfl,cells))

    return desired_cases
