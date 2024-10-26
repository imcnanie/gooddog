# Good Dog- Turn your perfectly good dog into robot arms
Unitree has decided to encrypt their RS485 CRC, so I recorded all the packets using the [freedog sdk](https://github.com/Bin4ry/free-dog-sdk) (shoutout to a sick project!) and play them back directly into the motor lines.

Yes this means we will finally be able to control our dogs without the brain guts! This is a proof of concept, feel free to use these tables to e.g. pixhawkify your dawg. Of course I'd love to decode the CRC so we don't need to record packets all the time, but it's progress! This repo should provide more than enough packets for CRC analysis. HMU if you want to work on this.

# Wiring
- I use a [U2D2](https://www.robotis.us/u2d2/), the adapter for controlling dynamixels. Go1's motors operate at 5 000 000 bps here, so we need a good RS485 adapter to talk to it.
- When recording, you need to splice into the rs485 lines and maintain the connection to the control board
- When driving, you need to disconnect the rs485 from the robot
- Keep in mind that there are 4 separate RS485 buses for each leg, so you'll need to splice into them separately if you're recording packets.

# Normal Operation
- unplug the legs, they are now free.
- hook up the RS485 adapter and power (TODO: images, explanation)
- run sudo ./exanoke_send_torque.py it will send a sine wave of torque values in the positive and negative direction on the front right middle joint (FR_1). you can change this by importing a different torque_table. See example_read_angle_space_mode.py for that.

# recording packets
- leave the motors plugged into the driver board
- boot the dog, put it in chilling mode:
```
L2 + A
L2 + A
L2 + B
L1 + L2 + START
```
- connect to the dog's wifi network
- start the logging script: `sudo ./log_packets_and_generate_LUT.py RR_0` (or RR_1, RR_2...) 
- start the freedog streaming script (WARNING: will immediately put full torque on an actuator!) (sweeps packets from -4.0 to 4.0 torque, set which actuator you're recording on the bottom of the script). I sweep pretty slow to make sure to capture all the packets, it will take a few minutes.
- when the streaming script is finished the leg will go limp, then you can ctrl+c the logging script, which will generate a lookup table based on that motor

# NixOS notes
- I use NixOS, so it will get the dependencies for me, if you use another OS, install the deps yourself, you can find them in the #! at the top of the file. (pyserial, numpy rn). Then you probably want to run them with python instead of ./ 

# Misc Notes
- The LUTs for FL_0, RL_0, FR_0, FL_0 will actually work for any *_0 motor (same goes for the *_1's *_2's). But I noticed on my dog the packets are slightly different. See below. I suspect this is calibration, or something in freedog, but it warrants futher investigation
  - RR_0: feee00ba0aff0000000000005fffff7fc aecff7f 0000e42702000000000087f39bd4
  - FL_0: feee00ba0aff0000000000005fffff7fc 5070080 0000e427020000000000676b3672
- The *_2 LUTs correspond to half the torque ~27k instead of ~40k. Again not sure if this is baked into freedog, but it probably has something to do with the lever arm on the pushrod
- I sent values from -4 to +4 torque. The freedog example goes from -5 to +5 but I really didn't want to break my robot. Also my dog is cut in half and has the motherboard precariously spilling out of its guts. Let me know if you need more torque, happy to help try it on your dog!
- The torque numbers seem to be in 10000Nm (50000 is 5Nm)

# TODO
- [x] parse angle from motors
- [x] make a # -> Nm table for the motor torques
- [ ] parse velocity, temp from motors
- [ ] realtime kernel?
- [ ] pictures on this readme

# special thanks/previous work
- [free dog sdk](https://github.com/Bin4ry/free-dog-sdk)
- [devemin's awesome X](x.com/devemin/)
- [Bin4ry](https://github.com/Bin4ry)
- [d0tslash](https://x.com/d0tslash)