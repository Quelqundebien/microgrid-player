#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 09:55:53 2021

@author: eloi_tr
"""

#import sys
#import os
#import pulp
import numpy as np

#prices = np.random.rand(48)

class Player:

	def __init__(self):
		# some player might not have parameters
		self.parameters = 0
		self.horizon = 48
        self.pimax = 10
        self.C = 30
        self.rhoc = 0.95
        self.rhod = 0.95
        self.size = 100 # en m2
        self.battery = 0

	def set_scenario(self, scenario_data):
		predata = scenario_data/solar_farm
        futurdata = np.zeros(self.horizon)
        n = len(scenario_data/solar)
        if  n != self.horizon:
            for i in range(self.horizon):
                futurdata[i] = predata[int(i*n/self.horizon)]
                self.data = futurdata
        else:
            self.data = predata

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
        if time < 3/4*(horizon):
            if prix < prixmoy:
                lbat = min(self.size*prod[time],self.pimax,(self.C-self.battery)/0.95)
                battery += lbat*self.rhoc
                battery = min(C,battery)
            if prix > prixmoi:
                lbat = (-1)*min(self.pimax,self.battery)
                battery += lbat/self.rhod
        else:
            lbat = (-1)*min(self.pimax,self.battery)
            battery += lbat/self.rhod
		return (-1)*(self.size*prod[time] - lbat)

	def compute_load(self, time):
		load = self.take_decision(time)
		# do stuff ?
		return load

	def reset(self):
		# reset all observed data
		pass



