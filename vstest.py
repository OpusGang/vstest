###########################################
# VSTEST                                  #
###########################################
# testing codecs' settings through vspipe


import os, sys, argparse, subprocess, re, datetime
from itertools import product
from decimal import *
from pathlib import Path
from vstestconfig import *


# LOADING ARGS AND CONFIG
#########################

# Defining vstest arguments
parser = argparse.ArgumentParser()
parser.add_argument('-codec', help="Codec to which settings are passed.", required=False)
parser.add_argument('-script', help="Path to testing script", required=False)
parser.add_argument('-folder', help="Path to testing folder", required=False)
parser.add_argument('-multipass', action="store_true", help="Multipass mode. Number of passes defined by config's 'multipass_opts'.", required=False)
parser.add_argument('-vbv', action="store_true", help="Enables VBV in testing mode.", required=False)
parser.add_argument('-predef', help="Choose a custom codec preset defined in the config file.", required=False)
parser.add_argument('-require', help="Force an inequality condition between 2 tested settings. Should be \'set1<set2\'", required=False)
parser.add_argument('-verbose', action="store_true", help="Displays additionnal information.", required=False)
parser.add_argument('-sim', action="store_true", help="Simulation mode. No encoding/removing is performed. Displays verbose information.", required=False)
parser.add_argument('-owrite', action="store_true", help="Overwrite existing encodes.", required=False)
parser.add_argument('-remove', action="store_true", help="Remove all encodes of the current tested setting.", required=False)
parser.add_argument('-clean', action="store_true", help="Remove all encodes of all tested settings.", required=False)
parser.add_argument('-gencomp', action="store_true", help="Generate a comparison script from the input encoding script.", required=False)
parser.add_argument('-extract', help="Choose how to extract frames from clip. Should be <length>:<every>:<offset>", required=False)
parser.add_argument('-editor', default='vsedit', help="Choose your prefered vapoursynth editor, named as you would call it from commandline. Default: vsedit", required=False)

# Parsing user arguments
vstest_opts, codec_args = parser.parse_known_intermixed_args()
if vstest_opts.sim == True: vstest_opts.verbose = True

# Loading codec opts from config file
if vstest_opts.codec is not None:
	file_ext = globals()[vstest_opts.codec]['file_ext']
	codec_opts_def = globals()[vstest_opts.codec]['codec_opts_def'].split(' ')
	multipass_opts = globals()[vstest_opts.codec]['multipass_opts']
	vbv_opts = globals()[vstest_opts.codec]['vbv_opts']
	num_frames_opt = globals()[vstest_opts.codec]['num_frames_opt']
	index = globals()[vstest_opts.codec]['index']
	demux_opt = globals()[vstest_opts.codec]['demux_opt']
	out_opt = globals()[vstest_opts.codec]['out_opt']
	if vstest_opts.predef is not None:
		for preset in globals()[vstest_opts.codec]['custom_preset']:
			if vstest_opts.predef == preset[0]: codec_opts_def = codec_opts_def + preset[1].split(' ')
			
if vstest_opts.folder is not None: folder = vstest_opts.folder
if vstest_opts.script is not None: script = vstest_opts.script
if vstest_opts.gencomp == True: gen_comp_script = vstest_opts.gencomp

if folder.rfind('/') < len(folder)-1: folder = folder + '/'

# DEFINING UTILITY FUNCTIONS
############################

# range for decimals
def frange(start=0, stop=1, step=1):		
    count = 0
    while True:
        temp = Decimal(start + count * step)
        if step > 0 and temp > stop:
            break
        elif step < 0 and temp < stop:
            break
        yield temp
        count += 1

