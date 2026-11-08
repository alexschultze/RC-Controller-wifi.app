#!/usr/bin/env python3
"""A fake WL Tech FPV car for testing the gateway without hardware.

Run it inside a namespace where it is 172.16.11.1:  python3 fake_car.py <id> <outdir>
It answers the hello, records the latest drive packet to <outdir>/<id>.json, and after
a hello sends a few video pieces (real header layout, the car's id as payload) to the
hello's source address on the port the hello names (1234).
"""
import json, os, socket, struct, sys, threading, time

cid, out = int(sys.argv[1]), sys.argv[2]
os.makedirs(out, exist_ok=True)
MAGIC = b"\xc6\x6c\xa5\x5a"


def video(dst):
    for fno in range(10):
        body = b"\x00\x00\x00\x01\x65" + bytes([cid]) * 200
        hdr = MAGIC + struct.pack("<IIIIHHII", len(body), fno, 0, 0, 1, 0, 0, len(body))
        s.sendto(hdr + body, dst)
        time.sleep(0.02)


def hello_loop():
    h = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    h.bind(("0.0.0.0", 23459))
    while True:
        data, src = h.recvfrom(256)
        h.sendto(data[:4] + bytes.fromhex("02000000 0100".replace(" ", "")), src)
        if len(data) == 16 and data[-2:] == b"\xd2\x04":       # names the video port
            threading.Thread(target=video, args=((src[0], struct.unpack("<H", data[-2:])[0]),), daemon=True).start()


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
threading.Thread(target=hello_loop, daemon=True).start()
c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.bind(("0.0.0.0", 23458))
n = 0
while True:
    d, src = c.recvfrom(64)
    n += 1
    if len(d) == 16 and d[0] == 0xCA and d[15] == 0x99:
        tmp = os.path.join(out, f".{cid}.tmp")
        with open(tmp, "w") as f:
            json.dump({"steer": d[9], "throttle": d[10], "xor_ok": d[14] == d[9] ^ d[10] ^ d[11] ^ d[12] ^ d[13],
                       "n": n, "from": src[0]}, f)
        os.replace(tmp, os.path.join(out, f"{cid}.json"))
