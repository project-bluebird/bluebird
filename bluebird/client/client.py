import sys

import msgpack
import zmq

import bluebird as bb
from bluebird.client.timer import Timer
from bluesky.network.client import Client
from bluesky.network.npcodec import decode_ndarray

# TODO Figure out what we need here
ACTNODE_TOPICS = [b'ACDATA', b'ROUTEDATA']


class ApiClient(Client):
    def __init__(self, actnode_topics=b''):
        super(ApiClient, self).__init__(ACTNODE_TOPICS)

        self.timer = Timer(self.receive, 1)
        self.timer.start()
        self.subscribe(b'SIMINFO')

    def close(self):
        # TODO Send quit signal properly
        self.timer.stop()

    def stream(self, name, data, sender_id):
        #bb.LOGGER.info(data)

        # Fill the stream cache with the sim data
        bb.STM_CACHE.fill(data)
        
        self.stream_received.emit(name, data, sender_id)

    def send_stackcmd(self, data=None, target=b'*'):
        self.send_event(b'STACKCMD', data, target)

    def send_event(self, name, data=None, target=None):
        print('ApiClient send_event!', file=sys.stderr)
        super().send_event(name, data, target)

    def event(self, name, data, sender_id):
        # print('ApiClient event!', file=sys.stderr)
        super().event(name, data, sender_id)

    def receive(self, timeout=0):
        try:
            socks = dict(self.poller.poll(timeout))
            if socks.get(self.event_io) == zmq.POLLIN:

                msg = self.event_io.recv_multipart()

                # Remove send-to-all flag if present
                if msg[0] == b'*':
                    msg.pop(0)

                route, eventname, data = msg[:-2], msg[-2], msg[-1]

                self.sender_id = route[0]
                route.reverse()
                pydata = msgpack.unpackb(data, object_hook=decode_ndarray, encoding='utf-8')

                print('Event: ' + str(eventname), file=sys.stderr)

                # Print the data, filtering out unwanted messages
                if isinstance(pydata, dict) and \
                        'text' in pydata and \
                        pydata['text'] != '':
                    print(pydata['text'], file=sys.stderr)

                if eventname == b'NODESCHANGED':
                    self.servers.update(pydata)
                    self.nodes_changed.emit(pydata)

                    # If this is the first known node, select it as active node
                    nodes_myserver = next(iter(pydata.values())).get('nodes')
                    if not self.act and nodes_myserver:
                        self.actnode(nodes_myserver[0])
                elif eventname == b'QUIT':
                    self.signal_quit.emit()
                else:
                    self.event(eventname, pydata, self.sender_id)

            if socks.get(self.stream_in) == zmq.POLLIN:
                msg = self.stream_in.recv_multipart()

                strmname = msg[0][:-5]
                sender_id = msg[0][-5:]
                pydata = msgpack.unpackb(msg[1], object_hook=decode_ndarray, encoding='utf-8')
                self.stream(strmname, pydata, sender_id)

            # If we are in discovery mode, parse this message
            if self.discovery and socks.get(self.discovery.handle.fileno()):
                dmsg = self.discovery.recv_reqreply()
                if dmsg.conn_id != self.client_id and dmsg.is_server:
                    self.server_discovered.emit(dmsg.conn_ip, dmsg.ports)

        except zmq.ZMQError:
            print('!!! zmq.ZMQError', file=sys.stderr)
            return False
