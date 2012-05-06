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

#This function looks for monitors connected to this computer and returns a dictionary with resolutions supported
def monitor_list():
	monitor, active_mode=parse_xrandr()
	print monitor
	print active_mode
	return monitor, active_mode

def parse_xrandr():
	command_line='xrandr'
	args = shlex.split(command_line)
	pipe = subprocess.Popen(args, shell=True, bufsize=256, stdout=subprocess.PIPE).stdout
	lines=pipe.readlines()
	pipe.close()
	monitor={}
	active_mode={}
	modes=[]
	last_device=None
	last_active_mode=None
	state=0
	for line in lines:
		if state==1:
			#Se buscan las resoluciones soportadas por el monitor
			if line.startswith('   '):
				mode=line.split()[0]
				modes.append(mode)
				if '*' in line:
					last_active_mode=mode
			else:
				#Se añaden las resoluciones encontradas al monitor
				state=0
				monitor[last_device]=modes
				active_mode[last_device]=last_active_mode
				modes=[]
				last_device=None
				last_active_mode=None
		if state==0 and not 'disconnected' in line and 'connected' in line:
			# Se encuentra un monitor conectado y funcionando
			last_device=line.split()[0]
			state=1
	if state==1 and last_device!=None:
		#Quedan resoluciones pendientes de añadir a la lista de monitores
		monitor[last_device]=modes
		active_mode[last_device]=last_active_mode
	return monitor, active_mode




#Sets mode (resolution) to device output. Example: set_monitor_mode('VGA1', '800x480')
def set_monitor_mode(monitor, mode):
	command_line='xrandr --output {monitor} --mode {mode}'.format(monitor=monitor, mode=mode)
	print command_line
	args = shlex.split(command_line)
	process = subprocess.Popen(args, shell=False)
	ok=process.wait()
	#print ok


#monitor=monitor_list()
#print monitor
#set_monitor_mode('LVDS1', '640x480')
#set_monitor_mode('LVDS1', '800x480')



