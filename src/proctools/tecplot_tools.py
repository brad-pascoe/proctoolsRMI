import tecplot
import pandas as pd
from tecplot.constant import PlotType, AxisMode, TextAnchor, CoordSys, ColorMapDistribution


def parse_arguments() -> (str,str):
    import sys
    import getopt

    argList = sys.argv[1:]
    options = 'co:V:'
    long_options = ['Connnect','Output=','Var=']
    # Set default value
    plot_var = 'f1'
    output_style = 'Time'
    try:
        arguments,values = getopt.getopt(argList,options,long_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-c", "--Connect"):
                tecplot.session.connect()
            elif currentArgument in ("-V", "--Var"):
                print(f"Received plotting variable: {currentValue}")
                if currentValue in ('f1','f','volfrac','VolFrac'):
                    plot_var = 'f1'
                elif currentValue in ('Pressure','pressure','p','P'):
                    plot_var = 'Pressure'
                else:
                    print(f"Plotting variable not recognised: {currentValue}")
            elif currentArgument in ("-o", "--Output"):
                if currentValue in ('t','Time','time','T'):
                    output_style = "Time"
                elif currentValue in ('timestep','Timestep','n'):
                    output_style = "Timestep"
                else:
                    print(f"Output style not recognised: {currentValue}")

    except getopt.error as err:
        print(str(err))
    print(f"Plotting for variable: {plot_var}")
    print(f"Output style for files: {output_style}")
    return (plot_var,output_style)


def get_plot3D_files(plot3d_directory: str, output_style="Time") -> (list[str],list[str]):
    import os
    import re
    import numpy as np
    if not os.path.exists(plot3d_directory):
        print(f'\t\tFolder does not exist: {plot3d_directory}')
        return (None,None)

    gridfiles: list[str] = [os.path.join(plot3d_directory,x) for x in os.listdir(plot3d_directory) if not x.startswith('.') if r'.g' in x]
    datafiles: list[str] = [os.path.join(plot3d_directory,x) for x in os.listdir(plot3d_directory) if not x.startswith('.') if r'.f' in x]

    # Sort files depending on case
    if output_style == 'Time':
        gridfiles.sort()
        datafiles.sort()
    elif output_style == "Timestep":
        data_timesteps: list[int] = []
        regex_string: str = r'\d+(?=\.)'
        for f in datafiles:
            f_name = os.path.basename(f)
            time_match = re.match(regex_string,f_name)
            if time_match is None:
                print(f"No match for {f_name}")
            else:
                time_value = time_match[0]
                data_timesteps.append(int(time_value))
        order = np.argsort(data_timesteps)
        datafiles = [datafiles[i] for i in order]

    # order = np.flip(np.argsort(strain_values))
    # cases = [(os.path.join(directory,files[i]),strain_values[i]) for i in order]
    return (gridfiles, datafiles)


def get_plot3D_times_and_zones(datafiles: list[str], output_style='Time') -> (list[str], int):
    import os
    import re

    if output_style == "Time":
        regex_string: str = r'\d+\.\d+(?=\.)'
    elif output_style == "Timestep":
        regex_string: str = r'\d+(?=\.)'
    else:
        print(f"Output style not accepted: {output_style}")
        print("Must be Time or Timestep")

    all_times = []
    unique_times = {}
    for f in datafiles:
        f_name = os.path.basename(f)
        time_match = re.match(regex_string,f_name)
        if time_match is None:
            print(f"No match for {f_name}")
        else:
            time_value = time_match[0]
            if unique_times.get(time_value) is None:
                unique_times[time_value] = 1
            else:
                unique_times[time_value] += 1
            if (output_style == "Time"):
                all_times.append(float(time_value))
            elif (output_style == "Timestep"):
                all_times.append(int(time_value))

    occurences = list(unique_times.values())
    if (min(occurences) != max(occurences)):
        print(f"Inconsistency in time outputs, ranging between ({min(occurences)},{max(occurences)})")
    else:
        zones = occurences[0]
    times = list(unique_times.keys())

    return times, zones


def load_plot3D_data(gridfiles: list[str], datafiles: list[str], frame: tecplot.layout.Frame) -> tecplot.data.dataset:

    frame.activate()
    dataset: tecplot.data.Dataset = tecplot.data.load_plot3d(grid_filenames=gridfiles,
                                                             solution_filenames=datafiles,
                                                             append=False,
                                                             frame=frame,
                                                             include_boundaries=False)
    # for i,zone in enumerate(dataset.zones()):
    #     solution_time = times[i//num_zones]
    #     zone.solution_time = float(solution_time)
    #     zone.strand = i % num_zones
    #     # print(i//num_zones, i % num_zones)
    #     
    # dataset.solution_time_clustering.time_scaling = tecplot.constant.TimeScaling.Linear

    # #!MC 1410
    # $!ExtendedCommand 
    #   CommandProcessorID = 'Strand Editor'
    #   Command = 'ZoneSet=1-204;MultiZonesPerTime=TRUE;ZoneGrouping=Time;GroupSize=4;AssignStrands=TRUE;StrandValue=1;AssignSolutionTime=TRUE;TimeValue=0;DeltaValue=1e-05;TimeOption=ConstantDelta;'
    return dataset


def make_standard_variable_names(dataset: tecplot.data.Dataset):
    var_names = ["X","Y","Z","MomentumX","MomentumY","MomentumZ","TotalEnegy","MassFraction1","MassFraction2","f1","f2","Density","Gamma","Pressure","Temperature"]
    for i in range(dataset.num_variables):
        dataset.variable(i).name = var_names[i]
    return


def load_f1_plot3D_data(gridfile: str, datafile: str, frame: tecplot.layout.Frame = None, scaling_factor: tuple[float,float,float] = (1.0,1.0,1.0),varname: str = "f1") -> tecplot.data.Dataset:

    # Load data
    frame.activate()
    dataset: tecplot.data.Dataset = tecplot.data.load_plot3d(grid_filenames=gridfile,
                                                             solution_filenames=datafile,
                                                             append=False, frame=frame,
                                                             include_boundaries=False)

    # Check for correct number of variables (3 coordinates and f1)
    if dataset.num_variables != 4:
        print(f"Expected only four variables, instead there are: {dataset.num_variables}")
        print(dataset.variable_names)

    # Rescale normalised grid
    Xscale, Yscale, Zscale = scaling_factor
    if Xscale != 1.0:
        tecplot.data.operate.execute_equation(f"{{X}}={{X}}*{Xscale}")
    if Yscale != 1.0:
        tecplot.data.operate.execute_equation(f"{{Y}}={{Y}}*{Yscale}")
    if Zscale != 1.0:
        tecplot.data.operate.execute_equation(f"{{Z}}={{Z}}*{Zscale}")

    # Rename the f1 variable to f1 (is loaded in as F1V1 or F2V1 by default)
    dataset.variable(3).name = varname
    return dataset


def load_special_plot3D_data(gridfile: str, datafile: str, frame: tecplot.layout.Frame = None) -> tecplot.data.Dataset:
    import math

    # Load data
    frame.activate()
    dataset: tecplot.data.Dataset = tecplot.data.load_plot3d(grid_filenames=gridfile,
                                                             solution_filenames=datafile,
                                                             append=False, frame=frame,
                                                             include_boundaries=False)

    # Check for correct number of variables (3 coordinates and f1)
    if dataset.num_variables != 5:
        print(f"Expected only five variables, instead there are: {dataset.num_variables}")
        print(dataset.variable_names)

    # Rename the f1 variable to f1 (is loaded in as F1V1 or F2V1 by default)
    # tecplot.data.operate.execute_equation(f"{{X}}={2.8*math.pi}-{{X}}")
    dataset.variable(3).name = r"$f_1$"
    dataset.variable(4).name = "Pressure"
    tecplot.data.operate.execute_equation("{Pressure}={Pressure}/1000")
    return dataset


def read_scaling_factor_file(case_dir: str,
                             f1_folder: str = "f1Plot3D",
                             scaling_filename:str = "scaling_factor.dat") -> pd.DataFrame:
    import os
    scaling_file = os.path.join(case_dir,f1_folder,scaling_filename)
    scaling_file_cols = ('Time','XScale','YScale','ZScale')
    scaling_data = pd.read_fwf(scaling_file,header=None,names=scaling_file_cols)
    return scaling_data


def extract_scaling_factor(filename: str, scaling_data: pd.DataFrame,varname="f1") -> tuple[float,float,float]:
    import os
    import re

    XScale = 1.0
    YScale = 1.0
    ZScale = 1.0

    basename = os.path.basename(filename)
    number_search = re.search(rf".+(?=(_{varname}).all.f)",basename)
    if number_search:
        time_value = float(number_search[0])
        time_data = scaling_data[scaling_data['Time'] == time_value]
        XScale = time_data.iloc[0]['XScale']
        YScale = time_data.iloc[0]['YScale']
        ZScale = time_data.iloc[0]['ZScale']

    return (XScale,YScale,ZScale)


def plot_f1_isosurface(frame: tecplot.layout.Frame, dataset: tecplot.data.Dataset, surface_value: float = 0.001,varname="f1") -> tecplot.plot.Cartesian3DFieldPlot:
    from tecplot.constant import PlotType, ColorMapDistribution, SurfacesToPlot, IsoSurfaceSelection
    import numpy as np

    plot: tecplot.plot.Cartesian3DFieldPlot = frame.plot(PlotType.Cartesian3D)
    axes = plot.axes

    # Set-up so x is in the vertical direction
    axes.x_axis.variable = dataset.variable('Y')
    axes.y_axis.variable = dataset.variable('Z')
    axes.z_axis.variable = dataset.variable('X')
    # Define isosurface values
    lower_surface = surface_value
    upper_surface = 1.0-surface_value
    if lower_surface > upper_surface:
        lower_surface, upper_surface = upper_surface,lower_surface

    plot.show_contour = True
    plot.activate()
    plot.show_edge = True
    plot.show_shade = False
    plot.show_isosurfaces = True
    plot.axes.orientation_axis.show = False
    # print(f"plot view width is {plot.view.width}")
    # print(f"plot view distance is {plot.view.distance}")
    # Plot volume fraction
    contour: tecplot.plot.ContourGroup = plot.contour(0)
    contour.variable = dataset.variable(varname)
    contour.colormap_name = 'Diverging - Blue/Red'
    contour.levels.reset_levels(np.linspace(lower_surface,upper_surface,15))  # .reset_to_nice()
    contour.legend.show = False
    contour.colormap_filter.distribution = ColorMapDistribution.Continuous

    # Apply cutoff
    cutoff: tecplot.plot.ContourColorCutoff = plot.contour(0).color_cutoff
    cutoff.include_min = True
    cutoff.include_max = True
    cutoff.max = upper_surface
    cutoff.min = lower_surface

    iso: tecplot.plot.IsosurfaceGroup = plot.isosurface(0)
    iso.show = True
    iso.definition_contour_group = plot.contour(0)
    iso.isosurface_selection = IsoSurfaceSelection.TwoSpecificValues
    iso.isosurface_values = [lower_surface,upper_surface]
    iso.contour.show = True
    iso.contour.flood_contour_group = plot.contour(0)

    for z in dataset.zones():
        fmap = plot.fieldmap(z)
        fmap.contour.flood_contour_group = plot.contour(0)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

    plot.view.width = 15

    return plot


def annotate_frame(frame: tecplot.layout.Frame, text_str: str, pos: tuple[float,float] = (1,1),size: int = 24) -> tecplot.annotation.Text:
    frame.activate()
    # tau_text = frame.add_text(r"Dummy")
    # print(tau_text)
    # tau_text.position = (75,25)
    # tau_text.type = tecplot.constant.TextType.LaTeX
    # tau_text.font.size = 24
    # tau_text.font.bold = True

    text = frame.add_text(text_str)
    text.anchor = tecplot.constant.TextAnchor.Center
    # print('added text')
    text.type = tecplot.constant.TextType.LaTeX
    # print('latex text')
    text.position = pos
    # print('set pos')
    text.font.size = size
    # print('set size')
    return text
