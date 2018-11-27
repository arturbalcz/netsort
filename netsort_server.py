import socket
import sys
import random
import math
from common.Datagram import Datagram
from common import utils
from common.values import Status, Mode, Operation, LOCAL_HOST, PORT, Error, MAX_DATAGRAM_SIZE


class Server:

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.on = True

        self.active_session_id = 0
        self.next_id = 1

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __receive_datagram(self) -> (Datagram, tuple):
        utils.log('receiving data')
        data, address = self.socket.recvfrom(1024)
        utils.log('received data from ' + str(address))
        utils.log('sending ack')
        self.__send_datagram(Datagram(Status.OK, self.active_session_id, Mode.ACK), address)
        return Datagram.from_msg(data), address

    def __send_datagram(self, datagram: Datagram, address: tuple, ack: bool=False) -> bool:
        utils.log('sending data to ' + str(address))
        self.socket.sendto(datagram.to_msg(), address)
        if ack:
            utils.log('waiting for ack')
            raw_ack, address = self.socket.recvfrom(1024)
            datagram = Datagram.from_msg(raw_ack)
            if datagram.mode == Mode.ACK and datagram.status == Status.OK:
                utils.log('got ack')
                return True
            else:
                utils.log('no ack')
                return False

        return True

    def listen(self) -> None:
        self.socket.bind((self.host, self.port))
        self.on = True
        while self.on:
            try:
                utils.log('waiting...')
                datagram, address = self.__receive_datagram()
                answer: Datagram
                try:
                    if datagram.mode == Mode.CONNECT:
                        if self.active_session_id == 0 and datagram.session_id == 0:
                            utils.log('creating new session ' + str(self.next_id) + ' ' + str(address))
                            self.active_session_id = self.next_id
                            self.next_id += 1
                            answer = Datagram(Status.OK, self.active_session_id, Mode.CONNECT)
                        else:
                            utils.log('wrong new session request from ' + str(self.next_id) + ' ' + str(address))
                            answer = Datagram(Status.REFUSED, 0, Mode.CONNECT)

                    elif datagram.session_id == self.active_session_id:
                        if datagram.mode == Mode.DISCONNECT:
                            utils.log('destroying session ' + str(self.next_id) + ' ' + str(address))
                            answer = Datagram(Status.OK, self.active_session_id, Mode.DISCONNECT)
                            self.active_session_id = 0
                            self.on = False
                        elif datagram.mode == Mode.OPERATION:
                            answer = self.__operation(datagram.session_id, datagram.operation, datagram.a, datagram.b)
                        # elif datagram.mode == Mode.SORT_ASC:
                        #     answer = self.__sort_asc(session_id)
                        # elif datagram.mode == Mode.SORT_DESC:
                        #     answer = self.__sort_desc(session_id)
                        else:
                            answer = self.__error(Error.UNAUTHORISED)
                    else:
                        answer = self.__error(Error.UNAUTHORISED)
                except Exception as e:
                    utils.log("exception: " + str(e), True)
                    answer = self.__error(Error.INTERNAL_SERVER_ERROR, Mode.ERROR, self.active_session_id)
                finally:
                    self.__send_datagram(answer, address, True)

            except (ConnectionAbortedError, ConnectionResetError):
                    utils.log('breaking listening for session: ' + str(self.active_session_id))

        utils.log('closing socket')
        self.socket.close()

    def __operation(self, session_id: int, operation: str, num_a: int, num_b: int) -> Datagram:
        utils.log('received call for ' + Operation.name_from_code(operation) + ' from session: ' + str(session_id))
        if operation == Operation.RAND:
            if num_a >= num_b:
                return self.__error(Error.INVALID_ARGUMENT, Mode.OPERATION, self.active_session_id, operation)

            result = random.randint(num_a + 1, num_b)  # randint -> [a, b], now -> (a, b]

        elif operation == Operation.MOD:
            if num_a <= 0 or num_b <= 0:
                return self.__error(Error.INVALID_ARGUMENT, Mode.OPERATION, self.active_session_id, operation)

            result = num_a % num_b

        elif operation == Operation.PYTH:
            if num_a <= 0 or num_b <= 0:
                return self.__error(Error.INVALID_ARGUMENT, Mode.OPERATION, self.active_session_id, operation)

            result = int(math.sqrt(num_a ** 2 + num_b ** 2))

        elif operation == Operation.MEAN:
            result = int((num_a + num_b) / 2)

        else:
            return self.__error(Error.OPERATION_NOT_RECOGNIZED, Mode.OPERATION, self.active_session_id, operation)

        answer = Datagram(Status.OK, session_id, Mode.OPERATION, operation, num_a, num_b, result)
        return answer

    def __sort_asc(self, session_id: int):
        return session_id

    def __sort_desc(self, session_id: int):
        return session_id

    @staticmethod
    def __error(code: str, mode: str = Mode.ERROR, session_id: int = 0, operation: str = '0') -> Datagram:
        utils.log(
            Error.name_from_code(code) + ' on session: ' + str(session_id) + ' mode: ' + Mode.name_from_code(mode),
            True
        )
        error = Datagram(Status.ERROR, session_id, mode, operation, a=int(code))
        return error


def main():
    args = sys.argv
    host = args[1] if len(args) > 1 else LOCAL_HOST
    port = int(args[2]) if len(args) > 2 else PORT
    server = Server(host, port)
    server.listen()


if __name__ == '__main__':
    main()
