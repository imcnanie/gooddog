# gooddawg WIP! Only 1 motor logged for now!
Unitree has decided to encrypt their RS485 CRC, so I am recording all the packets using the [freedog sdk](https://github.com/Bin4ry/free-dog-sdk) (shoutout to a sick project!) and playing them back directly into the motor lines.

Yes this means we will finally be able to control our dogs without the brain guts! This is a proof of concept, feel free to use these tables to e.g. pixhawkify your dawg. Of course I'd love to decode the CRC so we don't need to record packets all the time, but it's progress! This repo should provide more than enough packets for CRC analysis. HMU if you want to work on this.

# hookup
- I use a [U2D2](https://www.robotis.us/u2d2/), the adapter for controlling dynamixels. Go1's motors operate at 5 000 000 bps here, so we need a good RS485 adapter to talk to it.
- When recording, you need to splice into the rs485 lines and maintain the connection to the control board
- When driving, you need to disconnect the rs485 from the robot
- Keep in mind that there are 4 RS485 lines from each leg, so you'll need to splice into each of them separately if you're recording packets.

# normal operation
- unplug the legs, they are now free.
- hook up the RS485 adapter and power (TODO: images, explanation)
- run sudo ./send_torque_from_LUT.py it will send a somewhat light sine wave of torque values in the positive and negative direction on the rear right middle joint (RR_1)

# recording packets
- leave the motors plugged into the driver board
- boot the dog, put it in chilling mode:
`
L2 + A
L2 + A
L2 + B
L1 + L2 + START
`
- start the logging script: sudo ./log_packets_and_generate_LUT.py RR_0 (or RR_1, RR_2...) 
- start the freedog streaming script (sweeps packets from -4.0 to 4.0 torque, set which actuator you're recording on the top of the script). I sweep pretty slow to make sure to capture all the packets, it will take a few minutes.
- when the streaming script is finished the leg will go limp, then you can ctrl+c the logging script, which will generate a lookup table based on that motor (TODO: make it work for more than one motor)

connect to the dogs wifi network (TODO

# NixOS notes
- I use NixOS, so it will get the dependencies for me, if you use another OS, install the deps yourself, you can find them in the #! at the top of the file. (pyserial, numpy rn). Then you probably want to run them with python instead of ./ 

# Misc Notes
- The LUTs for FL_0, RL_0, FR_0, FL_0 will actually work for any *_0 motor (same goes for the _1s _2s). But I noticed on my dog the packets are slightly different. See below. I suspect this is calibration, or something in the freedog SDK, but it warrants futher investigation
  - RR_0: feee00ba0aff0000000000005fffff7fc aecff7f 0000e42702000000000087f39bd4
  - FL_0: feee00ba0aff0000000000005fffff7fc 5070080 0000e427020000000000676b3672
- The *_2 LUTs correspond to half the torque ~27k instead of ~40k. Again not sure if this is baked into freedog, but it probably has something to do with the lever arm on the pushrod
- I sent values from -4 to +4 torque, I will soon be coming up with a scale setup to convert these into Nm. The freedog example goes from -5 to +5 but I really didn't want to break my robot (there were reports of people burning out mosfets on their robots). Also my dog is cut in half and has the motherboard precariously spilling out of its guts. Let me know if you need more torque, happy to help try it on your dog!

# TODO
- double the fidelity of the packets (send half as slow)
  - upload the freedog driver script
- build lookup tables for all the motors
- parse feedback from motors
- realtime kernel?
- make a # -> Nm table for the motor torques
- pictures, better explanation on this readme

# special thanks/previous work
- [free dog sdk](https://github.com/Bin4ry/free-dog-sdk)
- [devemin's awesome X](x.com/devemin/)
- [Bin4ry](https://github.com/Bin4ry)
- [d0tslash](https://x.com/d0tslash)