# gooddawg WIP! Only 1 motor logged for now!
Unitree has decided to encrypt their RS485 CRC, so I am recording all the packets using the [freedog sdk](https://github.com/Bin4ry/free-dog-sdk) (shoutout to a sick project!) and playing them back directly into the motor lines.

Yes this means we will finally be able to control our dogs without the brain guts! This is a proof of concept, feel free to use these tables to e.g. pixhawkify your dawg. Of course I'd love to decode the CRC so we don't need to record packets all the time, but it's progress! HMU if you want to work on this.

# hookup
- I use a (U2D2)[https://www.robotis.us/u2d2/], the adapter for controlling dynamixels. Go1's motors operate at 5 000 000 bps here, so we need a good RS485 adapter to talk to it.

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
- start the logging script: sudo ./log_packets_and_generate_LUT.py
- start the freedog streaming script (sweeps packets from -4.0 to 4.0 torque).
- when the streaming script is finished the leg will go limp, then you can ctrl+c the logging script, which will generate a lookup table based on that motor (TODO: make it work for more than one motor)

connect to the dogs wifi network (TODO

# NixOS notes
- I use NixOS, so it will get the dependencies for me, if you use another OS, install the deps yourself, you can find them in the #! at the top of the file. (pyserial, numpy rn). Then you probably want to run them with python instead of ./ 

# TODO
- double the fidelity of the packets (send half as slow)
  - upload the freedog driver script
- build lookup tables for all the motors
- pictures, better explanation on this readme

# special thanks/previous work
- (free dog sdk)[https://github.com/Bin4ry/free-dog-sdk]  
- (devemin's awesome X)[x.com/devemin/]
- (Bin4ry)[https://github.com/Bin4ry]
- (d0tslash)[https://x.com/d0tslash]