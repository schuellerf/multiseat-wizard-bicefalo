#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright (C) 2011  P.L. Lucas, P.L. del Castillo
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require('2.0')
import gtk
import glob
import os.path

class MouseKeyboard:
	def find_devices(self):
		mouse1=glob.glob('/dev/input/by-path/*event-mouse')
		keyboard1=glob.glob('/dev/input/by-path/*event-kbd')
		mouse=[]
		for a in mouse1:
			mouse.append(os.path.basename(a))
		keyboard=[]
		for a in keyboard1:
			keyboard.append(os.path.basename(a))
		return mouse, keyboard
	
	def init_gui_devices(self, number_of_seats):
		mouse, keyboard=self.find_devices()
		self.mouse_combobox=[]
		self.keyboard_combobox=[]
		vbox=gtk.VBox()
		scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		scrolled_window.add_with_viewport(vbox)
		for n in range(0,number_of_seats):
			frame = gtk.Frame(label='Seat {0}'.format(n))
			vbox.pack_start(frame, False, False)
			hbox=gtk.HBox()
			frame.add(hbox)
			label=gtk.Label("Mouse:")
			hbox.pack_start(label, False, False)
			mouse_combobox= gtk.combo_box_new_text()
			x=0
			for m in mouse:
				mouse_combobox.append_text(m)
				if x==n:
					mouse_combobox.set_active(x)
				x+=1
			hbox.pack_start(mouse_combobox, False, False)
			label=gtk.Label("Keyboard:")
			hbox.pack_start(label, False, False)
			keyboard_combobox= gtk.combo_box_new_text()
			x=0
			for m in keyboard:
				keyboard_combobox.append_text(m)
				if x==n:
					keyboard_combobox.set_active(x)
				x+=1
			hbox.pack_start(keyboard_combobox, False, False)
			self.mouse_combobox.append(mouse_combobox)
			self.keyboard_combobox.append(keyboard_combobox)
			hbox.show_all()
		
		vbox.show_all()
		scrolled_window.show()
		return scrolled_window
	
	def reload_callback(self, widget, data=None):
		self.vbox.remove(self.scrolled_window)
		self.scrolled_window=self.init_gui_devices(self.number_of_seats)
		self.vbox.pack_start(self.scrolled_window)
	
	def set_number_of_seats(self, number_of_seats):
		self.number_of_seats=number_of_seats
	
	def init_gui_area(self, number_of_seats):
		self.set_number_of_seats(number_of_seats)
		self.scrolled_window=self.init_gui_devices(number_of_seats)
		vbox=gtk.VBox()
		vbox.pack_start(self.scrolled_window)
		hbox=gtk.HBox()
		vbox.pack_end(hbox, False, False)
		hbox.show()
		label=gtk.Label()
		label.set_markup("""<b>Description:</b> Select mouse and keyboard of each seat""")
		hbox.pack_start(label, True, True)
		label.show()
		button=gtk.Button(stock=gtk.STOCK_REFRESH)
		button.connect("clicked", self.reload_callback, None)
		hbox.pack_start(button, False, False)
		button.show()
		vbox.show()
		self.vbox=vbox
		return vbox

	
	def __init__(self):
		self.find_devices()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
	gui = MouseKeyboard()
	