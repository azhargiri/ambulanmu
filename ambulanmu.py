#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ambulanmu.py
#  
#  Copyright 2021 acep <acepby@gmail.com>
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

import logging
import os

from geojson import Point, Feature, FeatureCollection, dump
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import (
	Updater, 
	CommandHandler, 
	MessageHandler, 
	Filters, 
	ConversationHandler, 
	CallbackContext,
	CallbackQueryHandler,
)
from ambulan_data import Ambulan
from shelter import Shelter
from dotenv import load_dotenv,find_dotenv
from os import getenv
import json
import datetime


# TODO
# 1. Pendataan lokasi ambulanmu dengan form
# 2. Info lokasi ambulanmu terdekat 
# 3. tracking ambulan dan completion task ambulan tersebut
# 4. dashboard peta lokasi ambulan dan tracking perjalanan ambulanmu
# 5. pendaftaran lokasi relawan escorting ambulanmu
# 6. kirim lokasi ambulanmu yg sedang bertugas kepada relawan terdekat


#enable logging
logging.basicConfig(format='%(asctime)s - %(name)s -%(levelname)s - %(message)s',
					level=logging.INFO)
logger = logging.getLogger(__name__)

features = []

#load token
load_dotenv(find_dotenv())
TOKEN = getenv("TOKEN")

#set data ambulan
abm = Ambulan()
shelter = Shelter()
#abmlist = abm.listByKota()


DEST,LOC,AMBULANMU,SHELTERMU,LAYANAN,TRACKING,DETAIL = range(7)

#callback data
AMBULANMU,SHELTERMU,START_OVER,INFO,ANTAR_PASIEN,BACK,PILIHKOTA,TRACK= range(8)


def start(update, context):
	"""send message when the command /start is issued."""
	text =(
		'Selamat Datang {}, ini adalah bot untuk mencari informasi AmbulanMu dan shelter. \n'
		'Informasi yang disediakan saat ini adalah kontak untuk layanan-layanan tersebut \n'
		'Pilih Info yang ingin dicari'
		)
	#menu utama
	menu_keyboard = [
		[
			InlineKeyboardButton("🚑 AmbulanMu", callback_data=str(AMBULANMU)),
			InlineKeyboardButton("🏥 ShelterMu",callback_data=str(SHELTERMU)),
		]
	]

	menu_markup = InlineKeyboardMarkup(menu_keyboard)
	
	if context.user_data.get(START_OVER):
		user = update.callback_query.message.chat
		nama = checkNama(user)
		update.callback_query.answer()
		update.callback_query.edit_message_text(text.format(nama), parse_mode=ParseMode.MARKDOWN,reply_markup = menu_markup)
	else:
		if (update.message.from_user):
			user = update.message.from_user
		else:
			user = update.callback_query.message.chat
		nama = checkNama(user)
		update.message.reply_text(text.format(nama),parse_mode=ParseMode.MARKDOWN,reply_markup=menu_markup)
	
	context.user_data[START_OVER]=False
	return LAYANAN
	
def checkNama(user):
	if(user.last_name):
		nama = "*{} {}*".format(user.first_name,user.last_name)
	else:
		nama = "*{}*".format(user.first_name)
	return nama
	
#shelter
def sheltermu(update: Update, context: CallbackContext):
	text = ("*Info Shelter Isoman :*\n{}".format(getShelterMu(shelter.listByKota()))
			)
	keyboard= [[InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK))]]
	markup = InlineKeyboardMarkup(keyboard)
	update.callback_query.answer()
	update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,reply_markup = markup)
	context.user_data[START_OVER] = True
	return INFO
	
	
#ambulanmu
def ambulanmu(update:Update, context: CallbackContext):
	text = ("Akses untuk info ambulan dan antar pasien")
	keyboard = [
		[
			InlineKeyboardButton("ℹ️ Info AmbulanMu", callback_data=str(INFO)),
			InlineKeyboardButton("Antar Pasien", callback_data=str(ANTAR_PASIEN))
		],
		[
			InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK)),
		],
	]
	
	markup = InlineKeyboardMarkup(keyboard)
	update.callback_query.answer()
	update.callback_query.edit_message_text(text, reply_markup = markup)
	context.user_data[START_OVER] = True
	return INFO
	
#info
#list provinsi 
def ambulanmuByProv(update:Update, context:CallbackContext):
	global ListProv
	prov = abm.listProv()
	ListProv = prov
	button_list = [[InlineKeyboardButton(text = p,callback_data=str(p))] for p in prov]
	keyboard= [[InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK))]]
	button_list = button_list + keyboard
	menu = aturMenu(button_list,2)
	markup = InlineKeyboardMarkup(menu)
	text = ("Berikut Provinsi yang sudah menyediakan layanan AmbulanMu")
	update.callback_query.answer()
	update.callback_query.edit_message_text(text,reply_markup = markup)
	context.user_data[START_OVER] = True
	return INFO
	
