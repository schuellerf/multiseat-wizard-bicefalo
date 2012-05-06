#!/usr/bin/python
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

import shlex, subprocess
import pygtk
pygtk.require('2.0')
import gtk

from monitores import *

class USBsGUI:

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
		
		#print self.get_devices_list()

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
	
	def get_devices_list(self):
		model=self.seats_treeview.get_model()
		seats_usbs_list=[]
		n=0
		for seat_iter in self.iter_seats_list:
			if model.iter_has_child(seat_iter):
				usb_iter=model.iter_children(seat_iter)
			else:
				usb_iter=None
			seats_usbs_list.append([])
			x=0
			while usb_iter!=None:
				seats_usbs_list[n].append(str(model[usb_iter][0]))
				x+=1
				usb_iter=model.iter_next(usb_iter)
			n+=1
		return seats_usbs_list

	def set_number_of_seats(self, n):
		self.number_of_seats=n
		self.init_seats_list_model()

	def init_seats_list_model(self):
		model=self.seats_treeview.get_model()
		# Delete all items of treeview
		iters=[]
		itera=model.get_iter_first()
		while itera!=None:
			iters.append(itera)
			itera=model.iter_next(itera)
		for itera in iters:
			path = model.get_path(itera)
			model.remove(itera)
			model.row_deleted(path)
		self.iter_seats_list=[]
		for n in range(0,self.number_of_seats):
			itera=model.append(None, ['Seat '+str(n)])
			self.iter_seats_list.append(itera)
	
	def add_callback(self, widget, data=None):
		(model_usb, iter_usb) = self.ubs_treeview.get_selection().get_selected()
		(model_seat, iter_seat) = self.seats_treeview.get_selection().get_selected()
		usb=model_usb.get_value(iter_usb,0)
		if model_seat.iter_parent(iter_seat)!=None:
			iter_seat=model_seat.iter_parent(iter_seat)
		model_seat.append(iter_seat, [usb])
	
	def delete_callback(self, widget, data=None):
		(model_seat, iter_seat) = self.seats_treeview.get_selection().get_selected()
		if model_seat.iter_parent(iter_seat)!=None:
			path = model_seat.get_path(iter_seat)
			model_seat.remove(iter_seat)
			model_seat.row_deleted(path)
	
	def reload_callback(self, widget, data=None):
		model=self.ubs_treeview.get_model()
		iters=[]
		itera=model.get_iter_first()
		while itera!=None:
			iters.append(itera)
			itera=model.iter_next(itera)
		for itera in iters:
			path = model.get_path(itera)
			model.remove(itera)
			model.row_deleted(path)
		for usb in usb_list():
			model.append(None, [usb])
	
	def init_treeview(self, label):
		treestore = gtk.TreeStore(str)
		# create the TreeView using treestore
		treeview = gtk.TreeView(treestore)
		# create the TreeViewColumn to display the data
		tvcolumn = gtk.TreeViewColumn(label)
		# add tvcolumn to treeview
		treeview.append_column(tvcolumn)
		# create a CellRendererText to render the data
		cell = gtk.CellRendererText()
		# add the cell to the tvcolumn and allow it to expand
		tvcolumn.pack_start(cell, True)
		# set the cell "text" attribute to column 0 - retrieve text
		# from that column in treestore
		tvcolumn.add_attribute(cell, 'text', 0)
		# make it searchable
		treeview.set_search_column(0)
		# Allow sorting on the column
		tvcolumn.set_sort_column_id(0)
		# Allow drag and drop reordering of rows
		treeview.set_reorderable(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
		return treeview
	
	def init_gui_area(self):
		# create the TreeView using treestore
		self.ubs_treeview = self.init_treeview('Plugged devices')
		self.seats_treeview = self.init_treeview('Seats devices')
		#self.scrolled_window=self.init_usb_list_gui()
		vbox=gtk.VBox()
		label=gtk.Label()
		label.set_markup("""<b>Description:</b> Select devices of each seat. Plug a pendrive and push refresh to see available USB ports.""")
		vbox.pack_end(label, False, False)
		hbox=gtk.HBox()
		vbox.pack_start(hbox, True, True)
		vbox1=gtk.VBox()
		vbox2=gtk.VBox()
		hbox.pack_start(vbox1, True, True)
		hbox.pack_start(vbox2, True, True)
		scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		scrolled_window.add_with_viewport(self.ubs_treeview)
		scrolled_window.show()
		vbox1.pack_start(scrolled_window, True, True)
		scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		scrolled_window.add_with_viewport(self.seats_treeview)
		scrolled_window.show()
		vbox2.pack_start(scrolled_window, True, True)
		
		add_button=gtk.Button(stock=gtk.STOCK_ADD)
		add_button.connect("clicked", self.add_callback, None)
		vbox2.pack_start(add_button, False, False)
		add_button.show()
		
		remove_button=gtk.Button(stock=gtk.STOCK_REMOVE)
		remove_button.connect("clicked", self.delete_callback, None)
		vbox2.pack_start(remove_button, False, False)
		remove_button.show()
		
		refresh_button=gtk.Button(stock=gtk.STOCK_REFRESH)
		refresh_button.connect("clicked", self.reload_callback, None)
		vbox1.pack_start(refresh_button, False, False)
		refresh_button.show()
		refresh_button.connect("clicked", self.reload_callback, None)
		
		hbox.show_all()
		vbox1.show_all()
		vbox2.show_all()
		vbox.show_all()
		
		self.init_seats_list_model()
		
		return vbox

	def __init__(self, number_of_seats):
		self.number_of_seats=number_of_seats
	
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



#This function looks for usb pendrives connected to this computer and returns a list with host plugged
def usb_list():
	usb_list=parse_udisks_dump()
	return usb_list

def parse_udisks_dump():
	command_line='udisks --dump'
	pipe = subprocess.Popen(command_line, shell=True, bufsize=256, stdout=subprocess.PIPE).stdout
	lines=pipe.readlines()
	pipe.close()
	usb_list=[]
	last_device=None
	for line in lines:
		if 'native-path:' in line and '/usb' in line and 'host' in line :
			# Se encuentra un dispositivo conectado y funcionando
			last_device = line[line.find('/devices/'):line.find('/host')]
		elif 'mount paths:' in line and '/media' in line:
			usb_list.append(last_device)
	return usb_list


# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
	gui = USBsGUI(2)
	gui.init_window()
	gui.main()

#print usb_list()



