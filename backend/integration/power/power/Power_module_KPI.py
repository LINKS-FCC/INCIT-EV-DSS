"""
Created on Thu May 27 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""
import numpy as np

def Power_KPI(P_profile,Stays,Voltage_coef, Nominal_voltage, TNP, RES_profile):
     #Calculate voltage drop KPI
     Voltage_orig = np.array(P_profile)*Voltage_coef + Nominal_voltage
     Voltage_with_CSs = (np.array(P_profile)+np.array(Stays))*Voltage_coef + Nominal_voltage
     Voltage_drop_KPI = int(((Voltage_orig-Voltage_with_CSs)/Voltage_orig).max()*100)

     #Calculate Power demand KPI
     Power_demand_KPI = int((((np.array(Stays)/np.array(P_profile)))*100).max())

     #Calculate grid reinforcement KPI
     Voltage_violations = np.array((Voltage_with_CSs-0.9)<0)
     Power_violations = np.array(((np.array(P_profile)+np.array(Stays))/int(TNP) - 1) > 0)
     All_violations_tmp = Voltage_violations + Power_violations
     All_violations = np.sum((All_violations_tmp > 0).astype(int))
     if All_violations/24 > 0.2:
          GR_KPI = 'High'
     elif (All_violations / 24 < 0.2) and (All_violations / 24 > 0):
          GR_KPI = 'Low'
     else:
          GR_KPI = 'NA'
     if All_violations > 0:
          Voltage_events_KPI = int(np.sum(Voltage_violations) / 24 * 100)
          Power_events_KPI = int(np.sum(Power_violations) / 24 * 100)
     else:
          Voltage_events_KPI = 0
          Power_events_KPI = 0
     #Losses KPI
     Losses_KPI = '2-4%'

     #Zone self_consumption ratio KPI
     ZSCR_KPI = np.array(RES_profile)/(np.array(P_profile)+np.array(Stays))

     #Peak deviation KPI
     Peak_deviation_KPI = ((np.array(Stays)+np.array(P_profile))/np.array(P_profile)-1)*100

     return Voltage_drop_KPI, Power_demand_KPI, GR_KPI, Voltage_events_KPI, Power_events_KPI, Losses_KPI, ZSCR_KPI, Peak_deviation_KPI