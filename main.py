import streamlit as st

import os, sys, json, warnings, base64, pickle, requests
from pytube import YouTube, extract
import pandas as pd
from mega import Mega
mega = Mega()

from toolbox.st_utils import show_miro_logo

def is_valid_yt_vid_url(url):
	try:
		vid_id = extract.video_id(url)
		print(vid_id)
		return True
	except: # RegexMatchError:
		return False

def get_binary_file_downloader_html(bin_file, file_label='File', bPickle = False):
	'''
	ref: https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806/27
	'''
	with open(bin_file, 'rb') as f:
		data = f.read()
	data = pickle.dumps(data) if bPickle else data
	bin_str = base64.b64encode(data).decode()
	href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
	return href

@st.cache
def get_dl_link(v_stream, dl_dir = 'output/', filename_prefix = None, bOverwrite = False, m_obj = None):
	fp = os.path.join(dl_dir, filename_prefix + v_stream.default_filename)
	if not os.path.isfile(fp) or bOverwrite:
		print(f'Downloading {v_stream.default_filename}')
		fp = v_stream.download(output_path = dl_dir, skip_existing = True, filename_prefix = filename_prefix)
	else:
		print(f'video already exists: {fp}')
	file_type = 'Audio' if v_stream.includes_audio_track and not v_stream.includes_audio_track else 'Video'

	if m_obj:
		# with open(fp, 'rb') as f:
		# 	data = f.read()
		files = {'file': open(fp, 'rb')}
		response = requests.post('https://file.io', files = files)
		print(response.status_code)
		print(response.text)

		# file = m_obj.upload(fp)
		# print(file)
		# print(m_obj.export(fp.split('/')[-1]))
		# #url = m_obj.get_upload_link(file)
		# url = m_obj.get_link(file)
		# st.write(f'Download: {url}')
	else:
		return get_binary_file_downloader_html(fp, file_type, bPickle = True)

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
		"fps": i.fps,
		"bitrate": i.bitrate,
		"type": i.type,
		"codecs": i.parse_codecs(),
		"size (mb)": round(byte_size_convert(i.filesize, 'mb'),2)
		} for i in yt_streams]

def Main():
	st.set_page_config(layout = 'centered')
	show_miro_logo(width = 200, st_asset = st)
	st.header('pytube X streamlit')
	default_url = '' #'https://youtube.com/watch?v=2lAe1cqCOXo'
	vid_url = st.text_input('Enter Youtube Video URL',
				value = default_url)

	# m = mega.login()
	# st.write(m.get_quota())

	if is_valid_yt_vid_url(vid_url):
		yt = YouTube(vid_url)
		st.subheader(f'{yt.title}\nlength: `{yt.length}` seconds')
		st.image(yt.thumbnail_url, use_column_width = True)

		itag = st.empty()
		dl_button = st.empty()
		v_streams = yt.streams.filter(progressive = False).order_by("resolution").all()[::-1]
		v_streams_json = parse_yt_streams(v_streams)

		with st.beta_expander('Show Available Streams'):
			st.markdown('### [Dash](https://python-pytube.readthedocs.io/en/latest/user/quickstart.html#dash-vs-progressive-streams) Streams')
			st.dataframe(pd.DataFrame(v_streams_json))

		itag = itag.selectbox('Select itag to Download', options = [s['itag'] for s in v_streams_json])
		if dl_button.button(f'Download itag: {itag}'):
			s = yt.streams.get_by_itag(itag)
			# with st.spinner('Download in progress...'):
			# 	fp = s.download(skip_existing = True)
			# st.success(f'{s.default_filename} downloaded')
			# st.markdown(
			# 	get_binary_file_downloader_html(fp, 'Video'),
			# 	unsafe_allow_html = True
			# )
			st.markdown(
				get_dl_link(s, filename_prefix = f'itag{itag}_', m_obj = None),
				unsafe_allow_html = True
			)
	else:
		st.warning('please enter a valid YouTube Video URL')

if __name__ == '__main__':
	Main()