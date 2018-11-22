class Datagram:
    def __init__(
            self,
            status: str, mode: str, session_id: str='0',
            operation: str='o', a: str='0', b: str='0',
            result: str='0', result_id: str='0', last: bool = True
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

    def __str__(self) -> str:
        return \
            "{" + \
            " status=" + self.status + \
            " mode=" + self.mode + \
            " session_id=" + self.session_id + \
            " operation=" + self.operation + \
            " a=" + self.a + \
            " b=" + self.b + \
            " result=" + self.result + \
            " result_id=" + self.result_id + \
            " }"
