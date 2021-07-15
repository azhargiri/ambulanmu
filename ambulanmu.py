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
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
	Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
)

TOKEN = '180122124:AAFeshEOGZiBPbCHun443cAFI7s4x3Fh9Xw'

#enable logging
logging.basicConfig(format='%(asctime)s - %(name)s -%(levelname)s - %(message)s',
					level=logging.INFO)
logger = logging.getLogger(__name__)

features = []

def start(update, context):
	"""send message when the command /start is issued."""
	update.message.reply_text('''Met dateng, ni adalah bot utk tracking ambulanmu. \n /tracking : mulai tracking ambuulanmu''')

DEST,LOC = range(2)

def tracking(update: Update, context: CallbackContext):
	user = update.message.from_user
	print(update.update_id)
	logger.info("Driver: %s", user.first_name)
	update.message.reply_text(
		"Kemana tujuan ambulanmu?"
	)
	return DEST

def tujuan(update: Update, context: CallbackContext):
	user = update.message.from_user
	print(update.update_id)
	tujuan = update.message.text
	logger.info("Destination : %s", tujuan)
	update.message.reply_text(
		'Tujuan sudah dicatat. Silakan share live location (set 8 jam).',
		reply_markup = ReplyKeyboardRemove(),
	)
	return LOC

def location(update: Update, context: CallbackContext):
	print(update)
	last_id = update.update_id
	user = update.message.from_user
	live_update = update.message.location
	#live_update =
	#print(live_update)
	toGeoJson(last_id,user.first_name,live_update.longitude, live_update.latitude,'awal',update.message.date)
	update.message.reply_text('live location sudah di rekam. Selamat Bertugas')
	
	
	#getupdate = Update(last_id + 1)
	#print(getupdate.edit_message.location)
	return ConversationHandler.END
	
def cancel(update: Update, context: CallbackContext):
	user = update.message.from_user
	logger.info("Ambulan ID %s ga jadi ngantar.", user.first_name, update.message.text)
	update.message.reply_text('Tracking ambulan telah dibatalkan')
	return ConversationHandler.END

def getUpdateLoc(update: Update,context:CallbackContext):
	print(update.edited_message)
	global features
	updateId = update.update_id
	currData = update.edited_message
	tgl = currData.edit_date
	lon = currData.location.longitude
	lat = currData.location.latitude
	nm = currData.from_user
	toGeoJson(updateId,nm.first_name, lon,lat,'latest',tgl)
	writeGeoJson(features)
	
	
def toGeoJson(uid,nm,lon,lat,state,waktu):
	point = Point((lon,lat))
	waktu = str(waktu)
	features.append(Feature(geometry=point,properties={"upid":uid,"driver":nm,"longitude":lon,"latitude":lat,"waktu":waktu,"state":state}))
	
def writeGeoJson(features):
	feature_collection = FeatureCollection(features)
	with open("ambulan.geojson","w") as f:
		dump(feature_collection,f)

# TODO
# 1. Pendataan lokasi ambulanmu dengan form
# 2. Info lokasi ambulanmu terdekat 
# 3. tracking ambulan dan completion task ambulan tersebut
# 4. dashboard peta lokasi ambulan dan tracking perjalanan ambulanmu
# 5. pendaftaran lokasi relawan escorting ambulanmu
# 6. kirim lokasi ambulanmu yg sedang bertugas kepada relawan terdekat	

def main():
	updater = Updater("{}".format(TOKEN), use_context=True)
	dispatcher = updater.dispatcher
	
	dispatcher.add_handler(CommandHandler("start",start))
	
	loc_handler = ConversationHandler(
		entry_points = [CommandHandler('tracking', tracking)],
		states = {
			DEST: [MessageHandler(Filters.text & ~Filters.command, tujuan)],
			LOC : [MessageHandler(Filters.location,location)]
		},
		fallbacks = [CommandHandler('cancel',cancel)]
	)
	dispatcher.add_handler(loc_handler)
	dispatcher.add_handler(MessageHandler(Filters.all, getUpdateLoc))
	
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
				
