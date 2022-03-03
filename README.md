
vstest
======
vstest is a python script made to assist testing of codec's settings through vspipe. It takes the same arguments as the codec used and enables the generation of various encodes from a vapoursynth script, changing the value(s) of given setting(s) defined by a range and a step.

It was coded with modularity in mind, and attempts to enable anyone to test any setting of any codec. **It is however, at this stage, experimental.**

vstest:
- is available in 3 modes:
  1. **testing mode**, when a range and a step are detected, to test the corresponding codec settings
  2. **output mode**, when no codec settings have range and step, to encode a single file
  3. **maintenance mode**, when no codec settings are given, to perform vstest specific actions such as cleaning the test folder
- generates 2 vapoursynth scripts in `.scripts` from the input script:
	- an extraction script to test settings on a limited amount of frames
	- a comparison script to compare the resulting test encodes to the source
- detects if a test is already present and skip the encoding
- manages several passes
- names test encodes `<setting>_<value>.mkv` and place them in subfolders named `<setting>`
- creates a logfile in the testing folder where it appends all encoding logs from the codec.
- enables cleaning of test encodes.

<details><summary>`python vstest.py -h`</summary>
<p>
```sh
usage: vstest.py [-h] [-codec CODEC] [-script SCRIPT] [-folder FOLDER] [-multipass] [-predef PREDEF] [-require REQUIRE] [-verbose] [-sim] [-owrite] [-remove] [-clean] [-gencomp]
                 [-extract EXTRACT] [-editor EDITOR]

optional arguments:
  -h, --help        show this help message and exit
  -codec CODEC      Codec to which settings are passed.
  -script SCRIPT    Path to testing script
  -folder FOLDER    Path to testing folder
  -multipass        Multipass mode. Number of passes defined by config\'s 'multipass_opts'.
  -predef PREDEF    Choose a custom codec preset defined in the config file.
  -require REQUIRE  Force an inequality condition between 2 tested settings. Should be 'set1<set2'
  -verbose          Displays additionnal information.
  -sim              Simulation mode. No encoding/removing is performed. Displays verbose information.
  -owrite           Overwrite existing encodes.
  -remove           Remove all encodes of the current tested setting.
  -clean            Remove all encodes of all tested settings.
  -gencomp          Generate a comparison script from the input encoding script.
  -extract EXTRACT  Choose how to extract frames from clip. Should be <length>:<every>:<offset>
  -editor EDITOR    Choose your prefered vapoursynth editor, named as you would call it from commandline. Default: vsedit
```
</p>
</details>



## Defining vstest default options
Open `vstestconfig.py` and change the default options, especially:

```
script = '/home/user/encoding/scripts/encodingscript.vpy'
folder = '/home/user/encoding/tests/'
logs = True
gen_comp_script = True
repeat_src_comp = True
editor = 'vsedit'
```

- `script` is your encoding script, indexing the source and making all the necessary filtering
- `folder` is the folder in which test encodes will be placed (must be existing)
- `logs = True`  means logging is active
- `gen_comp_script = True` means the comparison script is generated and opened once test encodes are performed.
- `repeat_src_comp = True` means the source frame is repeated between each test encodes frames in the comparison script.
- `editor` is the editor opened to display the comparison script. **Right now only vsedit have been tested.**

Additionally, you may change the codec default options in `'codec_opts_def'` and the custom presets in `'custom_preset'` of the predefined codecs (x264, x265, SvtAv1EncApp and rav1e)



## Testing settings
### Basic command line
`python vstest.py -codec CODEC -extract LENGTH:EVERY:OFFSET [codec settings]`
where `[codec settings]` is a list of settings which can be:
- test-independent: a given value is assigned
- test-dependent: starting and ending values and a step are assigned, delimited and separated by special characters

By default, the delimiters are `[` and `]` and the separator is `/`. You can change these in the config file.
##### Example: Testing x264's crf with values from 16 to 19 by 0.5, with 5 bframes, on an extract made of 25 frames every 3000 frames (cutting the first and last 10000 frames)
`python vstest.py -codec x264 -extract 25:3000:10000 --crf [16/19/0.5] --bframes 5`
##### Example: Encoding the whole clip with x264 once the testing is done
`python vstest.py -codec x264 --crf 17.2 --bframes 5 --output output.mkv`
### Testing multiple settings at a time
You can test as many settings you want at a time. For x values of a first setting and y values of a second one, every possible combination is encoded, so it will generate x*y test encodes.
##### Example: Testing x264's aq-mode and aq-strength
`python vstest.py -codec x264 --aq-mode [1/3/1] --aq-strength [0.7/0.9/0.05]`
### Settings with multiple values
When several parameters are assigned to a given setting, they can be tested individually or tested as different settings.
##### Example: Testing x264's psy-rdo only
`python vstest.py -codec x264 --psy-rd [0.8/1.2/0.1]:0`
##### Example: Testing x264's psy-rdo and psy-trellis
`python vstest.py -codec x264 --psy-rd [0.8/1.2/0.1]:[0/0.25/0.05]`

