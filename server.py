import socket
import argparse
from typing import Optional
from utils import FrameData, frame_to_rgb, Scancode, TIME_TRIAL_KEYS
from multiprocessing import shared_memory
from policy import State, Action
from policy.random import RandomPolicy

SHM_NAME_SIZE = 64

def parse_arguments():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', help='Host address')
    parser.add_argument('--port', type=int, default=1234, help='Port number')
    return parser.parse_args()

def create_socket(host: str, port: int) -> socket.socket:
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

def send_input(client_socket: socket.socket, keys: set[Scancode]) -> None:
    key_list = [key.value for key in keys]
    buf = len(key_list).to_bytes(4, byteorder='little')
    buf += b''.join(key.to_bytes(4, byteorder='little') for key in key_list)
    buf = buf.ljust((32 + 1) * 4, b'\0')
    client_socket.sendall(buf)

def handle_connection(client_socket: socket.socket) -> None:
    policy = RandomPolicy(5000, TIME_TRIAL_KEYS, 0.1)
    shm = setup_shm(client_socket)
    try:
        while True:
            frame_data = read_frame_data(client_socket)
            if not frame_data:
                break
            frame_rgb = frame_to_rgb(frame_data, shm.buf)
            state = State(screen=frame_rgb)
            action = policy.get_action(state)
            if action is None:
                break
            send_input(client_socket, action.keys)
    finally:
        shm.close()
        client_socket.close()

def start_server(server_socket: socket.socket, host: str, port: int) -> None:
    # Listen for incoming connections
    server_socket.listen(1)
    print(f'Server is listening on {host}:{port}...')

    while True:
        print('Waiting for a connection...')
        client_socket, client_address = server_socket.accept()
        print('Connected to:', client_address)
        handle_connection(client_socket)

def main() -> None:
    args = parse_arguments()
    server_socket = create_socket(args.host, args.port)
    start_server(server_socket, args.host, args.port)

if __name__ == "__main__":
    main()
