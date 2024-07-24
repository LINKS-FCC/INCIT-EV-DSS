"""
Created on Tue May 18 2021
@author: Klemen Knez, FE, Ljubljana 2021, kk3026@student.uni-lj.si
Copyright (c) 2021.
"""

from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

def Occupacy_graph(Occupancy):
    fig, ax = plt.subplots(figsize=(6.3,4))
    fig.patch.set_facecolor('#F0F8FF')
    t = np.arange(24)
    ax.plot(t, np.array(Occupancy[0])*100,label='Fast CS')
    ax.plot(t, np.array(Occupancy[1])*100,label='Fast AC CS')
    ax.plot(t, np.array(Occupancy[2])*100,label='Slow CS')
    ax.set_xlabel('Time')
    ax.set_ylabel('Proportion of occupied charging stations / %')
    ax.set_xlim(0, 23)
    ax.set_ylim(0, 105)
    ax.set_title("Proportion of occupied charging stations in a zone")
    ax.legend()
    ax.set_xticks([0,4,8,12,16,20])
    ax.set_xticklabels([f'{i:0>2d}:00' for i in range(0,24,4)])
    plt.savefig('outputs/Occupacy_graph.png', bbox_inches='tight')
    return fig

def Zone_CS_load_graph(Borders, Stays):
    fig, ax1 = plt.subplots(figsize=(6.3,4))
    fig.patch.set_facecolor('#F0F8FF')
    t = np.arange(24)
    ax1.fill_between(t, np.array(Borders[0],dtype=float).max()*1.1,np.array(Borders[0],dtype=float),facecolor='red', label='High probability of voltage or power issues')
    ax1.fill_between(t, np.array(Borders[0],dtype=float), np.array(Borders[1],dtype=float),facecolor='yellow', label='Low probability of voltage or power issues')
    ax1.fill_between(t, np.array(Borders[1],dtype=float), 0,facecolor='green', label='No anticipated voltage or power issues')
    ax1.set_ylim(0, np.array(Borders[0]).max()*1.1)
    ax1.plot(t, np.array(Stays, dtype=float),linewidth=3,label='Zone CS load')
    ax1.vlines(np.arange(24),0,np.array(Borders[0], dtype=float).max()*1.1,'k',linewidth=0.5)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Power demand / kW')
    ax1.set_xlim(0, 23)
    ax1.set_title("Charging impact to power grid")
    ax1.legend()
    ax1.set_xticks([0,4,8,12,16,20])
    ax1.set_xticklabels([f'{i:0>2d}:00' for i in range(0,24,4)])
    plt.savefig('outputs/Zone_CS_load_graph.png', bbox_inches='tight')
    return fig

def Electricity_costs(abs_path,Stays):
    Price = np.array(pd.read_excel(abs_path+'Electricity cost profile.xlsx',header=None))
    fig, ax1 = plt.subplots(figsize=(6.3,4))
    fig.patch.set_facecolor('#F0F8FF')
    t = np.arange(24)
    lns1 = ax1.plot(t, np.cumsum((np.array(Stays, dtype=float)*Price[0])),linewidth=3,label='Electricity cost',color='red')
    ax1.vlines(np.arange(24),0,np.cumsum((np.array(Stays, dtype=float)*Price[0])).max()*1.1,'k',linewidth=0.5)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Electricity costs / €')
    ax1.set_xlim(0, 23)
    ax1.set_ylim(0, np.cumsum((np.array(Stays, dtype=float)*Price[0])).max()*1.1)
    ax2 = ax1.twinx()
    lns2 = ax2.plot(t,np.array(Stays, dtype=float), linewidth=3,label='Cumulative EV consumption')
    ax2.set_ylim(0, (np.array(Stays, dtype=float)).max()*1.1)
    ax2.set_ylabel('Cumulative EV consumption / kWh')
    ax1.set_title("Electricity cost and EV consumption")
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0)
    ax1.set_xticks([0,4,8,12,16,20])
    ax1.set_xticklabels([f'{i:0>2d}:00' for i in range(0,24,4)])
    plt.savefig('outputs/Electricity_costs.png', bbox_inches='tight')
    return fig