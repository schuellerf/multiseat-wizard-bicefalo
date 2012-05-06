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

from monitores import *

class MonitoresGUI:

	# This is a callback function. The data arguments are ignored
	# in this example. More on callbacks below.
	def hello(self, widget, data=None):
		print "Hello World"

	def delete_event(self, widget, event, data=None):
		# If you return FALSE in the "delete_event" signal handler,
		# GTK will emit the "destroy" signal. Returning TRUE means
		# you don't want the window to be destroyed.
		# This is useful for popping up 'are you sure you want to quit?'
		# type dialogs.
		print "delete event occurred"

		# Change FALSE to TRUE and the main window will not be destroyed
		# with a "delete_event".
		return False

	def destroy(self, widget, data=None):
		print "destroy signal occurred"
		gtk.main_quit()
	
	def get_active_text(self, combobox):
		model = combobox.get_model()
		active = combobox.get_active()
		if active < 0:
			return None
		return model[active][0]

	def init_monitor_list_gui(self):
		scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		vbox=gtk.VBox()
		scrolled_window.add_with_viewport(vbox)
		self.modes_combos={}
		for k,modes in self.monitor.iteritems():
			frame = gtk.Frame(label=k)
			vbox.pack_start(frame, False, False)
			frame.show()
			combobox = gtk.combo_box_new_text()
			x=0
			for mode in modes:
				combobox.append_text(mode)
				if x!=-1 and mode==self.monitor_active_mode[k]:
					combobox.set_active(x)
					x=-1
				x+=1
			frame.add(combobox)
			combobox.show()
			self.modes_combos[k]=combobox
		vbox.show()
		scrolled_window.show()
		return scrolled_window
	
	def reload_callback(self, widget, data=None):
		self.vbox.remove(self.scrolled_window)
		self.modes_combos={}
		self.scrolled_window=self.init_monitor_list_gui()
		self.vbox.pack_start(self.scrolled_window)
	
	def init_gui_area(self):
		self.scrolled_window=self.init_monitor_list_gui()
		vbox=gtk.VBox()
		vbox.pack_start(self.scrolled_window)
		hbox=gtk.HBox()
		vbox.pack_end(hbox, False, False)
		hbox.show()
		label=gtk.Label()
		label.set_markup("""<b>Description:</b> Select resolution of each screen""")
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
		self.monitor, self.monitor_active_mode=monitor_list()
		#self.init_window()
	
	def init_window(self):
		# create a new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

		# When the window is given the "delete_event" signal (this is given
		# by the window manager, usually by the "close" option, or on the
		# titlebar), we ask it to call the delete_event () function
		# as defined above. The data passed to the callback
		# function is NULL and is ignored in the callback function.
		self.window.connect("delete_event", self.delete_event)

		# Here we connect the "destroy" event to a signal handler.  
		# This event occurs when we call gtk_widget_destroy() on the window,
		# or if we return FALSE in the "delete_event" callback.
		self.window.connect("destroy", self.destroy)

		# Sets the border width of the window.
		self.window.set_border_width(10)

		# Creates a new button with the label "Hello World".
		self.button = gtk.Button("Hello World")

		# When the button receives the "clicked" signal, it will call the
		# function hello() passing it None as its argument.  The hello()
		# function is defined above.
		self.button.connect("clicked", self.hello, None)

		# This will cause the window to be destroyed by calling
		# gtk_widget_destroy(window) when "clicked".  Again, the destroy
		# signal could come from here, or the window manager.
		self.button.connect_object("clicked", gtk.Widget.destroy, self.window)

		# This packs the button into the window (a GTK container).
		self.window.add(self.init_gui_area())

		# The final step is to display this newly created widget.
		self.button.show()

		# and the window
		self.window.show()

	def main(self):
		# All PyGTK applications must have a gtk.main(). Control ends here
		# and waits for an event to occur (like a key press or mouse event).
		gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
	gui = MonitoresGUI()
	gui.main()
