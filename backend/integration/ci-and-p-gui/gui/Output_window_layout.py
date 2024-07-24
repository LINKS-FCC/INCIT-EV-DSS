"""
Created on Tue May 18 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""

import PySimpleGUI as sg

#Define output boxes and buttons
def layout(New_CSs, RHC, ECSF, ECSFAC, ECSS, TNP, EC, CPRU24, CPRU16, CPPV, VDKPI, PDKPI, GRKPI, VVKPI, PVKPI):
     #layout = [
     #   [sg.Button('Repeat analysis'), sg.Button('Exit')],
     #   [sg.Table(
     #       [['Fast CS', ECSF, New_CSs[0], Initial_costs_pu[0], Maintenance_costs_pu[0], Initial_costs],
     #        ['Fast ACCS', ECSFAC, New_CSs[1], Initial_costs_pu[1], Maintenance_costs_pu[1]],
     #        ['Slow CS', ECSS, New_CSs[2], Initial_costs_pu[2], Maintenance_costs_pu[2]]],
     #       headings=['Type of CS','Number of exi. CSs', 'Number of new CSs', 'Initial cost p.u. / €', 'Maintenance prices p.u. / €',
     #                 'Min. initial costs / €'],
     #       col_widths=[12, 19, 18, 24, 28, 25],
     #       row_colors=[(i, 'white', '#808080') for i in range(0, 1)] +
     #                  [(i, 'black', '#808080') for i in range(1, 2)] +
     #                  [(i, 'white', '#808080') for i in range(2, 3)],
     #       num_rows=3,
     #       justification="center",
     #       header_text_color='blue',
     #       auto_size_columns=False,
     #       key='-TABLE-', )],
     #   [sg.Table(
     #       [['Values', str(VDKPI), str(PDKPI), GRKPI, str(VVKPI), str(PVKPI)]],
     #       headings=['P module KPI', 'Vol. drop KPI / %', 'Pow. dem. KPI / %',
     #                 'Requi. grid rein.',
     #                 'Vol. vio. / %', 'Power vio. / %'],
     #       col_widths=[20, 20, 20, 20, 20, 20],
     #       row_colors=[(i, 'white', '#808080') for i in range(0, 1)],
     #       num_rows=1,
     #       justification="center",
     #       header_text_color='blue',
     #       auto_size_columns=False,
     #       key='-TABLE1-', )],
     #   [sg.Text('Residual hosting capacity: '+str(RHC)+' kW ('+str(int(RHC/int(TNP)*100))+'%)')],
     #   [sg.Text('Maximum ROI: ' + str(ROI) + '%')],
     #   [sg.Text('CAPEX: ' + str(CAPEX) + ' €')],
     #   [sg.Text('OPEX per year: ' + str(OPEX) + ' €')],
     #   [sg.Text('Daily energy consumption: ' + str(int(EC)) + ' kWh')],
     #   [sg.Text('CP relative use through whole day: ' + str(CPRU24) + '%')],
     #   [sg.Text('CP relative use 6:00-22:00: ' + str(CPRU16) + '%')],
     #   [sg.Text('CP per vehicle: ' + "{:.2f}".format(CPPV))],
     #   [sg.Canvas(key='-CANVAS1-'), sg.Canvas(key='-CANVAS2-')],
     #   [sg.Canvas(key='-CANVAS3-')]]
#
    #return layout
    return [ECSF, New_CSs[0], ECSFAC, New_CSs[1],
            ECSS, New_CSs[2],
            VDKPI, PDKPI, GRKPI, VVKPI, PVKPI, RHC, int(RHC/int(TNP)*100), EC, CPRU24, CPRU16, CPPV]


def layout_noCI(RHC, TNP, EC, CPRU24, CPRU16, CPPV):
    #layout = [
    #    [sg.Button('Repeat analysis'), sg.Button('Exit')],
    #    [sg.Text('Residual hosting capacity: '+str(RHC)+' kW ('+str(int(RHC/int(TNP)*100))+'%)')],
    #    [sg.Text('Daily energy consumption: ' + str(int(EC)) + ' kWh')],
    #    [sg.Text('CP relative use through whole day: ' + str(CPRU24) + '%')],
    #    [sg.Text('CP relative use 6:00-22:00: ' + str(CPRU16) + '%')],
    #    [sg.Text('CP per vehicle: ' + "{:.2f}".format(CPPV))],
    #    [sg.Canvas(key='-CANVAS1-'), sg.Canvas(key='-CANVAS2-')],
    #    [sg.Canvas(key='-CANVAS3-')]]
    ##return layout
    return [RHC, int(RHC/int(TNP)*100), EC, CPRU24, CPRU16, CPPV]
# Deine theme
def theme():
    theme = 'BluePurple'

    return theme
