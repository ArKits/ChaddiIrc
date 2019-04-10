import _thread
import time
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config

class InputChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        #print(f'event type: {event.event_type}  path : {event.src_path}')
        if event.src_path == "./input/input.txt":
            
            with open("./input/input.txt") as f:
                data = f.readlines()
            lastline = data[-1]
            f.close()

            print("Noticed changed in input.txt: " + lastline)

            bot.send_msg(lastline)

class Bot():
    def __init__(self):
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ircsock.connect((config.server, 6667))

        self.ircsock.send(bytes("USER " + config.bot_nick + " " + config.bot_nick + " " + config.bot_nick + " " + config.bot_nick + "\n", "UTF-8"))
        self.ircsock.send(bytes("NICK " + config.bot_nick + "\n", "UTF-8"))

    def join_chan(self, channel):
        self.ircsock.send(bytes("JOIN " + channel + "\n", "UTF-8"))
        ircmsg = ""
        while ircmsg.find("End of /NAMES list.") == -1:
            ircmsg = self.ircsock.recv(2048).decode("UTF-8")
            ircmsg = ircmsg.strip('\n\r')
            print(ircmsg)

    def send_msg(self, msg, target=config.channel):
        self.ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

    def listen(self):
        while True:
            ircmsg = self.ircsock.recv(2048).decode("UTF-8")
            ircmsg = ircmsg.strip('\n\r')

            if ircmsg.find("PRIVMSG") != -1:
                name = ircmsg.split('!',1)[0][1:]
                message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]

                if len(name) < 17:

                    pretty_message = "[" + name + "] : " + message + "\n"

                    print(pretty_message)

                    f = open("output.txt", "a")
                    f.write(pretty_message)
                    f.close()

                    if message.find("Hi") != -1 or message.find("hi") != -1:
                        self.send_msg("HIIEEE " + name + "!")

                    if name.lower() == config.admin_name.lower() and message.rstrip() == config.exit_code:
                        self.send_msg("BYEEE!")
                        self.ircsock.send(bytes("QUIT \n", "UTF-8"))
                        return


def print_time(threadName, delay):
    while True:
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))


def monitor_changes():
    event_handler = InputChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='./input/', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def make_bot():
    bot.join_chan(config.channel)
    bot.listen()


bot = Bot()

try:
    # _thread.start_new_thread( print_time, ("Thread-1", 2) )
    _thread.start_new_thread( monitor_changes, () )
    _thread.start_new_thread(make_bot, ())
except:
    print("Error: unable to start thread")

while 1:
    pass
