import network
import os
import machine
import json
import sys
from utime import sleep
from micropyserver import MicroPyServer
import time
import usocket as socket
import ustruct as struct

NTP_HOST = 'pool.ntp.org'

def blink(timer):
    led.toggle()

def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA)

def setTimeRTC():
    tm = getTimeNTP()
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))


def setup_ap(config):
    wap = network.WLAN(network.AP_IF)
    wap.ifconfig((config.ap_config['ip'], config.ap_config['subnet_mask'], '', ''))
    wap.config(essid=config.ap_config['ssid'], password=config.ap_config['wifi_password'])
    wap.active(True) 
    print(wap.ifconfig())

def run(config):
    network.country = config.user["country"]
    wifi = network.WLAN(network.STA_IF)
    wifi.config(pm = 0xa11140)
    wifi.active(True)
    wifi.connect(config.user["ssid"], config.user["pwd"], hostname=config.user["device_name"])
    while not wifi.isconnected() and wifi.status() >= 0:
        time.sleep(1)
    setTimeRTC()
    return

def getmachineid():
    mid = ""
    for b in machine.unique_id():
        mid += "{:02X}".format(b)
    return mid

def setup(request):
    server.send("<html />")
    
def save_config(request):
    if utils.get_request_method(request) != 'POST':
        server.send("Invalid request")
        return
    params = utils.get_request_post_params(request)
    if params["ssid"].strip() != '' and params["pwd"].strip() != '':
        config = {}
        config["ssid"] = params["ssid"].strip()
        config["pwd"] = params["pwd"]
        config["device_name"] = params["device_name"].strip()
        config["id_key"] = params["id_key"].strip()
        config["country"] = params["country"].strip().upper()
        if len(config["country"]) != 2:
            server.send("Wifi country must be set to a 2-digit country code")
            return
        config["updates"] = []
        if params["u"].strip() != '': config["updates"].append(params["u"].strip())
        file = open('user_config.py', 'w')
        print(json.dumps(config, separators=(',', ':')))
        file.write("user = " + json.dumps(config, separators=(',', ':')) + "\n")
        file.close()
        config["pwd"] = "*** redacted ***"
        server.send("<html><body><h1>Configuration saved</h1><pre>" + json.dumps(config) + "</pre><p>By the time you're reading this, this device has been rebooted with the new configuration. Check your DHCP server or the configured update endpoint for the new IP address. If this configuration doesn't work, unplug the device, hold down the reset button while powering on and release after about 5 seconds to reset the configuration.</p></body></html>")
        machine.reset()
    else:
        server.send("Must specify SSID and password")
        return

def overview(request):
    server.send("")

def status(request):
    server.send("")

def control(request):
    server.send("")

def control_plug(plug_index, val):
    

led = machine.Pin("LED", machine.Pin.OUT)
plugs = [False, False, False, False, False]

server = MicroPyServer()
try:
    import user_config
    timer = machine.Timer()
    timer.init(freq=2, mode=machine.Timer.PERIODIC, callback=blink)
    run(user_config)
    server.add_route("/", overview)
    server.add_route("/status", status)
    server.add_route("/control", control)
    timer.deinit()

except:
    timer = machine.Timer()
    timer.init(freq=.5, mode=machine.Timer.PERIODIC, callback=blink)
    import initial_config
    setup_ap(initial_config)
    server.add_route("/", setup)
    server.add_route("/save_config", save_config)

server.start()

