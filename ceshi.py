import socket
import threading
import time


def testconn(host, port):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect((host, port))
        return host + " Server is " + str(port) + " connect"
    except Exception:
        return host + " Server is " + str(port) + " not connect!"
    finally:
        sk.close()


class Test(threading.Thread):
    def __init__(self):
        pass

    def test(self):
        print(testconn('172.31.32.3', 22))

    def run(self):
        while True:
            # print time.strftime('%Y-%m-%d %H:%M:%S')
            self.test()
            time.sleep(1)


a = Test()
a.run()