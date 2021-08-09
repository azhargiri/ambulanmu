#!/usr/bin/env python # -*- coding: utf-8 -*-
#
#  ambulan_data.py
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

class Ambulan:
	def __init__(self):
		self.ambulan = pd.read_csv("ambulanmu.csv")

	def listByKota(self,kota=None):
		data = self.checkUpdateData()
		if (kota):
			nmKota = kota
			ambulanList = data.loc[data["Kota"] == kota]
		else:
			ambulanList = data
		return ambulanList

	def listKota(self):
		data = self.checkUpdateData()
		kotalist = data["Kota"].unique().tolist()
		return kotalist
    
	def listKotaByProvinsi(self, provinsi=None):
		kota_list = []
		data = self.checkUpdateData()

		if (provinsi):
			kota_list = data.loc[data["Provinsi"] == provinsi]["Kota"].unique().tolist()

		return kota_list

	def listProvinsi(self):
		data = self.checkUpdateData();
		provinsi_list = data["Provinsi"].unique().tolist()

		return provinsi_list

	def get_kota(self, kota):
		data = self.checkUpdateData()
		kota = data.loc[data['Kota'] == kota].at[0]

		return kota
		
	def checkUpdateData(self):
		oldData = self.ambulan 
		newData = pd.read_csv("ambulanmu.csv")
		
		if( len(newData) > len(oldData)):
			data = newData
		else: 
			data = oldData
		return data


'''
ambulan = Ambulan()
data = ambulan.listByKota()
print(data)
'''
