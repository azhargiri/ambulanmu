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
from dotenv import load_dotenv,find_dotenv
from os import getenv

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
abmlist = abm.listByKota()


DEST,LOC,AMBULANMU,SHELTERMU,LAYANAN,TRACKING = range(6)

#callback data
AMBULANMU,SHELTERMU,START_OVER,INFO,ANTAR_PASIEN,BACK = range(6)



#menu ambulanmu


#menu sheltermu

def start(update, context):
	"""send message when the command /start is issued."""
	text =(
		'Met dateng, ni adalah bot utk info ambulanmu dan shelter. \n'
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
		update.callback_query.answer()
		update.callback_query.edit_message_text(text, reply_markup = menu_markup)
	else:
		update.message.reply_text(text,reply_markup=menu_markup)
	
	context.user_data[START_OVER]=False
	return LAYANAN
	
#shelter
def sheltermu(update: Update, context: CallbackContext):
	text = ("Akses untuk Info Shelter Isoman\n"
			"Maaf data shelter belum ada"
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
def info_ambulanmu(update:Update, context:CallbackContext):
	keyboard= [[InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK))]]
	markup = InlineKeyboardMarkup(keyboard)
	text = "*Info dan list ambulanmu*: \n{}".format(getAmbulanMu(abmlist))
	update.callback_query.answer()
	update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,reply_markup = markup)
	context.user_data[START_OVER] = True
	return INFO

def getAmbulanMu(data):
	mydata = []
	for index,row in data.iterrows():
		mydata.append({"No":index+1, "Kota":row['Kota'],"Nama":row["Nama"],"Kontak":"+62"+str(row["Kontak"])})
	
	#print(mydata)
	dd = []
	for d in mydata:
		dt = ', '.join(map(str,d.values()))
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
	#print(update)
	tujuan = update.message.text
	print(tujuan)
	logger.info("Destination : %s", tujuan)
	update.message.reply_text(
		'Tujuan sudah dicatat. Silakan share live location (set 8 jam).'
	)
	return LOC

def location(update: Update, context: CallbackContext):
	keyboard= [[InlineKeyboardButton("🏠 Kembali",callback_data=str(BACK))]]
	markup = InlineKeyboardMarkup(keyboard)
	last_id = update.update_id
	user = update.message.from_user
	live_update = update.message.location
	text = ('live location sudah di rekam. Selamat Bertugas. \n')
	#live_update =
	#print(live_update)
	toGeoJson(last_id,user.first_name,live_update.longitude, live_update.latitude,'awal',update.message.date)
	update.message.reply_text(text,reply_markup = markup)
	
	context.user_data[START_OVER] = True
	#getupdate = Update(last_id + 1)
	#print(getupdate.edit_message.location)
	return ConversationHandler.END
	
def cancel(update: Update, context: CallbackContext) -> int:
	user = update.message.from_user
	logger.info("Ambulan ID %s ga jadi ngantar.", user.first_name, update.message.text)
	update.message.reply_text('Tracking ambulan telah dibatalkan')
	#context.user_data[START_OVER] = True
	return ConversationHandler.END

def getUpdateLoc(update: Update,context:CallbackContext):
	print(update)
	global features
	updateId = update.update_id
	currData = update.edited_message
	if currData :
		tgl = currData.edit_date
		lon = currData.location.longitude
		lat = currData.location.latitude
		nm = currData.from_user
		toGeoJson(updateId,nm.first_name, lon,lat,'latest',tgl)
		#writeGeoJson(features)
		
	
def toGeoJson(uid,nm,lon,lat,state,waktu):
	point = Point((lon,lat))
	waktu = str(waktu)
	myfeat = Feature(geometry=point,properties={"upid":uid,"driver":nm,"longitude":lon,"latitude":lat,"waktu":waktu,"state":state})
	writeGeoJson(myfeat)
	
	#features.append(Feature(geometry=point,properties={"upid":uid,"driver":nm,"longitude":lon,"latitude":lat,"waktu":waktu,"state":state}))
	
def writeGeoJson(features):
	feature_collection = FeatureCollection(features)
	with open("ambulan.geojson","a") as f:
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
			DEST: [MessageHandler(Filters.text & ~Filters.command, tujuan)],
			LOC : [MessageHandler(Filters.location,location)],
			INFO: [
				CallbackQueryHandler(info_ambulanmu,pattern='^' +str(INFO) + '$'),
				CallbackQueryHandler(tracking,pattern='^' +str(ANTAR_PASIEN) + '$'),
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
				
