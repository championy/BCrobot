from handle_web import *
from handle_warehouse import *
import threading


def runing_web():
    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    threading.Thread(target=runing_web, name='web_server').start()

    # threading.Thread(target=handle_start_warehouse, name='start_warehouse').start()
