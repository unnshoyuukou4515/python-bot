import requests
from bs4 import BeautifulSoup
import re


def get_weather_from_location_JP(original_location):
  # get postal code from location info
  location = re.findall('\d{3}-\d{4}', original_location)
  # postal code
  url = "https://weather.yahoo.co.jp/weather/search/?p=" + location[0]
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  content = soup.find(class_="serch-table")
  #inside that page includes url for the weather forcast for that area
  location_url = content.find('a').get('href')
  r = requests.get(location_url)
  soup = BeautifulSoup(r.text, 'html.parser')
  content = soup.find(id='yjw_pinpoint_today').find_all('td')
  info = []

  for each in content[1:]:
    info.append(each.get_text().strip('\n'))

 
  time = info[:8]
 
  weather = info[9:17]
 
  temperature = info[18:26]
 
  weather_info = [(time[i], weather[i], temperature[i]) for i in range(8)]

  result = [('{0[0]}: {0[1]}, {0[2]}°C'.format(weather_info[i])) for i in range(8)]
  result = (format(original_location) + '\n'.join(result) + '\n')

  return result



def get_weather_from_english():
    url = "https://www.yahoo.com/news/weather/tokyo"
    
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    target_elements = soup.find_all( class_= "Py(10px) Px(4px) Fz(0.8125rem)" )

    target_texts = [element.get_text() for element in target_elements]

    return '\n'.join(target_texts)

    