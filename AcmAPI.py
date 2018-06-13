import json
import requests
import time


class AcmAPI:

    class ACMExceptionSettingsUndone(Exception):
        pass

    class ACMExceptionZeroValue(Exception):
        pass

    class ACMExceptionTypeError(Exception):
        pass

    __slots__ = ['__unread_header', 'GET_UNREAD_MESSAGES', 'POST_SEND_MESSAGE', '__send_header', '__channel', '__key',
                 '__transmitter', '__caseID']

    def __init__(self, channel=None, key=None, trans=None, case_id=None):
        self.GET_UNREAD_MESSAGES = 'https://api.acm.chat/getMessages'
        self.POST_SEND_MESSAGE = None
        self.__unread_header = None
        self.__send_header = None
        self.__channel = channel
        self.__key = key
        self.__transmitter = trans
        self.__caseID = case_id
        if self.__all_check() is True:
            self.__settings_setup()

    def __get_check(self):
        if self.__channel is not None and self.__key is not None:
            return True
        else:
            return False

    def __post_send_check(self):
        if self.__key is not None and self.__channel is not None and self.__transmitter is not None:
            return True
        else:
            return False

    def __all_check(self):
        if self.__caseID is not None and self.__post_send_check() is True:
            return True
        else:
            return False

    def __settings_setup(self):
        if self.__get_check() is True:
            self.__unread_header = {"content-type": "text", "X-ACM-Chanel": self.__channel, "X-ACM-Key": self.__key,
                                    "X-ACM-Transmitter": self.__transmitter}
        else:
            raise self.ACMExceptionSettingsUndone
        #
        if self.__all_check() is True:
            self.__send_header = {'Content-type': 'application/json', 'X-ACM-Key': self.__key,
                                  'X-ACM-Chanel': self.__channel, 'X-ACM-Transmitter': self.__transmitter}
            self.POST_SEND_MESSAGE = 'https://api.acm.chat/rest/v2/cases/' + self.__caseID + '/chats/messages'
        else:
            raise self.ACMExceptionSettingsUndone

    # If you calling this function, you apply, that everything is fine
    def setup_environment(self, channel, key, trans, case_id):
        self.__channel = channel
        self.__key = key
        self.__transmitter = trans
        self.__caseID = case_id
        self.__settings_setup()

    def send_message_to_server(self, message):
        if self.__all_check() is False:
            raise self.ACMExceptionSettingsUndone
        try:
            str(message)
        except TypeError:
            raise self.ACMExceptionTypeError
        #
        if message is not '':
            try:
                pure_message = json.loads(message)
            except json.JSONDecodeError:
                pure_message = message
            data = {'message': pure_message}
            requests.post(self.POST_SEND_MESSAGE, headers=self.__send_header, data=json.dumps(data))
        else:
            # Null message is restricted
            raise self.ACMExceptionZeroValue

    """
    Generators work like any other iterable objects. 
    Make sure to Thread every instance of it or use subprocess.
    
    """
    # Function will return a generator with json object that will contain all subjects
    # In case if there are no messages you will receive None (like in redis when you pubsub)
    # Feel free to overwrite delay. Default is 1 sec.
    def receive_unread_json_raw(self, delay=1):
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

    # Function will return a generator filled with pure messages
    # In case if there are no messages you will receive None (like in redis when you pubsub)
    # Feel free to overwrite delay. Default is 1 sec.
    def receive_unread_message(self, delay=1):
        if not isinstance(delay, int):
            delay = 1
        print('Delay is - %d' % delay)
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

    # You'll receive a dict with request.header
    @property
    def read_headers(self):
        return self.__unread_header

    # In case of abuse, function is protected
    # USE AT YOUR OWN RISK
    def _add_to_unread_header(self, key, value):
        if self.__unread_header is None:
            raise self.ACMExceptionSettingsUndone
        else:
            self.__unread_header.setdefault(key, value)

    # # You'll receive a string with an API link to send JSON data on ACM servers
    @property
    def send_link(self):
        return ''.join(self.__transmitter)

    # You'll receive a dict with request.header
    @property
    def send_headers(self):
        return self.__send_header

    # In case of abuse, function is protected
    # USE AT YOUR OWN RISK
    def _add_to_send_header(self, key, value):
        if self.__send_header is None:
            raise self.ACMExceptionSettingsUndone
        else:
            self.__send_header.setdefault(key, value)
