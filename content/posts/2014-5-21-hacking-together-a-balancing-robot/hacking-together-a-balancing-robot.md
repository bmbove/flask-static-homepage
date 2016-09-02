title: Hacking Together a Balancing Robot
date: 2014-05-21 12:03:21.234141

As part of my digital logic design course, I had to put together a project to display in the class booth at the [2014 OSU Engineering Expo](http://engineering.oregonstate.edu/expo2014 "2014 Oregon State University Engineering Expo"). The only requirement was that the project made use of some piece of hardware that we had used in class or in a previous engineering class: the [Teensy 2.0](http://www.pjrc.com/store/teensy.html), the [Wunderboard](http://eecs.oregonstate.edu/education/hardware/wunder.2/), the [Lattice MachX02 FPGA](http://www.latticesemi.com/en/Products/DevelopmentBoardsAndKits/MachXO2BreakoutBoard.aspx), and/or the [Tekbot Robot Kit](http://eecs.oregonstate.edu/education/hardware/tekbot/). 

Brainstorming for a few weeks left me with some pretty obscure ideas that, while possibly awesome builds, would have been mostly beyond the capabilities of the hardware I was using and would also have taken too much time. After browsing some articles on [Hackaday](http://www.hackaday.com "Hackaday") and watching some cool youtube videos, I decided to go with the tried-and-true inverted pendulum- a self-balancing robot.

## Build

The parts were ordered from [Pololu](http://www.pololu.com): a TB6612FNG motor controller to drive the two DC motors; a MMA7361LC 3-axis accelerometer and a LPY550AL dual axis gyro for pitch sensing. To start out, everything was breadboarded so I could figure out how to interface with each sensor. I used an Arduino to read from the sensors and control the motor speed based on sensor output. This stage accumulated into having an Arduino and breadboard electrical-taped to the body of the robot and me attempting to control it over a serial connection, getting much too far ahead of myself. Thankfully I don't have any pictures of this.

![Prototyping](/static/image/blog/expobot/breadboard.jpg)

After I managed to make sense out of the gyro and accelerometer readings and
use the motor controller, I got to soldering a board together. The board was
basically divided into 3 parts- power distribution, microcontroller, and
'accessories'. The brains of the operation is an ATmega328p mostly because I'm
most comfortable with it and I have a small stockpile of them from free
samples. I also added on a
[nRF24L01](http://www.nordicsemi.com/eng/Products/2.4GHz-RF/nRF24L01
"nRF24L01")-based RF module so I could make adjustments over the air once I got
everything up and running.

Running the microcontroller at 5V would be easiest as far as programming and
timing, but the accelerometer, gyro, and the RF chip all required 3.3V (though
the nRF24 has 5V-tolerant data lines). Since the sensors wouldn't be drawing
much current, I just pulled off the 5V regulated line for my 3.3V regulator.
The IC used for the 3.3V rail was the LM317AT, which is a nifty little
regulator- it's output voltage is adjustable with a pair of resistors, so
although it was a bit more soldering than a set 3.3V reg, it was nice to have
in a pinch. I eventually ended up adding a monster capacitor on the line-in due
to problems with motor noise. The battery pack I used hovered around 8V when
fully charged- the motor controller got this full voltage to drive the motors.

Since I may want to use the ICs for other projects, everything was socketed in.
Female headers for the sensors/motor driver/RF module and a 28-pin DIP socket
for the microcontroller. I added a programming header so I could program the
microcontroller with an Arduino (I don't own some fancy dedicated AVR
programmer) and a couple LEDs for increased coolness.

![Completed Board](/static/image/blog/expobot/board.jpg)

<center>![Hello World](/static/image/blog/expobot/blink.gif)</center>

Now that it was all together, I strapped it on the robot body and started to
code. The first step was figuring out how to get a pitch in degrees from the
combined data from the accelerometer and gyro. First, reading the accelerometer
when the board is first powered up gives the approximate location of "down",
which I designated as either 0 degrees or 180 degrees depending on which side
the robot was laying on. I also took the average of 100 readings to get a
baseline value for all of the sensors. The ATmega328p has a built-in 10-bit DAC
and I used 3.3V as my reference voltage.

```c
void calibrateSensors(){
    float acc_conv = (.800/AREF) * 1024; // 1g - AREF is ~3.40V
    // take average of 100 readings
    for (uint8_t i = 0; i < 100; i++){
        zeroValues[0] += analogRead(GyroX);
        zeroValues[1] += analogRead(AccX);
        zeroValues[2] += analogRead(AccY);
        zeroValues[3] += analogRead(AccZ);
        delay(10);
    }

    zeroValues[0] /= 100; // Gyro X-axis
    zeroValues[1] /= 100; // Accelerometer X-axis
    zeroValues[2] /= 100; // Accelerometer Y-axis
    zeroValues[3] /= 100; // Accelerometer Z-axis  

    if (zeroValues[3] > 450){ 
        // +1g when lying on one side
        zeroValues[3] -= acc_conv; 
        pitch = 0;
    } 
    else {
        // -1g when lying on the other side
        zeroValues[3] += acc_conv; 
        pitch = 180;
    }
}
```

       
After a zeroing procedure and designating a reference point, one can get a
pretty good estimate of pitch using some trig. I moved the result of arctan
over by pi radians to keep the result between 0 and 360 degrees.

```
acc_angle = (arctan(accXvalue/accZvalue) + π) radians * 57.2957795 degrees/radians
```

From some research, I learned that while an accelerometer reading is pretty
accurate, it's also very sensitive to vibration (it's sensing any force that
acts on it). This might lead to some ugly data, so the accelerometer info is
combined with information from the gyro, which measures it's own current
angular velocity (around different axes- I was only interested in 1, however).
Of course, one can also get a rough estimate on current pitch by integrating
rotational velocities, but gyro sensors tend to have a certain amount of drift.
Integrating the measured rotational velocities also includes integrating the
drift error, compounding it over time and leading to bad data very quickly.

The solution to this problem is combining the output of both sensors with a
filter. This nullifies the shortcomings of both sensors and results in a very
accurate pitch calculation over time. Though I initially implemented a [Kalman
filter](https://en.wikipedia.org/wiki/Kalman_filter "Kalman Filter") using
[this library](https://github.com/TKJElectronics/KalmanFilter "Kalman Filter
Arduino Library"), I decided that it took too much processing power and instead
went with a basic complementary filter:
    
    
```
gyro_angle_change = gyro_rate * dt
new_pitch = pitch + gyro_angle_change
pitch = (.98 * new_pitch) + (.02 * acc_angle)
```

Once I was satisfied with the pitch detection, I moved on to the [PID
controller](https://en.wikipedia.org/wiki/PID_controller "PID Controller"). I
wrote my own PID function (and was successfully able to balance the robot with
it), but ended up going with the [Arduino PID
library](http://playground.arduino.cc/Code/PIDLibrary "Arduino PID Library")
for simplicity. I also chose to go this route because it will make it much
easier in the future to add a PID cascade so that I can drive the robot around
while it's standing up. I won't go into detail on PID control, but here's some
pseudocode taken from Wikipedia to show approximately what's going on:

```c
previous_error = 0 degrees
integral = 0 
setpoint = 90 degrees // 90 degrees is straight up and down
dt = 10 microseconds
start:
    error = setpoint - pitch
    integral = integral + (error * dt)
    derivative = (error - previous_error) / dt
    previous_error = error
    // this output is sent to the motors
    // Kp, Ki, and Kd are weights for each term, adjustable wirelessly
    output = Kp*error + Ki*integral + Kd*derivative
    wait(dt)
    goto start
```

I constrained the output of the PID controller to -255:255 (for PWM control)
and disabled it (and the motors) if the pitch was more than 20 degrees away
from the set point, since it would be impossible to recover from being that far
off balance. Tuning the controller (adjusting Kp, Ki, and Kd) was, by far, the
most difficult part of this project. Luckily, I was able to set up
communication between my Raspberry Pi and the robot control board using nRF24
modules so I could change the PID parameters wirelessly and without having to
reprogram the microcontroller. Even with this convenience however, it was still
a long and difficult process to properly tune the controller, and even then, I
still missed the mark. I mostly attribute this to the motors- they're small,
plastic-geared DC motors rated at 6V. They don't have much when it comes to
torque and speed, and the robot body is a decent-sized piece of aluminum.
Still, I was pretty happy with the results considering what I had to work with.

After a very long day of tuning, debugging, and part rearrangement, I finally
managed to get the little guy to stand on his own feet (or whatever) for the
first time:

<video controls="controls" width="640" height="360">
	<source src="http://www.brianbove.com/static/image/blog/expobot/first_balance.mp4" type="video/mp4" />
	<source src="http://www.brianbove.com/static/image/blog/expobot/first_balance.webm" type="video/webm" />
	<source src="http://www.brianbove.com/static/image/blog/expobot/first_balance.ogv" type="video/ogg" />
	<object type="application/x-shockwave-flash" data="http://releases.flowplayer.org/swf/flowplayer-3.2.1.swf" width="640" height="360">
		<param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.1.swf" />
		<param name="allowFullScreen" value="true" />
		<param name="wmode" value="transparent" />
		<param name="flashVars" value="config={'playlist':[{'url':'http%3A%2F%2Fwww.brianbove.com%2Fstatic%2Fimage%2Fblog%2Fexpobot%2Ffirst_balance.mp4','autoPlay':false}]}" />
		<span title="No video playback capabilities on your device! Sorry!">First Time Balancing</span>
	</object>
</video>

With this part of the project (mostly) done, I also incorporated the Teensy 2.0
into the system so I could drive my robot around with RF control. I picked up a
wired Xbox controller from the thrift store for cheap, wired some leads to the
potentiometers used for the analog sticks, and plugged those into the Teensy. I
put together a little board combining the Teensy and another nRF24 module
(these things are only $2, easy to use, and very useful), strapped it into the
memory card opening on the controller, and programmed the Teensy to send a
certain sequence for each combination of directions read from the analog stick
(left and forward, just forward, etc). I reprogrammed the robot control board
to listen for these commands when it was lying flat and to respond
appropriately, mostly by driving around and chasing my dog, who, unlike most
people today, still has a healthy fear of robots.

Now that the robot could mostly balance on his own and had some rudimentary RF
control, it was Expo time. One of the other guys strapped a USB nerf turret on
to his robot and we decided to hold an execution to test his aim and my
balance:

<video controls="controls" width="640" height="360">
	<source src="http://www.brianbove.com/static/image/blog/expobot/execution.mp4" type="video/mp4" />
	<source src="http://www.brianbove.com/static/image/blog/expobot/execution.webm" type="video/webm" />
	<source src="http://www.brianbove.com/static/image/blog/expobot/execution.ogv" type="video/ogg" />
	<object type="application/x-shockwave-flash" data="http://releases.flowplayer.org/swf/flowplayer-3.2.1.swf" width="640" height="360">
		<param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.1.swf" />
		<param name="allowFullScreen" value="true" />
		<param name="wmode" value="transparent" />
		<param name="flashVars" value="config={'playlist':[{'url':'http%3A%2F%2Fwww.brianbove.com%2Fstatic%2Fimage%2Fblog%2Fexpobot%2Fexecution.mp4','autoPlay':false}]}" />
		<span title="No video playback capabilities, please download the video below">Firing Squad</span>
	</object>
</video>
 
## Results

All-in-all, considering the initial hardware I had to work with (crappy motors,
heavy robot body), I think I managed alright for my first attempt at balancing
something. I learned about how cool PID control is, and while it can be fussy
and tuning is basically black magic, the fact that it can accurately control a
system that it knows next to nothing about is pretty neat. I did have to debug
all sorts of problems along the way- electrical and mechanical, analog and
digital, and though I worked out most of the kinks, some problems still
remained.

Here's some issues that I ran into and their solutions if I came up with one:

* Motor noise was resetting the microcontroller. I thought that the motor
  controller would have built-in protection for this, but it was still a
  problem. I ended up adding all sorts of ceramic capacitors to the motor- from
  one lead to another and to each lead to the motor body. I also added a 330uF
  cap to the line-in/motor voltage rail. This solved the problem for the 8V
  coming from my battery pack, but it persisted if I tried anything higher
  (even 9V). The motor controller was rated up to 13.5V. I think I could have
  added a handful of diodes to the motor controller output to mitigate this
  noise more successfully, but there wasn't room left on the board.

* The complementary filter was not responding quickly enough to angle changes,
  resulting in slow PID response and a wobbly robot. I don't know why this is,
  but I found that if I added a scale factor to the gyro output, the problem
  became much much smaller. This is most likely due to either an error in my
  math at some other point or an error in my understanding of how this
  particular gyro works.

* Weight distribution was an interesting problem for this robot. I tried
  several different configurations to see which balanced best. For standing
  still, I found that if I put the batteries below the motor axis, it could
  stand forever. However, in this configuration, though it could catch itself
  in one direction if it was disturbed, it wasn't able to in the opposite
  direction. I finally settled on placing the batteries directly above the
  motor axis.

* The major problem that I was not able to solve is that the robot can't
  effectively balance on hard surfaces. On carpet, it can balance by itself and
  respond to disturbances pretty easily, though once placed on a hard, flat
  surface such as wood, linoleum, or cement, it can't even balance standing
  still. I spent hours trying to adjust the PID parameters to achieve decent
  balance, but to no avail. At the expo, I ended up bringing a small kitchen
  towel with me so it could balance on the display table. My best guess is that
  this problem has a lot to do with the motors and wheels. The wheels used are
  sturdy foam, but still pliable. The motors leave the robot with too-low
  torque and the low tolerances in the gearing make for a decent amount of
  kickback, futher affecting stability. I think this problem could be solved
  with better (read: more expensive) motors and wheels, but that was outside
  the scope and budget of this project.

## Code

The complete code for this project is on github-
[Expobot](https://github.com/bmbove/expobot "Expobot"). A quick warning: I
didn't clean it up at all after initial development, so it's pretty ugly at
some points. I did manage to comment most of it though.

## References

* [RS4 - Self-Balancing Raspberry Pi Robot](http://letsmakerobots.com/node/38610)
* [nRF24 Arduino and Raspberry Pi Library](https://github.com/stanleyseow/RF24)
* [TJKElectronics Kalman Filter Library](https://github.com/TKJElectronics/KalmanFilter)
* [TJKElectronics Balancing Robot](https://github.com/TKJElectronics/BalancingRobot)
* [Accelerometer Pitch Measurment](http://www.hobbytronics.co.uk/accelerometer-info)
* [Arduino PID Library](http://playground.arduino.cc/Code/PIDLibrary)

### Other balacing robots that are way cooler than mine:

* [RS4](https://www.youtube.com/watch?v=O6XkH84JYjU)
* [B-Robot](https://www.youtube.com/watch?v=V-_uxpX9aFQ)
