#!/usr/bin/env python3
"""Four controller servers at once, each driving its own (fake) car through the gateway.

    python3 gateway/test_serve_sim.py [number_of_cars]      (as root)

Starts `fpv_car.py serve --car N` for every car and checks, over HTTP like a player's phone would:
 - /drive on port 8760+N moves only car N,
 - /video on port 8760+N delivers car N's picture (frames tagged with car N), not another car's.
"""
import json, os, struct, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FPV = os.path.join(HERE, "..", "termux", "fpv_car.py")
GW = os.path.join(HERE, "gateway.sh")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
out = tempfile.mkdtemp(prefix="fakecars-")
procs, fails = [], []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok: fails.append(what)


def get(n, path, timeout=3):
    return urllib.request.urlopen(f"http://127.0.0.1:{8760 + n}{path}", timeout=timeout)


try:
    subprocess.run([GW, "down", "all"], check=False)
    subprocess.run([GW, "sim-up", str(N)], check=True)
    for n in range(1, N + 1):
        procs.append(subprocess.Popen(["ip", "netns", "exec", f"cs{n}", sys.executable,
                                       os.path.join(HERE, "fake_car.py"), str(n), out]))
    time.sleep(1.0)
    for n in range(1, N + 1):
        procs.append(subprocess.Popen([sys.executable, FPV, "serve", "--car", str(n)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    time.sleep(1.5)

    for n in range(1, N + 1):                                    # each player drives their own car
        get(n, f"/drive?t={0.15 * n}&s={-0.2 * n}&ms=5000").read()
    time.sleep(0.6)
    for n in range(1, N + 1):
        with open(os.path.join(out, f"{n}.json")) as f: got = json.load(f)
        import importlib.util
        spec = importlib.util.spec_from_file_location("fpv_car", FPV); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        want = (m.to_byte(0.15 * n, m.LIMIT), m.to_byte(-0.2 * n, m.STEER_LIMIT))
        check((got["throttle"], got["steer"]) == want and got["xor_ok"],
              f"car {n}: /drive on port {8760 + n} reached car {n} only (throttle {got['throttle']}, steer {got['steer']})")

    for n in range(1, N + 1):                                    # each player sees their own car's picture
        seen, t0 = set(), time.time()
        r = get(n, "/video", timeout=8)
        while time.time() - t0 < 8 and not seen:
            head = r.read(5)
            if len(head) < 5: break
            size, flag = struct.unpack(">IB", head)
            frame = r.read(size)
            if len(frame) > 5 and frame[:4] == b"\x00\x00\x00\x01": seen.add(frame[5])
        r.close()
        check(seen == {n}, f"car {n}: /video on port {8760 + n} shows car(s) {sorted(seen)}")
finally:
    for p in procs: p.kill()
    subprocess.run([GW, "down", "all"], check=False)
print("\nALL PASSED" if not fails else f"\n{len(fails)} FAILED")
sys.exit(1 if fails else 0)
