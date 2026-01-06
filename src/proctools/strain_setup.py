# Key functions and values for quarterscale analysis
import numpy as np
from enum import Enum


class StrainProfile(Enum):
    NoStrain = 0
    ConstantVelocity = 1
    ConstantStrain = 2

    def __str__(self):
        return self.name

    def suffix(self):
        if self is StrainProfile.ConstantStrain:
            return "_CS"
        elif self is StrainProfile.ConstantVelocity:
            return "_CV"
        else:
            return ""

    def abbrv(self):
        if self is StrainProfile.ConstantStrain:
            return "CS"
        elif self is StrainProfile.ConstantVelocity:
            return "CV"
        else:
            return ""

    def strain_label(self,nondim_strain,precision=2):
        if self is StrainProfile.ConstantStrain:
            return rf"$\widehat{{S}}={nondim_strain:.{precision}f}$"
        elif self is StrainProfile.ConstantVelocity:
            return rf"$\widehat{{S}}_0={nondim_strain:.{precision}f}$"


class StrainInfo():
    def __init__(self,StrainProfile,strain_rate,initial_strain_time=0.0,direction=None):
        self.StrainProfile = StrainProfile
        self.strain_rate = strain_rate
        self.initial_strain_time = initial_strain_time
        self.direction = direction

    def get_suffix(self):
        if self.StrainProfile == StrainProfile.ConstantStrain:
            return "_CS"
        elif self.StrainProfile == StrainProfile.ConstantVelocity:
            return "_CV"
        return ""

    def get_label(self, nondim_strain: float, precision: int = 2) -> str:
        subscript = ""
        if self.direction == "Axial":
            subscript = "A"
        elif self.direction == "Transverse":
            subscript = "T"

        if self.StrainProfile == StrainProfile.ConstantVelocity:
            if subscript == "":
                subscript = "0"
            else:
                subscript += ",0"

        label = rf"$\widehat{{S}}_{{{subscript}}}={nondim_strain:.{precision}f}$"
        return label

    def get_strain(self,t):
        try:
            strain = np.zeros_like(t)
            if self.strain_rate != 0.0:
                for i,t_val in enumerate(t):
                    if t_val < self.initial_strain_time:
                        continue
                    elif self.StrainProfile == StrainProfile.ConstantStrain:
                        strain[i] = self.strain_rate
                    elif self.StrainProfile == StrainProfile.ConstantVelocity:
                        strain[i] = self.strain_rate/(1+self.strain_rate*(t_val-self.initial_strain_time))
        except TypeError:
            if self.strain_rate != 0.0:
                if t < self.initial_strain_time:
                    return 0
                elif self.StrainProfile == StrainProfile.ConstantStrain:
                    strain = self.strain_rate
                elif self.StrainProfile == StrainProfile.ConstantVelocity:
                    strain = self.strain_rate/(1+self.strain_rate*(t-self.initial_strain_time))
        return strain

    def get_strain_drag(self,t):
        if self.StrainProfile == StrainProfile.ConstantStrain:
            return 0
        elif self.StrainProfile == StrainProfile.ConstantVelocity:
            return -self.get_strain(t)**2
        return 0

    def get_expansion(self,t):
        try:
            expansion = np.ones_like(t)
            for i,t_val in enumerate(t):
                if t_val < self.initial_strain_time:
                    continue
                elif self.StrainProfile == StrainProfile.ConstantStrain:
                    expansion[i] = np.exp(self.strain_rate*(t_val-self.initial_strain_time))
                elif self.StrainProfile == StrainProfile.ConstantVelocity:
                    expansion[i] = 1+self.strain_rate*(t_val-self.initial_strain_time)
        except TypeError:
            if self.strain_rate != 0.0:
                if t < self.initial_strain_time:
                    expansion = 1
                elif self.StrainProfile == StrainProfile.ConstantStrain:
                    expansion = np.exp(self.strain_rate*(t-self.initial_strain_time))
                elif self.StrainProfile == StrainProfile.ConstantVelocity:
                    expansion = 1+self.strain_rate*(t-self.initial_strain_time)

        return expansion

    def get_alternate_time(self,t):
        t_hat = t.copy()
        if self.strain_rate == 0.0:
            return t_hat

        for i in range(len(t)):
            if t[i] <= self.initial_strain_time:
                continue
            elif self.StrainProfile == StrainProfile.ConstantStrain:
                t_hat[i] = self.initial_strain_time + (1.0-np.exp(-self.strain_rate*(t[i]-self.initial_strain_time)))/self.strain_rate
            elif self.StrainProfile == StrainProfile.ConstantVelocity:
                t_hat[i] = self.initial_strain_time + np.log(1+self.strain_rate*(t[i]-self.initial_strain_time))/self.strain_rate

        return t_hat

    def get_axial_linear_model(self,t,U0):
        if self.initial_strain_time != 0:
            print("Linear model assumes initial strain time is zero!")

        if self.strain_rate == 0.0:
            theory = t*U0
        elif self.StrainProfile == StrainProfile.ConstantStrain:
            theory = U0/self.strain_rate * (np.exp(self.strain_rate*t)-1)
        elif self.StrainProfile == StrainProfile.ConstantVelocity:
            expansion = 1 + self.strain_rate*t
            theory = U0/self.strain_rate * expansion * np.log(expansion)

        return theory

    def get_linear_model(self,t,U0):
        if self.initial_strain_time != 0:
            print("Linear model assumes initial strain time is zero!")

        if self.strain_rate == 0.0:
            theory = t*U0
        elif self.StrainProfile == StrainProfile.ConstantStrain:
            theory = U0/self.strain_rate * (np.exp(self.strain_rate*t)-1.0)
        elif self.StrainProfile == StrainProfile.ConstantVelocity:
            theory = U0/self.strain_rate * (1.0+self.strain_rate*t)*np.log(1+self.strain_rate*t)

        return theory


def get_strain_case_folders(dir: str,
                            strain_filter: float = None,
                            cfl_filter: float = None,
                            cell_filter: int = None,
                            profile_filter: StrainProfile = None) \
        -> list[str]:
    import os
    import re

    all_cases = os.listdir(dir)
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

        desired_cases.append((os.path.join(dir,case),profile,strain,cfl,cells))

    return desired_cases
