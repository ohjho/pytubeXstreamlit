import streamlit as st

import os, sys, json, warnings, base64, pickle
from pytube import YouTube, extract
import pandas as pd

from toolbox.st_utils import show_miro_logo, get_binary_file_downloader_html, get_fileio_download_link

def get_yt_obj(url):
	try:
		obj = YouTube(url)
		return obj
	except:
		return False

@st.cache
def get_dl_link(v_stream, dl_dir = 'output/', filename_prefix = None,
	bOverwrite = False, use_file_io = True, run_locally = False):
	fp = os.path.join(dl_dir, filename_prefix + v_stream.default_filename)
	if not os.path.isfile(fp) or bOverwrite:
		print(f'Downloading {v_stream.default_filename}')
		fp = v_stream.download(output_path = dl_dir, skip_existing = True, filename_prefix = filename_prefix)
	else:
		print(f'video already exists: {fp}')
	file_type = 'Audio' if v_stream.includes_audio_track and not v_stream.includes_audio_track else 'Video'

	if use_file_io:
		return get_fileio_download_link(fp, bVerbose = True)
	elif run_locally:
		return fp
	# else:
	# 	return get_binary_file_downloader_html(fp, file_type, bPickle = True)

def byte_size_convert(int_bytes, str_unit = 'b'):
	l_units = ['b', 'kb', 'mb', 'gb']
	str_unit = str_unit.lower()
	if str_unit not in l_units:
		raise ValueError(f'arg str_unit must be one of {l_units}')
	return int_bytes / (1024 ** l_units.index(str_unit))

def parse_yt_streams(yt_streams):
	'''
	ref: https://python-pytube.readthedocs.io/en/latest/_modules/pytube/streams.html
	'''
	return [
		{'itag': i.itag,
		'res': i.resolution,
		"fps": i.fps if hasattr(i, 'fps') else None,
		"bitrate": i.bitrate,
		"type": i.type,
		"has_audio": i.includes_audio_track,
		"codecs": i.parse_codecs(),
		"size (mb)": round(byte_size_convert(i.filesize, 'mb'),2)
		} for i in yt_streams]

def Main(run_locally = False):
	# setttings for get_dl_link
	mb_limit = 1000 if run_locally else 100
	use_file_io = False if run_locally else True
	output_dir = 'output/' if run_locally else '/tmp/'

	st.set_page_config(layout = 'centered')
	show_miro_logo(width = 200, st_asset = st)
	st.header('pytube X streamlit')
	default_url = '' #'https://youtube.com/watch?v=2lAe1cqCOXo'
	vid_url = st.text_input('Enter Youtube Video URL',
				value = default_url)
	bProgressive = st.checkbox('progressive streams', value = False,
					help = f'[what streams ?](https://pytube.io/en/latest/user/streams.html#dash-vs-progressive-streams)'
					)
	audio_only = st.checkbox('audio only', value = False)

	yt = get_yt_obj(vid_url)
	if yt:
		st.subheader(f'{yt.title}\nlength: `{yt.length}` seconds')
		with st.expander('video thumbnail image'):
			st.image(yt.thumbnail_url, use_column_width = True)

		user_input_container = st.empty()

		v_streams = yt.streams.filter(only_audio = True).all() if audio_only else \
					yt.streams.filter(progressive = bProgressive).order_by("resolution")[::-1]
		v_streams_json = parse_yt_streams(v_streams)

		with st.expander(f'Show Available Streams ({len(v_streams)})'):
			df = pd.DataFrame(v_streams_json)
			st.dataframe(df)

		with user_input_container.container():
			itag = st.selectbox('Select itag to Download', options = [s['itag'] for s in v_streams_json])
			isize = df.set_index('itag').at[itag, 'size (mb)']

			if isize > mb_limit:
				st.warning(f'Selected stream size ({isize} MB) is greater than our {mb_limit}MB limit :(')
				return None

			if st.button(f'Download itag: {itag}'):
				s = yt.streams.get_by_itag(itag)
				file_url = get_dl_link(s, filename_prefix = f'itag{itag}_',
				 			dl_dir = output_dir, use_file_io = use_file_io, run_locally = run_locally)

				if run_locally:
					with open(file_url,'rb') as fh:
						st.download_button(
							label = 'Download Video',
							data = fh,
							file_name = os.path.basename(file_url)
						)
					st.success(f'Downloaded to {file_url}')
				else:
					st.markdown(f'[Download Link]({file_url})')

	else:
		st.warning('please enter a valid YouTube Video URL')

if __name__ == '__main__':
	Main(run_locally = False)
