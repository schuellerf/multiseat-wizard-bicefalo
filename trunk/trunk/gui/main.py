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
import sys
import time
import gobject
import os
import sys
import os.path

from terminal import *
from monitores_gui import *
from mouse_keyboard import *
from usb import *

class MainGUI:

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
		gtk.main_quit()
	
	def page_wellcome(self):
		label=gtk.Label()
		label.show()
		label.set_markup("""<b>Description:</b>
		This program lets you install a multiseat system in your computer.
		""")
		return label
	
	def page_number_of_seats(self):
		hbox=gtk.HBox()
		label=gtk.Label('Number of seats:')
		hbox.pack_start(label, False, False)
		self.number_of_seats_entry=gtk.Entry()
		hbox.pack_start(self.number_of_seats_entry)
		hbox.show_all()
		return hbox
	
	def page_final(self):
		scrolled_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		hbox=gtk.HBox()
		scrolled_window.add_with_viewport(hbox)
		self.final_text=gtk.TextView()
		self.final_text.set_cursor_visible(False)
		#self.final_text.get_buffer().set_text('Multiseat summary:\n')
		hbox.pack_start(self.final_text, True, True)
		hbox.show_all()
		scrolled_window.show()
		return scrolled_window
		
	def write_summary(self, text):
		self.final_text.get_buffer().insert(self.final_text.get_buffer().get_end_iter(), text)
		#self.final_text.scroll_to_iter(self.final_text.get_buffer().get_end_iter(), 0.3)
	
	def update_number_seats_callback(self, editable, data=None):
		n=0
		try:
			n=int(self.number_of_seats_entry.get_text())
		except ValueError:
			return False
		self.mouse_keyboard.set_number_of_seats(n)
		self.mouse_keyboard.reload_callback(None)
		self.usbs.set_number_of_seats(n)

	def get_active_text(self, combobox):
		model = combobox.get_model()
		active = combobox.get_active()
		if active < 0:
			return None
		return model[active][0]

	def build_shell_script(self):
		shell="""#!/bin/bash

# For some reason I was unable to set the following in xorg.conf
# We need to turn off power management of the main X server because it doesn't
# see either of the keyboards and the mice so it will enter power-saving mode
# after 10 minutes
export DISPLAY=:0.0
xset s off
xset dpms 0 0 0
xset -dpms

runscreen () {{
	# $1 = number
	# $2 = geometry
	# $3 teclado
	# $4 ratón
	# $5 x
	# $6 y
	
	#xkb='xkbrules=xorg,xkbmodel=evdev,xkblayout=es'
	# Se prueba con la configuración de evdev en lugar de la de xorg
	xkb='xkbrules=evdev,xkbmodel=pc105,xkblayout=es'

	title="Escritorio Xephyr $1 `date -R`"
	xmessage -title "$title" -geometry $2+$5+$6 "$title" &
	sleep 15
	#xwininfo -tree -root
	id_parent=`xwininfo -tree -root | grep -e "$title" | awk '{{print $1}}'`
	echo $id_parent

	echo /home/multiseat/Xephyr :$1  -dpms -keybd "evdev,,device=$3,$xkb" -mouse "evdev,,device=$4" -screen $2 -parent $id_parent -retro
	/home/multiseat/Xephyr :$1 -keybd "evdev,,device=$3,$xkb" -mouse "evdev,,device=$4" -parent "$id_parent" -retro &   
}}

function sesion_usuario () {{
	export DISPLAY=:$1
	while [[ 1 -eq 1 ]] ; do
	xterm -e "echo 'user:' seat$1 'Password:' ; su -c '/home/multiseat/sesion.sh' seat$1"
	sleep 10
	done
}}

metacity &

sleep 5

		""".format(main=sys.argv[0])
		number_of_seats=0
		try:
			number_of_seats=int(self.number_of_seats_entry.get_text())
		except ValueError:
			return None
		
		# List of screen resolutions
		shell+='\n# Screen resolutions\n'
		last=None
		for k,combobox in  self.monitores.modes_combos.iteritems():
			if last!=None:
				shell+='xrandr --output {0} --right-of {1}\n'.format(k, last)
			mode=self.get_active_text(combobox)
			shell+='xrandr --output {0} --mode {1}\n'.format(k, mode)
			last=k
		
		# List of keyboard and mouse
		shell+='\n# Start Xephyr\n'
		for n in range(0,number_of_seats):
			mouse=self.get_active_text(self.mouse_keyboard.mouse_combobox[n])
			keyboard=self.get_active_text(self.mouse_keyboard.keyboard_combobox[n])
			x=0
			pos=0
			for k,combobox in  self.monitores.modes_combos.iteritems():
				if n==x:
					shell+='sleep 5\nrunscreen {display} {mode} "/dev/input/by-path/{kbd}" "/dev/input/by-path/{mouse}" {x} 0 &\n'.format(display=(n+1), mode=mode,kbd=keyboard, mouse=mouse, x=pos )
				mode=self.get_active_text(combobox)
				width=int(mode.split('x')[0])
				x+=1
				pos+=width
				
		# Init user sessions
		shell+='\n# Init user sessions\nsleep 20\n'
		for n in range(0,number_of_seats):
			shell+='sesion_usuario {0} & \n'.format(n+1)
			
		shell+='\n\nsleep 864000\n\n'

		return shell

	def summary_check_callback(self, container, widget, data=None):
		if widget==self.final_widget:
			self.final_text.get_buffer().set_text('Multiseat summary:\n')
			#self.write_summary('Multiseat summary:\n')
			# Check right number of seats
			number_of_seats=0
			try:
				number_of_seats=int(self.number_of_seats_entry.get_text())
				self.write_summary('Number of seats: {0}\n'.format(number_of_seats))
			except ValueError:
				self.write_summary('Number of seats: {0}\n'.format('Error'))
			
			# List of screen resolutions
			self.write_summary('Screen resolutions:\n')
			for k,combobox in  self.monitores.modes_combos.iteritems():
				mode=self.get_active_text(combobox)
				self.write_summary('\t{0}: {1}\n'.format(k, mode))
			
			# List of keyboard and mouse
			self.write_summary('Keyboard and mouse per seat:\n')
			for n in range(0,number_of_seats):
				mouse=self.get_active_text(self.mouse_keyboard.mouse_combobox[n])
				keyboard=self.get_active_text(self.mouse_keyboard.keyboard_combobox[n])
				self.write_summary('\tSeat {0}:\n\t\tMouse:\t\t{1}\n\t\tKeyboard:\t{2}\n'.format(n, mouse, keyboard))
			
			# List of USBs ports
			self.write_summary('USB ports per seat:\n')
			n=0
			for usbs in self.usbs.get_devices_list():
				self.write_summary('\tSeat {0}:\n'.format(n))
				for usb in usbs:
					self.write_summary('\t\t{0}\n'.format(str(usb)))
				self.write_summary('\n')
				
			self.write_summary('\n\n')
			
			print self.build_shell_script()
			
	def init_gui(self):
		self.assistant=gtk.Assistant()
		#self.assistant.set_forward_page_func(None, None)
		
		widget=self.page_wellcome()
		self.assistant.append_page(widget)
		self.assistant.set_page_title(widget, 'Bicéfalo')
		self.assistant.set_page_type(widget, gtk.ASSISTANT_PAGE_INTRO)
		self.assistant.set_page_complete(widget, True)
		
		widget=self.page_number_of_seats()
		self.assistant.append_page(widget)
		self.assistant.set_page_title(widget, 'Number of seats')
		self.assistant.set_page_complete(widget, True)
		
		self.monitores=MonitoresGUI()
		widget=self.monitores.init_gui_area()
		self.assistant.append_page(widget)
		self.assistant.set_page_title(widget, 'Screen')
		self.assistant.set_page_complete(widget, True)
		
		self.number_of_seats_entry.set_text(str(len(self.monitores.modes_combos)))
		
		self.mouse_keyboard=MouseKeyboard()
		widget=self.mouse_keyboard.init_gui_area(int(self.number_of_seats_entry.get_text()))
		self.assistant.append_page(widget)
		self.assistant.set_page_title(widget, 'Mouse and Keyboard')
		self.assistant.set_page_complete(widget, True)
		
		self.usbs=USBsGUI(int(self.number_of_seats_entry.get_text()))
		widget=self.usbs.init_gui_area()
		self.assistant.append_page(widget)
		self.assistant.set_page_title(widget, 'USB')
		self.assistant.set_page_complete(widget, True)
		
		widget=self.page_final()
		self.assistant.append_page(widget)
		self.assistant.set_page_title(widget, 'Summary')
		self.assistant.set_page_type(widget, gtk.ASSISTANT_PAGE_CONFIRM)
		self.assistant.set_page_complete(widget, True)
		self.final_widget=widget
		
		self.assistant.update_buttons_state()
		
		self.number_of_seats_entry.connect("changed", self.update_number_seats_callback)
		#self.assistant.connect("close", self.destroy)
		self.assistant.connect("cancel", self.destroy)
		self.assistant.connect("set-focus-child", self.summary_check_callback)
		self.assistant.connect("apply", self.apply_callback)
		
		return self.assistant
	
	def apply_callback(self,assistant, data=None):
		#terminal=Terminal()
		#terminal.exec_command("bash", [])
		number_of_seats=0
		try:
			number_of_seats=int(self.number_of_seats_entry.get_text())
		except ValueError:
			self.write_summary('Number of seats: {0}\n'.format('Error'))
			return False
		commands="# Se crean los usuarios del multiseat\n"
		for n in range(1, number_of_seats+1):
			commands+="useradd -m seat{n}\nprintf 'seat{n}\\nseat{n}' | passwd seat{n}\n".format(n=n)
		commands+="# Se crea el usuario multiseat\n"
		commands+="useradd -m multiseat\nprintf 'multiseat\\nmultiseat' | passwd multiseat\n"
		commands+="# Se copia el script de arranque en el usuario multiseat\n"
		commands+="cat <<EOF > /home/multiseat/multiseat.sh\n" +self.build_shell_script().replace('\\','\\\\').replace('$','\\$').replace('`','\\`')+"\nEOF\n"
		commands+="chown multiseat:multiseat /home/multiseat/multiseat.sh\n"
		commands+="chmod +x /home/multiseat/multiseat.sh\n"
		commands+="# Se configura el arranque automático del multiseat\n"
		commands+="""cat <<EOF > /usr/share/xsessions/mulsiseat.desktop
[Desktop Entry]
Encoding=UTF-8
Name=Multiseat
Comment=Multiseat session
Exec=/home/multiseat/multiseat.sh
TryExec=xterm
Icon=
Type=Application
X-Ubuntu-Gettext-Domain=gdm
EOF
"""
		commands+="chmod +r /usr/share/xsessions/mulsiseat.desktop\n"
