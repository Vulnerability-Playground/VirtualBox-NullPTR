#!/usr/bin/env python
# -*- coding: utf-8 -*-

__DATE__ = '08.04.2020'
__AUTHORS__ = ['cemonatk','FeCassie']
__VERSION__ = 0.9

from subprocess import check_output, PIPE, run
from datetime import datetime as dt

with open("fuzzinputs.txt") as file: # malicious - fuzzing payloads.
    fuzzlist = [line.strip() for line in file]

with open("payloadlist.txt",'r') as file: # babyfuzzer generated command lists with {{-DUMMY-}} string.
	commands = file.readlines()

# karray fireh.
for fuzz in fuzzlist:
	fuzz = fuzz.strip()
	for command in commands:
		command = command.strip().replace('{{-DUMMY-}}', fuzz.strip()).split(' ')
		if command[0] != '':
			try:
				retcode = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True).returncode
			except:
				print("Command didn't work -> {} {}\n".format(command, str(dt.now())))
			if retcode == -11:
				message = "[+] SIGSEGV [-11] -> "+' '.join(command)+" "+str(dt.now())+"\n"
				print(message)
				with open("results.txt",'a') as file:
					file.write(message)
