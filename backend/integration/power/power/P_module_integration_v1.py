"""
Created on Mon May 17 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""
import math
import pandas as pd
#import PySimpleGUI as sg
import sys
import Power_module_KPI as PM

def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)

def P_module(Solar_pp, Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, Stays, Zone_type, Expected_EV, TRNP, ML, PP, PPP,SPP, SPPP, TDP,AY, CIY):
    ############Original
    ##Determine vehicle parking duration
    #Short_stays = ((VP_matrix_short==1).sum(axis=0)*float(Expected_EV)).round(decimals=0)
    #Medium_stays = ((VP_matrix_medium == 1).sum(axis=0) * float(Expected_EV)).round(decimals=0)
    #Long_stays = ((VP_matrix_long == 1).sum(axis=0) * float(Expected_EV)).round(decimals=0)
    #Determine vehicle parking density
    #Short_stays_tmp = [normal_round(VP_matrix_short[i:i+2].mean()) for i in range(0,24,1)]
    #Medium_stays_tmp = [normal_round(VP_matrix_medium[i:i+2].mean()) for i in range(0,24,2)]
    #Long_stays_tmp = [normal_round(VP_matrix_long[i:i+2].mean()) for i in range(0,24,2)]

    #Added on 23.6.2021 by Klemen Knez
    Short_stays_tmp = VP_matrix_short.reset_index(drop=True)
    Medium_stays_tmp = VP_matrix_medium.reset_index(drop=True)
    Long_stays_tmp = VP_matrix_long.reset_index(drop=True)

    #Determine number of charging vehicles
    for i in range(24):
        if Short_stays_tmp.iloc[0,i] > Number_of_CS[0]:
            Short_stays_tmp.iloc[0,i]= Number_of_CS[0]
        if Medium_stays_tmp.iloc[0,i] > Number_of_CS[1]:
            Medium_stays_tmp.iloc[0,i] = Number_of_CS[1]
        if Long_stays_tmp.iloc[0,i] > Number_of_CS[2]:
            Long_stays_tmp.iloc[0,i] = Number_of_CS[2]
    ##Original
    #Stays = [(Short_stays_tmp[i]*50 + Medium_stays_tmp[i]*20 + Long_stays_tmp[i]*3.6) for i in range(24)]
    #Added by Klemen Knez in 23.06.2021 TODO: Hardcoded impact increment
    Stays = Stays*float(Expected_EV)
    Number_of_EVs = [(Short_stays_tmp[i] + Medium_stays_tmp[i]+ Long_stays_tmp[i]) for i in range(24)]
    #Determine zone general demand profile
    P_profile_database = pd.read_excel('datasets/P_module_generated_profiles.xlsx')
    #RES_profile_database = pd.DataFrame(Solar_pp).T
    #if not SPP:
    #    SPPP = 0
    if not (((P_profile_database.iloc[:,0] == Zone_type)*1)+((P_profile_database.iloc[:,1] == int(TRNP))*1)+((P_profile_database.iloc[:,2] == TDP)*1)).max() == 3:
        difference = abs(P_profile_database.iloc[:, 1] - int(TRNP)).idxmin()
        P_profile_tmp = P_profile_database.iloc[difference, 6:] * math.pow(1.018, int(AY) - 2020)
        P_profile = (P_profile_tmp * float(ML) / P_profile_database.iloc[difference, 3]).reset_index(drop=True) 
        #sg.popup('Our database does not contain demand profile for this type of network!')
        #sys.exit()
    #elif PP:
    #    P_profile_tmp = pd.DataFrame(PPP).T
    #    P_profile = P_profile_tmp.iloc[0,:].reset_index(drop=True) - RES_profile_database.iloc[0,:] * int(SPPP)
    else:
        P_profile_tmp = P_profile_database.iloc[(((P_profile_database.iloc[:, 0] == Zone_type) * 1) + ((P_profile_database.iloc[:, 1] == int(TRNP)) * 1) + ((P_profile_database.iloc[:,2] == TDP)*1)).idxmax(), 6:]*math.pow(1.018,int(AY)-2020)
        P_profile = (P_profile_tmp * float(ML) / P_profile_database.iloc[(((P_profile_database.iloc[:,0] == Zone_type) * 1) + ((P_profile_database.iloc[:,1] == int(TRNP)) * 1) + ((P_profile_database.iloc[:,2] == TDP)*1)).idxmax(), 3]).reset_index(drop=True)
                    
    Voltage_coef = float(P_profile_database.iloc[(((P_profile_database.iloc[:, 0] == Zone_type) * 1) + ((P_profile_database.iloc[:, 1] == int(TRNP)) * 1) + ((P_profile_database.iloc[:,2] == TDP)*1)).idxmax(), 4])
    Nominal_voltage = float(P_profile_database.iloc[(((P_profile_database.iloc[:, 0] == Zone_type) * 1) + ((P_profile_database.iloc[:, 1] == int(TRNP)) * 1) + ((P_profile_database.iloc[:,2] == TDP)*1)).idxmax(), 5])
    #Determine borders for traffic light approach
    Border_red = int(TRNP) * 1.2 - P_profile
    Border_Yellow = int(TRNP) - P_profile
    #Determine occupancy
    if Number_of_CS[0]>0:
        Occupancy_of_FastCS = [(Short_stays_tmp[i]/Number_of_CS[0]) for i in range(24)]
    else:
        Occupancy_of_FastCS = [0] * 24
    if Number_of_CS[1] > 0:
        Occupancy_of_FastACCS = [(Medium_stays_tmp[i] / Number_of_CS[1]) for i in range(24)]
    else:
        Occupancy_of_FastACCS = [0] * 24
    if Number_of_CS[2] > 0:
        Occupancy_of_SlowCS = [(Long_stays_tmp[i] / Number_of_CS[2]) for i in range(24)]
    else:
        Occupancy_of_SlowCS = [0] * 24
    #Residual hosting capacity
    if int(TRNP) - (P_profile+Stays).max() > 0:
        RHC = int(TRNP) - int((P_profile+Stays).max())
    else:
        RHC = 0
    #Prepare outputs
    Occupancy = [Occupancy_of_FastCS, Occupancy_of_FastACCS, Occupancy_of_SlowCS]
    Borders = [Border_red, Border_Yellow]

    [Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI, Losses_KPI, ZSCR_KPI, Peak_deviation_KPI] = PM.Power_KPI(P_profile,Stays,Voltage_coef, Nominal_voltage, TRNP, 0)

    return Occupancy, Borders, Stays, RHC, Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI, Losses_KPI, ZSCR_KPI, Peak_deviation_KPI
