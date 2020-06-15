#!/usr/bin/env python
# -*- coding: utf-8 -*-

__DATE__ = '08.04.2020'
__AUTHORS__ = ['cemonatk','FeCassie']
__VERSION__ = 0.9

from subprocess import check_output, PIPE, run
from yaml import FullLoader, load
from itertools import chain, combinations
from time import sleep
import re

def find_between(start, end, cmdoutput):
	cmdoutput = cmdoutput.lower().replace("\n","")
	pattern = r''+start+'.+?'+end
	matches = re.findall(pattern,cmdoutput)
	return matches

def config_parser(yaml_file='config.yaml'):
    with open(yaml_file) as file:
        config_dict = load(file, Loader=FullLoader)
    internalcommands = config_dict['internalcommands']
    return config_dict, internalcommands

def config_dict_reader(array, config_dict):
    contained_keys = []
    for key in config_dict.keys():
        mapping.append((key, config_dict[key]))
    for key in array:
        if key in config_dict.keys():
            contained_keys.append(key)
    return mapping, contained_keys

def param_cleaner(cmd_param, params):
    # 'relkeselose'[::-1]
    for param in params:
        #print(param)
        if param[1:-1] in cmd_param:
             cmd_param.remove(param[1:-1])
    return cmd_param, params

# https://www.youtube.com/watch?v=IWpBzKPjtc0
def param_parser(params):
    tmp_param = []
    for line in params:
        line = line[1:-1]
        if "|" in line:
            tmp_line = line.split('|')
            # +1 space"-srcformat vdi", "vmdk". amaan.
            for i in tmp_line:
                if i != '...':
                    tmp_param.append(i)
        else:
            tmp_param.append(line)
    return(tmp_param)

# https://leetcode.com/problems/subsets/
def powerset(arr):
	subsets =[[]]
	for element in arr:
		for i in range(len(subsets)):
			cur_set = subsets[i]
			subsets.append(cur_set + [element])
	return subsets

def remove_duplicates(array):
    tmp_arr = []
    uniq = [tmp_arr.append(x) for x in array if x not in tmp_arr]
    return tmp_arr

if __name__ == "__main__":
    command_list, payload, cmd_out, mapping, used, payloads, pre_payloads = [], [], [], [], [], [], []
    payload_map = {}
    config_dict, internalcommands = config_parser()
    fuzz_cmd = "VBoxManage internalcommands "
    # Overwrite internalcommads, since some of them in improper format. Fix later.
    internalcommands = ['debuglog', 'sethduuid', 'converthd']

    for internalcmd in internalcommands:
        params, cmd_param = [], []
        command = ["VBoxManage", "internalcommands", internalcmd]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        strout=str(result.stderr)
        cmd_out = find_between("commands:", "warning", strout)
        
        for commandout in cmd_out:
            params += find_between("\[", "\]", commandout)
            cmd_param += find_between("<", ">", commandout)

        cmd_param, params = param_parser(cmd_param), param_parser(params)
        cmd_param, params = param_cleaner(cmd_param, params)
        payload_map[internalcmd] = {'values': cmd_param, 'subcommands': params}
    
    # n^3
    for key in payload_map:
        for inner_key in payload_map[key]:
            for i in powerset(payload_map[key][inner_key]):
                if len(i) != 0:
                    tmp_str = '{}{} {}'.format(fuzz_cmd, key, ' '.join(i))
                    command_list.append(tmp_str)
  
    # test: command_list = ['VBoxManage internalcommands debuglog vmname --disable --destinations todo', 'VBoxManage internalcommands repairhd -dry-run -format VDI filename', 'VBoxManage internalcommands renamevmdk -from filename -to filename', 'VBoxManage internalcommands converthd -srcformat VDI -dstformat VDI inputfile outputfile']
    
    # oha for <3
    for command in command_list:
        mapping, contained_keys = config_dict_reader(command.split(' '), config_dict)
        
        for i in powerset(contained_keys):
            if len(i) != 0:
                payloads.append(command.replace(' '.join(i),"{{-DUMMY-}}"))

        for k, v in mapping:
            for payload in payloads:
                if type(v) != list:
                    payload = payload.replace(k, v)
                    pre_payloads.append(payload)
                else:
                    for item in v:
                        payload = payload.replace(k, item)
                        pre_payloads.append(payload)

        for payload_item in remove_duplicates(pre_payloads):
            print(payload_item)
