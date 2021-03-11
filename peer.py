import argparse
import socket
import os

class Peer:
    def __init__(self, local_port, file_name, list_addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.local_port = local_port
        self.list_addr = list_addr
        self.dict_chunks = dict()

        with open(file_name, 'r') as f:
            lines = f.readlines()
            for l in lines:
                split = l.split(':')
                self.dict_chunks[int(split[0])] = split[1].strip()

        print(self.dict_chunks)

    def query(self, response, addr, init):
        msg = (2).to_bytes(2, byteorder='big')
        msg += socket.inet_aton(addr[0])
        msg += addr[1].to_bytes(2, byteorder='big')
        ttl = 3 if init else int.from_bytes(response[8:10],  byteorder='big') - 1
        msg += (ttl).to_bytes(2, byteorder='big')
        msg += response[2:]

        if ttl > 0:
            return 

        for addr in list_addr:
            # self.socket.sendto(msg, addr)
            print('query sended to ', addr)

    def chunk_info(self, response, addr):
        num_chunks = int.from_bytes(response[2:4],  byteorder='big')
        list_chunks = [int.from_bytes(response[4+(2*i):6+(2*i)],  byteorder='big') 
                        for i in range(num_chunks)]

        intersect = list(set(list_chunks) & set(self.dict_chunks.keys()))

        if intersect:
            msg = (3).to_bytes(2, byteorder='big')
            msg += (len(intersect)).to_bytes(2, byteorder='big')

            for id_chunk in intersect:
                msg += (int(id_chunk)).to_bytes(2, byteorder='big')

            self.socket.sendto(msg, addr)

    def response(self, response, addr):
        num_chunks = int.from_bytes(response[2:4],  byteorder='big')
        list_chunks = [int.from_bytes(response[4+(2*i):6+(2*i)],  byteorder='big') 
                        for i in range(num_chunks)]
        
        print(num_chunks)
        print(list_chunks)
        for chunk_id in list_chunks:
            msg = (5).to_bytes(2, byteorder='big')
            msg += chunk_id.to_bytes(2, byteorder='big')
            msg += (os.stat('Chunks/BigBuckBunny_5.m4s').st_size).to_bytes(2, byteorder='big')

            with open('Chunks/'+self.dict_chunks[chunk_id], 'rb') as bf:
                msg += bf.read()
            
            self.socket.sendto(msg, addr)
            print('sended to ', addr)

        
    def start(self):
        self.socket.bind(('', self.local_port))

        while True:
            response, addr = self.socket.recvfrom(1024)
            msg_type = int.from_bytes(response[:2],  byteorder='big')
            
            if msg_type == 1: #hello
                print('hello')
                self.query(response, addr, init=True)
                self.chunk_info(response, addr)
            elif msg_type == 2: #query
                print('query')
                self.query(response, addr, init=False)
                self.chunk_info(response, addr)
            elif msg_type == 4: #get
                print('get')
                self.response(response, addr)
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initiate peer')
    parser.add_argument('local_port', help='')
    parser.add_argument('file_name', help='')
    parser.add_argument('list_addr', help='', nargs="+")
    args = parser.parse_args()

    local_port = int(args.local_port)
    file_name = args.file_name 
    list_addr = [(addr.split(':')[0], int(addr.split(':')[1]))for addr in args.list_addr]

    peer = Peer(local_port, file_name, list_addr)
    peer.start()

