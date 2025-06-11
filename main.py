import picodisplay as display
import time
import math
import gc
import machine
from micropython import const

gc.enable()
backlight = 0.7
plusDays = 0
change = 0

def circle(xpos0, ypos0, rad):
    x = rad - 1
    y = 0
    dx = 1
    dy = 1
    err = dx - (rad << 1)
    while x >= y:
        display.pixel(xpos0 + x, ypos0 + y)
        display.pixel(xpos0 + y, ypos0 + x)
        display.pixel(xpos0 - y, ypos0 + x)
        display.pixel(xpos0 - x, ypos0 + y)
        display.pixel(xpos0 - x, ypos0 - y)
        display.pixel(xpos0 - y, ypos0 - x)
        display.pixel(xpos0 + y, ypos0 - x)
        display.pixel(xpos0 + x, ypos0 - y)
        if err <= 0:
            y += 1
            err += dy
            dy += 2
        if err > 0:
            x -= 1
            dx += 2
            err += dx - (rad << 1)


def check_for_buttons():
    global backlight
    global plusDays
    global change
    if display.is_pressed(display.BUTTON_X):
        backlight += 0.05
        if backlight > 1:
            backlight = 1
        display.set_backlight(backlight)
    elif display.is_pressed(display.BUTTON_Y):
        backlight -= 0.05
        if backlight < 0:
            backlight = 0
        display.set_backlight(backlight)
    if display.is_pressed(display.BUTTON_A) and display.is_pressed(display.BUTTON_B):
        plusDays = 0
        change = 2
    elif display.is_pressed(display.BUTTON_A):
        plusDays += 86400
        change = 3
    elif display.is_pressed(display.BUTTON_B):
        plusDays -= 86400
        change = 3


def set_internal_time(utc_time):
    
# For the United States:
#   Valid for years 1900 to 2006, though DST wasn't adopted until the 1950s-1960s.
#   Begin DST: Sunday April (2+6*y-y/4) mod 7+1
#   End DST: Sunday October (31-(y*5/4+1) mod 7)

#   2007 and after:
#   Begin DST: Sunday March 14 - (1 + y*5/4) mod 7
#   End DST: Sunday November 7 - (1 + y*5/4) mod 7;

    year = time.localtime(utc_time)[0]  # Get current year
    
    # Time of March change to DST
    HHMarch   = time.mktime((year,3 ,(14-(int(1+year/5+4))%7),2,0,0,0,0,0))
    # Time of October change to EST
    HHOctober = time.mktime((year,11,(07-(int(1+year/5+4))%7),2,0,0,0,0,0))

    if utc_time < HHMarch :             # Are we before 2nd Sunday of March
        local_time=utc_time-5*3600      # EST: UTC-5H
    elif utc_time < HHOctober :         # Are we before last Sunday of October
        local_time=utc_time-4*3600      # DST: UTC-4H
    else:                               # We are after last Sunday of October
        local_time=utc_time-5*3600      # EST: UTC-5H    
    
    rtc_base_mem = const(0x4005c000)
    atomic_bitmask_set = const(0x2000)
    (year, month, day, hour, minute, second, wday, yday) = time.localtime(local_time)
    machine.mem32[rtc_base_mem + 4] = (year << 12) | (month << 8) | day
    machine.mem32[rtc_base_mem + 8] = ((hour << 16) | (minute << 8) | second) | (((wday + 1) % 7) << 24)
    machine.mem32[rtc_base_mem + atomic_bitmask_set + 0xc] = 0x10


def main():
    global change
    import planets
    import ds3231
    from pluto import Pluto
    ds = ds3231.ds3231()
    
    # Ensure that ds3231 time is UTC - GMT time - set_internal_time
    # will apply EST/DST offset 
    set_internal_time(ds.read_time())

    def draw_planets(HEIGHT, ti):
        PL_CENTER = (68, int(HEIGHT / 2))
        planets_dict = planets.coordinates(ti[0], ti[1], ti[2], ti[3], ti[4])
        # t = time.ticks_ms()
        display.set_pen(255, 255, 0)
        display.circle(int(PL_CENTER[0]), int(PL_CENTER[1]), 4)
        for i, el in enumerate(planets_dict):
            r = 8 * (i + 1) + 2
            display.set_pen(40, 40, 40)
            circle(PL_CENTER[0], PL_CENTER[1], r)
            feta = math.atan2(el[0], el[1])
            coordinates = (r * math.sin(feta), r * math.cos(feta))
            coordinates = (coordinates[0] + PL_CENTER[0], HEIGHT - (coordinates[1] + PL_CENTER[1]))
            for ar in range(0, len(planets.planets_a[i][0]), 5):
                x = planets.planets_a[i][0][ar] - 50 + coordinates[0]
                y = planets.planets_a[i][0][ar + 1] - 50 + coordinates[1]
                if x >= 0 and y >= 0:
                    display.set_pen(planets.planets_a[i][0][ar + 2], planets.planets_a[i][0][ar + 3],
                                    planets.planets_a[i][0][ar + 4])
                    display.pixel(int(x), int(y))
        # print("draw = " + str(time.ticks_diff(t, time.ticks_ms())))

    w = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    buf = bytearray(display.get_width() * display.get_height() * 2)
    display.init(buf)
    display.set_pen(0, 0, 0)
    display.clear()
    display.update()
    display.set_backlight(0.7)
    gc.collect()
    # _thread.start_new_thread(thread2, ())

    # WIDTH = const(240)
    HEIGHT = const(135)

    mi = -1
    pl = Pluto(display)

    seconds_absolute = time.time()
    ti = time.localtime(seconds_absolute + plusDays)
    da = ti[2]

    draw_planets(HEIGHT, ti)
    start_int = time.ticks_ms()
    while True:
        ticks_dif = time.ticks_diff(time.ticks_ms(), start_int)
        if ticks_dif >= 1000 or time.time() != seconds_absolute:
            seconds_absolute = time.time()
            ti = time.localtime(seconds_absolute + plusDays)
            start_int = time.ticks_ms()
            ticks_dif = 0
        if change > 0:
            ti = time.localtime(seconds_absolute + plusDays)
        if da != ti[2]:
            da = ti[2]
            change = 3

        if change > 0:
            if change == 1:
                display.set_pen(0, 0, 0)
                display.clear()
                draw_planets(HEIGHT, ti)
                if plusDays > 0:
                    display.set_led(0, 50, 0)
                elif plusDays < 0:
                    display.set_led(50, 0, 0)
                else:
                    display.set_led(0, 0, 0)
                change = 0
            else:
                change -= 1

        display.set_pen(0, 0, 0)
        display.rectangle(140, 0, 100, HEIGHT)
        display.rectangle(130, 0, 110, 35)
        display.rectangle(130, 93, 110, HEIGHT - 93)

        # Every minute reset Pluto
        if mi != ti[4]:
            mi = ti[4]
            pl.reset()
            # ds3231 time is UTC - GMT time - set_internal_time
            # will apply EST/DST offset when appropriate
            set_internal_time(ds.read_time())
            
        pl.step(ti[5], ticks_dif)
        pl.draw()

        display.set_pen(244, 170, 30)
        display.text("%02d %s %d " % (ti[2], m[ti[1] - 1], ti[0]), 132, 7, 70, 2)
        display.set_pen(65, 129, 50)
        display.text(w[ti[6]], 135, 93, 99, 2)
        display.set_pen(130, 255, 100)
        display.text("%02d:%02d" % (ti[3], ti[4]), 132, 105, 99, 4)
        display.update()
        check_for_buttons()
        time.sleep(0.01)

time.sleep(0.5)
main()