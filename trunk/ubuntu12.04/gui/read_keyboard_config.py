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

import subprocess

def read_keyboard_config():
	layout=None
	model=None
	rules=None
	process = subprocess.Popen(["setxkbmap", "-query"], stdout=subprocess.PIPE)
	config=process.stdout.readlines()
	process.stdout.close()
	for item in config:
		line=item.strip().split()
		if line[0]=='layout:':
			layout=line[1]
		elif line[0]=='model:':
			model=line[1]
		elif line[0]=='rules:':
			rules=line[1]
	return layout, model, rules
	#print config

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
	layout, model, rules=read_keyboard_config()
	print layout, model, rules