# checking user codec args and default opts for duplicates and merge them
def codec_opts_upd():
	global codec_opts
	global codec_opts_def
	global settings
	global codec_opts_passed
	for opt in settings:
		if opt[0:2] == '--' or (opt[0] == '-' and opt[1].isalpha()):
			if opt in codec_opts:
				k = codec_opts.index(opt)
				del codec_opts[k]
				if codec_opts[k][0:2] != '--' and (not (codec_opts[k][0] == '-' and codec_opts[k][1].isalpha())):
					del codec_opts[k]
	for opt in codec_opts + settings:
		if opt[0:2] == '--' or (opt[0] == '-' and opt[1].isalpha()):
			if opt in codec_opts_def:
				k = codec_opts_def.index(opt)
				del codec_opts_def[k]
				if codec_opts_def[k][0:2] != '--' and (not (codec_opts_def[k][0] == '-' and codec_opts_def[k][1].isalpha())):
					del codec_opts_def[k]

	codec_opts_passed = codec_opts + codec_opts_def
	if vstest_opts.verbose == True: print(' +options passed to codec: ',codec_opts_passed,'\n')


# Encode			
def encode(enc_opts):
	cmd = 'vspipe -c y4m ' + script + ' - | ' + vstest_opts.codec + ' ' + demux_opt + ' - ' + enc_opts
	log = ''
	if vstest_opts.verbose == True:
		print('$ ' + cmd,'\n')
	if vstest_opts.sim == False:
		# Popen to run the encode while continue reading code
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
		# while encoding, process output line by line
		prev = ''
		for line in iter(process.stdout.readline, ''):
			# if current and previous lines differ by more than digits, print and save log
			if re.sub('\d', '', line) != re.sub('\d', '', prev):
				print(line.strip())
				if logs == True: log = log + '\n' + line.strip()
				# if current and previous lines differ only by digits, print it as ephemeral
			else:
				print(line.strip(), end="\r")
			sys.stdout.flush()
			prev = line
			# open logfile and save log
		if logs == True:
			logfile = open(folder + vstest_opts.codec + '.log', "a+")
			logfile.write('########## ' + str(datetime.datetime.now()) + '\n')
			logfile.write(vstest_opts.codec + ' settings: ' + enc_opts)
			logfile.write('\n----------' + log + '\n----------\n\n')
			logfile.close()
		print('')
			
# Generate a vs script from an existing one and adds awsmfunc if not already used
def copyscript(inp, out):
	
	out_file = open(out, 'w+')
	inp_file = open(inp, 'r')
	
	#from the encoding script
	awsmf_name = ''
	for line in inp_file.readlines():
		if '.set_output()' not in line:
	 		out_file.write(line)
		 	if 'import awsmfunc' in line:
		 		if 'as' in line:
		 			awsmf_name = line[line.find(' as ')+3:].replace('\n', '')
		 		else:
		 			awsmf_name = 'awsmfunc'
		else:
		 	last = line.replace('.set_output()','')
		 	last = last.replace('\n','')
	inp_file.close
	
	# import awsmfunc if not already used
	if awsmf_name == '':
		out_file.write('\nimport awsmfunc as awsf')
		awsmf_name = 'awsf'
	out_file.close
	
	return last, awsmf_name

print('')

if vstest_opts.verbose == True:
	print('+USER ARGUMENTS')
	print(' +vstest options: ',str(vstest_opts).replace('Namespace(','').replace(')',''))
	print(' +codec user args: ',codec_args,'\n')
	
	print('+CONFIGURATION')
	print(' +vapoursynth script: ',script)
	print(' +testing folder: ',folder)
	print(' +delimiters and separator: ',delimiter1, delimiter2, separator)
	if vstest_opts.codec is not None:
		print(' +codec file extension: ',file_ext)
		print(' +codec output option: ',out_opt)
		print(' +codec default options: ',codec_opts_def)
		print(' +codec multipass options: ',multipass_opts)
		print(' +codec vbv disable options: ',vbv_opts,'\n')


# CLEANING TASK
###############

if vstest_opts.clean == True:
	cmd = 'rm -rf ' + folder + '*'
	if vstest_opts.verbose == True: print('$' + cmd, '\n')
	if vstest_opts.sim == False: subprocess.run(cmd, shell=True)
	print('Encodes in ' + folder + ' were removed.\n')
	