#list kota yg sudah ada layanan ambulanmu
def info_ambulanmu(update:Update, context:CallbackContext):
	global selectedProv
	global ListKota
		
	if(update.callback_query.data in ListProv):
		prov = update.callback_query.data
		selectedProv = update.callback_query.data
	else:
		prov= selectedProv
		
		
	kota = abm.listKota(prov)
	ListKota = kota
	
	button_list = [[InlineKeyboardButton(text = s,callback_data=str(s))] for s in kota]
	keyboard= [[InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK))]]
	button_list = button_list + keyboard
	menu = aturMenu(button_list,3)
	markup = InlineKeyboardMarkup(menu)
	text = ("Berikut Kota di *{}* yang sudah menyediakan layanan AmbulanMu").format(prov)
	update.callback_query.answer()
	update.callback_query.edit_message_text(text,parse_mode=ParseMode.MARKDOWN,reply_markup = markup)
	context.user_data[START_OVER] = True
	return DETAIL

def aturMenu(buttons,col):
	submenu =[]
	b = [buttons[i:i + col] for i in range(0,len(buttons),col)]
	
	for i in range(len(b)):
		if len(b[i]) > 2:
			submenu.append(b[i][0]+b[i][1]+b[i][2])
		elif len(b[i])>1:
			submenu.append(b[i][0]+b[i][1])
		else:
			submenu.extend(b[i])
	
	return submenu
	

#detail list ambulan tiap kota
def detailInfo(update: Update, context: CallbackContext):
	
	global selectedKota
	
	if(update.callback_query.data in ListKota):
		kota = update.callback_query.data
		selectedKota = update.callback_query.data
	else:
		kota = selectedKota
	
	
	text = "*Info dan list ambulanmu* di *{}*: \n{}".format(kota,getAmbulanMu(abm.listByKota(kota=kota)))
	keyboard= [[InlineKeyboardButton("Kota Lain",callback_data=str(PILIHKOTA)),
				InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK))]
				]
	markup = InlineKeyboardMarkup(keyboard)
	update.callback_query.answer()
	update.callback_query.edit_message_text(text,parse_mode=ParseMode.MARKDOWN,reply_markup = markup)
	context.user_data[START_OVER] = True
	
	return INFO
	
def getAmbulanMu(data):
	mydata = []
	for index,row in data.iterrows():
		mydata.append({"Nama":row["Nama"],"Kontak":"+62"+str(row["Kontak"])})
	
	#print(mydata)
	dd = []
	for d in mydata:
		dt = ', '.join(map(str,d.values()))
		dd.append(dt)
			
	return "\n".join(map(str,dd))

# get shelter
def getShelterMu(data):
	dd = []
	for d in data:
		d[0] ="*{}*".format(d[0])
		d[1] = "+62{}".format(d[1])
			
		dt = ', '.join(map(str,d))
		dd.append(dt)
			
	return "\n".join(map(str,dd))
	
	
#tracking ambulanmu
def tracking(update: Update, context: CallbackContext):
	#print(update)
	user = update.callback_query.message.from_user
	#print(update.update_id)
	logger.info("Driver: %s", user.first_name)
	text = "Kemana tujuan ambulanmu?"
	update.callback_query.answer()
	update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
	context.user_data[START_OVER] = True
	
	return DEST

def tujuan(update: Update, context: CallbackContext):
	user = update.message.from_user
	print(context.user_data)
	print("catat tujuan :",update)
	global tujuan
	tujuan = update.message.text
	
	#print(tujuan)
	logger.info("Destination : %s", tujuan)
	update.message.reply_text(
		'Tujuan sudah dicatat. Silakan share live location (set 8 jam).'
	)
	return LOC

def location(update: Update, context: CallbackContext):
	keyboard= [[InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK))]]
	markup = InlineKeyboardMarkup(keyboard)
	last_id = update.update_id
	user = update.message.chat
	driver ={}
	driver['id'] = user.id
	driver['username'] = user.username
	driver['firstname']=user.first_name
	
	live_update = update.message.location
	text = ('live location sudah di rekam. Selamat Bertugas. \n')
	#live_update =
	print("catat lokasi :",update)
	lokasi = "({},{})".format(live_update.longitude, live_update.latitude)
	#simpan data {user, lokasi=(lon,lat), tujuan,waktu}
	trackingLog(driver,tujuan,lokasi,update.message.date)
	toGeoJson(last_id,user.first_name,live_update.longitude, live_update.latitude,'awal',update.message.date)
	writeGeoJson(features)
	update.message.reply_text(text,reply_markup = markup)
	
	context.user_data[START_OVER] = True
	#getupdate = Update(last_id + 1)
	#print(getupdate.edit_message.location)
	return LAYANAN
	
