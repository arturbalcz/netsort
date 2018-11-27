# utils
LOCAL_HOST = '127.0.0.1'
PORT = 1500

MAX_DATAGRAM_SIZE = 2048


class Status:
    NEW = "0"
    OK = "1"
    REFUSED = "2"
    ERROR = "3"


class Mode:
    CONNECT = "0"
    DISCONNECT = "1"
    OPERATION = "2"
    SORT_ASC = "3"
    SORT_DESC = "4"
    ERROR = "5"
    ACK = "6"

    SORT_ASC_CMD = "asc"
    SORT_DESC_CMD = "dsc"

    @staticmethod
    def name_from_code(code: str) -> str:
        if code == Mode.CONNECT:
            return 'CONNECT'
        elif code == Mode.DISCONNECT:
            return 'DISCONNECT'
        elif code == Mode.OPERATION:
            return 'OPERATION'
        elif code == Mode.SORT_ASC:
            return 'SORT_ASC'
        elif code == Mode.SORT_DESC:
            return 'SORT_DESC'
        elif code == Mode.ERROR:
            return 'ERROR'
        elif code == Mode.ACK:
            return 'ACK'
        else:
            return 'unknown method'


class Operation:
    RAND = "a"
    RAND_CMD = 'rand'

    MOD = 'A'
    MOD_CMD = 'mod'

    PYTH = "b"
    PYTH_CMD = 'pyth'

    MEAN = "B"
    MEAN_CMD = 'mean'

    @staticmethod
    def name_from_code(code: str) -> str:
        if code == Operation.RAND:
            return Operation.RAND_CMD
        elif code == Operation.MOD:
            return Operation.MOD_CMD
        elif code == Operation.PYTH:
            return Operation.PYTH_CMD
        elif code == Operation.MEAN:
            return Operation.MEAN_CMD


class Error:
    SESSION_ID_NOT_FOUND = "0"
    UNAUTHORISED = "1"
    CANNOT_READ_DATAGRAM = "2"
    INTERNAL_SERVER_ERROR = "3"
    NOT_EXISTING_DATA = "4"
    INVALID_ARGUMENT = "5"
    MAX_VALUE_EXCEEDED = "6"
    OPERATION_NOT_RECOGNIZED = "7"

    @staticmethod
    def name_from_code(code: str) -> str:
        if code == Error.SESSION_ID_NOT_FOUND:
            return 'SESSION_ID_NOT_FOUND'
        elif code == Error.UNAUTHORISED:
            return 'UNAUTHORISED'
        elif code == Error.CANNOT_READ_DATAGRAM:
            return 'CANNOT_READ_DATAGRAM'
        elif code == Error.INTERNAL_SERVER_ERROR:
            return 'INTERNAL_SERVER_ERROR'
        elif code == Error.NOT_EXISTING_DATA:
            return 'NOT_EXISTING_DATA'
        elif code == Error.INVALID_ARGUMENT:
            return 'INVALID_ARGUMENT'
        elif code == Error.MAX_VALUE_EXCEEDED:
            return 'MAX_VALUE_EXCEEDED'
        elif code == Error.OPERATION_NOT_RECOGNIZED:
            return 'OPERATION_NOT_RECOGNIZED'
        else:
            return 'unknown error'

