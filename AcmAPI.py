from AcmException import ACMException
import json
import requests
import time


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
            self.__post_send = {'Content-type': 'application/json', 'X-ACM-Key': self.__key,
                                'X-ACM-Chanel': self.__channel, 'X-ACM-Transmitter': self.__team_header}
            self.POST_SEND_MESSAGE = 'https://api.acm.chat/rest/v2/cases/' + self.__caseID + '/chats/messages'
        else:
            raise ACMException(Exception)

    # If you calling this function, you apply, that everything is fine
    def setup_environment(self, channel, key, t_head, case_id):
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
            requests.post(self.POST_SEND_MESSAGE, headers=self.__post_send, data=json.dumps(data))
        else:
            # Incorrect message type
            raise ACMException(Exception)

    """
    Generators work like any other iterable objects. 
    Make sure to Thread every instance of it or use subprocess.
    
    """
    # Function will return a generator with json object that will contain all subjects
    # In case if there are no messages you will receive None (like in redis when you pubsub)
    # Feel free to overwrite delay. Default is 1 sec.
    def receive_unreaded_json_raw(self, delay=1):
        if not isinstance(delay, int):
            delay = 1
        while 1:
            receiver = requests.get(self.GET_UNREAD_MESSAGES, headers=self.__unread_header)
            try:
                raw_data = receiver.json()
                yield raw_data
                time.sleep(delay)
            except ValueError:
                yield None
                time.sleep(delay)

    # Function will return a generator with pure messages
    # In case if there are no messages you will receive None (like in redis when you pubsub)
    # Feel free to overwrite delay. Default is 1 sec.
    def recieve_unreaded_message(self, delay=1):
        if not isinstance(delay, int):
            delay = 1
        while 1:
            receiver = requests.get(self.GET_UNREAD_MESSAGES, headers=self.__unread_header)
            try:
                raw_data = receiver.json()
                message_body = raw_data[0]['nextState']
                message_text = message_body['message']
                yield message_text
                time.sleep(delay)
            except ValueError:
                yield None
                time.sleep(delay)
