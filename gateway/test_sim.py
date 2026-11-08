#!/usr/bin/env python3
"""End-to-end check of gateway.sh with fake cars (run as root, from anywhere):

    python3 gateway/test_sim.py [number_of_cars]

Sets up N fake cars that all have the SAME address (172.16.11.1), drives each one
through the gateway with the real termux/fpv_car.py Car class, and checks that
 - every car answers its hello,
 - every car receives only its own drive commands,
 - each car's video arrives at its own address, tagged with the right car.
"""
import json, os, socket, struct, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "termux"))
import fpv_car

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
GW = os.path.join(HERE, "gateway.sh")
out = tempfile.mkdtemp(prefix="fakecars-")
procs, fails = [], []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok: fails.append(what)


try:
    subprocess.run([GW, "down", "all"], check=False)
    subprocess.run([GW, "sim-up", str(N)], check=True)
    for n in range(1, N + 1):
        procs.append(subprocess.Popen(["ip", "netns", "exec", f"cs{n}", sys.executable,
                                       os.path.join(HERE, "fake_car.py"), str(n), out]))
    time.sleep(1.0)

    rx = []                                              # video receivers, one per car, own address each
    for n in range(1, N + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((f"10.77.{n}.1", 1234)); s.settimeout(0.2); rx.append(s)

    cars = [fpv_car.Car(ip=f"10.77.{n}.2") for n in range(1, N + 1)]
    for n, c in enumerate(cars, 1):
        check(c.start(), f"car {n}: hello answered through the gateway")
    for n, c in enumerate(cars, 1):
        c.set(0.2 * n if n <= 4 else 0.1, -0.1 * n if n <= 4 else 0.0)   # a different command per car
    time.sleep(0.6)
    for n in range(1, N + 1):
        with open(os.path.join(out, f"{n}.json")) as f: got = json.load(f)
        want_t = fpv_car.to_byte(0.2 * n if n <= 4 else 0.1, fpv_car.LIMIT)
        want_s = fpv_car.to_byte(-0.1 * n if n <= 4 else 0.0, fpv_car.STEER_LIMIT)
        check((got["throttle"], got["steer"]) == (want_t, want_s) and got["xor_ok"],
              f"car {n}: got its own command (throttle {got['throttle']}, steer {got['steer']}), packet valid")
        check(got["from"] == "172.16.11.2", f"car {n}: sees the gateway as 172.16.11.2")

    for n, s in enumerate(rx, 1):
        ids, src = set(), set()
        t0 = time.time()
        while time.time() - t0 < 1.5:
            try: d, a = s.recvfrom(2048)
            except socket.timeout: continue
            if d[:4] == b"\xc6\x6c\xa5\x5a": ids.add(d[32 + 5]); src.add(a[0])
        check(ids == {n} and src == {f"10.77.{n}.2"}, f"car {n}: video arrives on 10.77.{n}.1:1234 from {sorted(src)}, car id(s) {sorted(ids)}")
    for c in cars: c.close()
finally:
    for p in procs: p.kill()
    subprocess.run([GW, "down", "all"], check=False)
print("\nALL PASSED" if not fails else f"\n{len(fails)} FAILED")
sys.exit(1 if fails else 0)
