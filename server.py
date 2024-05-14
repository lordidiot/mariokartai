import socket
import argparse
from typing import Optional
from utils import FrameData, frame_to_rgb
from multiprocessing import shared_memory

SHM_NAME_SIZE = 64

def parse_arguments():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', help='Host address')
    parser.add_argument('--port', type=int, default=1234, help='Port number')
    return parser.parse_args()

def create_socket(host: str, port: int):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific address and port
    server_address = (host, port)
    server_socket.bind(server_address)
    return server_socket

def read_ints(client_socket: socket.socket, n: int) -> Optional[list]:
    buf = client_socket.recv(n * 4)
    if not buf:
        return None
    return [int.from_bytes(buf[i:i+4], byteorder='little') for i in range(0, len(buf), 4)]

def read_frame_data(client_socket: socket.socket) -> Optional[tuple[FrameData, bytes]]:
    vals = read_ints(client_socket, 6)
    if not vals:
        return None
    frame_data = FrameData(*vals)
    return frame_data

def setup_shm(client_socket: socket.socket) -> shared_memory.SharedMemory:
    name = client_socket.recv(SHM_NAME_SIZE).rstrip(b'\0').decode()
    name = name[1:] if name.startswith('/') else name
    return shared_memory.SharedMemory(name)

def start_server(server_socket: socket.socket, host, port):
    # Listen for incoming connections
    server_socket.listen(1)
    print(f'Server is listening on {host}:{port}...')

    while True:
        print('Waiting for a connection...')
        client_socket, client_address = server_socket.accept()
        print('Connected to:', client_address)
        try:
            shm = setup_shm(client_socket)
            while True:
                frame_data = read_frame_data(client_socket)
                if not frame_data:
                    break
                frame_rgb = frame_to_rgb(frame_data, shm.buf)
        finally:
            shm.close()
            client_socket.close()

def main():
    args = parse_arguments()
    server_socket = create_socket(args.host, args.port)
    start_server(server_socket, args.host, args.port)

if __name__ == "__main__":
    main()