#		commands+="mkdir -p /home/multiseat/.config/autostart\n"
#		commands+="chown multiseat:multiseat /home/multiseat/.config/autostart\n"
#		commands+="""cat <<EOF > /home/multiseat/.config/autostart/multiseat.desktop

#[Desktop Entry]
#Name=Multiseat
#Comment=Launch multiseat
#Icon=folder-remote
#Exec=/home/multiseat/multiseat.sh
#Terminal=false
#Type=Application
#EOF
#"""
		commands+="# Se copia Xephyr al directorio multiseat y se dan permisos en udev para iniciar Xephyr con el control de los dispositivos de entrada\n"
		commands+="cp ./Xephyr /home/multiseat/\n"
		commands+="chown multiseat:multiseat /home/multiseat/Xephyr\n"
		commands+="chmod u+x /home/multiseat/Xephyr\n"
		commands+="# Se hace que los ratones y teclados pertenezcan al usuario multiseat\n"
		commands+="""cat <<EOF > /etc/udev/rules.d/10-multiseat.rules
SUBSYSTEM=="input", OWNER="multiseat", GROUP="multiseat"
EOF



"""
		commands+="""# Se copia el fichero de arranque de los usuarios
cat <<EOF > /home/multiseat/sesion.sh
#!/bin/bash
#Se configura el mapa del teclado
export `dbus-launch`
# No es necesaria la siguiente línea si el mapa del teclado cargado en Xephyr, es el correcto, se comenta
#xterm -e 'xmodmap /home/multiseat/teclado.txt'
gnome-session
EOF

chown multiseat:multiseat /home/multiseat/sesion.sh
chmod +x /home/multiseat/sesion.sh

# Copia el mapa de teclado para que funcione en Xephyr
xmodmap -pke > /home/multiseat/teclado.txt
chown multiseat:multiseat /home/multiseat/teclado.txt
chmod +r /home/multiseat/teclado.txt

""".replace('\\','\\\\').replace('$','\\$').replace('`','\\`')
		# Gestión de USBs
		#udev_file=open("/etc/udev/rules.d/10-multiseat.rules",'w')
		udev_file=''
		fstab_file=''
		mkdir_file=''
		n_user=1
		n_usb=0
		for usbs in self.usbs.get_devices_list():
			user='seat{0}'.format(n_user)
			mkdir_file+='mkdir /home/{usuario}/usbdrive\nchown {usuario}:root /home/{usuario}/usbdrive\n'.format(usuario=user)
			for usb in usbs:
				udev_file+='SUBSYSTEMS=="usb", DRIVERS=="usb", DEVPATH=="{puesto}*", ATTRS{{product}}=="*", SYMLINK+="multiseatusb{n}", OWNER="{usuario}"\n'.format(usuario=user,puesto=usb,n=chr(n_usb+97))
				fstab_file+='/dev/multiseatusb{n} /home/{usuario}/usbdrive vfat rw,owner,noauto,group,flush,quiet,nodev,nosuid,noexec,noatime,dmask=007,fmask=117 0 0\n'.format(n=chr(n_usb+97), usuario=user)
				n_usb+=1
			n_user+=1
		commands+="""

# Se añaden las reglas udev para la gestión de pendrives
cat<<EOF >> /etc/udev/rules.d/10-multiseat.rules
{udev_file}
EOF

#Se modifica el fichero fstab
#Primero se elmina toda la configuración anterior
sed -e 's/\/dev\/multiseatusb.*//' /etc/fstab > /tmp/fstab
cat<<EOF >> /tmp/fstab
{fstab_file}
EOF
mv -f /tmp/fstab /etc/fstab

#Se crean los puntos de montaje en los directorios de los usuarios
{mkdir_file}

""".format(udev_file=udev_file,fstab_file=fstab_file, mkdir_file=mkdir_file)
		# Se añaden las entradas en el fichero fstab
		
		commands+="\npython {main} --info 'The End'\n".format(main=sys.argv[0])
		print commands
		f=open('/tmp/multiseat.sh','w')
		f.write(commands)
		f.close()
		os.system('bash /tmp/multiseat.sh')
		#timeout=gobject.timeout_add(1000, feed_terminal_callback, terminal, commands)
	
	def __init__(self):
		self.init_window()
	
	def init_window(self):
		# create a new window
		self.window = self.init_gui()

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

		# and the window
		self.window.show()
		self.window.maximize()

	def main(self):
		# All PyGTK applications must have a gtk.main(). Control ends here
		# and waits for an event to occur (like a key press or mouse event).
		gtk.main()

def feed_terminal_callback(terminal, commands):
	terminal.terminal.feed_child(commands+'\n')
	#gobject.source_remove(timeout)
	return False


# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
	if len(sys.argv)<2:
		gui = MainGUI()
		gui.main()
	elif sys.argv[1]=='--info':
		info=sys.argv[2]
		dialog=gtk.MessageDialog()
		dialog.set_markup(info)
		dialog.connect("delete_event", gtk.main_quit)
		dialog.connect("destroy", gtk.main_quit)
		dialog.show()
		gtk.main()
	elif sys.argv[1]=='--terminal':
		commands=sys.argv[2]
		terminal=Terminal()
		terminal.exec_command("bash", [])
		terminal.window.connect("delete_event", gtk.main_quit)
		terminal.window.connect("destroy", gtk.main_quit)
		timeout=gobject.timeout_add(1000, feed_terminal_callback, terminal, commands)
		gtk.main()
	elif sys.argv[1]=='--user-session':
		commands="""#!/bin/bash
#Se configura el mapa del teclado
export `dbus-launch`
metacity &
sleep 5
xmodmap '/usr/local/share/multiseat/teclado.txt'
bash
"""
		os.system(commands)
