#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  shelter.py
#  
#  Copyright 2021 acep <acep@ryzen-desk>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


import pandas as pd

class Shelter:
	def __init__(self):
		self.shelter = pd.read_csv("sheltermu.csv")

	def listByKota(self,kota=None):
		data = self.checkUpdateData()
		if (kota):
			nmKota = kota
			shelterList = data.loc[data["kota"] == kota]
			shelterList = shelterList.values.tolist()
		else:
			shelterList = data.values.tolist()
		return shelterList
		
	def listKota(self):
		data = self.checkUpdateData()
		kotalist = data["kota"].unique().tolist()
		return kotalist
		
	def checkUpdateData(self):
		oldData = self.shelter 
		newData = pd.read_csv("sheltermu.csv")
		
		if( len(newData) > len(oldData)):
			data = newData
		else: 
			data = oldData
		return data

'''
shelter = Shelter()
print(shelter.listByKota())
'''

