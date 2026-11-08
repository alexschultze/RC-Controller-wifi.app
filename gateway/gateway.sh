#!/bin/bash
# Multi-car gateway: one network namespace per car, so every car can keep its
# own Wi-Fi AND the same address (172.16.11.1) without the cars colliding.
#
#   root namespace          namespace gw<N>                     the car
#   10.77.<N>.1  <--veth--> host0 10.77.<N>.2 | car0 172.16.11.2 <--Wi-Fi--> 172.16.11.1
#
# Players talk to car N at 10.77.<N>.2 (same ports as the real car: 23458,
# 23459). Video the car sends back arrives at 10.77.<N>.1:1234 from 10.77.<N>.2.
# Needs root, iproute2 and nftables; Wi-Fi mode also needs iw and wpa_supplicant.
#
#   gateway.sh sim-up N        # N fake cars (veth) - runs anywhere, for testing
#   gateway.sh wifi-up N PHY SSID   # real car N: Wi-Fi adapter PHY (e.g. phy1) joins SSID
#   gateway.sh down N          # remove car N (or "all")
set -euo pipefail

nsname()  { echo "gw$1"; }
check_n() { [[ "$1" =~ ^[1-9][0-9]?$ ]] || { echo "car number must be 1-99" >&2; exit 2; }; }

base_up() {   # $1 = N: namespace, veth to the root namespace, NAT rules
  local n=$1 ns; ns=$(nsname "$n")
  ip netns add "$ns"
  ip link add "cgw$n" type veth peer name host0 netns "$ns"
  ip addr add "10.77.$n.1/30" dev "cgw$n"; ip link set "cgw$n" up
  ip netns exec "$ns" ip addr add "10.77.$n.2/30" dev host0
  ip netns exec "$ns" ip link set lo up
  ip netns exec "$ns" ip link set host0 up
  ip netns exec "$ns" sysctl -qw net.ipv4.ip_forward=1
  ip netns exec "$ns" sysctl -qw net.ipv4.conf.all.rp_filter=0
  ip netns exec "$ns" sysctl -qw net.ipv4.conf.default.rp_filter=0
  # Players -> car: anything arriving from the host side goes to the car, ports unchanged.
  # Car -> players: anything the car starts (its video, sent to our 172.16.11.2:1234)
  # goes to the root-namespace address of this car. Replies to our own packets
  # (hello answers) are handled by connection tracking, not these rules.
  ip netns exec "$ns" nft -f - <<NFT
table ip gw {
  chain pre {
    type nat hook prerouting priority dstnat;
    iifname "host0" dnat to 172.16.11.1
    iifname "car0"  dnat to 10.77.$n.1
  }
  chain post {
    type nat hook postrouting priority srcnat;
    oifname "car0"  masquerade
    oifname "host0" masquerade
  }
}
NFT
}

car_link_up() {   # the namespace's car-side interface is called car0 and has 172.16.11.2/24
  local ns; ns=$(nsname "$1")
  ip netns exec "$ns" ip addr add 172.16.11.2/24 dev car0
  ip netns exec "$ns" ip link set car0 up
}

cmd=${1:-}; shift || true
case "$cmd" in
  sim-up)    # N fake cars: each car lives in namespace cs<n> at 172.16.11.1
    check_n "$1"
    for n in $(seq 1 "$1"); do
      base_up "$n"
      ip netns add "cs$n"
      ip link add car0 netns "$(nsname "$n")" type veth peer name eth0 netns "cs$n"
      ip netns exec "cs$n" ip addr add 172.16.11.1/24 dev eth0
      ip netns exec "cs$n" ip link set lo up
      ip netns exec "cs$n" ip link set eth0 up
      car_link_up "$n"
    done ;;
  wifi-up)   # real car: move a Wi-Fi adapter into the namespace and join the car's open network
    n=$1; phy=$2; ssid=$3; check_n "$n"; ns=$(nsname "$n")
    base_up "$n"
    iw phy "$phy" set netns name "$ns"
    ifc=$(ip netns exec "$ns" iw dev | awk '/Interface/{print $2; exit}')
    [ -n "$ifc" ] || { echo "no interface appeared in $ns for $phy" >&2; exit 1; }
    ip netns exec "$ns" ip link set "$ifc" down
    ip netns exec "$ns" ip link set "$ifc" name car0
    mkdir -p /run/fpvgw
    printf 'ctrl_interface=/run/fpvgw/ctl%s\nnetwork={\n  ssid="%s"\n  key_mgmt=NONE\n}\n' "$n" "$ssid" > "/run/fpvgw/wpa$n.conf"
    ip netns exec "$ns" wpa_supplicant -B -i car0 -c "/run/fpvgw/wpa$n.conf" -P "/run/fpvgw/wpa$n.pid"
    car_link_up "$n" ;;
  down)
    targets=${1:-all}
    if [ "$targets" = all ]; then targets=$(ip netns list | awk '/^(gw|cs)[0-9]+/{print $1}' | sed 's/^[a-z]*//' | sort -un); fi
    for n in $targets; do
      [ -f "/run/fpvgw/wpa$n.pid" ] && kill "$(cat "/run/fpvgw/wpa$n.pid")" 2>/dev/null || true
      ip link del "cgw$n" 2>/dev/null || true
      ip netns del "$(nsname "$n")" 2>/dev/null || true
      ip netns del "cs$n" 2>/dev/null || true
    done ;;
  *) sed -n '2,15p' "$0"; exit 2 ;;
esac
