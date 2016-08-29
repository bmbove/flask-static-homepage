title: Power Supply Gets a Display
date: 2015-02-23 00:20:32.735200

![Complete](/static/image/blog/psu/completed.jpg)

This project has its roots in another bit of coursework from last term. In the 
lab that went along with my microelectronics course, we had to build a bench
power supply using discrete components (BJTs). This was really the first time
where we weren't just given some schematics and told "build this"- instead
we were given a list of specs and told "meet these", which was pretty cool.

Anyways, my design worked out and my power supply was fully functional. 
Unfortunately, the only way to actually set the voltage to something known was
to hook a multimeter up to the terminals. Seeing as having this power supply
will be handy and it was definitely a very practical application of course
material, I decided to give it an upgrade and add a display to it to make it
more usable.

Desired Features:
================
 * Display voltages of both channels (one positive and one negative wrt ground)
 * Display current output of both channels
 * Display all of this data at the same time (single screen)
 * Digital, so microcontroller involved. I chose to use an AVR.
 * AVR programmed in plain C (no Wiring/Arduino stuff)

<br/>
Design Considerations:
---------------------------
The unregulated voltages reach +/-17V and the regulated voltages are between
+/-2-13V, so I can't measure them directly with the onboard ADC. These
voltages will have to be scaled down. The negative voltage may/will have to be
inverted.

Measuring current is as easy as knowing Ohm's law and having a known resistor
value. The current-liming power resistor that was built into the circuit
will make for a good Rtest at .68Ohms, but the voltage drop will normally
be on the 10's of mV scale, which I'm not sure at this point I'll be able to
measure. This difference will have to be scaled up.

There are two viable options for reference voltage when designing this- either
the power supply ground, which is the center-tap of a 24V transformer, or the
negative side of the transformer. While the immediate choice would probably
be the to just use the "established" ground of the power supply and chassis
for uniformity and safety's sake, using the -17V side has a couple advantages,
with the main one being that there is no risk of negative voltages on the 
ADC pins of the microcontroller damaging things.

Design
--------
-------------------------------------------------------------------------------------------
I used the psu ground as the display/AVR ground. I could have scale the voltages
with simple voltage dividers, but I had to invert the negative
voltage, so it made more sense to use an inverting op amp for both scaling and
inverting on the negative channel. I used I supposed what amounts to a
difference amplifier on the positive channel to avoid the inverting (can't 
have negative gain on a non-inverting amplifier, which I need). 

![Inverting Amplifier for Negative Voltage](/static/image/blog/psu/vminusmeasureschem.jpg)

I decided to measure the current by taking the voltage on either side of my
test resistor and putting it through a difference amplifier with high gain. The
same circuit works for both channels- the inputs needed to be swapped though
for a positive measurement.

![Difference Amplifier for Current Measurement](/static/image/blog/psu/imeasureschem.jpg)

