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

# example basictreeview.py

import pygtk
pygtk.require('2.0')
import gtk
import vte

class Terminal:
	def __init__(self):
		self.terminal = vte.Terminal()
		self.terminal.set_scrollback_lines(1000000)
		#self.terminal.connect("child-exited", self.start)
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		#self.window.set_icon(gtk.gdk.pixbuf_new_from_file(install_path+'/icons/lukecastleslideshow.svg'))
		self.window.set_title("Terminal")
		self.window.set_size_request(700, 400)
		self.window.connect("delete_event", self.delete_event)
		self.vbox=gtk.VBox()
		self.window.add(self.vbox)
		self.vbox.show()
		self.vbox.pack_start(self.terminal)
		self.terminal.show()
		#self.terminal.fork_command("/bin/sh", ["/bin/sh"])
		self.window.show()
	
	def exec_command(self, command, arguments):
		#self.terminal.feed(command+"\n")
		self.terminal.fork_command(command, arguments)
	
	def delete_event(self, widget, event=None, data=None):
		self.window.destroy()
		self.window=None
		return False