import os
import numpy as np
import pandas as pd
from proctools.rmi import RMI_Parameters


def _time2tau_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    return rmi_parameters.time2tau if rmi_parameters is not None else 1.0


def _wavelength_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    return rmi_parameters.lambda_bar if rmi_parameters is not None else 1.0


def _tke_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    if rmi_parameters is None:
        return 1.0
    return 1.0/(0.5*rmi_parameters.rhoplus_bar*rmi_parameters.U0**2*rmi_parameters.lambda_bar*(2*np.pi)**2)


def _omega_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    if rmi_parameters is None:
        return 1.0
    return 1.0/(rmi_parameters.rhoplus_bar*rmi_parameters.lambda_bar**(-2)*rmi_parameters.U0**2)


def load_integral_width_data(folder: str) -> pd.DataFrame:
    integral_width_filename = "simulation_integral_width.dat"
    integral_width_cols = ["Time","W","Theta","Xi"]
    integral_width_file = os.path.join(folder,integral_width_filename)
    return pd.read_fwf(integral_width_file,header=None,names=integral_width_cols,usecols=range(4))


def load_michael_iw_data(folder: str) -> pd.DataFrame:
    integral_width_filename = "simulation_integral_width.dat"
    integral_width_cols = ["Time","W","h","Theta","Xi"]
    integral_width_file = os.path.join(folder,integral_width_filename)
    return pd.read_fwf(integral_width_file,header=None,names=integral_width_cols,usecols=range(5))


def nondimensionalise_integral_width(integral_width_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    integral_width_data["Tau"] = integral_width_data["Time"]*_time2tau_scaling(rmi_parameters)
    integral_width_data["WNorm"] = integral_width_data["W"]/_wavelength_scaling(rmi_parameters)
    return integral_width_data


def load_tke_data(folder: str) -> pd.DataFrame:
    tke_filename = "simulation_tke.dat"
    tke_cols = ["Time","TKE","TKX","TKY","TKZ"]
    tke_file = os.path.join(folder,tke_filename)
    return pd.read_fwf(tke_file,header=None,names=tke_cols,usecols=range(5))


def load_michael_tke_data(folder: str) -> pd.DataFrame:
    tke_filename = "simulation_integral_ke.dat"
    tke_cols = ["Time","TKE","TKX","TKY","TKZ"]
    tke_file = os.path.join(folder,tke_filename)
    return pd.read_fwf(tke_file,header=None,names=tke_cols,usecols=range(5))


def nondimensionalise_tke(tke_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    tke_data['Tau'] = tke_data['Time']*_time2tau_scaling(rmi_parameters)
    tke_data['TKR'] = 2*tke_data['TKX']/(tke_data['TKY']+tke_data['TKZ'])
    scaling = _tke_scaling(rmi_parameters)
    tke_data['TKX'] *= scaling
    tke_data['TKY'] *= scaling
    tke_data['TKZ'] *= scaling
    tke_data['TKE'] *= scaling
    return tke_data


def load_vorticity_data(folder: str) -> pd.DataFrame:
    vorticity_filename = "simulation_omega.dat"
    vorticity_cols = ["Time","Omega","OmegaX","OmegaY","OmegaZ"]
    vorticity_file = os.path.join(folder,vorticity_filename)
    return pd.read_fwf(vorticity_file,header=None,names=vorticity_cols,usecols=range(5))


def nondimensionalise_vorticity(vorticity_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    vorticity_data['Tau'] = vorticity_data['Time']*_time2tau_scaling(rmi_parameters)
    scaling = _omega_scaling(rmi_parameters)
    vorticity_data['Omega'] *= scaling
    vorticity_data['OmegaX'] *= scaling
    vorticity_data['OmegaY'] *= scaling
    vorticity_data['OmegaZ'] *= scaling
    return vorticity_data


def load_mix_limits_data(folder: str) -> pd.DataFrame:
    mix_filename = "simulation_mix_limits.dat"
    mix_cols = ["Time","Xmin","Xmax","XDiff","XCentre"]
    mix_file = os.path.join(folder,mix_filename)
    mix_data = pd.read_fwf(mix_file,header=None,names=mix_cols,usecols=range(5))
    mix_data["Amplitude"] = mix_data["XDiff"]/2.0
    return mix_data


def nondimensionalise_mix_limits(mix_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    mix_data["AmpNorm"] = mix_data["Amplitude"]/_wavelength_scaling(rmi_parameters)
    mix_data["Tau"] = mix_data["Time"]*_time2tau_scaling(rmi_parameters)
    return mix_data


def load_bubblespike_data(folder: str) -> pd.DataFrame:
    bubblespike_filename = "simulation_bubblespike.dat"
    bubblespike_cols = ["Time", "XCentre","Hb","Hs"]
    bubblespike_file = os.path.join(folder,bubblespike_filename)
    bubblespike_data = pd.read_fwf(bubblespike_file,header=None,names=bubblespike_cols)
    bubblespike_data["Ratio"] = bubblespike_data["Hs"]/bubblespike_data["Hb"]
    return bubblespike_data


def nondimensionalise_bubblespike(bubblespike_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    bubblespike_data["Tau"] = bubblespike_data["Time"]*_time2tau_scaling(rmi_parameters)
    wavelength = _wavelength_scaling(rmi_parameters)
    bubblespike_data['Hb'] /= wavelength
    bubblespike_data['Hs'] /= wavelength
    bubblespike_data['H'] = bubblespike_data['Hb']+bubblespike_data['Hs']
    return bubblespike_data


def load_spherical_mix_limits(folder: str, timeScaling: float = 1.0, radiusScaling: float = 1.0):
    import os
    import pandas as pd
    mix_limits_filename = "MixLimits.dat"
    mix_limits_cols = ["Time","RadiusCentre","RadiusSpike","RadiusBubble","PeakUrRad","RadiusMin2"]
    mix_limits_file = os.path.join(folder,mix_limits_filename)
    if not os.path.exists(mix_limits_file):
        print(f"File {mix_limits_file} not found in directory {folder}")
        return None
    mix_limits_data = pd.read_fwf(mix_limits_file,header=None,names=mix_limits_cols)
    mix_limits_data["Time"] *= timeScaling
    mix_limits_data["RadiusCentre"] *= radiusScaling
    mix_limits_data["RadiusSpike"] *= radiusScaling
    mix_limits_data["RadiusBubble"] *= radiusScaling

    return mix_limits_data
