import os, sys, io, json, requests, base64, pickle, warnings
import streamlit as st
import numpy as np
from PIL import Image
import urllib.request as urllib

def show_miro_logo(use_column_width = False, width = 100, st_asset= st.sidebar):
	logo_url = 'https://miro.medium.com/max/1400/0*qLL-32srlq6Y_iTm.png'
	st_asset.image(logo_url, use_column_width = use_column_width, channels = 'BGR', output_format = 'PNG', width = width)

def file_selector(folder_path='.', st_asset = st, extension_tuple = None,
	str_msg = "Select a file", get_dir = False):
	'''
	using streamlit selectbox to return a filepath
	'''
	if not folder_path:
		return None
	else:
		if not os.path.isdir(folder_path):
			st_asset.warning(f'`{folder_path}` is not a valid directory path')
			return None

		filenames = os.listdir(folder_path)
		if get_dir:
			filenames = [f for f in filenames if os.path.isdir(os.path.join(folder_path, f))]
		elif extension_tuple:
			filenames = [f for f in filenames if f.endswith(extension_tuple) and os.path.isfile(os.path.join(folder_path, f))]
		selected_filename = st_asset.selectbox(str_msg, sorted(filenames))
		return os.path.join(folder_path, selected_filename)

def get_image(st_asset = st.sidebar, as_np_arr = False, extension_list = ['jpg', 'jpeg', 'png']):
	image_url = st_asset.text_input("Enter Image URL")
	image_fh = st_asset.file_uploader(label = "Update your image", type = extension_list)

	if image_url and image_fh:
		st_asset.warning(f'image url takes precedence over uploaded image file')

	im = None

	if image_url:
		response = urllib.urlopen(image_url)
		im = Image.open(io.BytesIO(bytearray(response.read())))
	elif image_fh:
		im = Image.open(image_fh)

	if im and as_np_arr:
		im = np.array(im)
	return im

def get_ext_host_ip_add():
	ip = requests.get('https://api.ipify.org').text
	return ip

def get_table_download_link(df, st_asset = st):
	"""
	Generates a link allowing the data in a given panda dataframe to be downloaded
	reference https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
	in:  dataframe
	out: href string
	"""
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
	href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
	st_asset.markdown(href, unsafe_allow_html = True)

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

def get_fileio_download_link(fp, bVerbose = False):
	'''
	100mb size limit, upload file to file.io and return download url
	'''
	if bVerbose:
		print(f'uploading {fp} to file.io')
	files = {'file': open(fp, 'rb')}
	response = requests.post('https://file.io', files = files)
	if response.status_code == 200:
		return json.loads(response.text)['link']
	else:
		warnings.warn(f'get_fileio_download_link: file.io upload error status code {response.status_code}')
		return None
