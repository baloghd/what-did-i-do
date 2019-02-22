from bs4 import BeautifulSoup
import requests
from typing import List, Dict
import random
import pandas as pd

def fetch_soup(link: str) -> BeautifulSoup:
    desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
    req = requests.get(link, headers = {'User-Agent': random.choice(desktop_agents)})
    soup = BeautifulSoup(req.content, "html5lib")
    return soup

oldal_link = "http://www.police.hu/hu/koral/elfogatoparancs-alapjan-korozott-szemelyek?ent_szemely_elfpar_viselt_nev_teljes=&ent_szemely_elfpar_szuletesi_hely=&ent_szemely_elfpar_kore_jogalap=All&ent_szemely_elfpar_kore_szerv=All&ent_szemely_elfpar_kori_szerv=All&min=&max=&page="

def get_links_from_oldal(oldal_link: str) -> List[str]:
	soup = fetch_soup(oldal_link)
	emberek = soup.find_all("div", {'class': 'overlay'})
	# a kép nélküliek kiválogatása
	emberek = [str(ember) for ember in emberek if "silhouettes" not in str(ember)]
	ember_linkek = [BeautifulSoup(ember, "html5lib").find("a")['href'] for ember in emberek]
	return ember_linkek

def get_ember(ember_link: str) -> pd.DataFrame:
	soup = fetch_soup(ember_linkek[0])

	keplinkek = soup.find_all("img")
	mugshot_link = ""

	for kep in keplinkek:
		if kep.has_attr('src') and 'public_thumbnails' in kep['src']:
			mugshot_link = kep['src']
			break
	
	fields = soup.find_all("div", {"class": ["line", "left", "float-none"]})
	ext_fields = [f.text.strip() for f in fields if ":" in f.text.strip()]
	df = pd.DataFrame([field.split(":") for field in ext_fields])
	df = df.loc[:, :1]

	tr = df.T.copy()
	tr.columns = df[0].values
	adatok = tr.drop(index = 0)

	oszlopok = [
	'Név', 'Nem', 'Születési hely', 'Születési dátum', 'Állampolgárság',
	'Körözést elrendelő szerv', 'Körözési eljárást lefolytató szerv',
	'Körözés jogalapja, bűncselekmény megnevezése, minősítése'
	]

	adatok = adatok[oszlopok]
	return adatok

def get_kep_plusz_jogalap(oldal_link: str) -> Dict[int, List[str]]:
	soup = fetch_soup(oldal_link)
	adatok = [x.find_all('div') for x in soup.find_all("div", {"class": "overlay"})]
	adat_dict = dict()
	for korozes in adatok:
		i = random.randint(0, 1239129385)
		kep_link, jogalap = "", ""
		for item in korozes:
			if item.find('img'):
				kep_link = item.find('img')['src']
			if item.has_attr('class') and item['class'][0] == "jogalap":
				jogalap = item.text.strip()
		adat_dict[i] = [kep_link, jogalap]
	return adat_dict

def oldal_get_loop(tol: int, ig: int) -> Dict[str, List[str]]:
	adat_dict_start = dict()
	for index in range(tol, ig + 1):
		adat_dict_start.update(get_kep_plusz_jogalap(oldal_link + str(index)))
	return adat_dict_start
