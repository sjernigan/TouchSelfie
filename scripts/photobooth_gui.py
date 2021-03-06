'''
Open source photo booth.

Kevin Osborn and Justin Shaw
WyoLum.com
'''

## imports
from tkkb import Tkkb
import time
from Tkinter import *
import tkMessageBox
import ImageTk
from mailfile import *
import custom
import Image
import config
from constants import *

## This is a simple GUI, so we allow the root singleton to do the legwork
root = Tk()
root.attributes("-fullscreen",True)

def screenshot(*args):
    import screenshot
    screenshot.snap()
root.bind('<F12>', screenshot)

### booth cam may need to present a file dialog gui.  So import after root is defined.
from boothcam import *

## set display geometry
WIDTH = 800
HEIGHT = 480
albumID_informed = False ### only show albumID customize info once

## set photo size to fit nicely in screen
SCALE = 1.8

## the countdown starting value
# COUNTDOWN1 = custom.countdown1 ### use custom.countdown1 reference directly

## put the status widget below the displayed image
STATUS_H_OFFSET = 100 ## was 210

## only accept button inputs from the AlaMode when ready
Button_enabled = False

import signal
TIMEOUT = .3 # number of seconds your want for timeout

last_snap = time.time()

tkkb = None
def launch_tkkb(*args):
    '''
    Launch on screen keyboard program called tkkb-keyboard.
    install with '$ sudo apt-get install tkkb-keyboard'
    '''
    global tkkb
    if tkkb is None:
        tkkb = Toplevel(root)
        def onEnter(*args):
            kill_tkkb()
            sendPic()
        Tkkb(tkkb, etext, onEnter=onEnter)
        etext.config(state=NORMAL)
        tkkb.wm_attributes("-topmost", 1)
        tkkb.transient(root)
        tkkb_button.config(command=kill_tkkb, text="Close KB")
        tkkb.protocol("WM_DELETE_WINDOW", kill_tkkb)
        
def kill_tkkb():
    '''
    Delete on screen keyboard program called tkkb-keyboard.
    '''
    global tkkb
    if tkkb is not None:
        tkkb.destroy()
        try:
            tkkb_button.config(command=launch_tkkb, text="Open KB")
            tkkb = None
        except:
            pass
    # can.delete("text")
    # can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="OK", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
    # can.update()
    # time.sleep(3)
    # can.delete("all")
    # im = Image.open(custom.PROC_FILENAME)
    # display_image(im)
    # #can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Touch here when ready", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
    # can.update()

    # time.sleep(10)
    # etext.delete(0, END)
    # can.delete("all")
    # im = Image.open(custom.SPLASH_FILENAME)
    # display_image(im)
    # can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Touch here when ready", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
    # can.update()
    # can.focus_set()


def interrupted(signum, frame):
    "called when serial read times out"
    print 'interrupted!'
    signal.signal(signal.SIGALRM, interrupted)

def display_image(im=None):
    '''
    display image im in GUI window
    '''
    global image_tk
    
    x,y = im.size
    x = int(x / SCALE)
    y = int(y / SCALE)

    im = im.resize((x,y));
    image_tk = ImageTk.PhotoImage(im)

    ## delete all canvas elements with "image" in the tag
    can.delete("image")
    can.create_image([(WIDTH + x) / 2 - x/2,
                      0 + y / 2], 
                     image=image_tk, 
                     tags="image")

def refresh_oauth2_credentials():
    if custom.SIGN_ME_IN:
        if setup_google():
            print 'refreshed!', custom.oauth2_refresh_period
        else:
            print 'refresh failed'
        root.after(custom.oauth2_refresh_period, refresh_oauth2_credentials)
    
def check_and_snap(force=False, countdown1=None):
    '''
    Check button status and snap a photo if button has been pressed.

    force -- take a snapshot regarless of button status
    countdown1 -- starting value for countdown timer
    '''
    global  image_tk, Button_enabled, last_snap, signed_in
    
    if countdown1 is None:
        countdown1 = custom.countdown1
    if signed_in:
        #send_button.config(state=NORMAL)
        etext.config(state=NORMAL)
    else:
        #send_button.config(state=DISABLED)
        etext.config(state=DISABLED)
    if (Button_enabled == False):
        ## inform alamode that we are ready to receive button press events
        ## ser.write('e') #enable button (not used)
        Button_enabled = True
        # can.delete("text")
        # can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Press button when ready", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
        # can.update()
        
    ## get command string from alamode
