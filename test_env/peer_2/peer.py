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
        if init:
            print('query')
            msg = (2).to_bytes(2, byteorder='big')
            msg += socket.inet_aton(addr[0])
            print('ip from query')
            print(addr[0])
            print(socket.inet_aton(addr[0]))
            msg += addr[1].to_bytes(2, byteorder='big')
            ttl = 3 
            msg += (ttl).to_bytes(2, byteorder='big')
            msg += response[2:]

            print('ttl=', ttl)
            if ttl < 1:
                return 

            for addr in self.list_addr:
                self.socket.sendto(msg, addr)
                print('query sended to ', addr)
        else:
            print('query')
            msg = response[0:8]
            ttl = int.from_bytes(response[8:10],  byteorder='big') - 1
            msg += (ttl).to_bytes(2, byteorder='big')
            msg += response[10:]

            print('ttl=', ttl)
            if ttl < 1:
                return 

            for addr in self.list_addr:
                self.socket.sendto(msg, addr)
                print('query sended to ', addr)

    def chunk_info(self, response, addr=None):
        if addr:
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
                print('(hello)send chunk info to ', addr)

        else:
            print('chunk info from query')
            addr = (socket.inet_ntoa(response[2:6]), int.from_bytes(response[6:8],  byteorder='big'))
            num_chunks = int.from_bytes(response[10:12],  byteorder='big')
            list_chunks = [int.from_bytes(response[12+(2*i):14+(2*i)],  byteorder='big') 
                            for i in range(num_chunks)]
            print('addr= ', addr)

            intersect = list(set(list_chunks) & set(self.dict_chunks.keys()))

            if intersect:
                msg = (3).to_bytes(2, byteorder='big')
                msg += (len(intersect)).to_bytes(2, byteorder='big')

                for id_chunk in intersect:
                    msg += (int(id_chunk)).to_bytes(2, byteorder='big')

                self.socket.sendto(msg, addr)
                print('(query)send chunk info to ', addr)


    def response(self, response, addr):
        print('reponse')
        num_chunks = int.from_bytes(response[2:4],  byteorder='big')
        list_chunks = [int.from_bytes(response[4+(2*i):6+(2*i)],  byteorder='big') 
                        for i in range(num_chunks)]
        
        print('num_chunks= ', num_chunks)
        print('list_chunks= ', list_chunks)
        for chunk_id in list_chunks:
            print('chunk_id= ', chunk_id)
            msg = (5).to_bytes(2, byteorder='big')
            msg += chunk_id.to_bytes(2, byteorder='big')
            msg += (os.stat(self.dict_chunks[chunk_id]).st_size).to_bytes(2, byteorder='big')

            with open(self.dict_chunks[chunk_id], 'rb') as bf:
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
                print('addr=', addr)
                self.query(response, addr, init=True)
                self.chunk_info(response, addr)
            elif msg_type == 2: #query
                print('query')
                print('ip= ', socket.inet_ntoa(response[2:6]))
                print('porto= ', int.from_bytes(response[6:8],  byteorder='big'))
                print('ttl= ', int.from_bytes(response[8:10],  byteorder='big'))
                print('quantidade de chunks= ', int.from_bytes(response[10:12],  byteorder='big'))
                print('addr=', addr)
                self.query(response, addr, init=False)
                self.chunk_info(response)
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
    print('list_addr=', list_addr)

    peer = Peer(local_port, file_name, list_addr)
    peer.start()

