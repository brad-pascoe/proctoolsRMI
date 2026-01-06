import os
import pandas as pd
from proctools.rmi import RMI_Parameters


def load_integral_width_data(folder: str, time2tau: float = 1, wavelength: float = 1, rmi_parameters: RMI_Parameters = None) -> pd.DataFrame:

    integral_width_filename = "simulation_integral_width.dat"
    integral_width_cols = ["Time","W","Theta","Xi"]
    integral_width_file = os.path.join(folder,integral_width_filename)
    integral_width_data = pd.read_fwf(integral_width_file,header=None,names=integral_width_cols,usecols=range(4))

    if rmi_parameters is not None:
        time2tau = rmi_parameters.time2tau
        wavelength = rmi_parameters.lambda_bar

    integral_width_data["Tau"] = integral_width_data["Time"]*time2tau
    integral_width_data["WNorm"] = integral_width_data["W"]/wavelength
    return integral_width_data


def load_michael_iw_data(folder: str, time2tau: float = 1, wavelength: float = 1, rmi_parameters: RMI_Parameters = None) -> pd.DataFrame:

    integral_width_filename = "simulation_integral_width.dat"
    integral_width_cols = ["Time","W","h","Theta","Xi"]
    integral_width_file = os.path.join(folder,integral_width_filename)
    integral_width_data = pd.read_fwf(integral_width_file,header=None,names=integral_width_cols,usecols=range(5))

    if rmi_parameters is not None:
        time2tau = rmi_parameters.time2tau
        wavelength = rmi_parameters.lambda_bar

    integral_width_data["Tau"] = integral_width_data["Time"]*time2tau
    integral_width_data["WNorm"] = integral_width_data["W"]/wavelength
    return integral_width_data


def load_tke_data(folder: str, time2tau: float = 1, tke_scaling: float = 1, rmi_parameters: RMI_Parameters = None) -> pd.DataFrame:
    import numpy as np

    if rmi_parameters is not None:
        time2tau = rmi_parameters.time2tau
        tke_scaling = 1.0/(0.5*rmi_parameters.rhoplus_bar*rmi_parameters.U0**2*rmi_parameters.lambda_bar*(2*np.pi)**2)

    tke_filename = "simulation_tke.dat"
    tke_cols = ["Time","TKE","TKX","TKY","TKZ"]
    tke_file = os.path.join(folder,tke_filename)
    tke_data = pd.read_fwf(tke_file,header=None,names=tke_cols,usecols=range(5))
    tke_data['Tau'] = tke_data['Time']*time2tau
    tke_data['TKR'] = 2*tke_data['TKX']/(tke_data['TKY']+tke_data['TKZ'])
    tke_data['TKX'] *= tke_scaling
    tke_data['TKY'] *= tke_scaling
    tke_data['TKZ'] *= tke_scaling
    tke_data['TKE'] *= tke_scaling

    return tke_data


def load_michael_tke_data(folder: str, time2tau: float = 1, tke_scaling: float = 1, rmi_parameters: RMI_Parameters = None) -> pd.DataFrame:
    import numpy as np

    if rmi_parameters is not None:
        time2tau = rmi_parameters.time2tau
        tke_scaling = 1.0/(0.5*rmi_parameters.rhoplus_bar*rmi_parameters.U0**2*rmi_parameters.lambda_bar*(2*np.pi)**2)

    tke_filename = "simulation_integral_ke.dat"
    tke_cols = ["Time","TKE","TKX","TKY","TKZ"]
    tke_file = os.path.join(folder,tke_filename)
    tke_data = pd.read_fwf(tke_file,header=None,names=tke_cols,usecols=range(5))
    tke_data['Tau'] = tke_data['Time']*time2tau
    tke_data['TKR'] = 2*tke_data['TKX']/(tke_data['TKY']+tke_data['TKZ'])
    tke_data['TKX'] *= tke_scaling
    tke_data['TKY'] *= tke_scaling
    tke_data['TKZ'] *= tke_scaling
    tke_data['TKE'] *= tke_scaling

    return tke_data


def load_vorticity_data(folder: str, time2tau: float = 1, omega_scaling: float = 1,rmi_params: RMI_Parameters = None) -> pd.DataFrame:

    if rmi_params is not None:
        time2tau = rmi_params.time2tau
        omega_scaling = 1.0/(rmi_params.rhoplus_bar*rmi_params.lambda_bar**(-2)*rmi_params.U0**2)

    vorticity_filename = "simulation_omega.dat"
    vorticity_cols = ["Time","Omega","OmegaX","OmegaY","OmegaZ"]
    vorticity_file = os.path.join(folder,vorticity_filename)
    vorticity_data = pd.read_fwf(vorticity_file,header=None,names=vorticity_cols,usecols=range(5))
    vorticity_data['Tau'] = vorticity_data['Time']*time2tau
    vorticity_data['Omega'] *= omega_scaling
    vorticity_data['OmegaX'] *= omega_scaling
    vorticity_data['OmegaY'] *= omega_scaling
    vorticity_data['OmegaZ'] *= omega_scaling
    return vorticity_data


def load_mix_limits_data(folder: str, time2tau: float = 1, wavelength: float = 1, rmi_params: RMI_Parameters = None) -> pd.DataFrame:
    if rmi_params is not None:
        wavelength = rmi_params.lambda_bar
        time2tau = rmi_params.time2tau

    mix_filename = "simulation_mix_limits.dat"
    mix_cols = ["Time","Xmin","Xmax","XDiff","XCentre"]
    mix_file = os.path.join(folder,mix_filename)
    mix_data = pd.read_fwf(mix_file,header=None,names=mix_cols,usecols=range(5))
    mix_data["Amplitude"] = mix_data["XDiff"]/2.0
    mix_data["AmpNorm"] = mix_data["Amplitude"]/wavelength
    mix_data["Tau"] = mix_data["Time"]*time2tau

    return mix_data


def load_bubblespike_data(folder: str, time2tau: float = 1, wavelength: float = 1, rmi_parameters: RMI_Parameters = None) -> pd.DataFrame:

    if rmi_parameters is not None:
        time2tau = rmi_parameters.time2tau
        wavelength = rmi_parameters.lambda_bar

    bubblespike_filename = "simulation_bubblespike.dat"
    bubblespike_cols = ["Time", "XCentre","Hb","Hs"]
    bubblespike_file = os.path.join(folder,bubblespike_filename)
    bubblespike_data = pd.read_fwf(bubblespike_file,header=None,names=bubblespike_cols)
    bubblespike_data["Tau"] = bubblespike_data["Time"]*time2tau
    bubblespike_data["Ratio"] = bubblespike_data["Hs"]/bubblespike_data["Hb"]
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
