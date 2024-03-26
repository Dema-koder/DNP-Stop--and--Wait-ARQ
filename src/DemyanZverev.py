import argparse
import os.path
from socket import socket, AF_INET, SOCK_DGRAM

buffer_size = 20480

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port_number", type=int)
    parser.add_argument("max_clients", type=int)
    args = parser.parse_args()

    port_number = args.port_number
    max_clients = args.max_clients

    connected_clients = []
    chunk_no = 0

    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind(('0.0.0.0', port_number))
        print(f"{'0.0.0.0', port_number}:   Listening...")
        while True:
            try:
                data, addr = s.recvfrom(buffer_size)
                received_ack_type = data[:1].decode()
                received_seqno = int(data[2:3].decode())
                if received_ack_type == 's':
                    print(f"{addr}: {data.decode()}")
                    message = data.decode().split("|")
                    received_file_name = message[2]
                    received_file_size = int(message[3])
                    if len(connected_clients) < max_clients:
                        send_data = f"a|{(received_seqno + 1) % 2}".encode()
                        s.sendto(send_data, addr)
                        if os.path.isfile(received_file_name):
                            print("File already exist")
                        if received_file_name.lower().endswith(".png"):
                            file = open(received_file_name, "wb")
                        else:
                            file = open(received_file_name, "w")
                        connected_clients.append(addr)
                    else:
                        send_data = f"n|{(received_seqno + 1) % 2}".encode()
                        s.sendto(send_data, addr)
                elif received_ack_type == 'd':
                    chunk_no = chunk_no + 1
                    print(f"{addr}: {data[:3].decode()}|chunk{chunk_no}")
                    send_data = f"a|{(received_seqno + 1) % 2}".encode()
                    s.sendto(send_data, addr)
                    if received_file_name.lower().endswith(".png"):
                        received_data = data[4:]
                    else:
                        received_data = data[4:].decode()
                    file.write(received_data)
                    received_file_size -= len(received_data)
                    if received_file_size <= 0:
                        chunk_no = 0
                        print(f"Received {received_file_name}")
                        file.close()
                        for i in range(len(connected_clients)):
                            if connected_clients[i] == addr:
                                connected_clients.pop(i)
                                break
                else:
                    raise "Incorrect Type"
            except KeyboardInterrupt:
                print("Shutting down...")
                exit()