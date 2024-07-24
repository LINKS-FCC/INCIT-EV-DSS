"""
Created on Fri May 14 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""

import PySimpleGUI as sg
import ci.CI_module as CI
import power.P_module as P
import gui.Input_window_layout as IWL
import gui.Output_window_layout as OWL
import gui.Graphs as GR
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import pandas as pd
import numpy as np
matplotlib.use('TkAgg')

#Define function which collects input parameters
def Inputs():
    #Define window input layout
    sg.theme(IWL.theme())
    layout = IWL.layout()
    #Open window
    window = sg.Window('Enter inputs', layout).Finalize()
    window.Maximize()
    window.Element('P_path').Update(visible=False)
    window.Element('RES_power').Update(visible=False)
    window.Element('ECSF').Update(visible=False)
    window.Element('ECSFAC').Update(visible=False)
    window.Element('ECSS').Update(visible=False)
    while True:
        event, values = window.read()
        #Give user chance to define path to his own demand profile
        if values['P_profile']:
            window.Element('P_path').Update(visible=True)
        if not values['P_profile']:
            window.Element('P_path').Update(visible=False)
        if values['RES']:
            window.Element('RES_power').Update(visible=True)
        if not values['RES']:
            window.Element('RES_power').Update(visible=False)
        if values['ECSFT']:
            window.Element('ECSF').Update(visible=True)
        if values['ECSFACT']:
            window.Element('ECSFAC').Update(visible=True)
        if values['ECSST']:
            window.Element('ECSS').Update(visible=True)
        if not values['ECSFT']:
            window.Element('ECSF').Update(visible=False)
        if not values['ECSFACT']:
            window.Element('ECSFAC').Update(visible=False)
        if not values['ECSST']:
            window.Element('ECSS').Update(visible=False)


        #When user submits input parameters, execute CI and P module
        #At the end present results in a separate window
        if event == "Submit":
            #Close window
            window.close()
            #Define zone type
            Zone_type = 'Commercial' * values['Commercial'] + 'Residental' * values['Residental']
            #Define time dependency inputs
            Time_dependency = 'Weekdays' * values['Weekdays'] + 'Weekends' * values['Weekends']
            #Execute CI module
            if int(values['CIY']) == 1:
                [New_CSs, Number_of_CS, Initial_costs_pu, Maintenance_costs_pu, Initial_costs, Maintenance_costs, VP_matrix_short, VP_matrix_medium, VP_matrix_long, ROI, CPPV] = CI.CI_module(values[0], values[1], values[2],values['ECSF'],values['ECSFAC'],values['ECSS'],values['CIY'],values['ROIG'])
            else:
                [Number_of_CS, VP_matrix_short,VP_matrix_medium, VP_matrix_long, ROI, CPPV] = CI.CI_module(values[0], values[1], values[2], values['ECSF'],values['ECSFAC'], values['ECSS'],values['CIY'],values['ROIG'])
            #Execute P module
            [Occupancy, Borders, Stays, RHC, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI] = P.P_module(values[0], Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, Zone_type, values[2], values[3], values[4], values['P_profile'], values['P_path'],values['RES'],values['RES_power'],Time_dependency,values['AY'],values['CIY'])
            #Present results
            if int(values['CIY']) == 1:
                Outputs(values[0],New_CSs, Initial_costs_pu, Maintenance_costs_pu, Initial_costs, Maintenance_costs, Occupancy, Borders, Stays, RHC, values['CIY'], values['ECSF'],values['ECSFAC'], values['ECSS'], ROI, values['LW'], values[3], CPPV, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI)
            else:
                Outputs(values[0],([0,0,0]), 0, 0, 0, 0, Occupancy, Borders, Stays, RHC, values['CIY'], values['ECSF'],values['ECSFAC'], values['ECSS'], ROI, 0, values[3], CPPV, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI)
            break
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break

    window.close()

#Define function which presents outputs
def Outputs(abs_path,New_CSs, Occupancy, Borders, Stays, RHC, CIY, ECSF, ECSFAC, ECSS, LW, TNP, CPPV, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI,Losses_KPI, ZSCR_KPI, Peak_deviation_KPI):
    Price = np.array(pd.read_excel(abs_path + 'Electricity cost profile.xlsx', header=None), dtype=float)
    Month_electricity_costs = np.sum((np.array(Stays, dtype=float)*Price[0]))
    #CAPEX = Initial_costs + int(LW)
    #OPEX = Maintenance_costs + int(Month_electricity_costs*12)
    Energy_consumption = np.round(np.sum(Stays))

    CP_relative_use_24 = int((np.array(Occupancy[0]).mean()+np.array(Occupancy[1]).mean()+np.array(Occupancy[2]).mean())/3*100)
    CP_relative_use_16 = int((np.array(Occupancy[0][5:21]).mean()+np.array(Occupancy[1][5:21]).mean()+np.array(Occupancy[2][5:21]).mean())/3*100)

    sg.theme(OWL.theme())
    if int(CIY) == 1:
       #layout = OWL.layout(New_CSs, Initial_costs_pu, Maintenance_costs_pu, Initial_costs, RHC, ECSF, ECSFAC, ECSS, ROI, CAPEX, OPEX, TNP, Energy_consumption, CP_relative_use_24, CP_relative_use_16, CPPV, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI)
       outputs = OWL.layout(New_CSs,RHC, ECSF, ECSFAC, ECSS,
                        TNP, Energy_consumption, CP_relative_use_24, CP_relative_use_16, CPPV,
                           Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI)

    else:
        #layout = OWL.layout_noCI(RHC, TNP, Energy_consumption, CP_relative_use_24, CP_relative_use_16, CPPV)
        outputs = OWL.layout_noCI(RHC, TNP, Energy_consumption, CP_relative_use_24, CP_relative_use_16, CPPV)

    outputs=[Occupancy[0]*100,Occupancy[1]*100,Occupancy[2]*100,Borders[0],Borders[1],Stays,Price,outputs]
    return outputs
    ##Open window
    ##window = sg.Window('Analysis report', layout, font='Courier 12',scrollable=True).Finalize()
    ##window.Maximize()
    #window = sg.Window("Analysis report", resizable=True).Layout([[sg.Column(layout=layout,size=(1000,800), scrollable=True)]]).Finalize()
    ##window.Maximize()
    ##Draw occupacy graph
    #fig = GR.Occupacy_graph(Occupancy)
    #fig_canvas_agg = draw_figure(window['-CANVAS1-'].TKCanvas, fig)
    ##Draw Zone_CS_load_graph
    #fig = GR.Zone_CS_load_graph(Borders, Stays)
    #fig_canvas_agg = draw_figure(window['-CANVAS2-'].TKCanvas, fig)
    #fig = GR.Electricity_costs(abs_path,Stays)
    #fig_canvas_agg = draw_figure(window['-CANVAS3-'].TKCanvas, fig)
    #while True:
    #    event, values = window.read()
    #    if event == 'Repeat analysis':
    #        #Close window
    #        window.close()
    #        #Open inputs window
    #        Inputs()
    #    elif event =='Exit' or event == sg.WIN_CLOSED:
    #        break
    #window.close()
#
#Define function for drawing figure
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

#Initialisation
#Inputs()
