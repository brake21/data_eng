import os
import sys
import time
import requests
import random
from collections import defaultdict

output_list = []

class WeatherApi():
    def __init__(self):
        """
        Initiates weather Class
        """
        self.weather_api_key = "8416480761a5437cbf1e4e5d69b957df"
        self.weather_base_url =  "https://api.weatherbit.io/v2.0/"

    def make_api_call(self, url, method='get',params=None):
        """
       makes http request to the API mentioned
       :param url: url to make the request
       :type url: str
       :param method: http verb
       :type method: str
       :param params: query parameters
       :type params: dict
       :return: api response
       :type : json
       """
        max_attempts = 1
        attempts = 0
        while attempts < max_attempts:
            if method == 'get':
                response = requests.get(url, params=params)

            else:
                print('Not a get method')
                break
            try:
                response.raise_for_status()
            except Exception as e:
                time.sleep((2 ** attempts) + random.random())
                attempts += 1

                if attempts == max_attempts:
                    raise Exception(f'Error While making api call: {e}')
            else:
                if response.content:
                    return response.json()
                else:
                    break

    def _weather_make_url(self):
        """
        generates url to call the weather api
        :return: url
        :type str
        """
        url = os.path.join ( self.weather_base_url, 'current')
        return url

    def call_api(self, zipcode):
        """
       generates url to call the zip code api
       :param zip code: zip code to get current weather
       :type state: integer
       :return: api response
       :type dict
       """
        params = { 'postal_code': zipcode, "country" : 'US', "key": self.weather_api_key}
        url = self._weather_make_url()
        return self.make_api_call(url, params=params)


class ZipCodeApi(WeatherApi):

    def __init__(self):
        """
        Inherits weather class
        """
        self.zipcode_api_key = "1hJmEzujlOw1a2M5c3kDhqKe0EKCDUUasIpxsBO1bWdlBpRJwZMEOo4Bi2w0e6mP"
        self.zipcode_base_url = "https://www.zipcodeapi.com/rest/"
        super().__init__()


    def _make_url(self, state, format='json'):
        """
        generates url to call the zip code api
        :param state: for now only zipcodes from california state is pulled
        :type state: str
        :param format: default response format is JSON
        :type format: str
        :return: url
        :type str
        """
        response_format = f"state-zips.{format}"
        url = os.path.join(self.zipcode_base_url, self.zipcode_api_key, response_format, state.upper())
        return url

    def get_weather(self):
        """
        Get the weather information for each zip
        :return:
        """
        url = self._make_url('ca')
        response = self.make_api_call(url)
        #picking only few zipcodess
        zipcodes = response["zip_codes"][0:100]
        for each_zip in zipcodes:
            response = self.call_api(each_zip)
            if response:
                output_list.extend(response['data'])

def analyze_data():
    """
    Groups by the weather information by city
    :return: metrics
    """
    metrics = {}
    print(f"len of list {len(output_list)} ")
    for each in output_list:
        if ( each['city_name'] not in metrics ):
            metrics[each['city_name']] = defaultdict(list)
        metrics[each['city_name']]['wind_spd'].append(each['wind_spd'])
        metrics[each['city_name']]['temp'].append(each['temp'])
        metrics[each['city_name']]['uv'].append(each['uv'])
    return metrics

def download_aggregate():
    """
    aggregates the wind speed, temperature, UV index by city
    :return:
    """
    wrapper = ZipCodeApi()
    wrapper.get_weather()
    metrics = analyze_data()
    for key in metrics:
        print(f"City_name: {key}, Max_wind_speed: {max(metrics[key]['wind_spd'])}, "
              f"min_wind_speed: {min(metrics[key]['wind_spd'])}, "
              f"average_wind_speed : {sum(metrics[key]['wind_spd'])/len(metrics[key]['wind_spd'])},"
              f"Max_temperature: {max(metrics[key]['temp'])}, "
              f"min_temperature: {min(metrics[key]['temp'])}, "
              f"average_temperature : {sum(metrics[key]['temp'])/len(metrics[key]['temp'])},"
              f"Max_uv_index: {max(metrics[key]['uv'])}, "
              f"min_uv_index: {min(metrics[key]['uv'])}, "
              f"average_uv_index : {sum(metrics[key]['uv']) / len(metrics[key]['uv'])}"
              )

if __name__ == '__main__':
    try:
        download_aggregate()
    except Exception as e:
        raise Exception(f"Error processing the records :{e}")
    print('Script completed successfully')
    sys.exit(0)

