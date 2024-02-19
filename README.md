# piPlug

### Introduction
---
piPlug uses a [Raspberry Pi Pico W](https://www.raspberrypi.com/products/raspberry-pi-pico/) with its GPIO and relays/relay boards to create a minimalist smart plug. It uses a MicroPython based web server ([MicroPyServer](https://github.com/troublegum/micropyserver/tree/master)) to provide the initial configuration web interface, an overview page, and endpoints to get and set outlet states.
### Background
---
When setting up smart plugs and other devices, I got annoyed with all the apps, hubs and other proprietary mechanisms to deal with. My intention was to communicate with devices using Node Red running on IOBroker (although I didn't really want to lock in to IOBroker or Node Red,) but I kept having to use device specific adapters with authentication mechanisms of questionable reliability or longevity. Since my requirements are pretty simple, I decided to simply create cheap smart plugs myself that do as little as possible.
I want an inexpensive device that survives getting unplugged without proper shutdowns, controls up to 5 outlets per device, communicates via HTTP, can push outlet states to configurable HTTP endpoints, can be controlled using simple HTTP requests, provides a very basic "security" mechanism to prevent household members from randomly turning outlets on and off in their web browsers, uses household wifi, emits an access point for configuration purposes if not yet configured, and can be "factory"-reset easily to reconfigure.    
### Hardware
---
* Raspberry Pi Pico W (~ $6)
* Hi-Link HLK-PM01 220V-5V step-down power supply module (~$4.50) 
* 1-channel 5V relay modules 10A - 250VAC (~$1 each)
* Power strip with up to 5 outlets and enough space to put all the components inside (~$5)
### Software
---
* MicroPython firmware
### Installation
---
* Checkout or download the contents of the install folder of this repository
* Download the [MicroPython firmware](https://micropython.org/resources/firmware/RPI_PICO_W-20240105-v1.22.1.uf2) (or find a different version and download it [here](https://micropython.org/download/RPI_PICO_W/))
* Unplug the Pi Pico W, hold down the bootsel button while plugging it into your computer
* Wait for the USB mass storage device to appear and copy the MicroPython firmware onto it. It will automatically reset.
* Deploy the previously downloaded contents of the install folder of this repository to the Raspberry Pi Pico W
* Unplug the Raspberry Pi Pico from your computer
* Install the hardware:

![Hardware](/hardware.png)
### Use
---
>*Note:* I don't think it's necessary to run a DHCP server just for the initial configuration. There is a pure python based implementation somewhere that will probably work but the overhead (and space needed) is quite significant. If you think this initial setup is too much work, just create a `user_config.py` manually (see below) and copy it onto the pi. In that case, you can skip all the initial configuration. The device should boot straight into the user configuration (as a wifi client using DHCP.) 

#### Initial configuration
* Plug the piPlug you just created into an outlet. 
* After a few seconds, its LED will blink fast - you should see a new wifi SSID on your computer starting with `piPlug-`. Connect to it - the password is `12345678`.
* Set your computer's IP address on this network to `192.168.0.2`, subnet mask `255.255.255.0`. You don't need a default gateway or DNS. 
* Access [http://192.168.0.1](http://192.168.0.1) in your web browser.
* This should be displayed: ![Initial configuration web page](/initial_config_screenshot.png)
* Enter your own wifi's information (Pi Picos only support 2.4GHz wifi, so make sure you use that)
	* `SSID`: your wifi's name
	* `Password`: your wifi's password
	* `Country`: the two-letter code of your country (important for the wifi bands to be used and cannot be omitted) - something like `US`, `DE`, `CN`, `PL` etc
* Configure the remaining properties:
	* `Name`: choose a name for this piPlug. It will be its new hostname, and visible like this to your DHCP server. The name will also be communicated back when HTTP requests are made, so you can use it to identify the device later
	* `Identification`: optional - an arbitrary string, e.g. a uuid or a salt, that you can use as a very, *very* basic, *unencrypted* security key. If you set this, you will need to provide this string every time you call one of the endpoints (i.e., to turn an outlet on or off.) If you leave this empty, you won't need to provide this key when calling endpoints.  
	* `Status updates`: optional - provide a URL (must be http - SSL is *not* supported) that this piPlug calls whenever an outlet changes its state. It will also call this endpoint right after it boots, so you can use this request to advertise the DHCP-assigned IP address.  
	* Hit save. You'll see an overview page with a brief config overview. At that time, the Pico is already rebooting and should be back up a few seconds later.  

#### Headless configuration
If you don't want to use the initial configuration mechanism, you can provide your own `user_config.py`. Create a file with the following contents (edit values as described) and place it into the root folder of your Pico's internal storage.
```python
user = {
	#Your wifi network name
	"ssid": "My Wifi SSID",
	#Your wifi network password
	"pwd": "password",
	#A custom hostname for this piPlug
	"device_name": "piplug1",
	#A custom key, or empty if not needed
	"id_key": "changeme",
	#The wifi country 2-letter code
	"country": "US",
	#An array of update URLs that will be informed 
	#after the device boots or the state of an outlet changes.
	#This MUST be unencrypted. SSL is not supported.
	"updates": ["http://my-home-server.local:8081/devices/statusupdate"]
}
```

### Disclaimer
Everything you do based on this is at your own risk. You'll probably be dealing with 230V or 110V that can seriously hurt or kill you. You might break equipment, cause a fire or other damage to yourself, your property, others, or other people's property. That's on you - I'm not taking any responsibility for any of that.
