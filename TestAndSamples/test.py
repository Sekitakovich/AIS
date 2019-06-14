from typing import Dict


class Tako(object):

    def __init__(self, *, value: int):

        self.value = value


class Main(object):

    def __init__(self, *, body: Dict[int, Tako]):

        self.body = body


body = {}  # type: Dict[int, Tako]

body[1] = Tako(value=100)
body[2] = Tako(value=200)
body[3] = Tako(value=300)


main = Main(body=body)

print(main)

