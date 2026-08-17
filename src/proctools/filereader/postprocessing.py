import os
import math
import pandas as pd
import re
from proctools.filereader.custom import load_tecplot
from proctools.rmi import RMI_Parameters


def _time2tau_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    return rmi_parameters.time2tau if rmi_parameters is not None else 1.0


def _wavelength_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    return rmi_parameters.lambda_bar if rmi_parameters is not None else 1.0


def _mixed_mass_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    if rmi_parameters is None:
        return 1.0
    return 1.0/(4.0*rmi_parameters.rhoplus_bar*rmi_parameters.lambda_bar*(2.0*math.pi)**2)


def _ke_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    if rmi_parameters is None:
        return 1.0
    return 1.0/(0.5*rmi_parameters.rhoplus_bar*rmi_parameters.U0**2)


def _kbar_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    return rmi_parameters.kbar if rmi_parameters is not None else 1.0


def _stress_scaling(rmi_parameters: RMI_Parameters | None) -> float:
    return 1.0/rmi_parameters.U0**2 if rmi_parameters is not None else 1.0


def load_planar_average_tecdata(folder,time):
    planar_average_folder = "PlanarAverage"
    planar_average_files = [x for x in os.listdir(os.path.join(folder,planar_average_folder)) if 'PlanarAverage.tec.dat' in x]
    for file in planar_average_files:
        file_time = float(re.findall('(.+).PlanarAverage.tec.dat',file)[0])
        if (file_time != time):
            continue
        planar_average_file = os.path.join(folder,planar_average_folder,file)
        planar_average_data = load_tecplot(planar_average_file,True,True)
        return planar_average_data
    raise FileNotFoundError


def load_results_cross(folder: str) -> pd.DataFrame:
    results_cross_filename = "results_cross.dat"
    results_cross_cols = ["Time","XCross","TransverseL","TransverseLAlt"]
    results_cross_file = os.path.join(folder,results_cross_filename)
    return pd.read_fwf(results_cross_file,header=None,names=results_cross_cols,usecols=range(3))


