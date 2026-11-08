# Parked idea: a camera-less RC car with our own radio link (notes for later)

Not started. This is the alternative to the Wi-Fi camera cars of the main multiplayer track
(`docs/MULTIPLAYER.md`): a better-quality car, no built-in camera, driven by a radio we control.

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

1. Pick the car (Traxxas Slash 2WD, Reflex 14B, or the Tamiya option once verified).
2. Bench test with one car: ExpressLRS PWM receiver, throttle on channel 2 for Traxxas-style ESCs, wheels off the ground.
3. Scale to four cars with four binding phrases; test that they do not interfere.
4. Camera: own small camera per car, all joining one shared Wi-Fi network (no four-network problem).
5. Controller: reuse the controller page, with a radio backend (serial channel data to the transmitter modules)
   instead of the Wi-Fi car backend.
