# Parked idea: a camera-less RC car with our own radio link (notes for later)

Not started. This is the alternative to the Wi-Fi camera cars of the main multiplayer track
(`docs/MULTIPLAYER.md`): a better-quality car, no built-in camera, driven by a radio we control.

## TOP OPTIONS (chosen by the project owner)

1. **Tamiya** (TT-02 / TT-02B, e.g. the XB ready-to-run versions): about 150 EUR for the complete car (owner's figure;
   US retail for the XB Dual Ridge TT-02B 57876 was about 152 USD). ESC (TEU-105BK / 106BK or sensored TBLE-04S) is
   separate from the TRU-08 receiver, so only the receiver gets replaced. 1:10.
2. **MJX 14210 Hyper Go** (1:14 truggy, "Version 2"): the [China-Gadgets review](https://www.china-gadgets.de/mjx-14210-hyper-go/)
   (dated 22 Aug 2024; price and stock likely stale) lists "ab 125,97 EUR" via Banggood (EU warehouse), 144,96 EUR with
   two batteries. 4WD, 2852 brushless 4400 kV with fan, 45A ESC with heatsink, 2S 7.4 V 3000 mAh included (3S fits),
   55 km/h on 2S, 4-channel 2.4 GHz pistol-grip transmitter (3 AA, not included). The review says the manufacturer puts
   "den separaten 2,4 GHz-Empfaenger" in a sealed box above the drivetrain, and describes the ESC separately; it never
   says outright that ESC and receiver are not a 2-in-1 unit, and it does not mention the antenna. Confirm on the car.

## The gist (remember this)

[gist.github.com/fengye/354b5fbde72a75d74c5115856c797e2e](https://gist.github.com/fengye/354b5fbde72a75d74c5115856c797e2e),
"Tamiya FineSpec 2.4G Drive Protocol" by fengye, last active 4 Jan 2021. It documents the wire and signal between a
Tamiya ESC (TEU-105BK) and the TRU-08 receiver, and the TSU-03 servo (driven the same way):
- Three wires: red = + voltage (ESC to receiver), black = - voltage (ESC to receiver), white = driving signal (receiver to ESC).
- Signal: **57.67 Hz** (17.34 ms cycle), neutral 1500 us, **full forward 1100 us, full reverse 1900 us** (direction is
  inverted compared with usual hobby gear). The servo: centre 1500 us, left 1100 us, right 1900 us.
- ESC: max 60 A, input 6.6-7.2 V, output to the receiver 6.0 V; signal voltage 4.8-7.2 V (servo 4.8-6.0 V).
- It gives no channel numbers or receiver pinout, and does not name its manual.

What this means for a replacement receiver (inferences, not tested): a standard ELRS PWM receiver (about 50 Hz,
1000-2000 us) needs the **throttle channel reversed** and its end points set to about 1100-1900 us for the Tamiya ESC;
whether the ESC accepts 50 Hz instead of 57.67 Hz is unknown. Treat all of this as a single community source.

## Constraint to remember

**This route needs a hardware modification.** The stock radio link is typically proprietary, so we replace the
receiver, and that means one of:
- fit a **new ESC** (and receiver), or
- choose a car whose **ESC can be replaced or is already separate from the receiver**.

Cars with a combined ESC/receiver board are poor candidates: the whole board is the proprietary part.

## What was found (searches, Nov 2026; not hands-on)

- Combined ESC + receiver, proprietary: Womaqu (the HS10422 accessory listing shows a "waterproof 45A brushed
  ESC/receiver combo"); Wltoys 144001 (combined board).
- Separate ESC and receiver, standard throttle pulses: Traxxas Slash 2WD (XL-5 ESC, 3-channel receiver; the ESC
  goes in channel 2, steering is channel 1; reprogram the ESC after swapping; check polarity), and Team Associated
  Reflex 14B (1:14; Reedy ESC and 2-channel receiver; RTR listing discontinued).
- Replacement receivers: ExpressLRS PWM receivers for cars (e.g. RadioMaster ER5C-i, BetaFPV micro PWM) with ESC
  calibration described in the ExpressLRS docs. A transmitter module per car, each with its own binding phrase.
- No public reverse engineering found for cheap cars that have a screen remote and built-in camera.

## Remark from the project owner (not verified yet)

- **Tamiya has low-cost options: about 150 EUR for the complete car.**
- Its receiver, **TRU-08**, seems to have **just 3x3 pins for the radio control outputs**, i.e. plain servo-style
  headers. If so, a standard receiver could replace it directly.

To check before buying anything: whether the Tamiya car's ESC is separate from the receiver (or what ESC
it ships with), what the TRU-08 pins carry (steering, throttle, aux), whether the stock radio can be replaced
with a standard 2.4 GHz receiver, and the exact model, scale and price.

## If this track is picked up

1. Pick the car: the two TOP OPTIONS above (Tamiya, MJX 14210), or Traxxas Slash 2WD / Reflex 14B as documented fallbacks.
2. Bench test with one car: ExpressLRS PWM receiver, throttle on channel 2 for Traxxas-style ESCs, wheels off the ground.
3. Scale to four cars with four binding phrases; test that they do not interfere.
4. Camera: own small camera per car, all joining one shared Wi-Fi network (no four-network problem).
5. Controller: reuse the controller page, with a radio backend (serial channel data to the transmitter modules)
   instead of the Wi-Fi car backend.