Taking the usual operating ranges into consideration, I set the gain of all the
op amps to result in a meaningful output between 0 and 5V. The output was 
clamped by zener diodes to avoid damage to the uc. Since I was using 4 op amps
and quad op amps happen to be a thing, I used the
[LM2902N Quad Op Amp](http://www.taydaelectronics.com/datasheets/A-287.pdf).

For the LCD, I found a cheap 2x16 character LCD on eBay based on the common
and well-documented
[Hitachi HD44780 LCD controller](https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller).

I chose to use an ATmega328p as my microcontroller, since I have a small stock
pile of them thanks to some samples I received from Atmel some time ago.

Build
------
-------------------------------------------------------------------------------------------
The build isn't particularly interesting- there's no cool hardware or any
interesting problems to solve besides where to put things. Trying to route
almost 20 resistors around the op amp IC was a challenge. 


![Board- front and back](/static/image/blog/psu/board.jpg)

This would have been
a great opportunity to design and etch my own board, and though I did think
about it, I was quickly overwhelmed by KiCAD and picking part footprints.
Oh well. My homemade [wiring pencil](https://en.wikipedia.org/wiki/Wiring_pencil)
made short work of the point-to-point stuff.

![Intravenous copper injections](/static/image/blog/psu/pencil.jpg)

Interestingly enough, I did have to build a simplified replica of the circuit used 
for regulation on the PSU to step the voltage down from +/-17V to +/-15V (and
regulate it) to keep it within specs for the op amp.

The HD44780 for the LCD uses 8 pins/bits for communication, but also supports
a 4 bit mode, where 4 pins are used and bytes are transferred one nibble at
a time. Though I had an abundance of pins on the AVR, I went with 4-bit mode
(4 pins, 4 wires) to save some time and space. I also tied the read select pin
to ground on the LCD since I wouldn't be reading from it.

Software
-----------
-------------------------------------------------------------------------------------------
I've never programmed a microcontroller in C prior to this. My experience with C
is/was pretty limited and is mostly from making modifications here and there
to open source software that I use. Even so, I don't think the language is as
important as the mindset when programming at this level. I found it really
cool to be working with directly with the hardware- manipulating registers
and having things happen physically because of it. I spend most of my time
on computers a million layers of abstraction away from this kind of control,
and even using the Arduino ecosystem sets quite a bit of distance between 
the hardware and programmer.

Since this was new to me, I practiced with some basic stuff first- blinking
an LED and taking ADC readings. I spent quite a bit of time reading the
datasheet and figuring it all out.
After this I jumped into getting the display
to work. The communication protocol is pretty simple- set the pins where
they need to be, then pulse the EN pin according to the datasheet. The
initialization process is all done 4 bits at a time, then after that, all
communication is 8 bits (but still just 4 bits at a time). 

    // display driver needs 8 bits per character but can accept
    // 4 bits twice for less wires
    void _write_byte(uint8_t to_write){

        uint8_t bottom = to_write & 0x0F;
        uint8_t top = (to_write >> 4) & 0x0F;

        int i;
    
        // send the top 4 bits
        for(i=0; i < 4; i++)
            _set_pin(port[i], pin[i], (top >> i & 0x01));
        _pulse_enable();

        // send the bottom 4 bits
        for(i=0; i < 4; i++)
            _set_pin(port[i], pin[i], (bottom >> i & 0x01));
        _pulse_enable();

    }

Eventually, I was able to get the LCD displaying words (that I told it to
display). I also discovered that it was possible to set the LCD as stdout so
that I could use `printf` to write to it. The way I understand it, you create
a stream that streams it's input (one byte at a time) to a function, in this case
"put_char", which writes the byte it received to the LCD. Then you set that
stream as stdout.

    FILE lcd_stream = FDEV_SETUP_STREAM(
        put_char,
        NULL,
        _FDEV_SETUP_WRITE
    );
    stdout = &lcd_stream;

![To Crush Your Enemies](/static/image/blog/psu/crushyourenemies.jpg)

Once I could write arbitrary strings to the LCD, I turned my attention to
taking proper ADC readings. The ATmega328p has a 10-bit ADC sitting behind an
8 (or 6?) channel mux. This should allow me to read down to about 5mV resolution
reading from the op amp output, but the signal I'm interested in has been
scaled down, so realistically, I'd be able to achieve about 25mV resolution.
this would be fine for measuring voltages, as I doubt my regulating circuit
is capable of maintaining that kind of stability.

I needed higher resolution though for measuring the current, at least for
the lower end. I read a little bit on [oversampling](http://www.atmel.com/Images/doc8003.pdf), and the technique seemed 
simple enough- for every extra bit of resolution, the number of samples 
needed increases by a factor of 4. So, for 12-bit resolution, I would
need to average 16 samples together for each reading.

Another issue with ADC readings, especially with the added resolution, was noise.
To try to limit this, I used an [exponential moving average](http://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average).

    void adc_add_reading(struct ADCCh *ch, uint16_t reading){
        // oversample to get 12 bit resolution.
        // wait for 16 new samples (factor of 4 per extra bit)
        // then compute new voltage value using exponentially weighted
        // running average. 
        reading <<= 2;
        if(ch->sample_count == 15){ 

            ch->samples[15] = reading;

            uint8_t i;
            uint16_t average = 0;
            for(i=0; i < 16; i++){
                average += ch->samples[i];
            }
            average >>= 4;
            ch->value = average;

            uint32_t new_v= ((uint32_t)ch->value * AREF * 10000) >> 12;
            int32_t prev_v = ch->voltage - ((ch->voltage * SCALE)/100);
            ch->voltage = ((new_v * SCALE)/100) + prev_v;
            ch->voltage = new_v;

            ch->sample_count = 0;
        }
        else{
            ch->samples[ch->sample_count] = reading;
            ch->sample_count++;
        }
    }

When a new ADC reading is available, an interrupt is triggered that adds
the new sample to the average (for that channel) and changes to the
next channel in the list. 

    // Interrupt- when a new ADC reading is available
    ISR(ADC_vect){

        uint8_t low = ADCL;
        uint8_t high = ADCH;
        uint16_t reading = ((high << 8) | low);

        // add reading in, switch to next channel
        adc_add_reading(adc_lst->cur, reading);
        next_adc(adc_lst);
        ADMUX = (ADMUX & 0xF0) | adc_lst->cur->channel;

    }

I was taking a data structures class at the time,
so I got fancy and implemented the ADC queue as a circularly linked list.

    struct ADCCh{
        // ADC channel
        uint8_t channel;
        // samples taken
        uint16_t samples[16];
        // count of samples to put towards next value
        uint8_t sample_count;
        // raw adc value
        uint16_t value;
        // computed voltage
        uint32_t voltage;
        // next channel
        struct  ADCCh *next;
    };
    struct ADCList{
        uint16_t size;
        struct ADCCh *front;
        struct ADCCh *cur;
    };

To convert the ADC readings to real values, I took about 25 samples at
varying voltages and currents for every measurement and obtained a fit function
through the Sheets app on Google Drive. Since the 328p doesn't have an FPU,
all math was done in fixed point, then the decimal was placed when it came
time to push the number to the LCD.

Results
---------
-------------------------------------------------------------------------------------------
The whole thing worked nearly as expected. Testing with a digital multimeter, 
the voltage measurements were very accurate (somewhat more so that the DMM, since
it only goes to tenths precision). I knew that it would be difficult to obtain
a high degree of accuracy with the current measurements, but they were very
close. I don't have a way to put a precise, controlled current through anything,
so I relied on a DC motor, putting friction on the shaft to use it as my
current sink. Accuracy was good down to about 50mA and stayed accurate until
around 800mA. The PSU is designed to limit current to 1A, so around 8-900mA,
the current limiting starts to take effect. I was slightly off with my
gain in the op amps used to measure the current, so 5V (and the limit of my
measurements) turned out to be around 860mA

[Complete code on Github](https://github.com/bmbove/avr_psu_display)

References
=======
 * [A classmate's implementation of a similar idea](https://github.com/dylanmackenzie/avr-power-supply-display)
 * [AVR121: Enhancing ADC resolution by
oversampling](http://www.atmel.com/Images/doc8003.pdf)
 * [Bit Twiddling Hacks](https://graphics.stanford.edu/~seander/bithacks.html)
 * [The ADC of the AVR](http://maxembedded.com/2011/06/the-adc-of-the-avr/)
 * [Analog to Digital Converter - AVR Beginners](http://www.avrbeginners.net/architecture/adc/adc.html)