# EXTRACTING
############

if vstest_opts.extract is not None:
	#Check if script folder exists
	if not Path(folder + '.scripts/').is_dir():
		os.mkdir(folder + '.scripts/')
	
	length = vstest_opts.extract[0:vstest_opts.extract.find(':')]
	every = vstest_opts.extract[vstest_opts.extract.find(':') + 1:vstest_opts.extract.rfind(':')]
	offset = vstest_opts.extract[vstest_opts.extract.rfind(':') + 1:]
	
	# Create extract script
	last, awsmf_name = copyscript(script, folder + '.scripts/extract.vpy')
	extract_script = open(folder + '.scripts/extract.vpy', 'a')
	extract_script.write('\next = ' + awsmf_name + '.SelectRangeEvery(clip=' + last + ', every='+ every +', length=' + length + ', offset=' + offset +')')
	extract_script.write('\next.set_output()')
	extract_script.close()
	script = folder + '.scripts/extract.vpy'

# CHECKING ARGUMENTS FOR TESTING
################################

codec_opts = []
settings = []
valuess = []
codec_opts_passed = []

for i in range(0,len(codec_args)-1):
	opt = codec_args[i]
	opt1 = codec_args[i+1]
	if (opt[0:2] == '--' or (opt[0] == '-' and opt[1].isalpha())) and (opt1[0:2] != '--' and (not (opt1[0] == '-' and opt1[1].isalpha()))):
		# Current opt is a setting to test
		if delimiter1 in opt1:
			opt1 = [opt1]
			settings.append(opt)
			values = opt1
			# multitesting for the current opt
			while delimiter1 in values[0]:
				param = opt1[0][opt1[0].find(delimiter1)+1:opt1[0].find(delimiter2)]
				tvalues = list(frange(Decimal(param.split(separator)[0]),Decimal(param.split(separator)[1]),Decimal(param.split(separator)[2])))
				values = [y[0:y.find(delimiter1)] + str(x) + y[y.find(delimiter2)+1:] for x in tvalues for y in opt1]
				opt1 = values
			valuess.append(values)
		# current opt is not a setting to test
		else:
			codec_opts.append(opt)
			codec_opts.append(opt1)

if vstest_opts.verbose == True:
	print('+REQUESTED TESTING')
	print(' +settings to test: ',settings)
	print(' +values to test per setting: ',valuess)
	print(' +codec options: ',codec_opts,'\n')

# ENCODING LOOP
###############

info = os.popen('vspipe -c y4m ' + script + ' -i - ')
for i in info:
	if i[0:6] == 'Frames':
		if num_frames_opt:
			info = num_frames_opt + i.split(':')[1]
		else:
			info = ''

# No encodes
if codec_opts == [] and settings == []:
	pass

# encoding single file: codec options without settings to test
elif codec_opts != [] and settings == []:

	codec_opts = codec_args
	codec_opts_upd()
	print('(1/1) Encoding output\n')
	if vstest_opts.multipass is False:
			encode(' '.join(codec_opts_passed) + ' ' + info)
	else:
		for p in range(1,len(multipass_opts)+1):
			print('> Pass ' + str(p))
			encode(' '.join(codec_opts_passed) + ' ' + multipass_opts[p-1] + ' ' + info)