def myconverter(o):
	if isinstance(o,datetime.datetime):
		return o.__str__()

def trackingLog(user,tujuan,lokasi,waktu):
	tdata = {}
	tdata['user'] = user
	tdata['lokasi']=lokasi
	tdata['tujuan']= tujuan
	tdata['waktu']=str(waktu)
	#tdata ="'user':{},'lokasi':{},'tujuan':{},'waktu':{}".format(user,tujuan,lokasi,waktu)
	toDir = "data"
	file_name = "antarpasien.json"
	toData = os.path.join(toDir,file_name)
	with open(toData,"a+") as fs:
		fs.seek(0)
		if len(fs.read()) == 0:
			fs.write(json.dumps(tdata))
		else:
			fs.write(f',{json.dumps(tdata)}')
	
		
def cancel(update: Update, context: CallbackContext) -> int:
	user = update.message.from_user
	text = (
				"Tracking ambulan telah dibatalkan.\n\n"
				"/start untuk memulai kembali bot"
			)
	logger.info("Ambulan ID %s ga jadi ngantar.", user.first_name)
	update.message.reply_text(text)
	context.user_data[START_OVER] = False
	return ConversationHandler.END

def getUpdateLoc(update: Update,context:CallbackContext):
	#print(update)
	global features
	updateId = update.update_id
	currData = update.edited_message
	if currData :
		tgl = currData.edit_date
		lon = currData.location.longitude
		lat = currData.location.latitude
		nm = currData.from_user
		toGeoJson(updateId,nm.first_name, lon,lat,'latest',tgl)
		writeGeoJson(features)
		
	
def toGeoJson(uid,nm,lon,lat,state,waktu):
	global features
	point = Point((lon,lat))
	waktu = str(waktu)
	#myfeat = Feature(geometry=point,properties={"upid":uid,"driver":nm,"longitude":lon,"latitude":lat,"waktu":waktu,"state":state})
	#features.append(Feature(geometry=point,properties={"upid":uid,"driver":nm,"longitude":lon,"latitude":lat,"waktu":waktu,"state":state}))
	features.insert(0,Feature(geometry=point,properties={"upid":uid,"driver":nm,"longitude":lon,"latitude":lat,"waktu":waktu,"state":state}))
	#writeGeoJson(features)
	
def writeGeoJson(features):
	feature_collection = FeatureCollection(features)
	with open("ambulan.geojson","w") as f:
		dump(feature_collection,f)

	

def main():
	updater = Updater("{}".format(TOKEN), use_context=True)
	dispatcher = updater.dispatcher
	
	dispatcher.add_handler(CommandHandler("start",start))
	
	#tracking ambulance handler
	tracking_handler = ConversationHandler(
		entry_points = [CommandHandler('tracking', tracking)],
		states = {
			DEST: [MessageHandler(Filters.text & ~Filters.command, tujuan)],
			LOC : [MessageHandler(Filters.location,location)],
		},
		fallbacks = [CommandHandler('cancel',cancel)],
	)
	
	layanan_handler = ConversationHandler(
		entry_points =[
						CallbackQueryHandler(ambulanmu,pattern='^' +str(AMBULANMU) +'$'),
						CallbackQueryHandler(sheltermu,pattern='^' +str(SHELTERMU) + '$'),
		],
		states = {
			DEST: [MessageHandler(Filters.text & ~Filters.command, tujuan),
				CommandHandler('cancel',cancel)
			],
			LOC : [
				MessageHandler(Filters.location,location),
				CommandHandler('cancel',cancel)
			],
			INFO: [
				CallbackQueryHandler(ambulanmuByProv,pattern='^' +str(INFO) + '$'),
				CallbackQueryHandler(tracking,pattern='^' +str(ANTAR_PASIEN) + '$'),
				CallbackQueryHandler(start,pattern='^' +str(BACK) + '$'),
				CallbackQueryHandler(info_ambulanmu),
				
			],
			DETAIL:[
				CallbackQueryHandler(detailInfo),
				CallbackQueryHandler(info_ambulanmu,pattern='^' +str(PILIHKOTA) + '$'),
				CallbackQueryHandler(start,pattern='^' +str(BACK) + '$')
			],
			LAYANAN:[
				CallbackQueryHandler(ambulanmu,pattern='^' +str(AMBULANMU) + '$'),
				CallbackQueryHandler(sheltermu,pattern='^' +str(SHELTERMU) + '$'),
				CallbackQueryHandler(start,pattern='^' +str(BACK) + '$')
			]
			},
		fallbacks = [],
	)
	
	dispatcher.add_handler(layanan_handler)
	dispatcher.add_handler(MessageHandler(Filters.all, getUpdateLoc))
	
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
				
