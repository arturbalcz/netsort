import sys
import socket
import bitstring
import time
from threading import Thread, Lock
from common import utils
from common.values import Status, Mode, Operation, LOCAL_HOST, PORT, DATAGRAM_SIZE, Error
from common.Datagram import Datagram
from typing import List


class Client:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.session_id = 0
        self.connected = False
        self.connected_lock = Lock()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_alive_handler = None

    def start(self):
        self.__connect()
        if self.connected:
            self.is_alive_handler = Thread(name='is_alive_handler', target=self.__is_alive)
            self.is_alive_handler.start()
            self.__menu()
            self.is_alive_handler.join()

    def __menu(self):
        print('You can now use netcalc')
        print(Operation.POWER_CMD + ' a b\t: raise a to the power of b')
        print(Operation.LOG_CMD + ' a b\t\t: get the logarithm of b of the base of a')
        print(Operation.GEO_MEAN_CMD + ' a b\t\t: get the geometric mean of a and b')
        print(Operation.BIN_COE_CMD + ' a b\t\t: get the value of binomial coefficient a choose b')
        print(Mode.QUERY_BY_SESSION_ID_CMD + '\t\t: get all calculations')
        print(Mode.QUERY_BY_RESULT_ID_CMD + ' id\t: get calculation by its id')
        print('exit\t\t: exit netcalc')

        while self.connected:
            print('>', end=' ')
            command = input()
            if not self.connected:
                break
            elif command == 'exit':
                self.__disconnect()
                break
            else:
                command = command.split()

                if command[0] == Mode.QUERY_BY_SESSION_ID_CMD and len(command) == 1:
                    self.__query_by_session_id()
                elif command[0] == Mode.QUERY_BY_RESULT_ID_CMD and len(command) == 2:
                    try:
                        result_id = int(command[1])
                    except ValueError:
                        print('invalid argument')
                    else:
                        self.__query_by_result_id(result_id)
                elif len(command) == 3:
                    try:
                        a = float(command[1])
                        b = float(command[2])
                    except ValueError:
                        print('invalid arguments')
                    else:
                        operation: int = -1
                        if command[0] == Operation.POWER_CMD:
                            operation = Operation.POWER
                        elif command[0] == Operation.LOG_CMD:
                            operation = Operation.LOG
                        elif command[0] == Operation.GEO_MEAN_CMD:
                            operation = Operation.GEO_MEAN
                        elif command[0] == Operation.BIN_COE_CMD:
                            operation = Operation.BIN_COE

                        if a == float('inf') or b == float('inf'):
                            print('numbers exceed value limit')
                        if operation == -1:
                            print('invalid command')
                        else:
                            self.__operation(operation, a, b)
                else:
                    print('invalid command')

    def __send_datagram(self, datagram: Datagram) -> List[Datagram]:
        self.socket.sendall(datagram.get_bytes())
        answer = list()
        last = False
        while last is False:
            answer_bin = self.socket.recv(DATAGRAM_SIZE)
            try:
                answer_data = Datagram.from_bytes(answer_bin)
            except (bitstring.ReadError, ValueError, TypeError) as e:
                utils.log('error reading datagram: ' + str(e), True)
                print('error reading datagram')
            else:
                if answer_data.last:
                    last = True

                if answer_data.status == Status.ERROR:
                    print(
                        'error on server: ' + Mode.name_from_code(answer_data.mode) + ' - ' + Error.name_from_code(answer_data.a)
                    )
                elif answer_data.status == Status.REFUSED:
                    print(
                        'server refused to ' + Mode.name_from_code(answer_data.mode) +
                        ' reason: ' + Error.name_from_code(answer_data.a)
                    )
                answer.append(answer_data)

        return answer

    def __connect(self) -> None:
        self.connected_lock.acquire()
        utils.log('connecting to : ' + self.host + ':' + str(self.port))
        self.socket.connect((self.host, self.port))
        datagram = Datagram(Status.NEW, Mode.CONNECT)
        answer = self.__send_datagram(datagram)[0]
        self.session_id = answer.session_id
        if answer.status == Status.OK:
            utils.log('connected to : ' + self.host + ':' + str(self.port))
            self.connected = True
        else:
            utils.log(self.host + ':' + str(self.port) + ' refused to connect')
            self.connected = False
        self.connected_lock.release()

    def __disconnect(self) -> None:
        self.connected_lock.acquire()
        utils.log('disconnecting from : ' + self.host + ':' + str(self.port))
        datagram = Datagram(Status.NEW, Mode.DISCONNECT, self.session_id)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            utils.log('disconnected from : ' + self.host + ':' + str(self.port))
            self.socket.close()
            self.connected = False
        else:
            utils.log(
                'cannot disconnect from : ' + self.host + ':' + str(self.port) + ' error code: ' + str(answer.a),
                True
            )
        self.connected_lock.release()

    def __is_alive(self) -> None:
        while self.connected:
            self.connected_lock.acquire()
            datagram = Datagram(Status.NEW, Mode.IS_ALIVE, self.session_id)
            answer: List[Datagram]

            try:
                answer = self.__send_datagram(datagram)[0]
            except (ConnectionAbortedError, ConnectionResetError):
                utils.log('server went down')
                self.connected = False

            if answer.status != Status.OK:
                utils.log('server rejected session')
                self.connected = False
            if not self.connected:
                print('press ENTER to exit')
            self.connected_lock.release()
            time.sleep(1)

    def __operation(self, operation: int, a: float, b: float):
        datagram = Datagram(Status.NEW, Mode.OPERATION, self.session_id, operation, a, b)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            print(str(answer.result) + '\t:' + str(answer.result_id))

    def __query_by_session_id(self):
        datagram = Datagram(Status.NEW, Mode.QUERY_BY_SESSION_ID, self.session_id)
        answer = self.__send_datagram(datagram)
        if answer[0].status == Status.OK:
            for result in answer:
                print('session_id = ' + str(result.session_id) + "\t" +
                      ' result id = ' + str(result.result_id) + "\t" +
                      ' operation: ' + str(Operation.name_from_code(result.operation)) + "\t" +
                      ' a = ' + str(result.a) + "\t" +
                      ' b = ' + str(result.b) + "\t" +
                      ' result = ' + str(result.result))

    def __query_by_result_id(self, result_id: int):
        datagram = Datagram(Status.NEW, Mode.QUERY_BY_RESULT_ID, self.session_id, result_id=result_id)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            # TODO: [Artur] improve presentation of result
            print('session_id = ' + str(answer.session_id) + "\t" +
                  ' result id = ' + str(answer.result_id) + "\t" +
                  ' operation: ' + str(Operation.name_from_code(answer.operation)) + "\t" +
                  ' a = ' + str(answer.a) + "\t" +
                  ' b = ' + str(answer.b) + "\t" +
                  ' result = ' + str(answer.result))


def main():
    args = sys.argv
    host = args[1] if len(args) > 1 else LOCAL_HOST
    port = int(args[2]) if len(args) > 2 else PORT
    client = Client(host, port)
    client.start()


if __name__ == '__main__':
    main()
