#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 09:55:53 2021

@author: eloi_tr
"""

#import sys
import os
import pulp
import numpy as np
from numpy import genfromtxt
import pandas as pd


df = pd.read_csv(os.path.join(os.getcwd(),"pv_prod_scenarios.csv"), sep = ";", decimal = ".")
#prices = np.random.rand(48)
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
        print("data = ",self.data)
            
    def set_scenario_data(self,lpv):
        self.data=np.zeros(self.horizon)
        sc_init = np.array(lpv[(lpv["day"]==self.day) & (lpv["region"]==self.region)])
        for i in range(0,int(self.horizon/2)):
            self.data[2*i]=sc_init[i,3]*self.size/1000
            self.data[2*i+1]=sc_init[i,3]*self.size/1000

    def set_prices(self, prices):
        self.prices = prices

    def compute_all_load(self):
        load = np.zeros(self.horizon)
        pb_name = "decision"
        lp = pulp.LpProblem(pb_name + ".lp", pulp.LpMinimize)
        lp.setSolver()
        lbat_c = {}
        lbat_d = {}
        lbat = {}
        batterie = {}
        for t in range(self.horizon):
            #lbat[t] = {}
            #batterie[t] = {}
            #création des variablse
            var_name = "batterie_" + str(t)
            batterie[t] = pulp.LpVariable(var_name,0.0,self.C)
            var_name = "lbat_c_" + str(t)
            lbat_c[t] = pulp.LpVariable(var_name,0,self.pimax)
            var_name = "lbat_d_" + str(t)
            lbat_d[t] = pulp.LpVariable(var_name,0,self.pimax)
        #Les contraintes
        deltat = 24/self.horizon
        lp += batterie[0] == 0,"batterie_initiale"
        for t in range(self.horizon):
            lp += lbat_c[t] <= self.data[t],"charge_"+str(t)
            lp += lbat_d[t] <= self.data[t],"decharge_"+str(t)
        for t in range(1,self.horizon):
            lp += batterie[t] <= batterie[t-1] + lbat_c[t]*self.rhoc*deltat - deltat*lbat_d[t]/self.rhod,"batterie"+str(t)
        lp.setObjective(pulp.lpSum(((lbat_c[t]-lbat_d[t]-self.data[t])*self.prices[t])*deltat for t in range(self.horizon)))
        lp.solve()
        #model = Model(lp,lbat)
        #solve(model, pb_name)
        #results = getResultsModel(pb,model,pb_name)
        #printResults(pb, model, pb_name,[],results)
        for t in range(self.horizon):
            lbat[t] = lbat_c[t] - lbat_d[t]
        for t in range(self.horizon):
            load[t] = pulp.value(lbat_c[t])- pulp.value(lbat_d[t])-self.data[t]
            self.bill += load[t]*self.prices[t]*deltat
        #self.bill = value(lp.objective)
        for i in range(48):
            nivbat[i] = pulp.value(batterie[i])
        return load

    def take_decision(self, time):
        load = 0
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
    plt.plot([i for i in range(48)],[30 for i in range(48)])