#    command = ser.readline().strip()
    command=""
    if Button_enabled and (force or command == "snap"):
        ## take a photo and display it
        Button_enabled = False
        can.delete("text")
        can.update()

        #change to take four pictures
        #im = snap(can, countdown1=countdown1, effect='None')
        im = snap(can, countdown1=countdown1, effect='Four')
        if im is not None:
            display_image(im)
            can.update()
            time.sleep(2)
            can.delete("text")
            can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Now email it to yourself", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
            can.update()
            time.sleep(1.5)
            launch_tkkb()
            if signed_in:
                if custom.albumID == 'None':
                    global albumID_informed
                    if not albumID_informed:
                        tkMessageBox.showinfo(
                            'Album ID not set',
                            'Click Customize to select albumID',
                            parent=root
                        )
                        albumID_informed = True
                else:
                    try:
                        googleUpload(custom.PROC_FILENAME)
                    except Exception, e:
                        tkMessageBox.showinfo("Upload Error", str(e) +
                                              '\nUpload Failed:%s' % e)
                    
                    # signed_in = False
            can.delete("text")
            # can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Press button when ready", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
            can.update()
    else:
        ### what command did we get?
        if command.strip():
            print command
    if not force:
        ## call this function again in 100 ms
        root.after_id = root.after(100, check_and_snap)

## for clean shutdowns
root.after_id = None
def on_close(*args, **kw):
    '''
    when window closes cancel pending root.after() call
    '''
    if root.after_id is not None:
        root.after_cancel(root.after_id)

    root.quit()
root.protocol('WM_DELETE_WINDOW', on_close)

def force_snap(countdown1=None):
    if countdown1 is None:
        countdown1 = custom.countdown1
    check_and_snap(force=True, countdown1=countdown1)



#if they enter an email address send photo. add error checking
def sendPic(*args):
    #print 'got %s' % email_addr.get()
    if email_addr.get() == "exit":
        if root.after_id is not None:
            root.after_cancel(root.after_id)
        root.quit()
    elif email_addr.get() == "customize":
        custom.customize(root)#.pack(side=LEFT)
    elif signed_in:
        try:
            sendMail(email_addr.get().strip(),
                     custom.emailSubject,
                     custom.emailMsg,
                     custom.PROC_FILENAME)
            etext.delete(0, END)
            etext.focus_set()
            kill_tkkb()
            can.delete("text")
            can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Sent", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
            can.update()
            time.sleep(0.5)

        except Exception, e:
            print 'Send Failed::', e
            can.delete("text")
            can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Send failed, bad address", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
            can.update()
            time.sleep(2)
            can.delete("all")
            im = Image.open(custom.PROC_FILENAME)
            display_image(im)
            #can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Touch here when ready", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
            can.update()

        etext.delete(0, END)
        can.delete("all")
        im = Image.open(custom.SPLASH_FILENAME)
        display_image(im)
        can.create_text(WIDTH/2, HEIGHT - STATUS_H_OFFSET, text="Touch here when ready", font=custom.CANVAS_FONT, fill=custom.FONT_COLOR, tags="text")
        can.update()
    else:
        print 'Not signed in'

#ser = findser()


#bound to text box for email
email_addr = StringVar()

w, h = root.winfo_screenwidth(), root.winfo_screenheight()

# root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (WIDTH, HEIGHT))
root.focus_set() # <-- move focus to this widget
frame = Frame(root)

#b = Button(frame, text="exit", command=on_close) 
#b.pack(side=LEFT)

#Button(frame, text="Customize", command=lambda *args: custom.customize(root)).pack(side=LEFT)
tkkb_button = Button(frame, command=launch_tkkb, text="Launch-KB")
# tkkb_button.pack(side=LEFT)
#send_button = Button(frame, text="SendEmail", command=sendPic, font=custom.BUTTON_FONT)
#send_button.pack(side=RIGHT)

## add a text entry box for email addresses
etext = Entry(frame,width=40, textvariable=email_addr, font=custom.BUTTON_FONT)
etext.pack()
frame.pack()
etext.bind('<Button-1>', launch_tkkb)

def labeled_slider(parent, label, from_, to, side, variable):
    frame = Frame(parent)
    Label(frame, text=label).pack(side=TOP)
    scale = Scale(frame, from_=from_, to=to, variable=variable, resolution=1).pack(side=TOP)
    frame.pack(side=side)
    return scale

## add a software button in case hardware button is not available
interface_frame = Frame(root)

snap_button = Button(interface_frame, text="snap", command=force_snap, font=custom.BUTTON_FONT)
# snap_button.pack(side=RIGHT) ## moved to canvas
interface_frame.pack(side=RIGHT)

## the canvas will display the images
can = Canvas(root, width=WIDTH, height=HEIGHT)
can.pack()
def snap_callback(*args):
    force_snap()
can.bind('<Button-1>', snap_callback)

## sign in to google?
if custom.SIGN_ME_IN:
    signed_in = setup_google()
else:
    signed_in = False
if not signed_in:
    #send_button.config(state=DISABLED)
    etext.config(state=DISABLED)

### take the first photo (no delay)
force_snap(countdown1=0)

### check button after waiting for 200 ms
root.after(200, check_and_snap)
if custom.SIGN_ME_IN:
    root.after(custom.oauth2_refresh_period, refresh_oauth2_credentials)
root.wm_title("Photobooth")
etext.focus_set()
# etext.bind("<Enter>", sendPic)
#on_rgb_change()
root.mainloop()


