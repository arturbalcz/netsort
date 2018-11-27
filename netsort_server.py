import socket
import sys
from math import factorial, log, sqrt

from threading import Thread, Lock

from common.Datagram import Datagram
from common import utils
from common.values import Status, Mode, Operation, LOCAL_HOST, PORT, Error, DATAGRAM_SIZE
from typing import List


class Server(Thread):

    def __init__(self, host: str, port: int) -> None:
        super().__init__(name='server')
        self.host = host
        self.port = port
        self.on = True

        self.sessions = {}
        self.next_id = 1
        self.next_id_lock = Lock()

        self.next_result_id = 1

    def run(self) -> None:
        self.listen()

    def stop(self) -> None:
        self.on = False
        utils.log('stopping listening...')
        for session in self.sessions:
            self.sessions[session] = False
            session.join()
        utils.log('all sessions closed')

    def menu(self):
        print('You can now use netsort server')
        print('exit\t\t: turn off and exit netsort server')
        while True:
            command = input()
            if command == 'exit':
                self.stop()
                break
            else:
                print('invalid command')

    def listen(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.host, self.port))
        while self.on:
            try:
                data, address = s.recvfrom(DATAGRAM_SIZE)
                utils.log('connected by ' + str(address))
                handler = Handler(
                    name="handler_for_" + str(address),
                    server=self,
                    connection=connection,
                    address=address
                )
                self.sessions[handler] = True
                handler.start()
            except socket.timeout:
                pass

    def handle_incoming_connection(self, connection: socket, address: tuple, handler) -> None:
        session_id = 0
        while self.sessions[handler]:
            try:
                data = connection.recvfrom(DATAGRAM_SIZE)
                answer: Datagram = None
                # noinspection PyBroadException
                try:
                    datagram = data
                    # utils.log('received: ' + str(datagram))
                    answer: bytes
                    if datagram.mode == Mode.CONNECT:
                        answer, session_id = self.__connect(address)
                    elif datagram.session_id == session_id:
                        if datagram.mode == Mode.DISCONNECT:
                            answer = self.__disconnect(datagram.session_id, address)
                            self.sessions[handler] = False
                        elif datagram.mode == Mode.OPERATION:
                            answer = self.__operation(datagram.session_id, datagram.operation, datagram.a, datagram.b)
                        elif datagram.mode == Mode.SORT_ASC:
                            answer = self.__sort_asc(session_id)
                        elif datagram.mode == Mode.SORT_DESC:
                            answer = self.__sort_desc(session_id)
                    else:
                        answer = self.__error(Error.UNAUTHORISED)
                except Exception as e:
                    utils.log("exception: " + str(e), True)
                    answer = self.__error(Error.INTERNAL_SERVER_ERROR, Mode.ERROR, session_id)
                finally:
                    connection.sendto(answer)
            except (ConnectionAbortedError, ConnectionResetError):
                utils.log('breaking listening for session: ' + str(session_id))
                self.sessions[handler] = False

        connection.close()
        utils.log('session closed: ' + str(session_id))

    def __connect(self, address: tuple) -> (bytes, int):
        self.next_id_lock.acquire()
        given_id = self.next_id
        self.next_id += 1
        self.next_id_lock.release()
        answer = Datagram(Status.OK, Mode.CONNECT, given_id)
        utils.log('new session: ' + str(given_id) + ' : ' + str(address[0]))
        return answer, given_id

    @staticmethod
    def __disconnect(session_id: int, address: tuple) -> str:
        answer = Datagram(Status.OK, Mode.DISCONNECT, session_id)
        utils.log('removed session: ' + str(session_id) + ' : ' + str(address))
        return str(answer)

    def __operation(self, session_id: int, operation: str, num_a: int, num_b: int) -> str:
        utils.log('received call for ' + Operation.name_from_code(operation) + ' from session: ' + str(session_id))

        answer = Datagram(Status.OK, Mode.OPERATION, session_id, operation, num_a, num_b)
        answer.result_id = self.next_result_id

        return str(answer)

    def __sort_asc(self, session_id: int):
        return session_id

    def __sort_desc(self, session_id: int):
        return session_id

    @staticmethod
    def __error(code: str, mode: str = Mode.ERROR, session_id: int = 0, operation: str = '0') -> str:
        utils.log(
            Error.name_from_code(code) + ' on session: ' + str(session_id) + ' mode: ' + Mode.name_from_code(mode),
            True
        )
        error = Datagram(Status.ERROR, mode, session_id, operation, a=int(code))
        return str(error)


class Handler(Thread):

    def __init__(self, name: str, server: Server, address: tuple, connection: socket) -> None:
        super().__init__(name=name)
        self.server = server
        self.address = address
        self.connection = connection

    def run(self) -> None:
        self.server.handle_incoming_connection(self.connection, self.address, self)

    def stop(self):
        self.server.sessions[self] = False
        self.connection.close()


def main():
    args = sys.argv
    host = args[1] if len(args) > 1 else LOCAL_HOST
    port = int(args[2]) if len(args) > 2 else PORT
    server = Server(host, port)
    server.start()
    server.menu()
    server.join()


if __name__ == '__main__':
    main()