def nondimensionalise_results_cross(results_cross_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    results_cross_data['Tau'] = results_cross_data['Time']*_time2tau_scaling(rmi_parameters)
    results_cross_data['L'] = results_cross_data['TransverseL']/_wavelength_scaling(rmi_parameters)
    return results_cross_data


def load_mixed_mass(folder: str) -> pd.DataFrame:
    mixed_mass_filename = "results_mixed_mass.dat"
    mixed_mass_cols = ["Time", "MixedMass","Psi"]
    mixed_mass_file = os.path.join(folder,mixed_mass_filename)
    return pd.read_fwf(mixed_mass_file,header=None,names=mixed_mass_cols)


def nondimensionalise_mixed_mass(mixed_mass_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    mixed_mass_data["Tau"] = mixed_mass_data["Time"]*_time2tau_scaling(rmi_parameters)
    mixed_mass_data["MixedMass"] *= _mixed_mass_scaling(rmi_parameters)
    return mixed_mass_data


def load_spectrum_data(file: str) -> pd.DataFrame:
    spectrum_cols = ["X", "Wavenumber","Ex","Ey","Ez"]
    spectrum_data = pd.read_fwf(file, header=None, names=spectrum_cols)
    spectrum_data['Transverse'] = 0.5*(spectrum_data['Ey']+spectrum_data['Ez'])
    spectrum_data['Anisotropy'] = spectrum_data['Ex']/spectrum_data['Transverse']
    return spectrum_data


def nondimensionalise_spectrum(spectrum_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    ke_scaling = _ke_scaling(rmi_parameters)
    spectrum_data['Ex'] *= ke_scaling
    spectrum_data['Ey'] *= ke_scaling
    spectrum_data['Ez'] *= ke_scaling
    spectrum_data['Transverse'] *= ke_scaling
    spectrum_data['Wavenumber'] /= _kbar_scaling(rmi_parameters)
    return spectrum_data


def load_decomposed_spectrum_data(file: str) -> pd.DataFrame:
    spectrum_cols = ["Wavenumber","Ey","Ez","EyD","EzD","EyS","EzS"]
    spectrum_data = pd.read_fwf(file, header=None, names=spectrum_cols)
    spectrum_data['Transverse'] = 0.5*(spectrum_data['Ey']+spectrum_data['Ez'])
    spectrum_data['Dilatational'] = 0.5*(spectrum_data['EyD'] + spectrum_data['EzD'])
    spectrum_data['Solenoidal'] = 0.5*(spectrum_data['EyS'] + spectrum_data['EzS'])
    return spectrum_data


def nondimensionalise_decomposed_spectrum(spectrum_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    ke_scaling = _ke_scaling(rmi_parameters)
    spectrum_data['Ey'] *= ke_scaling
    spectrum_data['Ez'] *= ke_scaling
    spectrum_data['Transverse'] *= ke_scaling
    spectrum_data['Dilatational'] *= ke_scaling
    spectrum_data['Solenoidal'] *= ke_scaling
    spectrum_data['Wavenumber'] /= _kbar_scaling(rmi_parameters)
    return spectrum_data


def load_bubblespike_data(folder: float, time2tau: float = 1, wavelength: float = 1) -> pd.DataFrame:
    bubblespike_filename = "results_bubblespike.dat"
    bubblespike_cols = ["Time", "hBubble","hSpike","hb0","hs0","hb1","hs1","hb2","hs2","hb3","hs3"]
    bubblespike_file = os.path.join(folder,bubblespike_filename)
    bubblespike_data = pd.read_fwf(bubblespike_file,header=None,names=bubblespike_cols,usecols=range(11))
    bubblespike_data["Tau"] = bubblespike_data["Time"]*time2tau
    bubblespike_data["hBubble"] /= wavelength
    bubblespike_data["hSpike"] /= wavelength
    for i in range(4):
        bubblespike_data[f"hb{i}"] /= wavelength
        bubblespike_data[f"hs{i}"] /= wavelength
    bubblespike_data["Bubble"] = 1.1*bubblespike_data["hb2"]
    bubblespike_data["Spike"] = 1.1*bubblespike_data["hs2"]
    return bubblespike_data


def load_planar_average_data(folder,time):
    planar_average_folder = "PlanarAverage"
    planar_average_cols = ["X","FavreU","FavreV","FavreW","Pressure","Y1","f1","Density","TKE","TKE2","MeanU","MeanV","MeanW","f1f2"]
    planar_average_files = [x for x in os.listdir(os.path.join(folder,planar_average_folder)) if '.PlanarAverage.dat' in x]
    for file in planar_average_files:
        file_time = float(re.findall('.+(?=.PlanarAverage.dat)',file)[0])
        if (file_time != time):
            continue
        planar_average_file = os.path.join(folder,planar_average_folder,file)
        planar_average_data = pd.read_fwf(planar_average_file,header=None,names=planar_average_cols)
        return planar_average_data
    raise FileNotFoundError


def load_planar_average_dataV2(folder,time):
    planar_average_folder = "PlanarAverage"
    planar_average_cols = ["X","FavreU","FavreV","FavreW","Pressure","Y1","f1","Density","TKE","TKE2","MeanU","MeanV","MeanW","f1f2","Energy"]
    planar_average_files = os.listdir(os.path.join(folder,planar_average_folder))
    for file in planar_average_files:
        file_time = float(re.findall('.+(?=.PlanarAverage2.dat)',file)[0])
        if (file_time != time):
            continue
        planar_average_file = os.path.join(folder,planar_average_folder,file)
        planar_average_data = pd.read_fwf(planar_average_file,header=None,names=planar_average_cols)
        return planar_average_data


def load_tke_data(folder: str, time2tau: float = 1, tke_scaling: float = 1) -> pd.DataFrame:
    tke_filename = "results_tke.dat"
    tke_cols = ["Time","TKX","TKY","TKZ"]
    tke_file = os.path.join(folder,tke_filename)
    tke_data = pd.read_fwf(tke_file,header=None,names=tke_cols,usecols=range(4))
    tke_data['Tau'] = tke_data['Time']*time2tau
    tke_data['TKX'] *= tke_scaling
    tke_data['TKY'] *= tke_scaling
    tke_data['TKZ'] *= tke_scaling
    tke_data["TKE"] = tke_data["TKX"]+tke_data["TKY"]+tke_data["TKZ"]
    return tke_data


def load_favre_stress_data(case_folder: str, time: float) -> pd.DataFrame:
    rs_file = os.path.join(case_folder,"ReynoldsStress",f"{time:.8f}_Favre.dat")
    return pd.read_fwf(rs_file,usecols=range(7))


def nondimensionalise_favre_stress(rs_data: pd.DataFrame, rmi_parameters: RMI_Parameters | None = None) -> pd.DataFrame:
    stress_scaling = _stress_scaling(rmi_parameters)
    stress_cols = ["u1u1","u2u2","u3u3","u1u2","u1u3","u2u3"]
    for col in stress_cols:
        rs_data[col] *= stress_scaling
    return rs_data