### vstest testing options
#### Managing multipasses
You can encode several passes with `-multipass` 
##### Example: Testing x264's qcomp in two pass mode with a bitrate of 8000kbps
`python vstest.py -codec x264 -multipass --qcomp [0.6/0.8/0.04] --bitrate 8000`
#### Using custom presets
You can use a custom preset of settings defined in the config file with `-predef`. vstest comes with the following predefined sets:
- For x264:
	- `BR`: `--colormatrix bt709 --colorprim bt709 --transfer bt709`
	- `PAL`: `--colormatrix bt470bg --colorprim bt470bg --transfer bt470bg`
	- `NTSC`: `--colormatrix smpte170m --colorprim smpte170m --transfer smpte170m`
- For x265:
	- `HDR420`: `--colorprim 9 --colormatrix 9 --transfer 16 --hdr10 --hdr10-opt`
	- `HDR444`: `--colorprim 9 --colormatrix 9 --transfer 16 --hdr10 --no-hdr10-opt`
	- `SDR`: `--colorprim 1 --colormatrix 1 --transfer 1 --no-hdr10-opt`

##### Example: Encoding with the x264's custom preset 'PAL' to set colormatrix, colorprimaries and transfer to bt470bg
`python vstest.py -codec x264 -predef PAL --output movie.mkv`
#### Overwriting or removing test encodes
vstest will skip the encoding if a test encode already exist. However:
- `-owrite`  will force it to re-encode
- `-remove` will delete all test encodes for the current tested settings prior to encoding

#### Imposing a condition between settings
This is as of now very limited. When testing several settings, you can enforce an inequality between 2 of them with the `-require` option of vstest.
##### Example: Testing x264's ipratio and pbratio only for ipratio>pbratio
`python vstest.py -codec x264 --ipratio [1.2/1.4/0.1] --pbratio [1.1/1.3/0.1] -require 'pbratio<ipratio'`

## Additional vstest options
#### Changing defaults

vstest can change your default vstest settings for the current encoding with the options:
- `-script`  to change the path of the script
- `-folder` to change the path of the testing folder
- `-editor` to change the editor/viewer started once test encodes are done and the comparison script generated
- `-gencomp` to activate the generation of the comparison script if it is disabled in your confif file.

#### Debug options

Mainly for debug purposes:
- `-verbose` will display detailed information
- `-sim` is a simulation mode that print the commands it would have executed and set the verbose mode on

