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
#prices = np.random.rand(48)

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
        self.horizon = 48
        self.prod = genfromtxt("pv_prod_scenarios.csv", delimiter = ";", usecols=3)
        self.prod2 = np.array(df["pv_prod (W/m2)"])
        self.data = np.zeros(self.horizon)
        self.bill = 0

    def set_scenario(self, scenario_data):
        predata = scenario_data
        futurdata = np.zeros(self.horizon)
        n = len(scenario_data)
        if  n != self.horizon:
            for i in range(self.horizon):
                futurdata[i] = predata[int(i*n/self.horizon)]
                self.data = futurdata
            else:
                self.data = predata
            
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
        load = (-1)*(self.size*prod[time] - lbat)/1000
        self.bill += load * self.prices[time]
        return load

    def compute_load(self, time):
        load = self.take_decision(time)
		# do stuff ?
        return load

    def reset(self):
		# reset all observed data
        pass


def run():
    player = Player()
    prices= 4 + 4*np.random.rand(48) 
    player.set_prices(prices)
    lpv=pd.read_csv("pv_prod_scenarios.csv",delimiter=";")
    player.set_scenario_data(lpv)
    result=player.compute_all_load()
    print("niveau de batterie =", player.battery)
    print(result)
    print("bill = ",player.bill)



