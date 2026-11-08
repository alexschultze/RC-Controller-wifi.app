# Multiplayer: several cars at once

Goal: 2-4 WL Tech FPV cars driven at the same time, each by its own player.

## The problem

- Each car opens its **own open Wi-Fi** (`WL_FPV_CAR_xxxxxxxx`, the 8 digits differ per car).
- A phone joins **one** Wi-Fi at a time, so one phone cannot reach four cars. (Some newer Android phones
  allow a second connection; none are known to allow four.)
- Every car is **`172.16.11.1`** and gives its client `172.16.11.2`. Four cars joined at once would
  fight over the same addresses, and the video always comes back to the same port (UDP 1234).

## The solution: a gateway with one Wi-Fi adapter and one network namespace per car

Hardware: a Linux box (Raspberry Pi 4/5 or any PC) and one USB Wi-Fi adapter per car, with a driver that
supports station mode. The box's own Wi-Fi (or Ethernet) is the network the players use.

```
 players' phones ---- gateway's own network ---- root namespace
                                                   10.77.N.1 <--veth--> [ namespace gwN ]
                                                                         10.77.N.2 | car0 172.16.11.2
                                                                                          |  Wi-Fi adapter N
                                                                                     car N, 172.16.11.1
```

- Namespace `gwN` holds Wi-Fi adapter N, so car N's `172.16.11.x` network never meets the others'.
- A few NAT rules in each namespace (see `gateway/gateway.sh`) make car N look like **`10.77.N.2`**:
  packets sent there reach the car (same ports 23458/23459), and the car's video comes back to
  **`10.77.N.1:1234`**, arriving from `10.77.N.2`. The source address tells you which car it is.
- No relay program is needed; this is the kernel's NAT. Existing code only needs the car's address:
  `Car(ip="10.77.2.2")`.

## What is tested, and what is not

`python3 gateway/test_sim.py 4` (as root) builds four **fake** cars that all have `172.16.11.1`, drives each
with the real `termux/fpv_car.py` `Car` class through the gateway, and checks that every car answers the hello,
gets only its own commands, and that its video arrives at its own address. It passes here.

Not tested: real Wi-Fi. `gateway.sh wifi-up N PHY SSID` (moves the adapter into the namespace, joins the open
car network with `wpa_supplicant`, gives it `172.16.11.2`) has not been run on hardware. Things to try first:

1. Does the adapter's driver move into a namespace (`iw phy phyX set netns name gwN`) and join an open network?
2. Four cars at once on 2.4 GHz: do they share a channel, and how many keep a clean 720p picture?

## Running four cars

```
sudo gateway/gateway.sh wifi-up 1 phy1 WL_FPV_CAR_12345678     # once per car: adapter phy, car's Wi-Fi name
sudo gateway/gateway.sh wifi-up 2 phy2 WL_FPV_CAR_23456789     # ... up to 4 (find phyN with `iw dev`)
gateway/start_cars.sh 4                                       # one controller page per car
```

Car N's controller page is then `http://<gateway address>:876N` (8761-8764). `fpv_car.py serve --car N` drives car N at
`10.77.N.2`, takes its video on `10.77.N.1` and serves the page on port 8760+N; add `--listen 0.0.0.0` to open it to
the network (`start_cars.sh` does). There is no password, so use a network you trust.
A page opened over plain `http://` from another machine can't decode H.264 in the browser; it falls back to
MJPEG, which needs `ffmpeg` on the gateway.

Also tested here: `python3 gateway/test_serve_sim.py 4` starts four of these servers against four fake cars and
checks each page's `/drive` and `/video` reach only its own car.

## Choosing the four adapters

Not tested on hardware. Needs: station mode, a driver in the kernel (no out-of-tree driver to build), 2.4 GHz
(the cars are 2.4 GHz only). A web search suggests MT7612U (in the kernel since 4.19) and MT7610U adapters
are well supported on Linux, but I found nothing confirming four of them working together as clients on a Pi.
Buy one first, check `lsusb` for the exact chipset, and test it in the namespace before buying the other three.
Put the adapters on a powered USB hub (four adapters can exceed a Pi's USB power budget).

## Next steps

- Hardware test with one real car and one adapter, then four.
- Player-to-car assignment, a lobby, then game modes (races, tag) on top.
