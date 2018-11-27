import sys
import socket
import time
from common import utils
from common.values import Status, Mode, Operation, LOCAL_HOST, PORT, MAX_DATAGRAM_SIZE, Error
from common.Datagram import Datagram
from typing import List


class Client:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.session_id = 0
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.__connect()
        if self.connected:
            self.__menu()

    def __menu(self):
        print('You can now use netsort')
        print(Operation.RAND_CMD + ' a b\t: get random value between a and b')
        print(Operation.MOD_CMD + ' a b\t\t: get the value of a mod b')
        print(Operation.PYTH_CMD + ' a b\t\t: op3')
        print(Operation.MEAN_CMD + ' a b\t\t: op4')
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
                                            command[0] == Operation.PYTH_CMD or command[0] == Operation.MEAN_CMD):
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
                        elif command[0] == Operation.PYTH_CMD:
                            operation = Operation.PYTH
                        elif command[0] == Operation.MEAN_CMD:
                            operation = Operation.MEAN

                        if operation == -1:
                            print('invalid command')
                        else:
                            self.__operation(operation, a, b)
                else:
                    print('invalid command')

    def __send_ack(self):
        print('sending ack')
        self.socket.sendto(Datagram(Status.OK, self.session_id, Mode.ACK).to_msg(), (self.host, self.port))

    def __send_datagram(self, datagram: Datagram) -> List[Datagram]:
        print('sending data')
        self.socket.sendto(datagram.to_msg(), (self.host, self.port))

        print('waiting for ack...')
        ack, addr = self.socket.recvfrom(MAX_DATAGRAM_SIZE)
        if Datagram.from_msg(ack).mode == Mode.ACK:
            print('got ack')
        else:
            print('no ack')
            raise Exception('no ack')

        print('getting response')
        answer = list()
        last = False
        while last is False:
            raw_data, address = self.socket.recvfrom(MAX_DATAGRAM_SIZE)
            print('got datagram')
            self.__send_ack()
            data = Datagram.from_msg(raw_data)

            if data.last:
                    last = True

            if data.status == Status.ERROR:
                print(
                    'error on server: ' + Mode.name_from_code(data.mode) + ' - ' + Error.name_from_code(str(data.a))
                )
            elif data.status == Status.REFUSED:
                print(
                    'server refused to ' + Mode.name_from_code(data.mode) +
                    ' reason: ' + Error.name_from_code(data.a)
                )
            answer.append(data)

        return answer

    def __connect(self) -> None:
        datagram = Datagram(Status.NEW, 0, Mode.CONNECT)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            self.session_id = answer.session_id
            print('connected with session id ' + str(self.session_id))
            self.connected = True
        else:
            print('could not connect')
            self.connected = False

    def __disconnect(self) -> None:
        utils.log('disconnecting from : ' + self.host + ':' + str(self.port))
        datagram = Datagram(Status.NEW, self.session_id, Mode.DISCONNECT)
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

    def __operation(self, operation: str, a: int, b: int):
        datagram = Datagram(Status.NEW, self.session_id, Mode.OPERATION, operation, a, b)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            print(str(answer.result))

    def __sort_asc(self):
        print('n/a')

    def __sort_desc(self):
        print('n/a')


def main():
    args = sys.argv
    host = args[1] if len(args) > 1 else LOCAL_HOST
    port = int(args[2]) if len(args) > 2 else PORT
    client = Client(host, port)
    client.start()


if __name__ == '__main__':
    main()
