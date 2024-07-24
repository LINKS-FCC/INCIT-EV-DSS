"""
Created on Thu May 13 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""

import pandas as pd
import numpy as np
import math
import os.path
from numpy import random

def normal_round(n):
    if n - math.floor(n) < 0.5 and math.floor(n) > 0:
        return math.floor(n)
    elif n - math.floor(n) < 0.5 and math.floor(n) == 0:
        return 1
    else:
        return math.ceil(n)

def CI_module(CI_database, VP_matrix_all, VP_matrix_short_tmp,VP_matrix_medium_tmp,VP_matrix_long_tmp, Expected_EV, ECSF, ECSFAC, ECSS, CIY, Start_parking_time, Start_energy, End_energy):
    #Load CI Database
    CI_database = pd.DataFrame(CI_database)
    
    #Sort CSs based on nominal power and installation costs
    FCS_database = CI_database.loc[CI_database.iloc[:,1]>20,:].sort_values('installation_cost')
    FACCS_database = CI_database.loc[(CI_database.iloc[:,1]<20) & (CI_database.iloc[:,1]>10),:].sort_values('installation_cost')
    SCS_database = CI_database.loc[CI_database.iloc[:,1]<10,:].sort_values('installation_cost')

    #Create database based on CS type
    if (os.path.exists('datasets/Output database for customer.xlsx'))==False:
        writer = pd.ExcelWriter('outputs/Output database for customer.xlsx', engine='xlsxwriter')
        dfs = {'Fast CS database': FCS_database,'Fast AC CS database': FACCS_database,'Slow CS database': FCS_database }
        for sheetname, df in dfs.items():
            df.to_excel(writer, sheet_name=sheetname, index=False)
            worksheet = writer.sheets[sheetname]  # pull worksheet object
            for idx, col in enumerate(df):  # loop through all columns
                series = df[col]
                max_len = max((
                    series.astype(str).map(len).max(),  # len of largest item
                    len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
                worksheet.set_column(idx, idx, max_len)  # set column width
        writer.save()
    ###UB & M module inputs#####
    VP_matrix_short = VP_matrix_short_tmp.apply(np.ceil)
    VP_matrix_medium = VP_matrix_medium_tmp.apply(np.ceil)
    VP_matrix_long = VP_matrix_long_tmp.apply(np.ceil)

    Number_of_vehicles = VP_matrix_long.sum().sum()+VP_matrix_medium.sum().sum()+VP_matrix_short.sum().sum()
    ################################
    ##Until we have realistic inputs
    #VP_matrix_all= pd.read_excel(abs_path+VP_matrix_file)
    #VP_matrix = VP_matrix_all.iloc[3:,:]
    #sum_tmp = VP_matrix.sum(axis=1)
    #VP_matrix_short = VP_matrix.loc[sum_tmp<5,:]
    #VP_matrix_medium = VP_matrix.loc[((sum_tmp>4) & (sum_tmp<17)),:]
    #VP_matrix_long = VP_matrix.loc[sum_tmp>16,:]
    #Number_of_vehicles = len(VP_matrix_long)-3
    ################################

    #Compute number of new CSs
    if int(CIY) == 1:
        #NFastCS = normal_round(VP_matrix_short.sum(axis=0).mean()*float(Expected_EV)-int(ECSF))
        #NFastACCS = normal_round(VP_matrix_medium.sum(axis=0).mean()*float(Expected_EV)-int(ECSFAC))
        #NSlowCS = normal_round(VP_matrix_long.sum(axis=0).mean()*float(Expected_EV)-int(ECSS))
        NFastCS = normal_round(float(VP_matrix_short.mean(axis=1)*float(Expected_EV)-int(ECSF)))
        if NFastCS < 0:
            NFastCS = 0  
        NFastACCS = normal_round(float(VP_matrix_medium.mean(axis=1)*float(Expected_EV)-int(ECSFAC)))
        if NFastACCS < 0:
            NFastACCS = 0
        NSlowCS = normal_round(float(VP_matrix_long.mean(axis=1)*float(Expected_EV)-int(ECSS)))
        if NSlowCS < 0:
            NSlowCS = 0
        FastCS = int(ECSF) + NFastCS
        FastACCS = int(ECSFAC) + NFastACCS
        SlowCS = int(ECSS) + NSlowCS
        #if NFastCS < 1:
        #    #sg.popup('There is no need for any additional Fast CS. Additional network analysis will include only existing CSs.')
        #    FastCS = int(ECSF)
        #    NFastCS = 0
        #if FastACCS < 1:
        #    #sg.popup('There is no need for any additional Fast AC CS. Additional network analysis will include only existing CSs')
        #    FastACCS = int(ECSFAC)
        #    NFastACCS = 0
        #if SlowCS < 1:
        #    #sg.popup('There is no need for any additional Slow CS. Additional network analysis will include only existing CSs')
        #    SlowCS = int(ECSS)
        #    NSlowCS = 0
        #Determine minimum initial and maintenance costs
        # Prepare outputs
        New_CSs = [NFastCS, NFastACCS, NSlowCS]
        Number_of_CS = [FastCS, FastACCS, SlowCS]

        if Number_of_vehicles != 0:
            CPPV = (NFastCS+NFastACCS+NSlowCS+FastCS+FastACCS+SlowCS)/Number_of_vehicles
        else:
            CPPV = 0

        #Start_parking_time = pd.read_csv()  # 24x24 matrika 24 ur prihoda, 24 različnih ur postanka
        #Start_energy = pd.read_csv()  # 24x24 matrika
        #End_energy = pd.read_csv()  # 24x24 matrika

        Power_slow = SCS_database.iloc[0, 1]  # kW
        Power_medium = FACCS_database.iloc[0, 1]
        Power_fast = FCS_database.iloc[0, 1]

        Number_of_fast_CS = Number_of_CS[0]
        Number_of_medium_CS = Number_of_CS[1]
        Number_of_slow_CS = Number_of_CS[2]

        #Start_parking_time.iloc[Start_parking_time.iloc[:, :] < 0] = 0
        Charging_vehicles = VP_matrix_all.apply(np.ceil)
        Actual_new_vehicles = Start_parking_time.apply(np.ceil)


        #index_fast = np.array(Charging_vehicles.iloc[0:24, 0:5].sum(axis=1) <= Number_of_fast_CS).astype(int)
        #index_medium = np.array(Charging_vehicles.iloc[0:24, 5:17].sum(axis=1) <= Number_of_medium_CS).astype(int)
        #index_slow = np.array(Charging_vehicles.iloc[0:24, 16:24].sum(axis=1) <= Number_of_slow_CS).astype(int)
#
        #for i in range(0, 24):
        #    if index_fast[i] == 0:
        #        Overflow = Charging_vehicles.iloc[0:24, 0:5].sum(axis=1) - Number_of_fast_CS
        #        for j in range(0, Overflow):
        #            Actual_charging_vehicles.iloc[i, random.choice([1, 2, 3, 4])] = Charging_vehicles.iloc[
        #                                                                                i, (np.arange(1., 5.))] - 1
#
        #    if index_medium[i] == 0:
        #        Overflow = Charging_vehicles.iloc[0:24, 5:17].sum(axis=1) - Number_of_medium_CS
        #        for j in range(0, Overflow):
        #            Actual_charging_vehicles.iloc[i, random.choice([1, 2, 3, 4])] = Charging_vehicles.iloc[
        #                                                                                i, (np.arange(5, 17))] - 1
#
        #    if index_slow[i] == 0:
        #        Overflow = Charging_vehicles.iloc[0:24, 16:24].sum(axis=1) - Number_of_slow_CS
        #        for j in range(0, Overflow):
        #            Actual_charging_vehicles.iloc[i, random.choice([1, 2, 3, 4])] = Charging_vehicles.iloc[
        #                                                                                i, (np.arange(5, 17))] - 1

        # Calculate charging time based on power of CS
        Time_of_charging = pd.DataFrame(0, index=range(24),columns=range(24))
        #Time_of_charging.iloc[0:24, 0] = 0
        Energy_needs_to_be_recharged = pd.DataFrame(index=range(24),columns=range(24))
        End_energy_tmp= pd.DataFrame(index=range(24), columns=range(24))
        for i in range(0,24):
            for j in range (0,24):
                if i+j < 23:
                    End_energy_tmp.iloc[i,j] = End_energy.iloc[i+j+1,j]
                else:
                    End_energy_tmp.iloc[i,j] = End_energy.iloc[i+j-23,j]

        Energy_needs_to_be_recharged = End_energy_tmp - Start_energy


        for i in range(0, 24):
            if i > 0:
                Leaving_cars_fast = Charging_vehicles.iloc[i-1, 0:5].sum(axis=0) + Start_parking_time.iloc[i, 0:5].sum(axis=0) - Charging_vehicles.iloc[i, 0:5].sum(axis=0)
                Leaving_cars_medium = Charging_vehicles.iloc[i-1, 5:17].sum(axis=0) + Start_parking_time.iloc[i, 5:17].sum(axis=0) - Charging_vehicles.iloc[i, 5:17].sum(axis=0)
                Leaving_cars_slow = Charging_vehicles.iloc[i-1, 17:24].sum(axis=0) + Start_parking_time.iloc[i, 17:24].sum(axis=0) - Charging_vehicles.iloc[i, 17:24].sum(axis=0)

                if Leaving_cars_slow < 0:
                    Leaving_cars_slow = 0

                if ((Charging_vehicles.iloc[i-1, 0:5].sum(axis=0) - Leaving_cars_fast) >= 0):
                    Number_of_free_CS_fast = np.ceil(Number_of_fast_CS - Charging_vehicles.iloc[i-1, 0:5].sum(axis=0) + Leaving_cars_fast)
                else:
                    Number_of_free_CS_fast = Number_of_fast_CS

                if ((Charging_vehicles.iloc[i-1, 5:17].sum(axis=0) - Leaving_cars_medium) >= 0):
                    Number_of_free_CS_medium = np.ceil(Number_of_medium_CS - Charging_vehicles.iloc[i-1, 5:17].sum(axis=0) + Leaving_cars_medium)
                else:
                    Number_of_free_CS_medium = Number_of_medium_CS

                if ((Charging_vehicles.iloc[i-1, 17:24].sum(axis=0) - Leaving_cars_slow) >= 0):
                    Number_of_free_CS_slow = np.ceil(Number_of_slow_CS - Charging_vehicles.iloc[i-1, 0:5].sum(axis=0) + Leaving_cars_slow)
                else:
                    Number_of_free_CS_slow = Number_of_slow_CS

                index_fast = np.array(Charging_vehicles.iloc[i, 0:5].sum(axis=0) <= Number_of_free_CS_fast).astype(int)
                index_medium = np.array(Charging_vehicles.iloc[i, 5:17].sum(axis=0) <= Number_of_free_CS_medium).astype(int)
                index_slow = np.array(Charging_vehicles.iloc[i, 17:24].sum(axis=0) <= Number_of_free_CS_slow).astype(int)
                if index_fast == 0:
                    possible_chances = [0,1,2,3,4]
                    Overflow = (Start_parking_time.iloc[i, 0:5].sum(axis=0) - Number_of_free_CS_fast).astype(int)
                    for j in range(0, Overflow):
                        if possible_chances:
                            idx = 1
                            while idx == 1:
                                index = random.choice(possible_chances)
                                if Actual_new_vehicles.iloc[i, index] > 0:
                                    Actual_new_vehicles.iloc[i, index] = Actual_new_vehicles.iloc[i, index] - 1
                                    idx = 0
                                else:
                                    possible_chances.remove(index)
                                if not possible_chances:
                                    idx = 0

                if index_medium == 0:
                    possible_chances = [5,6,7,8,9,10,11,12,13,14,15,16]
                    Overflow = (Start_parking_time.iloc[i, 5:17].sum(axis=0) - Number_of_free_CS_medium).astype(int)
                    for j in range(0, Overflow):
                        if possible_chances:
                            idx = 1
                            while idx == 1:
                                index = random.choice(possible_chances)
                                if Actual_new_vehicles.iloc[i, index] > 0:
                                    Actual_new_vehicles.iloc[i, index] = Actual_new_vehicles.iloc[i, index] - 1
                                    idx = 0
                                else:
                                    possible_chances.remove(index)
                                if not possible_chances:
                                    idx = 0


                if index_slow == 0:
                    possible_chances = [17,18,19,20,21,22,23]
                    Overflow = (Start_parking_time.iloc[i, 17:24].sum(axis=0) - Number_of_free_CS_slow).astype(int)
                    for j in range(0, Overflow):
                        if possible_chances:
                            idx = 1
                            while idx == 1:
                                index = random.choice(possible_chances)
                                if Actual_new_vehicles.iloc[i, index] > 0:
                                    Actual_new_vehicles.iloc[i, index] = Actual_new_vehicles.iloc[i, index] - 1
                                    idx = 0
                                else:
                                    possible_chances.remove(index)
                                if not possible_chances:
                                    idx = 0

                for j in range(0, 24):
                        if j < 5:  # Hitra polninica
                            if (Start_parking_time.iloc[i, j] > 0) and (Actual_new_vehicles.iloc[i, j]>0):
                                Time_of_charging.iloc[i, j] = ((Actual_new_vehicles.iloc[i, j]/Start_parking_time.iloc[i, j])*Energy_needs_to_be_recharged.iloc[i, j]) / (Power_fast * Actual_new_vehicles.iloc[i, j] * (j + 1)) * 100
                                if Time_of_charging.iloc[i, j] > 100:
                                    Time_of_charging.iloc[i, j] = 100
                            else:
                                Time_of_charging.iloc[i, j] = 0

                        elif j > 16:  # Počasna polnilnica
                            if (Start_parking_time.iloc[i, j] > 0) and (Actual_new_vehicles.iloc[i, j]>0):
                                Time_of_charging.iloc[i, j] = ((Actual_new_vehicles.iloc[i, j] / Start_parking_time.iloc[i, j]) * Energy_needs_to_be_recharged.iloc[i, j]) / (Power_medium * Actual_new_vehicles.iloc[i, j] * (j + 1)) * 100
                                if Time_of_charging.iloc[i, j] > 100:
                                    Time_of_charging.iloc[i, j] = 100
                            else:
                                Time_of_charging.iloc[i, j] = 0

                        else:  # Srednje hitra polnilnica
                            if (Start_parking_time.iloc[i, j] > 0) and (Actual_new_vehicles.iloc[i, j]>0):
                                Time_of_charging.iloc[i, j] = ((Actual_new_vehicles.iloc[i, j] / Start_parking_time.iloc[i, j]) * Energy_needs_to_be_recharged.iloc[i, j]) / (Power_slow * Actual_new_vehicles.iloc[i, j] * (j + 1)) * 100
                                if Time_of_charging.iloc[i, j] > 100:
                                    Time_of_charging.iloc[i, j] = 100
                            else:
                                Time_of_charging.iloc[i, j] = 0

            else:
                Number_of_free_CS_fast = Number_of_fast_CS - Charging_vehicles.iloc[i, 0:5].sum(axis=0)
                Number_of_free_ACCS_fast = Number_of_medium_CS - Charging_vehicles.iloc[i, 5:17].sum(axis=0)
                Number_of_free_CS_slow = Number_of_slow_CS - Charging_vehicles.iloc[i, 17:24].sum(axis=0)
                if Number_of_free_CS_fast < 0:
                    possible_chances = [0,1, 2, 3, 4]
                    Overflow = (Start_parking_time.iloc[i, 0:5].sum(axis=0) - Number_of_free_CS_fast).astype(int)
                    if Overflow > 0:
                        for j in range(0, Overflow):
                            if possible_chances:
                                idx = 1
                                while idx == 1:
                                    index = random.choice(possible_chances)
                                    if Actual_new_vehicles.iloc[i, index] > 0:
                                        Actual_new_vehicles.iloc[i, index] = Actual_new_vehicles.iloc[i, index] - 1
                                        idx = 0
                                    else:
                                        possible_chances.remove(index)
                                    if not possible_chances:
                                        idx = 0
                if Number_of_free_ACCS_fast < 0:
                    possible_chances = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
                    Overflow = (Start_parking_time.iloc[i, 5:17].sum(axis=0) - Number_of_free_ACCS_fast).astype(int)
                    if Overflow > 0:
                        for j in range(0, Overflow):
                            if possible_chances:
                                idx = 1
                                while idx == 1:
                                    index = random.choice(possible_chances)
                                    if Actual_new_vehicles.iloc[i, index] > 0:
                                        Actual_new_vehicles.iloc[i, index] = Actual_new_vehicles.iloc[i, index] - 1
                                        idx = 0
                                    else:
                                        possible_chances.remove(index)
                                    if not possible_chances:
                                        idx = 0
                if Number_of_free_CS_slow < 0:
                    possible_chances = [17, 18, 19, 20, 21, 22, 23]
                    Overflow = (Start_parking_time.iloc[i, 17:24].sum(axis=0) - Number_of_free_CS_slow).astype(int)
                    if Overflow > 0:
                        for j in range(0, Overflow):
                            if possible_chances:
                                idx = 1
                                while idx == 1:
                                    index = random.choice(possible_chances)
                                    if Actual_new_vehicles.iloc[i, index] > 0:
                                        Actual_new_vehicles.iloc[i, index] = Actual_new_vehicles.iloc[i, index] - 1
                                        idx = 0
                                    else:
                                        possible_chances.remove(index)
                                    if not possible_chances:
                                        idx = 0


                for j in range(0, 24):
                    if j < 5:  # Hitra polninica
                        if (Start_parking_time.iloc[i, j] > 0) and (Actual_new_vehicles.iloc[i, j]>0):
                            Time_of_charging.iloc[i, j] = ((Actual_new_vehicles.iloc[i, j] / Start_parking_time.iloc[i, j]) * Energy_needs_to_be_recharged.iloc[i, j]) / (Power_fast * Actual_new_vehicles.iloc[i, j] * (j + 1)) * 100
                            if Time_of_charging.iloc[i, j] > 100:
                                Time_of_charging.iloc[i, j] = 100

                    elif j > 16:  # Počasna polnilnica
                        if (Start_parking_time.iloc[i, j] > 0) and (Actual_new_vehicles.iloc[i, j]>0):
                            Time_of_charging.iloc[i, j] = ((Actual_new_vehicles.iloc[i, j] / Start_parking_time.iloc[i, j]) * Energy_needs_to_be_recharged.iloc[i, j]) / (Power_medium * Actual_new_vehicles.iloc[i, j] * (j + 1)) * 100
                            if Time_of_charging.iloc[i, j] > 100:
                                Time_of_charging.iloc[i, j] = 100

                    else:  # Srednje hitra polnilnica
                        if (Start_parking_time.iloc[i, j] > 0) and (Actual_new_vehicles.iloc[i, j]>0):
                            Time_of_charging.iloc[i, j] = ((Actual_new_vehicles.iloc[i, j] / Start_parking_time.iloc[i, j]) * Energy_needs_to_be_recharged.iloc[i, j]) / (Power_slow * Actual_new_vehicles.iloc[i, j] * (j + 1)) * 100
                            if Time_of_charging.iloc[i, j] > 100:
                                Time_of_charging.iloc[i, j] = 100


        Time_of_charging_fast = Time_of_charging.iloc[0:24, 0:5]
        Time_of_charging_medium = Time_of_charging.iloc[0:24, 5:17]
        Time_of_charging_slow = Time_of_charging.iloc[0:24, 17:24]

        Charging_time = [Time_of_charging_fast, Time_of_charging_medium, Time_of_charging_slow]

        # Calculate SOC
        SOC_tmp = pd.DataFrame(index=range(24),columns=range(24))
        SOC_tmp.iloc[0, 0:24] = Start_energy.iloc[0, 0:24]
        SOC_tmp.iloc[0:24,0:24] = 0# Starting energy of all vehicles based on parking duration
        SOC_arriving = Start_energy
        SOC_leaving = End_energy_tmp
        SOC_charging = pd.DataFrame(index=range(24), columns=range(24))
        SOC_charging.iloc[0, :] = 0
        #SOC_charging.iloc[:, 0] = 0
        SOC_charging.iloc[1::,0:5] = Actual_new_vehicles.iloc[1::,0:5]* Power_fast*Time_of_charging.iloc[1::,0:5]/100
        SOC_charging.iloc[1::, 5:17] = Actual_new_vehicles.iloc[1::, 5:17] * Power_medium * Time_of_charging.iloc[1:, 5:17]/100
        SOC_charging.iloc[1::, 17::] = Actual_new_vehicles.iloc[1:, 17::] * Power_slow * Time_of_charging.iloc[1:, 17::]/100
        Energy_needs_to_be_recharged_actual = Energy_needs_to_be_recharged*Actual_new_vehicles/Start_parking_time

        for i in range(0, 24):
            for j in range(0, 24):
                if (j<5) :
                    SOC_charging_tmp = Power_fast*Actual_new_vehicles.iloc[i,j]
                    if (SOC_charging.iloc[i,j] < Power_fast*Actual_new_vehicles.iloc[i,j]):
                        SOC_charging_tmp = SOC_charging.iloc[i,j]
                    Time_tmp = (np.ceil((j + 1)*Time_of_charging.iloc[i,j])).astype(int)
                    for k in range(1,Time_tmp):
                        if ((i+k)>23) or ((j-k)<1):
                            break
                        SOC_charging.iloc[i+k,j-k] = SOC_charging.iloc[i+k,j-k] + SOC_charging_tmp
                        if (SOC_charging.iloc[i,j] - k*Power_fast*Actual_new_vehicles.iloc[i,j])<0:
                            SOC_charging_tmp = 0
                        elif (SOC_charging.iloc[i,j] - k*Power_fast*Actual_new_vehicles.iloc[i,j])<(Power_fast*Actual_new_vehicles.iloc[i,j]):
                                SOC_charging_tmp = SOC_charging.iloc[i,j] - k*Power_fast*Actual_new_vehicles.iloc[i,j]
                        else:
                            SOC_charging_tmp = Power_fast * Actual_new_vehicles.iloc[i, j]
                elif (j > 16):
                    SOC_charging_tmp = Power_slow * Actual_new_vehicles.iloc[i, j]
                    if (SOC_charging.iloc[i, j] < Power_slow * Actual_new_vehicles.iloc[i, j]):
                        SOC_charging_tmp = SOC_charging.iloc[i, j]
                    Time_tmp = (np.ceil((j + 1)*Time_of_charging.iloc[i,j])).astype(int)
                    for k in range(1, Time_tmp):
                        if((i + k) > 23) or ((j - k) < 1):
                            break
                        SOC_charging.iloc[i + k, j - k] = SOC_charging.iloc[i + k, j - k] + SOC_charging_tmp
                        if (SOC_charging.iloc[i, j] - k * Power_slow * Actual_new_vehicles.iloc[i, j]) < 0:
                            SOC_charging_tmp = 0
                        elif (SOC_charging.iloc[i, j] - k * Power_slow * Actual_new_vehicles.iloc[i, j]) < (Power_slow * Actual_new_vehicles.iloc[i, j]):
                            SOC_charging_tmp = SOC_charging.iloc[i, j] - k * Power_slow * Actual_new_vehicles.iloc[i, j]
                        else:
                            SOC_charging_tmp = Power_slow * Actual_new_vehicles.iloc[i, j]
                else:
                    SOC_charging_tmp = Power_slow * Actual_new_vehicles.iloc[i, j]
                    if (SOC_charging.iloc[i, j] < Power_slow * Actual_new_vehicles.iloc[i, j]):
                        SOC_charging_tmp = SOC_charging.iloc[i, j]
                    Time_tmp = (np.ceil((j + 1)*Time_of_charging.iloc[i,j])).astype(int)
                    for k in range(1, Time_tmp):
                        if ((i + k) > 23) or ((j - k) < 1):
                            break
                        SOC_charging.iloc[i + k, j - k] = SOC_charging.iloc[i + k, j - k] + SOC_charging_tmp
                        if (SOC_charging.iloc[i, j] - k * Power_slow * Actual_new_vehicles.iloc[i, j]) < 0:
                            SOC_charging_tmp = 0
                        elif (SOC_charging.iloc[i, j] - k * Power_slow * Actual_new_vehicles.iloc[i, j]) < (Power_slow * Actual_new_vehicles.iloc[i, j]):
                            SOC_charging_tmp = SOC_charging.iloc[i, j] - k * Power_slow * Actual_new_vehicles.iloc[i, j]
                        else:
                            SOC_charging_tmp = Power_slow * Actual_new_vehicles.iloc[i, j]

        for i in range(1, 24):
            for j in range(0, 24):
                if i - j > 0 and (Start_parking_time.iloc[i-j-1, j])>0:
                    SOC_tmp.iloc[i, j] = SOC_tmp.iloc[i - 1, j] + SOC_arriving.iloc[i, j] + SOC_charging.iloc[i, j] - SOC_leaving.iloc[i, j] * (Actual_new_vehicles.iloc[i-j-1, j] / Start_parking_time.iloc[i-j-1, j])
                elif i - j < 0 and (Start_parking_time.iloc[ i - j +23, j]) > 0:
                    SOC_tmp.iloc[i, j] = SOC_tmp.iloc[i - 1, j] + SOC_arriving.iloc[i, j] + SOC_charging.iloc[i, j] - SOC_leaving.iloc[i, j] * (Actual_new_vehicles.iloc[i - j +23, j] / Start_parking_time.iloc[ i - j +23, j])
                else:
                    SOC_tmp.iloc[i, j] = SOC_tmp.iloc[i - 1, j] + SOC_arriving.iloc[i, j]

        #SOC_of_charging_fast = (SOC_tmp.iloc[0:24, 0:5]).sum(axis=1)
        #SOC_of_charging_medium = (SOC_tmp.iloc[0:24, 5:17]).sum(axis=1)
        #SOC_of_charging_slow = (SOC_tmp.iloc[0:24, 17:24]).sum(axis=1)
        #SOC = [SOC_of_charging_fast, SOC_of_charging_medium, SOC_of_charging_slow]
        SOC = SOC_tmp.sum(axis=1)

        return New_CSs, Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, CPPV, Charging_time, SOC
    else:
        FastCS = int(ECSF)
        FastACCS = int(ECSFAC)
        SlowCS = int(ECSS)
        #Prepare outputs
        Number_of_CS = [FastCS,FastACCS,SlowCS]
        if Number_of_vehicles != 0:
            CPPV = (FastCS+FastACCS+SlowCS)/Number_of_vehicles
        else:
            CPPV = 0
        return Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, CPPV
