from decouple import config
import requests
import re
from loguru import logger

X_RAPIDAPI_KEY = config('RAPIDAPI_KEY')


class ParsingLocError(Exception):
    pass


class ParsingLocNull(Exception):
    pass


def get_locations_from_api(loc_name):
    url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    querystring = {'query': loc_name,
                   'locale': 'en_US',
                   'currency': 'USD'}
    headers = {
        'x-rapidapi-host': 'hotels4.p.rapidapi.com',
        'x-rapidapi-key': X_RAPIDAPI_KEY
    }
    logger.info(f'Attempt to request locations from API')
    try:
        response = requests.request('GET', url, headers=headers,
                                    params=querystring, timeout=20)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException

        locations: dict = parse_data_to_list(data)
        return locations
    except requests.exceptions.RequestException as e:
        return {'err': f'Server error: {e}'}
    except ParsingLocError:
        return {'err': 'Error of parsing info from Hotels api'}
    except ParsingLocNull:
        return {'null': 'Nothing found for your request'
                       '\nTry to input new name '
                       'or restart for new command'}
    except Exception as e:
        return {'err': f'Error: {e}'}


def parse_data_to_list(data: requests) -> dict:
    try:
        locations = dict()
        if len(data.get('suggestions')[0].get('entities')) > 0:
            for item in data.get('suggestions')[0].get('entities'):
                location_name = re.sub('<([^<>]*)>', '', item['caption'])
                locations[item['destinationId']] = location_name
            return locations
        else:
            raise ParsingLocNull
    except ParsingLocNull:
        raise ParsingLocNull
    except Exception:
        raise ParsingLocError
