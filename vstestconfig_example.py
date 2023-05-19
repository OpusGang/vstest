# VSTEST CONFIG FILE
####################

# vstest settings

script = '/home/user/encoding/scripts/encodingscript.vpy'
folder = '/home/user/encoding/tests/'

delimiter1 = '['
delimiter2 = ']'
separator = '/'

logs = True
gen_comp_script = True
repeat_src_comp = True

editor = 'vsedit'

# codecs' defaults

x264 = {
    'demux_opt': '--demuxer y4m',
    'file_ext': 'h264',
    'out_opt': '--output',
    'codec_opts_def': '--preset veryslow --profile high --threads auto --level 4.1 --b-adapt 2 --min-keyint 25 --vbv-bufsize 78125 --vbv-maxrate 62500 --rc-lookahead 60 --me umh --direct auto --subme 11 --trellis 2 --no-dct-decimate --no-fast-pskip --deblock -3:-3 --qcomp 0.6 --ipratio 1.30 --pbratio 1.20 --aq-mode 3 --aq-strength 0.8 --merange 32 --no-mbtree --psy-rd 1:0 --bframes 16',
    'multipass_opts': ['--pass 1 --stats x264.stats','--pass 2 --stats x264.stats'],
    'custom_preset': [['BR','--colormatrix bt709 --colorprim bt709 --transfer bt709'],['PAL','--colormatrix bt470bg --colorprim bt470bg --transfer smpte170m'],['NTSC','--colormatrix smpte170m --colorprim smpte170m --transfer smpte170m']],
    'index':'core.ffms2.Source',
    'vbv_opts':'--vbv-bufsize 0 --vbv-maxrate 0',
    'num_frames_opt': '--frames',
}

x265 = {
    'demux_opt': '--y4m',
    'file_ext': 'h265',
    'out_opt': '--output',
    'codec_opts_def': '--preset veryslow --level-idc 5.1 --no-amp --no-rect --no-open-gop --no-cutree --no-sao --rdoq-level 2 --rc-lookahead 60 --ref 6 --bframes 16 --rd 4 --subme 5 --high-tier --range limited --aud --repeat-headers --cbqpoffs -2 --crqpoffs -2 --qcomp 0.6 --aq-mode 3 --aq-strength 1 --deblock -3:-3 --ipratio 1.3 --pbratio 1.2 --psy-rd 1 --psy-rdoq 1 --no-strong-intra-smoothing --output-depth 10 --input-depth 10',
    'multipass_opts': ['--pass 1 --stats x265.stats','--pass 2 --stats x265.stats'],
    'custom_preset': [['HDR420','--colorprim 9 --colormatrix 9 --transfer 16 --hdr10 --hdr10-opt'],['HDR444','--colorprim 9 --colormatrix 9 --transfer 16 --hdr10 --no-hdr10-opt'],['SDR','--colorprim 1 --colormatrix 1 --transfer 1 --no-hdr10-opt']],
    'index':'core.ffms2.Source',
    'vbv_opts':'--vbv-bufsize 0 --vbv-maxrate 0',
    'num_frames_opt': '--frames',
}

SvtAv1EncApp = {
    'demux_opt': '-i stdin',
    'file_ext': 'av1',
    'out_opt': '--output',
    'codec_opts_def': '--preset 8 --rc 0',
    'multipass_opts': ['--output-stat-file svtav1encapp.stats','--input-stat-file svtav1encapp.stats'],
    'custom_preset': [],
    'index':'core.ffms2.Source',
    'vbv_opts':'',
    'num_frames_opt': '-n',
}

rav1e = {
    'demux_opt': '',
    'file_ext': 'ivf',
    'out_opt': '--output',
    'codec_opts_def': '--speed 2',
    'multipass_opts': ['--first-pass rav1e_stats.json','--second-pass rav1e_stats.json'],
    'custom_preset': [],
    'index':'core.ffms2.Source',
    'vbv_opts':'',
    'num_frames_opt': '',
}
