import json
import os
import re
import sys

from urllib import request
from bs4 import BeautifulSoup

''' HOW TO USE:$ python3 app.py DATPIFF_URL_GOES_HERE '''

def main(url):
	base_url = 'http://www.datpiff.com'
	save_directory = '../downloads'

	mixtap_page_data = request.urlopen(url)
	mixtape_page = BeautifulSoup(mixtap_page_data, 'html.parser')
	
	html_token_div = mixtape_page.find('div', 
		attrs = {
			'onclick': re.compile('openMixtape')
		})

	token = re.search(
		r'\((.*?)\)', 
		str(html_token_div)
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

	url_track_prefix = re.findall(r'\s*var trackPrefix = \'(.*?)\';', script)
	track_objs = re.findall(r'\s*playerData\.tracks\.push\((.*?)\);', script)
	mixtape_title = re.findall(r'\s*\"title\":\"(.*?)\"', script)[0].replace('\'', '')
	artist_name = re.findall(r'\s*\"artist\":\"(.*?)\"', script)[0].replace('\'', '')

	for t in track_objs:
		url_track = re.findall(r'\s*concat\((.*?)\),', t)[0].strip().replace('\'', '')
		
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

if __name__ == '__main__':
	url = str(sys.argv[1])
	main(url)