<details><summary>`python vstest.py -codec x264 -multipass --bitrate 8000 --bframes 5 --ipratio '[1.2/1.4/0.1]' --pbratio '[1.1/1.3/0.1]' -require 'pbratio<ipratio' -sim`</summary>
<p>
```sh
+USER ARGUMENTS
 +vstest options:  clean=False, codec='x264', cond='pbratio<ipratio', customset=None, editor='vsedit', folder=None, multipass=True, owrite=False, remove=False, script=None, sim=True, verbose=True
 +codec user args:  ['--bitrate', '8000', '--bframes', '5', '--ipratio', '[1.2/1.4/0.1]', '--pbratio', '[1.1/1.3/0.1]'] 

+CONFIGURATION
 +vapoursynth script:  /home/user/encoding/scripts/tests.vpy
 +testing folder:  /home/user/encoding/tests/
 +delimiters and separator:  [ ] /
 +codec file extension:  mkv
 +codec output option:  --output
 +codec default options:  ['--preset', 'veryslow', '--profile', 'high', '--threads', 'auto', '--level', '4.1', '--b-adapt', '2', '--min-keyint', '25', '--vbv-bufsize', '78125', '--vbv-maxrate', '62500', '--rc-lookahead', '240', '--me', 'umh', '--direct', 'auto', '--subme', '11', '--trellis', '2', '--no-dct-decimate', '--no-fast-pskip', '--deblock', '-3:-3', '--qcomp', '0.6', '--ipratio', '1.30', '--pbratio', '1.20', '--aq-mode', '3', '--aq-strength', '0.8', '--merange', '32', '--no-mbtree', '--psy-rd', '1:0', '--bframes', '16']
 +codec multipass options:  ['--pass 1 --stats x264.stats', '--pass 2 --stats x264.stats'] 

+REQUESTED TESTING
 +settings to test:  ['--ipratio', '--pbratio']
 +values to test per setting:  [['1.2', '1.3', '1.4'], ['1.1', '1.2', '1.3']]
 +codec options:  ['--bitrate', '8000', '--bframes', '5'] 

 +pools of values to test:  [('1.2', '1.1'), ('1.3', '1.1'), ('1.3', '1.2'), ('1.4', '1.1'), ('1.4', '1.2'), ('1.4', '1.3')]
 +options passed to codec:  ['--bitrate', '8000', '--bframes', '5', '--preset', 'veryslow', '--profile', 'high', '--threads', 'auto', '--level', '4.1', '--b-adapt', '2', '--min-keyint', '25', '--vbv-bufsize', '78125', '--vbv-maxrate', '62500', '--rc-lookahead', '240', '--me', 'umh', '--direct', 'auto', '--subme', '11', '--trellis', '2', '--no-dct-decimate', '--no-fast-pskip', '--deblock', '-3:-3', '--qcomp', '0.6', '--aq-mode', '3', '--aq-strength', '0.8', '--merange', '32', '--no-mbtree', '--psy-rd', '1:0'] 

(1/6) Processing encode with --ipratio 1.2 --pbratio 1.1 

> Pass 1
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.2 --pbratio 1.1 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.2_pbratio_1.1.mkv --pass 1 --stats x264.stats 

> Pass 2
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.2 --pbratio 1.1 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.2_pbratio_1.1.mkv --pass 2 --stats x264.stats 

(2/6) Processing encode with --ipratio 1.3 --pbratio 1.1 

> Pass 1
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.3 --pbratio 1.1 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.3_pbratio_1.1.mkv --pass 1 --stats x264.stats 

> Pass 2
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.3 --pbratio 1.1 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.3_pbratio_1.1.mkv --pass 2 --stats x264.stats 

(3/6) Processing encode with --ipratio 1.3 --pbratio 1.2 

> Pass 1
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.3 --pbratio 1.2 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.3_pbratio_1.2.mkv --pass 1 --stats x264.stats 

> Pass 2
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.3 --pbratio 1.2 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.3_pbratio_1.2.mkv --pass 2 --stats x264.stats 

(4/6) Processing encode with --ipratio 1.4 --pbratio 1.1 

> Pass 1
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.4 --pbratio 1.1 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.4_pbratio_1.1.mkv --pass 1 --stats x264.stats 

> Pass 2
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.4 --pbratio 1.1 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.4_pbratio_1.1.mkv --pass 2 --stats x264.stats 

(5/6) Processing encode with --ipratio 1.4 --pbratio 1.2 

> Pass 1
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.4 --pbratio 1.2 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.4_pbratio_1.2.mkv --pass 1 --stats x264.stats 

> Pass 2
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.4 --pbratio 1.2 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.4_pbratio_1.2.mkv --pass 2 --stats x264.stats 

(6/6) Processing encode with --ipratio 1.4 --pbratio 1.3 

> Pass 1
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.4 --pbratio 1.3 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.4_pbratio_1.3.mkv --pass 1 --stats x264.stats 

> Pass 2
$ vspipe --y4m /home/user/encoding/scripts/tests.vpy - | x264 --demuxer y4m - --ipratio 1.4 --pbratio 1.3 --bitrate 8000 --bframes 5 --preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 240 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --output /home/user/encoding/tests/ipratio.pbratio/ipratio_1.4_pbratio_1.3.mkv --pass 2 --stats x264.stats 
```
</p>
</details>

## Adding a new codec

vstest comes with x264, x265, SvtAv1EncApp and rav1e predefined. To use a new codec, you will need to open the config file and append the following code:

```
<codec> = {
	'demux_opt': '<demux command>',
	'file_ext': '<extension>',
	'codec_opts_def': '<codec default options>',
	'out_opt': '<output option>',
	'multipass_opts': ['<codec options for pass 1>','<codec options for pass 2>','...'],
	'custom_preset': [['preset1_name','preset1_opts'],['preset2_name','preset2_opts'],[...]]
	'index':'<vapoursynth function for indexing>',
}
```

where:
- `<codec>` it the name of the codec as you will call it from command line
- `<demux command>` is the codec option used to input the vapoursynth pipe
- `<extension>` is the file extension of the encodes
- `<output option>` is the codec option to define the output path
- `<codec default options>` are the default options of the codec. Those are overwritten by codec options given in vstest arguments
- `['<codec options for pass 1>','<codec options for pass 2>','...']` is a list of options which are respectively fed to the codec for the consecutive passes in `-multipass` mode. The number of elements in this list defines the number of passes.
- `[['preset1_name','preset1_opts'],['preset2_name','preset2_opts'],[...]]` is a list of cutom presets. Each of them is a list which first item is the preset's name and second item is its settings
- `<vapoursynth function for indexing>` is the function used to index the test encodes in the comparison script

