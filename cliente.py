import argparse
import socket
import select

class Cliente:
    def __init__(self, ip_port, list_chunks):
         self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         self.ip_port = ip_port
         self.list_chunks = list_chunks

    def hello(self):
        msg = (1).to_bytes(2, byteorder='big')
        msg += (len(self.list_chunks)).to_bytes(2, byteorder='big')
        
        for id_chunk in self.list_chunks:
            msg += (int(id_chunk)).to_bytes(2, byteorder='big')

        self.socket.sendto(msg, self.ip_port)
        print('hello sended')

    def get(self, addr_peer, list_chunks_availables):
        msg = (4).to_bytes(2, byteorder='big')
        msg += (len(list_chunks_availables)).to_bytes(2, byteorder='big')
        
        for id_chunk in list_chunks_availables:
            msg += (int(id_chunk)).to_bytes(2, byteorder='big')

        self.socket.sendto(msg, addr_peer)
        print('get sended')
        
    def start(self):
        self.hello()

        self.available_chunks = dict()
        while True:
            ready = select.select([self.socket], [], [], 5)
            if ready[0]:
                response, addr = self.socket.recvfrom(1024)
                msg_type = int.from_bytes(response[:2],  byteorder='big')
                print('receive chunk info from ', addr)
            
                if msg_type == 3:
                    num_chunks = int.from_bytes(response[2:4],  byteorder='big')

                    for i in range(num_chunks):
                        chunk_id = int.from_bytes(response[4+(2*i):6+(2*i)],  byteorder='big')
                        if chunk_id not in list(self.available_chunks.keys()):
                            self.available_chunks[chunk_id] = addr
            
                print('available_chunks= ', self.available_chunks)
                print('available_chunks= ', set(list(self.available_chunks.keys())))

                if set(list(self.available_chunks.keys())) == set(self.list_chunks):
                    break

            else:
                break
        
        for addr_peer in set(self.available_chunks.values()):
            list_chunks_availables = [k for k,v in self.available_chunks.items() if v == addr_peer]
            print('list_chunks_availables= ', list_chunks_availables)
            self.get(addr_peer, list_chunks_availables)

        list_chunks_received = list()
        while True:
            ready = select.select([self.socket], [], [], 5)
            if ready[0]:
                response, addr = self.socket.recvfrom(2048)            
                print('received from ', addr)
                msg_type = int.from_bytes(response[:2],  byteorder='big')
                if msg_type == 5:
                    print('response received')
                    chunk_id = int.from_bytes(response[2:4],  byteorder='big')
                    chunk_size = int.from_bytes(response[4:6],  byteorder='big')
                    payload = response[6:6+chunk_size]

                    print('msg_type=', msg_type)
                    print('chunk_id=', chunk_id )
                    print('chunk_size=', chunk_size)


                    list_chunks_received.append(chunk_id)
                    print(list_chunks_received)


                    with open(f'new_chunk_{chunk_id}', 'wb') as f:
                        f.write(payload)
                    
                    with open(f'output-{socket.gethostbyname(socket.gethostname())}.log', 'a') as log_f:
                        log_f.write(f"{addr[0]}:{addr[1]} - {chunk_id}\n")



                    print(set(self.list_chunks))
                    print(set(list_chunks_received))
                    if set(list_chunks_received) == set(self.list_chunks):
                        print('All done.')
                        break

            else:
                print('timeout')
                print(set(self.list_chunks))
                print(set(list_chunks_received))
                list_chunks_not_availables = set(self.list_chunks) - set(list_chunks_received)

                print('list_chunks_not_availables=', list_chunks_not_availables)
                for chunk_id in list_chunks_not_availables:
                    with open(f'output-{socket.gethostbyname(socket.gethostname())}.log', 'a') as log_f:
                        log_f.write(f"0.0.0.0:0 - {chunk_id}\n")                    

                break






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initiate client')
    parser.add_argument('ip_port', help='')
    parser.add_argument('list_chunks', help='')
    args = parser.parse_args()

    ip_port = (args.ip_port.split(':')[0], int(args.ip_port.split(':')[1]))
    list_chunks = [int(i) for i in args.list_chunks.split(',')]

    cliente = Cliente(ip_port, list_chunks)
    cliente.start()