# Testing mode
else:
	
	# Building the pools to encode
	if vstest_opts.require is not None:
		# inequality condition between 2 tested settings
		pools = []
		for k, values in enumerate(product(*valuess)):
			set1 = vstest_opts.require[0:vstest_opts.require.find('<')]
			set2 = vstest_opts.require[vstest_opts.require.find('<')+1:]
			if values[settings.index('--' + set1)] < values[settings.index('--' + set2)]:
				pools.append(values)
	else:
		pools = list(product(*valuess))
		
	if vstest_opts.verbose == True: print(' +pools of values to test: ',pools)
	
	codec_opts_upd()
	
	# Number of encodes and parent folder
	n = len(pools)
	parent = str(settings).replace('--', '').replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').replace(',', '.') + '/'
	
	# removing task for current settings
	if vstest_opts.remove == True:
		cmd = 'rm -rf ' + folder + parent + '*'
		if vstest_opts.verbose == True: print('$' + cmd, '\n')
		if vstest_opts.sim == False: subprocess.run(cmd, shell=True)
		print('Encodes in ' + folder + parent + ' were removed.\n')
	
	# Encoding each pool
	for k, values in enumerate(pools):
		
		# building opts for tested settings
		test = ''
		for i, value in enumerate(values):
			test = test + ' ' + settings[i] + ' ' + str(value)
		test = test[1:]
		
		# test's name
		name = str(test).replace('--', '').replace(':', '.').replace(' ', '_') + '.' + file_ext
		
		# create folder if necessary
		if not Path(folder + parent).is_dir():
			os.mkdir(folder + parent)
		
		# encode path
		enc_path = folder + parent + name
		codec_opts_passed.append(out_opt)
		codec_opts_passed.append(enc_path)
			
		# encoding
		print('(' + str(k+1) + '/' + str(n) + ') Processing encode with ' + str(test),'\n')
		
		if vstest_opts.multipass is False:
			if not Path(enc_path).is_file() or vstest_opts.owrite == True:
					if vstest_opts.vbv == True:
						encode(test + ' ' + ' '.join(codec_opts_passed) + ' ' + info)
					else:
						encode(test + ' ' + ' '.join(codec_opts_passed) + ' ' + vbv_opts + ' ' + info)
			elif Path(enc_path).is_file():
				print('Skipping encoding as file ' + enc_path + ' already exists.\n')
		else:
			if not Path(enc_path).is_file() or vstest_opts.owrite == True:
				for p in range(1,int(len(multipass_opts))+1):
					print('> Pass ' + str(p))
					if vstest_opts.vbv == True:
						encode(test + ' ' + ' '.join(codec_opts_passed) + ' ' + multipass_opts[p-1] + ' ' + info)
					else:
						encode(test + ' ' + ' '.join(codec_opts_passed) + ' ' + multipass_opts[p-1] + ' ' + vbv_opts + ' ' + info)
			elif Path(enc_path).is_file():
				print('Skipping encoding as file ' + enc_path + ' already exists.\n')
		
		codec_opts_passed = codec_opts_passed[:-2]
	

# COMPARISON SCRIPT
###################
	
	if gen_comp_script == True:
		
		# Create comparison script
		last, awsmf_name = copyscript(folder + '.scripts/extract.vpy', folder + '.scripts/comparison.vpy')
		comp_file = open(folder + '.scripts/comparison.vpy', 'a')

		files = sorted(os.listdir(folder + parent))
		
		comp_file.write("\nclips = [" + str(awsmf_name + ".FrameInfo(" + last + ", 'Source')").strip('\'') + ', ')
		for f in files:
			if f.endswith('.' + file_ext):
				if repeat_src_comp == True:
					comp_file.write(str(awsmf_name + ".FrameInfo(" + index + "(r\'" + folder + parent + f + "\'), \'" + f.replace('_',' ').replace('.' + file_ext,'') + "\')").replace('\"','') + ', ' + str(awsmf_name + ".FrameInfo(" + last + ", 'Source')").strip('\'') + ', ')
				else:
					comp_file.write(str(awsmf_name + ".FrameInfo(" + index + "(r\'" + folder + parent + f + "\'), \'" + f.replace('_',' ').replace('.' + file_ext,'') + "\')").replace('\"','') + ', ')
		comp_file.write(str(awsmf_name + ".FrameInfo(" + last + ", 'Source')]").strip('\''))
		
		comp_file.write('\ncomparison = core.std.Interleave(clips)')
		comp_file.write('\ncomparison.set_output()')
		comp_file.close()
		
		# starting vs editor and opening script for user comparison
		subprocess.call([vstest_opts.editor, folder + '.scripts/comparison.vpy'], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
