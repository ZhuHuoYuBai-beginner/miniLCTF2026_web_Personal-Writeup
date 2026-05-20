import socket
import sys
import time
import random
import string
import zlib

PROTOCOL_VERSION = 340  # Minecraft 1.12.2


def varint(value):
    out = b""
    value &= 0xFFFFFFFF
    while True:
        temp = value & 0x7F
        value >>= 7
        if value:
            temp |= 0x80
        out += bytes([temp])
        if not value:
            break
    return out


def read_varint(sock):
    num_read = 0
    result = 0

    while True:
        data = sock.recv(1)
        if not data:
            raise EOFError("connection closed")

        byte = data[0]
        result |= (byte & 0x7F) << (7 * num_read)
        num_read += 1

        if num_read > 5:
            raise ValueError("varint too big")

        if not (byte & 0x80):
            return result


def read_packet(sock):
    length = read_varint(sock)
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise EOFError("connection closed")
        data += chunk
    return data


def read_varint_from_bytes(data, offset=0):
    num_read = 0
    result = 0

    while True:
        if offset >= len(data):
            raise EOFError("truncated varint")

        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << (7 * num_read)
        num_read += 1

        if num_read > 5:
            raise ValueError("varint too big")

        if not (byte & 0x80):
            return result, offset


def decode_packet(raw, compression_threshold=None):
    if compression_threshold is not None:
        data_length, offset = read_varint_from_bytes(raw)
        body = raw[offset:]

        if data_length != 0:
            body = zlib.decompress(body)
            if len(body) != data_length:
                raise ValueError("bad decompressed packet length")
    else:
        body = raw

    packet_id, offset = read_varint_from_bytes(body)
    return packet_id, body[offset:]


def send_packet(sock, packet_id, payload=b"", compression_threshold=None):
    packet = varint(packet_id) + payload

    if compression_threshold is not None:
        if len(packet) >= compression_threshold:
            packet = varint(len(packet)) + zlib.compress(packet)
        else:
            packet = varint(0) + packet

    sock.sendall(varint(len(packet)) + packet)


def mc_string(text):
    data = text.encode("utf-8")
    return varint(len(data)) + data


def read_mc_string(data, offset=0):
    length, offset = read_varint_from_bytes(data, offset)
    value = data[offset:offset + length].decode("utf-8", errors="replace")
    return value, offset + length


def main():
    if len(sys.argv) != 4:
        print("usage: python mc_send_chat.py <host> <port> <message>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    message = sys.argv[3]

    username = "ctf" + "".join(random.choice(string.ascii_letters) for _ in range(6))

    s = socket.create_connection((host, port), timeout=10)

    # Handshake, next state = login
    handshake = (
        varint(PROTOCOL_VERSION)
        + mc_string(host)
        + port.to_bytes(2, "big")
        + varint(2)
    )
    send_packet(s, 0x00, handshake)

    # Login Start
    send_packet(s, 0x00, mc_string(username))

    compression_threshold = None

    # Login phase
    while True:
        raw = read_packet(s)
        packet_id, body = decode_packet(raw, compression_threshold)

        if packet_id == 0x00:
            reason, _ = read_mc_string(body)
            print(f"server disconnected during login: {reason}")
            return

        if packet_id == 0x01:
            print("server requires encryption/online-mode, this simple script cannot continue")
            return

        if packet_id == 0x03:
            compression_threshold, _ = read_varint_from_bytes(body)
            print(f"[+] compression enabled, threshold = {compression_threshold}")

        if packet_id == 0x02:
            print(f"[+] login success as {username}")
            break

    time.sleep(1)

    # Play state: serverbound Chat Message packet id = 0x02 in Minecraft 1.12.2
    send_packet(s, 0x02, mc_string(message), compression_threshold=compression_threshold)

    print("[+] chat payload sent")
    time.sleep(2)
    s.close()


if __name__ == "__main__":
    main()
