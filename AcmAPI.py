from AcmException import ACMException
import json
import requests


class AcmAPI:
    def __init__(self, channel=None, key=None, t_head=None, case_id=None):
        self.GET_UNREAD_MESSAGES = 'https://api.acm.chat/getMessages'
        self.POST_SEND_MESSAGE = None
        self.__unread_header = None
        self.__post_send = None
        self.__channel = channel
        self.__key = key
        self.__team_header = t_head
        self.__caseID = case_id
        if self.__all_check() is True:
            self.__settings_setup()

    def __get_check(self):
        if self.__channel is not None and self.__key is not None:
            return True
        else:
            return False

    def __post_send_check(self):
        if self.__key is not None and self.__channel is not None and self.__team_header is not None:
            return True
        else:
            return False

    # Just checking all globs, nothing special
    def __all_check(self):
        if self.__key is not None and self.__channel is not None and self.__team_header is not None and self.__caseID is not None:
            return True
        else:
            return False

    def __settings_setup(self):
        if self.__get_check() is True:
            self.__unread_header = {"content-type": "text", "X-ACM-Chanel": self.__channel, "X-ACM-Key": self.__key,
                                    "X-ACM-Transmitter": self.__team_header}
        else:
            raise ACMException(Exception)
        if self.__caseID is not None and self.__post_send_check() is True:
            print(3)
            self.__post_send = {'Content-type': 'application/json', 'X-ACM-Key': self.__key,
                                'X-ACM-Chanel': self.__channel, 'X-ACM-Transmitter': self.__team_header}
            self.POST_SEND_MESSAGE = 'https://api.acm.chat/rest/v2/cases/' + self.__caseID + '/chats/messages'
        else:
            raise ACMException(Exception)

    # If you calling this function, you apply, that everything is fine
    async def setup_environment(self, channel, key, t_head, case_id):
        self.__channel = channel
        self.__key = key
        self.__team_header = t_head
        self.__caseID = case_id
        self.__settings_setup()

    def send_message_to_server(self, message):
        if self.__all_check() is False:
            raise ACMException(Exception)
        if type(message) is str and message is not '':
            try:
                pure_message = json.loads(message)
            except json.JSONDecodeError:
                pure_message = message
            data = {'message': pure_message}
            print('All ready')
            print(self.POST_SEND_MESSAGE)
            print(data)
            print(self.__post_send)
            requests.post(self.POST_SEND_MESSAGE, headers=self.__post_send, data=json.dumps(data))
        else:
            # Incorrect message type
            raise ACMException(Exception)

    # Function will return a json string that will contain all subjects
    def receive_unreaded_json_raw(self):
        receiver = requests.get(self.GET_UNREAD_MESSAGES, headers=self.__unread_header)
        try:
            raw_data = receiver.json()
            return raw_data
        except ValueError:
            return {}

    # Function will return a json string that will contain all subjects
    def recieve_unreaded_message(self):
        receiver = requests.get(self.GET_UNREAD_MESSAGES, headers=self.__unread_header)
        try:
            raw_data = receiver.json()
            message_pool = []
            for every_message in range(0, len(raw_data)):
                message_body = raw_data[every_message]['nextState']
                message_text = message_body['message']
                message_pool.append(message_text)
            return message_pool
        except ValueError:
            return []
