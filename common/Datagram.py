class Datagram:
    status_key: str = 's',
    mode_key: str = 'm',
    operation_key: str = 'o',
    id_key: str = 'i',
    session_key: str = 'e',
    a_key: str = 'a',
    b_key: str = 'b',
    result_key: str = 'r',
    last_key: str = 'l'

    def __init__(
            self,
            status: str, mode: str, session_id: int=0,
            operation: str='o', a: int=0, b: int=0,
            result: int=0, result_id: int=0, last: bool=1

    ) -> None:
        super().__init__()
        self.status = status
        self.mode = mode
        self.session_id = session_id
        self.operation = operation
        self.a = a
        self.b = b
        self.result = result
        self.result_id = result_id
        self.last = last

    @classmethod
    def from_str(cls):

        operation = datagram.read('uint:2')
        a = datagram.read('float:64')
        b = datagram.read('float:64')
        status = datagram.read('uint:2')
        session_id = datagram.read('uint:16')
        mode = datagram.read('uint:3')
        result = datagram.read('float:64')
        result_id = datagram.read('uint:32')
        last = datagram.read("bool")

        return cls(status, mode, session_id, operation, a, b, result, result_id, last)

    def __str__(self) -> str:
        return self.status_key + "->" + str(self.status) + " " + \
            self.mode_key + "->" + str(self.mode) + " " + \
            self.session_key + "->" + str(self.session_id) + " " + \
            self.operation_key + "->" + str(self.operation) + " " + \
            self.a_key + "->" + str(self.a) + " " + \
            self.b_key + "->" + str(self.b) + " " + \
            self.operation_key + "->" + str(self.result) + " " + \
            self.result_key + "->" + str(self.result_id)
