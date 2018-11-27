import time


class Datagram:

    operation_key: str = 'o'
    status_key: str = 's'
    id_key: str = 'i'
    mode_key: str = 'm'
    a_key: str = 'Na'
    b_key: str = 'Nb'
    result_key: str = 'r'
    timestamp_key: str = 't'
    last_key: str = 'l'

    STOP = '#'
    ARROW = '->'

    def __init__(
            self,
            status: str, session_id: int, mode: str, operation: str = "0",
            a: int=0, b: int=0, result: int=0, last: bool=1
    ) -> None:
        super().__init__()
        self.operation = operation
        self.status = status
        self.session_id = session_id
        self.mode = mode
        self.a = a
        self.b = b
        self.result = result
        self.timestamp = int(time.time())
        self.last = last

    @classmethod
    def __get_param(cls, msg: str, key) -> str:
        begin = msg.find(key) + len(key)
        operation = msg[begin + len(cls.ARROW):msg.find(cls.STOP, begin)]
        return operation

    @classmethod
    def from_msg(cls, msg: bytes):
        msg_str = msg.decode('ascii')
        print('from: ' + msg_str)
        operation = cls.__get_param(msg_str, cls.operation_key)
        status = cls.__get_param(msg_str, cls.status_key)
        session_id = int(cls.__get_param(msg_str, cls.id_key))
        mode = cls.__get_param(msg_str, cls.mode_key)
        a = int(cls.__get_param(msg_str, cls.a_key))
        b = int(cls.__get_param(msg_str, cls.b_key))
        result = int(cls.__get_param(msg_str, cls.result_key))
        timestamp = int(cls.__get_param(msg_str, cls.timestamp_key))
        last = bool(cls.__get_param(msg_str, cls.last_key))

        datagram = cls(status, session_id, mode, operation, a, b, result, last)
        datagram.timestamp = timestamp
        return datagram

    def to_msg(self) -> bytes:
        msg = ''
        msg += Datagram.operation_key + Datagram.ARROW + self.operation + self.STOP
        msg += Datagram.status_key + Datagram.ARROW + self.status + self.STOP
        msg += Datagram.id_key + Datagram.ARROW + str(self.session_id) + self.STOP
        msg += Datagram.mode_key + Datagram.ARROW + self.mode + self.STOP
        msg += Datagram.a_key + Datagram.ARROW + str(self.a) + self.STOP
        msg += Datagram.b_key + Datagram.ARROW + str(self.b) + self.STOP
        msg += Datagram.result_key + Datagram.ARROW + str(self.result) + self.STOP
        msg += Datagram.timestamp_key + Datagram.ARROW + str(self.timestamp) + self.STOP
        msg += Datagram.last_key + Datagram.ARROW + str(self.last) + self.STOP

        print('parsed: ' + msg)
        return bytes(msg, 'ascii')

    def __str__(self) -> str:
        return self.status_key + Datagram.ARROW + str(self.status) + "\n" + \
            self.mode_key + Datagram.ARROW + str(self.mode) + "\n" + \
            self.id_key + Datagram.ARROW + str(self.session_id) + "\n" + \
            self.operation_key + Datagram.ARROW + str(self.operation) + "\n" + \
            self.a_key + Datagram.ARROW + str(self.a) + "\n" + \
            self.b_key + Datagram.ARROW + str(self.b) + "\n" + \
            self.result_key + Datagram.ARROW + str(self.result) + "\n" + \
            self.last_key + self.ARROW + str(self.last) + "\n"
