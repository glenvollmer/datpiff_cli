import json
import os
import re
import sys

from urllib import request
from bs4 import BeautifulSoup


def get_mixtape_data(url):

	mixtape_data = {}
	base_url = 'http://www.datpiff.com'

	mixtap_page_data = request.urlopen(url)
	mixtape_page = BeautifulSoup(mixtap_page_data, 'html.parser')
	
	html_token_div = mixtape_page.find('div', 
		attrs = {
			'onclick': re.compile('openMixtape')
		})
	
	html_token_div_str = str(html_token_div)
	
	token = re.search(
		r'\((.*?)\)', 
		html_token_div_str
	).group(1).split('\'')[1]

	player_data = request.urlopen(base_url + '/player/' + token)
	player_page = BeautifulSoup(player_data, 'html.parser')

	iframe_src = player_page.find('iframe',
		attrs = {
			'src': True
		})['src']

	iframe_data = request.urlopen(iframe_src)
	iframe_page = BeautifulSoup(iframe_data, 'html.parser')
	
	script = iframe_page.select(
		'script[src="/js/player.js"]:first-of-type + script'
		)[0].getText()
	
	mixtape_data['url_track_prefix'] = re.findall(
		r'\s*var trackPrefix = \'(.*?)\';', 
		script)

	mixtape_data['track_data']= re.findall(
		r'\s*playerData\.tracks\.push\((.*?)\);', 
		script)

	mixtape_data['mixtape_title'] = re.findall(
		r'\s*\"title\":\"(.*?)\"', 
		script)[0].replace('\'', '')

	mixtape_data['artist_name'] = re.findall(
		r'\s*\"artist\":\"(.*?)\"', 
		script)[0].replace('\'', '')

	return mixtape_data


def download_mixtape(save_dir, mixtape_data):
	
	save_directory = save_dir
	track_data = mixtape_data['track_data']
	url_track_prefix = mixtape_data['url_track_prefix']
	artist_name = mixtape_data['artist_name']
	mixtape_title = mixtape_data['mixtape_title']

	for t in track_data:
		url_track = re.findall(
			r'\s*concat\((.*?)\),', 
			t)[0].strip().replace('\'', '')
		
		audio_data = request.urlopen(
			(url_track_prefix[0] + url_track).replace(' ', '%20'))

		print('DOWNLOADING: ', url_track)
		mixtape_dir = save_directory + '/' + artist_name + ' - ' + str(mixtape_title.replace(' ', '_'))
		file_path = mixtape_dir + '/' + url_track

		if not os.path.isdir(mixtape_dir):
			os.mkdir(mixtape_dir)

		with open(file_path, 'wb') as f:
			f.write(audio_data.read())
			f.flush()
			os.fsync(f.fileno())
			f.close()
	return


def get_cli_input():
	cli_input_data = {}
	
	cli_input_data['url'] = str(sys.argv[1])
	cli_input_data['save_dir'] = str(sys.argv[2])

	return cli_input_data


if __name__ == '__main__':
	cli_input = get_cli_input()

	mixtape_data = get_mixtape_data(cli_input['url'])
	download_mixtape(cli_input['save_dir'], mixtape_data)