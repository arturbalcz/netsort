import sys
import socket
import datetime
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
        print(Operation.PYTH_CMD + ' a b\t: get the value of square root of a squared times b squared')
        print(Operation.MEAN_CMD + ' a b\t: get the value of arithmetic mean of a and b')
        print(Mode.SORT_ASC_CMD + '\t\t: sort number series in ascending order')
        print(Mode.SORT_DESC_CMD + ' \t\t: sort number series in descending order')
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

                if command[0] == Mode.SORT_ASC_CMD:
                    self.__sort(False)
                elif command[0] == Mode.SORT_DESC_CMD:
                    self.__sort(True)
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
        utils.log('sending ack')
        self.socket.sendto(Datagram(self.session_id, Mode.ACK, Status.OK).to_msg(), (self.host, self.port))

    def __send_datagram(self, datagram: Datagram) -> List[Datagram]:
        utils.log('sending data')
        # send data
        self.socket.sendto(datagram.to_msg(), (self.host, self.port))

        utils.log('waiting for ack...')
        # wait for ack
        ack, addr = self.socket.recvfrom(MAX_DATAGRAM_SIZE)
        if Datagram.from_msg(ack).mode == Mode.ACK:
            utils.log('got ack')
        else:
            utils.log('no ack')
            raise Exception('no ack')

        # listen for response
        utils.log('getting response')
        answer = list()
        last = False
        while last is False:
            # get response chunk
            raw_data, address = self.socket.recvfrom(MAX_DATAGRAM_SIZE)
            utils.log('got datagram')
            self.__send_ack()
            data = Datagram.from_msg(raw_data)

            # check is next chunk is comming
            if data.last:
                    last = True

            if data.status == Status.ERROR:
                print(
                    'error on server: ' + Mode.name_from_code(data.mode) + ' - ' + str(data.error)
                )
            elif data.status == Status.REFUSED:
                print(
                    'server refused to ' + Mode.name_from_code(data.mode) +
                    ' reason: ' + str(data.error)
                )
            answer.append(data)

        return answer

    def __connect(self) -> None:
        # send datagram with connection request
        datagram = Datagram(0, Mode.CONNECT, Status.NEW)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            self.session_id = answer.session_id
            print('connected with session id ' + str(self.session_id))
            self.connected = True
        else:
            print('could not connect')
            self.connected = False

    def __disconnect(self) -> None:
        # send datagram with disconnection request
        utils.log('disconnecting from : ' + self.host + ':' + str(self.port))
        datagram = Datagram(self.session_id, Mode.DISCONNECT, Status.NEW)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            utils.log('disconnected from : ' + self.host + ':' + str(self.port))
            self.socket.close()
            self.connected = False
        else:
            utils.log(
                'cannot disconnect from : ' + self.host + ':' + str(self.port) + ' error code: ' + str(answer.error),
                True
            )

    def __operation(self, operation: str, a: int, b: int):
        datagram = Datagram(self.session_id, Mode.OPERATION, Status.NEW, operation, a, b)
        answer = self.__send_datagram(datagram)[0]
        if answer.status == Status.OK:
            print(
                str(answer.result) +
                '\t: ' + datetime.datetime.fromtimestamp(answer.timestamp).strftime('%H:%M:%S')
            )

    def __sort(self, dsc: bool):
        # read numbers
        print('input numbers + #: ')
        numbers = []
        read = ''
        while read != '#':
            read = input()
            if read != '#':
                try:
                    numbers.append(int(read))
                except ValueError:
                            print('invalid number ' + read)

        mode = Mode.SORT_DESC if dsc else Mode.SORT_ASC

        # send all numbers
        for i in range(0, len(numbers) - 1):
            datagram = Datagram(self.session_id, mode, Status.NEW, a=numbers[i], last=False)
            utils.log('sending ' + str(numbers[i]))
            self.socket.sendto(datagram.to_msg(), (self.host, self.port))
            utils.log('waiting for ack...')
            ack, address = self.socket.recvfrom(MAX_DATAGRAM_SIZE)
            if Datagram.from_msg(ack).mode == Mode.ACK:
                utils.log('got ack')
            else:
                utils.log('no ack')
                raise Exception('no ack')

        utils.log('sending last ' + str(numbers[len(numbers) - 1]))
        answer = self.__send_datagram(
            Datagram(self.session_id, mode, Status.NEW, a=numbers[len(numbers) - 1], last=True)
        )

        # wait for answer
        sorted_numbers = []
        for a in answer:
            sorted_numbers.append(a.a)

        print(sorted_numbers)


def main():
    args = sys.argv
    host = args[1] if len(args) > 1 else LOCAL_HOST
    port = int(args[2]) if len(args) > 2 else PORT
    client = Client(host, port)
    client.start()


if __name__ == '__main__':
    main()
