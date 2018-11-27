import sys
import socket
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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.__connect()
        if self.connected:
            self.__menu()

    def __menu(self):
        print('You can now use netsort')
        print(Operation.RAND_CMD + ' a b\t: get random value between a and b')
        print(Operation.MOD_CMD + ' a b\t\t: get the value of a mod b')
        print(Operation.OP_3_CMD + ' a b\t\t: op3')
        print(Operation.OP_4_CMD + ' a b\t\t: op4')
        print(Mode.SORT_ASC + '\t\t: sort number series in ascending order')
        print(Mode.SORT_DESC + ' id\t: sort number series in descending order')
        print('exit\t\t: exit netsort')

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

                if command[0] == Mode.SORT_ASC:
                    self.__sort_asc()
                elif command[0] == Mode.SORT_DESC:
                    self.__sort_desc()
                elif len(command) == 3 and (command[0] == Operation.RAND_CMD or command[0] == Operation.MOD_CMD or
                                            command[0] == Operation.OP_3_CMD or command[0] == Operation.OP_4_CMD):
                    try:
                        a = int(command[1])
                        b = int(command[2])
                    except ValueError:
                        print('invalid arguments')
                    else:
                        operation: str = '0'
                        if command[0] == Operation.RAND_CMD:
                            operation = Operation.RAND
                        elif command[0] == Operation.MOD_CMD:
                            operation = Operation.MOD
                        elif command[0] == Operation.OP_3_CMD:
                            operation = Operation.OP_3
                        elif command[0] == Operation.OP_4_CMD:
                            operation = Operation.OP_4

                        if a == int('inf') or b == int('inf'):
                            print('numbers exceed value limit')
                        if operation == -1:
                            print('invalid command')
                        else:
                            self.__operation(operation, a, b)
                else:
                    print('invalid command')

    def __send_datagram(self, datagram: Datagram) -> List[Datagram]:
        self.socket.sendto(datagram, (self.host, self.port))
        answer = list()
        last = False
        while last is False:
            answer_data = self.socket.recvfrom(DATAGRAM_SIZE)

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
        self.socket.bind((self.host, self.port))
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

    def __operation(self, operation: str, a: int, b: int):
        datagram = Datagram(Status.NEW, Mode.OPERATION, self.session_id, operation, a, b)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            print(str(answer.result) + '\t:' + str(answer.result_id))

    def __sort_asc(self):

    def __sort_desc(self):

def main():
    args = sys.argv
    host = args[1] if len(args) > 1 else LOCAL_HOST
    port = int(args[2]) if len(args) > 2 else PORT
    client = Client(host, port)
    client.start()


if __name__ == '__main__':
    main()
