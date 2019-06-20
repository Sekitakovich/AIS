import os
import websocket_server
import logging
from multiprocessing import Process
import setproctitle


class Server(Process):
    """ create websocket server thread """
    """ https://github.com/Pithikos/python-websocket-server """

    def __init__(self, *, name: str ="websocketServer", port: int):

        super().__init__()  # never forget!

        self.daemon = True
        self.name = name

        setproctitle.setproctitle('EE:' + name)

        self.engine = websocket_server.WebsocketServer(port=port, host='0.0.0.0')  # inaddr_any

        self.engine.set_fn_new_client(self.welcome)
        self.engine.set_fn_message_received(self.repeater)
        self.engine.set_fn_client_left(self.goodbye)

        self.logger = logging.getLogger("Log")

    def quit(self):
        self.engine.shutdown()  # どうやらこれで終了できそう

    # def broadcast(self, *, message: str):
    #
    #     if len(self.engine.clients):
    #         try:
    #             self.engine.send_message_to_all(message)
    #         except (ValueError, TimeoutError, ConnectionResetError, OSError) as e:
    #             self.logger.debug(msg=e)
    #
    #     return
    #
    def goodbye(self, client, server):
        pass

    def welcome(self, client, server):
        pass

    # def currentGuests(self) -> int:
    #     return len(self.engine.clients)
    #
    def repeater(self, client, server, message):
        talker = client['id']
        for a in server.clients:
            if a['id'] != talker:
                try:
                    self.engine.send_message(a, message)
                except (TimeoutError, ConnectionResetError, OSError) as e:
                    self.logger.debug(msg=e)
                    pass

    def run(self):

        self.logger.debug(msg='process %d' % os.getpid())
        self.engine.run_forever()  # Notice!

