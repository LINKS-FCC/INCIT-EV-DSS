"""
Created on Thu May 13 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""

import pandas as pd
import math
import os.path
import PySimpleGUI as sg

def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)

def CI_module(abs_path,VP_matrix_file, Expected_EV, ECSF, ECSFAC, ECSS, CIY, ROIG):
    #Load CI Database
    CI_database = pd.read_excel(abs_path+'/CI_database.xlsx')

    #Sort CSs based on nominal power and installation costs
    FCS_database = CI_database.loc[CI_database.iloc[:,1]>20,:].sort_values('Installation costs / €')
    FACCS_database = CI_database.loc[(CI_database.iloc[:,1]<20) & (CI_database.iloc[:,1]>10),:].sort_values('Installation costs / €')
    SCS_database = CI_database.loc[CI_database.iloc[:,1]<10,:].sort_values('Installation costs / €')

    #Create database based on CS type
    if (os.path.exists(abs_path + '\Output database for customer.xlsx'))==False:
        writer = pd.ExcelWriter(abs_path + '\Output database for customer.xlsx', engine='xlsxwriter')
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

    VP_matrix_short = pd.DataFrame()
    VP_matrix_medium = pd.DataFrame()
    VP_matrix_long = pd.DataFrame()
    #for i in range (0,24):
        #VP_matrix_tmp = pd.read_csv(abs_path + 'Piero/parking_' + str(i) + 'h_mean_7_days.csv', header=None, index_col=None)
        #VP_matrix_all = VP_matrix_all.append(VP_matrix_tmp.iloc[0,:]*100) #TODO: *100 only to scale inputs to make an example

    # TODO: *100 only to scale inputs to make an example
    # TODO: *insert variable to select different zone. This wil be added after first compatibility test
    VP_matrix_short_tmp = pd.read_excel(abs_path + 'parking_short_mean_7_days.xlsx', header=None, index_col=None)
    VP_matrix_short = VP_matrix_short.append(VP_matrix_short_tmp.iloc[0,:]*100)
    VP_matrix_medium_tmp = pd.read_excel(abs_path + 'parking_medium_mean_7_days.xlsx', header=None, index_col=None)
    VP_matrix_medium = VP_matrix_medium.append(VP_matrix_medium_tmp.iloc[0, :] * 100)
    VP_matrix_long_tmp = pd.read_excel(abs_path + 'parking_long_mean_7_days.xlsx', header=None, index_col=None)
    VP_matrix_long = VP_matrix_long.append(VP_matrix_long_tmp.iloc[0, :] * 100)
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
        NFastACCS = normal_round(float(VP_matrix_medium.mean(axis=1)*float(Expected_EV)-int(ECSFAC)))
        NSlowCS = normal_round(float(VP_matrix_long.mean(axis=1)*float(Expected_EV)-int(ECSS)))
        FastCS = int(ECSF) + NFastCS
        FastACCS = int(ECSFAC) + NFastACCS
        SlowCS = int(ECSS) + NSlowCS
        if NFastCS < 1:
            sg.popup('There is no need for any additional Fast CS. Additional network analysis will include only existing CSs.')
            FastCS = int(ECSF)
            NFastCS = 0
        if FastACCS < 1:
            sg.popup('There is no need for any additional Fast AC CS. Additional network analysis will include only existing CSs')
            FastACCS = int(ECSFAC)
            NFastACCS = 0
        if SlowCS < 1:
            sg.popup('There is no need for any additional Slow CS. Additional network analysis will include only existing CSs')
            SlowCS = int(ECSS)
            NSlowCS = 0
        #Determine minimum initial and maintenance costs
        FastCS_min_installation_price = FCS_database.iloc[0,2]
        FastACCS_min_installation_price = FACCS_database.iloc[0,2]
        SlowCS_min_installation_price = SCS_database.iloc[0,2]
        FastCS_min_maintenance_price = FCS_database.iloc[0,3]
        FastACCS_min_maintenance_price = FACCS_database.iloc[0,3]
        SlowCS_min_maintenance_price = SCS_database.iloc[0,3]
        # Prepare outputs
        New_CSs = [NFastCS, NFastACCS, NSlowCS]
        Number_of_CS = [FastCS, FastACCS, SlowCS]
        Initial_costs_pu = [FastCS_min_installation_price, FastACCS_min_installation_price,SlowCS_min_installation_price]
        Maintenance_costs_pu = [FastCS_min_maintenance_price, FastACCS_min_maintenance_price,SlowCS_min_maintenance_price]
        Initial_costs = FastCS_min_installation_price * NFastCS + FastACCS_min_installation_price * NFastACCS + SlowCS_min_installation_price * NSlowCS
        Maintenance_costs = FastCS_min_maintenance_price * NFastCS + FastACCS_min_maintenance_price * NFastACCS + SlowCS_min_maintenance_price * NSlowCS
        ROI = int((int(ROIG)-Initial_costs)/Initial_costs*100)
        CPPV = (NFastCS+NFastACCS+NSlowCS+FastCS+FastACCS+SlowCS)/Number_of_vehicles
        return New_CSs, Number_of_CS, Initial_costs_pu, Maintenance_costs_pu, Initial_costs, Maintenance_costs, VP_matrix_short, VP_matrix_medium, VP_matrix_long, ROI, CPPV
    else:
        FastCS = int(ECSF)
        FastACCS = int(ECSFAC)
        SlowCS = int(ECSS)
        #Prepare outputs
        Number_of_CS = [FastCS,FastACCS,SlowCS]
        ROI = 0
        CPPV = (FastCS+FastACCS+SlowCS)/Number_of_vehicles
        return Number_of_CS, VP_matrix_short, VP_matrix_medium, VP_matrix_long, ROI, CPPV
