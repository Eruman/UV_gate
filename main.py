import machine, time
import neopixel
import utime
import ds1302
from struct import *

def play_sound(pin, frequency, duration):
    buzzer = machine.PWM(machine.Pin(pin))
    buzzer.freq(frequency)
    buzzer.duty_u16(512)  
    utime.sleep_ms(duration)
    buzzer.duty_u16(0)  

p = machine.Pin(7, machine.Pin.OUT)
k = 16
n = neopixel.NeoPixel(p, k)

def rgb(color = 1):
    for i in range(k):
        if color == 0: n[i] = (0, 0, 0)
        if color == 1: n[i] = (i * 2, 0, 0)
        if color == 2: n[i] = (0, i * 2, 0)
        if color == 3: n[i] = (0, 0, i * 2)
    n.write()

button_1 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
button_2 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
relay    = machine.Pin(2, machine.Pin.OUT)
pir      = machine.Pin(6, machine.Pin.IN)
state    = 0
timer    = 0

def syrene():
    for i in range(500,1000,10):
        play_sound(14, i, 15)

#                 (           clk,            dio,             cs)
ds = ds1302.DS1302(machine.Pin(5),machine.Pin(18),machine.Pin(19))

def save( data ):
    a = list(pack(">L", data))
    for i in range(len(a)):
        ds.ram(i+10, a[i])
    
def load():
    b = bytes([ds.ram(i) for i in range(10,14)])
    return unpack(">L", b)[0]

#save(8000*60*60) #Сохранить число секунд ресурса лампы
res = load()                   #Загрузить значение ресурса лампы
print("Текущий ресурс лампы:", res,"сек, ", int(res/360)/10, "ч")    

syrene()
start_time = utime.ticks_ms()

while True:
    #print(state, timer)
    if pir.value() == 1:
        state = 2
        timer = 50

    if button_1.value() == 1:
        state = 1
        timer = 50
     
    if button_2.value() == 1:
        state = 1
        timer = 50
        
    if timer > 0:
        timer = timer - 1
   
    #----------------------------------------------------- автомат
    if timer == 0:
        if state == 3:
            state = 0
            end_time = utime.ticks_ms()
            execution_time = utime.ticks_diff(end_time, start_time)
            print(int(execution_time/1000),"сек время исполнения.")
            res = load()                   #Загрузить значение ресурса лампы
            print("Текущий ресурс лампы:", res,"сек ", int(res/360)/10, "ч")    
        
        if state == 1 or state == 2:
            start_time = utime.ticks_ms()
            state = 3
            timer = int(5 * 60 * 9.7)  #  5 мин
            if load() < 8000*1200:
                timer = int( timer / 5 * 6 )
            elif load() < 8000*2400:
                timer = int( timer / 5 * 5.5 )
            
    if state == 0:
        relay.value(0)
        rgb(0)

    if state == 1 or state == 2: 
        relay.value(0)
        rgb(2)
        play_sound(14, 1000 - timer * 10, 50)
    
    if state == 3:
        relay.value(1)
        rgb(1)
        if timer%10 == 0:
            res = load()
            #print(res)
            if res < 1000:
                print("Ресурс лампы исчерпан.")
                while True:
                    relay.value(0)
                    syrene()
                    rgb(3)
                    time.sleep(.5)
                    rgb(0)
                    time.sleep(1)                    
            save(res - 1)
            #print(timer)
        time.sleep(.05) 
    
    time.sleep(.05)
