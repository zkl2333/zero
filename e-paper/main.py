#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

import logging
from waveshare_epd import epd2in13bc
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import socket

import struct 
import smbus
 
def readVoltage(bus):
     "This function returns as float the voltage from the Raspi UPS Hat via the provided SMBus object" 
     address = 0x36 
     read = bus.read_word_data(address, 2) 
     swapped = struct.unpack("<H", struct.pack(">H", read))[0] 
     voltage = swapped * 1.25 /1000/16 
     return voltage 
def readCapacity(bus): 
    "This function returns as a float the remaining capacity of the battery connected to the Raspi UPS Hat via the provided SMBus object" 
    address = 0x36 
    read = bus.read_word_data(address, 4) 
    swapped = struct.unpack("<H", struct.pack(">H", read))[0] 
    capacity = swapped/256 
    return capacity 

bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1) 

logging.basicConfig(level=logging.DEBUG)

_local_ip = None

def get_ip():
    """
    这个方法是目前见过最优雅获取本机服务器的IP方法了。没有任何的依赖，也没有去猜测机器上的网络设备信息。
    而且是利用 UDP 协议来实现的，生成一个UDP包，把自己的 IP 放如到 UDP 协议头中，然后从UDP包中获取本机的IP。
    这个方法并不会真实的向外部发包，所以用抓包工具是看不到的。但是会申请一个 UDP 的端口，所以如果经常调用也会比较耗时的，这里如果需要可以将查询到的IP给缓存起来，性能可以获得很大提升。
    :return:
    """
    global _local_ip
    s = None
    try:
        if not _local_ip:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            _local_ip = s.getsockname()[0]
        return _local_ip
    except:
        return u"无网络"
    finally:
        if s:
            s.close()
  
try:
    logging.info("epd2in13bc Demo")
    
    epd = epd2in13bc.EPD()
    logging.info("init and Clear")
    epd.init()
    time.sleep(1)
    
    # Drawing on the image
    logging.info("Drawing")    
    font20 = ImageFont.truetype('/home/pi/workspace/e-paper/pic/Font.ttc', 20)
    font18 = ImageFont.truetype('/home/pi/workspace/e-paper/pic/Font.ttc', 18)
    
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...") 
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    HRYimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image  
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)
    drawblack.text((10, 0), u"你好 Vincent", font = font20, fill = 0)
    drawblack.text((10, 20), u"当前IP:"+get_ip(), font = font20, fill = 0)
    drawblack.text((10, 80), u"当前电量:"+ str(round(readCapacity(bus), 2)) + "%", font = font20, fill = 0)

    epd.display(epd.getbuffer(HBlackimage),epd.getbuffer(HRYimage))
    time.sleep(2)
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13bc.epdconfig.module_exit()
    exit()

