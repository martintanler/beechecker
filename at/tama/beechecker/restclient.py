import requests

from at.tama.beechecker.sensor.hivedata import HiveData

_host = 'https://beechecker.tk/'


class RestClient:

    @staticmethod
    def request_token(mail: str, pwd: str):
        response = requests.post(_host + "service/token", json={"email": mail,
                                                                       "password": pwd}, verify=True)
        #print('response: ', response.content.decode(encoding='UTF-8'))

        return response.content.decode(encoding='UTF-8')

    @staticmethod
    def put_sensor_data(data: HiveData, token: str):
        #print("test " + requests.get(_host + "beechecker/service/sensordata").content.decode(encoding='UTF-8'))
        response = requests.post(_host + "service/sensordata", json=RestClient.to_json(data, token), verify=True)
        #response = requests.post(_host + "beechecker/service/sensordata", json={"userToken": "myToken"})

        #print('response: ', response.status_code)

        return response.content.decode(encoding='UTF-8')

    @staticmethod
    def to_json(data: HiveData, token: str):

        send_data = {
            "userToken": token,
            "time": data.get_stored_at().replace(microsecond=0).replace(tzinfo=None).isoformat()
        }
        RestClient.append_to(send_data, "hiveName", data.get_hive_bezeichnung)
        RestClient.append_to(send_data, "weight", data.get_weight)
        RestClient.append_to(send_data, "tempIn", data.get_temp_in)
        RestClient.append_to(send_data, "tempOut", data.get_temp_out)
        RestClient.append_to(send_data, "humidityIn", data.get_humidity_in)
        RestClient.append_to(send_data, "humidityOut", data.get_humidity_out)
        RestClient.append_to(send_data, "humidityOut", data.get_humidity_out)

        result = send_data
        #print(result)
        return result

    @staticmethod
    def append_to(local_dic: dict, key: str,  getter):
        result = getter()
        if result is not None:
            local_dic[key] = result
