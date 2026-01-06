import os
import pandas as pd
import re
from proctools.filereader.custom import load_tecplot
from proctools.rmi import RMI_Parameters


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


def load_results_cross(folder: str,RMI: RMI_Parameters = None) -> pd.DataFrame:
    results_cross_filename = "results_cross.dat"
    results_cross_cols = ["Time","XCross","TransverseL","TransverseLAlt"]
    results_cross_file = os.path.join(folder,results_cross_filename)
    results_cross_data = pd.read_fwf(results_cross_file,header=None,names=results_cross_cols,usecols=range(3))

    if RMI is not None:
        results_cross_data['Tau'] = results_cross_data['Time']*RMI.time2tau
        results_cross_data['L'] = results_cross_data['TransverseL']/RMI.lambda_bar
    return results_cross_data


def load_mixed_mass(folder: str, time2tau: float = 1, mixedMassNonDim: float = 1.0, rmi_params: RMI_Parameters = None) -> pd.DataFrame:
    import math

    if rmi_params is not None:
        time2tau = rmi_params.time2tau
        # mixedMassNonDim = 1.0/(rmi_params.rhoplus_bar*rmi_params.lambda_bar*(2.0*math.pi)**2)
        mixedMassNonDim = 1.0/(4.0*rmi_params.rhoplus_bar*rmi_params.lambda_bar*(2.0*math.pi)**2)
    mixed_mass_filename = "results_mixed_mass.dat"
    mixed_mass_cols = ["Time", "MixedMass","Psi"]
    mixed_mass_file = os.path.join(folder,mixed_mass_filename)
    mixed_mass_data = pd.read_fwf(mixed_mass_file,header=None,names=mixed_mass_cols)
    mixed_mass_data["Tau"] = mixed_mass_data["Time"]*time2tau
    mixed_mass_data["MixedMass"] *= mixedMassNonDim
    return mixed_mass_data


def load_spectrum_data(file: str, rmi_params: RMI_Parameters = None) -> pd.DataFrame:
    from math import pi
    spectrum_cols = ["X", "Wavenumber","Ex","Ey","Ez"]
    spectrum_data = pd.read_fwf(file, header=None, names=spectrum_cols)
    spectrum_data['Transverse'] = 0.5*(spectrum_data['Ey']+spectrum_data['Ez'])
    spectrum_data['Anisotropy'] = spectrum_data['Ex']/spectrum_data['Transverse']

    if rmi_params is not None:
        KE_nondim = 1.0/(0.5*rmi_params.rhoplus_bar*rmi_params.U0**2)  # *rmi_params.lambda_bar*(2*pi)**2
        spectrum_data['Ex'] *= KE_nondim
        spectrum_data['Ey'] *= KE_nondim
        spectrum_data['Ez'] *= KE_nondim
        spectrum_data['Transverse'] *= KE_nondim
        spectrum_data['Wavenumber'] /= rmi_params.kbar
    return spectrum_data


def load_decomposed_spectrum_data(file: str, rmi_params: RMI_Parameters = None) -> pd.DataFrame:
    spectrum_cols = ["Wavenumber","Ey","Ez","EyD","EzD","EyS","EzS"]
    spectrum_data = pd.read_fwf(file, header=None, names=spectrum_cols)
    spectrum_data['Transverse'] = 0.5*(spectrum_data['Ey']+spectrum_data['Ez'])
    spectrum_data['Dilatational'] = 0.5*(spectrum_data['EyD'] + spectrum_data['EzD'])
    spectrum_data['Solenoidal'] = 0.5*(spectrum_data['EyS'] + spectrum_data['EzS'])

    if rmi_params is not None:
        KE_nondim = 1.0/(0.5*rmi_params.rhoplus_bar*rmi_params.U0**2)  # *rmi_params.lambda_bar*(2*pi)**2
        spectrum_data['Ey'] *= KE_nondim
        spectrum_data['Ez'] *= KE_nondim
        spectrum_data['Transverse'] *= KE_nondim
        spectrum_data['Dilatational'] *= KE_nondim
        spectrum_data['Solenoidal'] *= KE_nondim
        spectrum_data['Wavenumber'] /= rmi_params.kbar
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


def load_favre_stress_data(case_folder: str, time: float, time2tau: float = 1, stress_scaling: float = 1, rmi_param: RMI_Parameters = None) -> pd.DataFrame:

    if rmi_param is not None:
        time2tau = rmi_param.time2tau
        stress_scaling = 1.0/rmi_param.U0**2
    rs_file = os.path.join(case_folder,"ReynoldsStress",f"{time:.8f}_Favre.dat")
    rs_cols = ["Time","u1u1","u2u2","u3u3","u1u2","u1u3","u2u3"]
    rs_data = pd.read_fwf(rs_file,usecols=range(7))
    # rs_data = pd.read_fwf(rs_file,header=None,names=rs_cols,usecols=range(7))
    # rs_data['Tau'] = rs_data['Time']*time2tau
    for col in rs_cols[1:]:
        rs_data[col] *= stress_scaling
    return rs_data
