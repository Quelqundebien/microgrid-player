#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 09:55:53 2021

@author: eloi_tr
"""

#import sys
import os
#import pulp
import numpy as np
from numpy import genfromtxt
import pandas as pd


df = pd.read_csv(os.path.join(os.getcwd(),"pv_prod_scenarios.csv"), sep = ";", decimal = ".")
nivbat = np.zeros(48)
class Player:

    def __init__(self):
        self.region = "grand_sud_ouest"
        self.day = "23/10/2014"
        self.parameters = 0
        self.size = 100 # en m2
        self.rhoc = 0.95
        self.rhod = 0.95
        self.battery = 0
        self.pimax = 10
        self.C = 30        
        self.bill = 0
        self.horizon = 48
        df = pd.read_csv('pv_prod_scenarios.csv', sep=';')
        df = df[(df['region'] == self.region) & (df['day'] == self.day)]
        self.prod = df[['pv_prod (W/m2)']]
        self.l_pv = np.array(self.prod)
        self.l_pv = (-1)*self.size*self.l_pv/1000
        self.l_pv = np.repeat(self.l_pv,2)
        #self.prod = genfromtxt("pv_prod_scenarios.csv", delimiter = ";", usecols=3)
        #self.prod2 = np.array(df["pv_prod (W/m2)"])
        self.data = np.zeros(self.horizon)
        self.bill = 0

    def set_scenario(self, scenario_data):
        df2 = scenario_data
        df2 = df2[(df2['region'] == self.region) & (df2['day'] == self.day)]
        self.prod = df2[['pv_prod (W/m2)']]
        self.l_pv = np.array(self.prod)
        self.l_pv = (-1)*self.size*self.l_pv/1000
        self.l_pv = np.repeat(self.l_pv,2)
        #self.prod = genfromtxt("pv_prod_scenarios.csv", delimiter = ";", usecols=3)
        #self.prod2 = np.array(df["pv_prod (W/m2)"])
        self.data = np.zeros(self.horizon)
            
    def set_scenario_data(self,lpv):
        self.data=np.zeros(self.horizon)
        sc_init = np.array(lpv[(lpv["day"]==self.day) & (lpv["region"]==self.region)])
        for i in range(0,int(self.horizon/2)):
            self.data[2*i]=sc_init[i,3]
            self.data[2*i+1]=sc_init[i,3]

    def set_prices(self, prices):
        self.prices = prices

    def compute_all_load(self):
        load = np.zeros(self.horizon)
        for time in range(self.horizon):
            load[time] = self.compute_load(time)
        return load

    def take_decision(self, time):
        deltat = 24/self.horizon
        prixmoy = sum(self.prices)/len(self.prices)
        prix = self.prices[time]
        prod = self.data
        lbat = 0
        if time < 3/4*(self.horizon):
            if prix < prixmoy:
                lbat = min(self.size*prod[time],self.pimax,(self.C-self.battery)/0.95)
                self.battery += lbat*self.rhoc
                self.battery = min(self.C,self.battery)
            if prix > prixmoy:
                lbat = (-1)*min(self.pimax,self.battery)
                self.battery += lbat/self.rhod
        else:
            lbat = (-1)*min(self.pimax,self.battery)
            self.battery += lbat/self.rhod
        load = (-1)*(self.size*prod[time] - lbat)*deltat/1000
        self.bill += load * self.prices[time]
        nivbat[time] = self.battery
        return load

    def compute_load(self, time):
        load = self.take_decision(time)
		# do stuff ?
        return load

    def reset(self):
		# reset all observed data
        pass

import matplotlib.pyplot as plt
def run():
    player = Player()
    prices= [4 - abs(t-24)/8 for t in range(48)]
    player.set_prices(prices)
    lpv=pd.read_csv("pv_prod_scenarios.csv",delimiter=";")
    player.set_scenario_data(lpv)
    result=player.compute_all_load()
    print("charge =")
    print(result)
    print("batterie", player.battery)
    print("bill = ",player.bill)
    plt.subplot(121)
    plt.plot([i for i in range(48)],result)
    plt.subplot(122)
    plt.plot([i for i in range(48)],nivbat)



