"""
Created on Tue May 18 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""

import PySimpleGUI as sg

#Define input boxes and buttons
def layout():
    layout = [[sg.Text('Absolute path'), sg.InputText(default_text ="C:/Stvari_KK/INCIT_EV_CI_P_Modul/")],
              [sg.Text('Which year would you like to analyse?'), sg.InputText(default_text="2020",key='AY')],
              [sg.Text('Do you want to analyse the effect of the new charging infrastructure?'), sg.Radio("Yes", 'RADIO3', default=True, key='CIY'),sg.Radio("No", 'RADIO3', key='CIN')],
              [sg.Text('VP matrix file'), sg.InputText(default_text ="testdata_100.xlsx")],
              [sg.Text('Zone type'), sg.Radio("Commercial", 'RADIO1',default=True, key='Commercial'), sg.Radio("Residental",'RADIO1', key='Residental')],
              [sg.Text('Time-dependent parameter:'), sg.Radio("Weekdays", 'RADIO2', default=True, key='Weekdays'), sg.Radio("Weekends", 'RADIO2', key='Weekends')],
              [sg.Checkbox('User defined demand profile', default = False, enable_events = True, key = 'P_profile', size = (15, 1)),
               sg.InputText(default_text ='P_profile_UL.xlsx', size=(15, 1), justification='left', key='P_path')],
              [sg.Checkbox('Consider cumulative RES in kW', default=False, enable_events=True, key='RES',
                           size=(25, 1)),sg.InputText(default_text='100', key='RES_power',size=(15, 1))],
              [sg.Checkbox('Existing Fast CSs (number)', default=False, enable_events=True, key='ECSFT', size=(22, 1)), sg.InputText(default_text='0', key='ECSF', size=(15, 1))],
              [sg.Checkbox('Existing Fast AC CSs (number)', default=False, enable_events=True,key='ECSFACT'), sg.InputText(default_text='0', key='ECSFAC', size=(15, 1))],
              [sg.Checkbox('Existing Slow CSs (number)', default=False, enable_events=True, key='ECSST'),sg.InputText(default_text='0', key='ECSS', size=(15, 1))],
              [sg.Text('Expected share of EV'), sg.InputText(default_text="1")],
              [sg.Text('Transformer nominal power / kVA'), sg.InputText(default_text="5000")],
              [sg.Text('Peak loading / %'), sg.InputText(default_text="83.5")],
              [sg.Text('Estimated gain from investment / €'), sg.InputText(default_text="100000", key="ROIG")],
              [sg.Text('Estimated price for earthworks, installations, etc. / €'), sg.InputText(default_text="50000", key="LW")],
              [sg.Submit(), sg.Cancel()]]

    return layout

#Define theme
def theme():
    theme = 'BluePurple'

    return theme