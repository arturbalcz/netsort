# utils
LOCAL_HOST = '127.0.0.1'
PORT = 1500

DATAGRAM_SIZE = 248


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
    SORT_DESC = "3"
    ERROR = "5"

    QUERY_BY_SESSION_ID_CMD = ''
    QUERY_BY_RESULT_ID_CMD = 'result'

    @staticmethod
    def name_from_code(code: str) -> str:
        if code == Mode.CONNECT:
            return 'CONNECT'
        elif code == Mode.DISCONNECT:
            return 'DISCONNECT'
        elif code == Mode.OPERATION:
            return 'OPERATION'
        elif code == Mode.SORT_ASC:
            return ''
        elif code == Mode.SORT_DESC:
            return 'QUERY_BY_RESULT_ID'
        elif code == Mode.ERROR:
            return 'ERROR'
        else:
            return 'unknown method'


class Operation:
    RAND = "a"
    RAND_CMD = 'draw'

    MOD = 'A'
    MOD_CMD = 'mod'

    OP_3 = "b"
    OP_3_CMD = 'op3'

    OP_4 = "B"
    OP_4_CMD = 'op4'

    @staticmethod
    def name_from_code(code: str) -> str:
        if code == Operation.RAND:
            return Operation.RAND_CMD
        elif code == Operation.MOD:
            return Operation.MOD_CMD
        elif code == Operation.OP_3:
            return Operation.OP_3_CMD
        elif code == Operation.OP_4:
            return Operation.OP_4_CMD


class Error:
    SESSION_ID_NOT_FOUND = "0"
    UNAUTHORISED = "1"
    CANNOT_READ_DATAGRAM = "2"
    INTERNAL_SERVER_ERROR = "3"
    NOT_EXISTING_DATA = "4"
    INVALID_ARGUMENT = "5"
    MAX_VALUE_EXCEEDED = "6"

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
        else:
            return 'unknown error'

