import time
from mcculw import ul
from ALR32XX.ALR32XX import *
import tkinter as tk
import tkinter.ttk as ttk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)


degree_sign = u'\N{DEGREE SIGN}'
count = 0
board_num = 0  # DAQ board stuff, only need if more than 1
channel = (0, 1, 2, 3, 4, 5, 6, 7)
updata = [[] for x in range(len(channel))]
plotdata = [[] for x in range(len(channel))]
side_outer_temp = ul.t_in(board_num, channel[4], 0)
side_inner_temp = ul.t_in(board_num, channel[5], 0)
total_error = 0


def plot():

    for x in range(8):
        updata[x].append(ul.t_in(board_num, channel[x], 0)) # third argument is scale (c,f,k)
        plotdata[x].append(ul.t_in(board_num, channel[x], 0))
        

    # top
    plt.subplot(4, 1, 1)
    ax1.cla()
    plt.plot(updata[2][len(updata[2])-300:], 'r')
    plt.plot(updata[3][len(updata[3])-300:], 'b')
    # side
    plt.subplot(4, 1, 2)
    ax2.cla()
    plt.plot(updata[4][len(updata[4])-300:], 'r')
    plt.plot(updata[5][len(updata[5])-300:], 'b')
    # bottom
    plt.subplot(4, 1, 3)
    ax3.cla()
    plt.plot(updata[6][len(updata[6])-300:], 'r')
    plt.plot(updata[7][len(updata[7])-300:], 'b')
    # flow
    plt.subplot(4, 1, 4)
    ax4.cla()
    plt.plot(updata[0][len(updata[0])-300:], 'r')
    plt.plot(updata[1][len(updata[1])-300:], 'b')

    plt.ylabel('Temperature/C')
    plt.xlabel('Time/s')

    canvas.draw()
    root.after(1000, plot)  #todo maybe dont keep redrawing them
    #todo how often do we need to update it
    #todo could i clear and redraw after a certain amount of time
    #todo only plot last few seconds or whatever, and store the rest
    #todo or maybe remove some elements when it gets very big like every 5th list, don't really lose any data
    #todo maybe loop this shit

def run(): #todo dont start until operating temperature has been put in
    global side_outer_temp
    global side_inner_temp
    global count
    global start_time
    dt = 500
    if count == 0:
        popup()
        run_btn.config(state="disabled")
        global ps1, ps2
        ps1 = ALR32XX('ALR3206D')
        ps1.MODE("NORMAL")
        ps1.OUT('ON', 1)
        ps1.OUT('ON', 2)
        ps1.Ecrire_tension(12, 2)
        plot()
        # time.sleep(5)
        # ps2 = ALR32XX('ALR3206D')
        # ps2.MODE("NORMAL")
        # ps2.OUT("ON", 1)
        # ps2.OUT("ON", 1)
        # ps1.Ecrire_tension(5, 1)
        start_time = time.time()

    top_diff = ul.t_in(board_num, channel[3], 0) - ul.t_in(board_num, channel[2], 0)
    side_diff = ul.t_in(board_num, channel[5], 0) - ul.t_in(board_num, channel[4], 0)
    bottom_diff = ul.t_in(board_num, channel[7], 0) - ul.t_in(board_num, channel[6], 0)
    
    #My actual Comtroller

    Kp = 50
    Ki = 200
    Kd = 300

    new_side_outer_temp = ul.t_in(board_num, channel[4], 0)
    new_side_inner_temp = ul.t_in(board_num, channel[5], 0)
    Dside_diff = ((new_side_outer_temp - side_outer_temp)/(dt/1000))-((new_side_inner_temp - side_inner_temp)/(dt/1000))
    total_error =+ (side_diff*Ki*(dt/1000))

    

    P = Kp*side_diff
    I = total_error
    D = -Kd*Dside_diff
    PID = P + I + D
    print("P = "+str(P)+" + I = "+str(I)+" + D = "+str(D))
    print(str(PID))
    if PID < 0:
        v_in = 0
    elif PID > 32:
        v_in = 32
    else:
        v_in = PID

    side_outer_temp = new_side_outer_temp
    side_inner_temp = new_side_inner_temp

    # todo only turn controller on once error is pretty small
    ps1.Ecrire_tension(v_in, 1)  # sets voltage, first param v, second which channel

    # updates data boxes
    # for i in chan_data:
    #chan_data[0].config(text=str(round(ps1.Mesure_tension(1), 3)) + "V" +
    #                         "\n" + str(round(ps1.Mesure_tension(1)*ps1.Mesure_courant(1), 3)) + "W")
    # #flow_lbl.config(text=flow_rate + " m/s")
    # #core_temp_lbl.config(text= core_temp + " " + degree_sign + "C")

    duration = time.time() - start_time
    eta_lbl.config(text=str(time.strftime("%H:%M:%S", time.gmtime(duration))))

    cp = 4200
    rho = 1000
    #v_flow = 0.007/1000 * ps1.Mesure_tension() # m^3/sec
    power_lbl.config(text=str(cp*rho*0.1 *
                              (ul.t_in(board_num, channel[1], 0) - ul.t_in(board_num, channel[0], 0))) + "W")

    root.after(dt, run) #todo how long for this and for plot
    count += 1
#todo error handling

def popup():
    pop = tk.Toplevel(root)
    pop.geometry("500x200")
    pop.title("poperating temp")
    tk.Label(pop, text="GIVE ME AN OPERATING TEMPERATURE").place(x=150, y=80)
    global temptry
    temptry = tk.Entry(pop).place(x=150, y=160)
    #tk.Button(pop, text="ENTER", command=getit)

# def getit():
#     print(temptry.get()) #todo get this working


def stop():
    global ps1, ps2
    ps1.MODE("NORMAL")
    ps1.OUT('OFF', 1)
    ps1.OUT('OFF', 2)
    plt.plot(range(len(updata[4])),updata[4])
    plt.plot(range(len(updata[5])),updata[5])
    plt.show()

    # ps2.MODE("NORMAL")
    # ps2.OUT('OFF', 1)
    # ps2.OUT('OFF', 2)


def close_window():
    try:
        ps1.MODE("NORMAL")
        ps1.OUT('OFF', 1)
        ps1.OUT('OFF', 2)
    except NameError:
        print("power supply isn't connected but don't you worry your little cotton socks i will close myself anyway :)")
        root.destroy()


root = tk.Tk()  # creates main window
root.title("Calorimeter")
root.configure(bg="gray10")


for i in range(2):
    root.columnconfigure(i, weight=1, minsize=75)
    root.rowconfigure(i, weight=1, minsize=50)

frame_1 = tk.Frame(master=root, bg="gray10")
frame_1.grid(row=0, column=0, rowspan=3, columnspan=1, sticky="nw")

frame_2 = tk.Frame(master=root, bg="gray10")
frame_2.grid(row=0, column=4, rowspan=4, columnspan=1, sticky="ns")

frame_3 = tk.Frame(master=root, height=40, bg="gray10")
frame_3.grid(row=4, column=0, columnspan=5, sticky="ew"+"ns")


#############
###FRAME 1###
#############

matplotlib.rc('axes',edgecolor='w')
plot_x = 7
plot_y = 8
wall_fig1 = plt.figure(figsize=(plot_x, plot_y))
wall_fig1.set_facecolor("#1A1A1A")

#top
plt.subplot(4, 1, 1)
plt.plot(updata[2], 'r', label="TOP-OUTSIDE")
plt.plot(updata[3], 'b', label="TOP-INSIDE")
ax1=plt.gca()
plt.legend()
# side
plt.subplot(4, 1, 2)
plt.plot(updata[4], 'r', label="SIDE-OUTSIDE")
plt.plot(updata[5], 'b', label="SIDE-INSIDE")
ax2=plt.gca() #can refer to each subplot if need
plt.legend()
# bottom
plt.subplot(4, 1, 3)
plt.plot(updata[6], 'r', label="BOTTOM-OUTSIDE")
plt.plot(updata[7], 'b', label="BOTTOM-INSIDE")
ax3=plt.gca()
plt.legend()
# flow
plt.subplot(4, 1, 4)
plt.plot(updata[0], 'r', label="IN-FLOW")
plt.plot(updata[1], 'b', label="OUT-FLOW")
ax4=plt.gca()
plt.legend()

axes_vec =[ax1,ax2,ax3,ax4]
for ax in axes_vec:
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

plt.ylabel('Temperature/C')
plt.xlabel('Time/s')

canvas = FigureCanvasTkAgg(wall_fig1, master=frame_1)
canvas.get_tk_widget().pack()


#############
###FRAME 2###
#############

for i in range(2):
    frame_2.columnconfigure(i, weight=1, minsize=75)
    frame_2.rowconfigure(i, weight=1, minsize=50)


chan_labels = [0, 0, 0]
chan_data = [0, 0, 0]

for n in range(3):
    chan_labels[n] = tk.Label(text="Channel " + str(n+1),
                              fg="blue",
                              bg="white",
                              height=4,
                              width=30,
                              master=frame_2,
                              )
    chan_labels[n].pack(pady=5)

    chan_data[n] = tk.Label(text="Data " + str(n+1),
                            fg="blue",
                            bg="white",
                            height=4,
                            width=30,
                            master=frame_2,
                            )
    chan_data[n].pack(pady=5)


flow_lbl = tk.Label(text="flow rates",
                    fg="blue",
                    bg="white",
                    height=4,
                    width=30,
                    master=frame_2,
                    )
flow_lbl.pack(padx=10, pady=10)

core_temps_lbl = tk.Label(text="temp of cores",
                          fg="red",
                          bg="blue",
                          height=4,
                          width=30,
                          master=frame_2,
                          )
core_temps_lbl.pack(padx=10, pady=10)


#############
###FRAME 3###
#############

for i in range(2):
    frame_3.columnconfigure(i, weight=1, minsize=75)
    frame_3.rowconfigure(i, weight=1, minsize=50)


temp_lbl = tk.Label(text="Target Operating temperature: ",
                    fg="white",
                    bg="black",
                    width="30",
                    master=frame_3,
                    )
temp_lbl.grid(row=0, column=0, sticky="w")


run_btn = tk.Button(text="RUN",
                    fg="white",
                    bg="black",
                    height=2,
                    width=10,
                    master=frame_3,
                    command=run
                    )
run_btn.grid(row=0, column=1, sticky="w", padx=150)

stop_btn = tk.Button(text="STOP",
                     fg="white",
                     bg="red",
                     height=4,
                     width=10,
                     master=frame_3,
                     command=stop
                     )
stop_btn.grid(row=1, column=1, sticky="w", padx=150)

runtime_lbl = tk.Label(text="running time",
                       fg="white",
                       bg="blue",
                       height=2,
                       width=30,
                       master=frame_3,
                       )
runtime_lbl.grid(row=0, column=3)

eta_lbl = tk.Label(text ="eta (both in hrs/minutes and the time it will finsih)",
                   fg="white",
                   bg="blue",
                   height=2,
                   width=30,
                   master=frame_3,
                   )
eta_lbl.grid(row=1, column=3)

power_lbl = tk.Label(text="DUT power",
                     fg="blue",
                     bg="white",
                     height=2,
                     width=30,
                     master=frame_3,
                     )
power_lbl.grid(row=0, column=4, sticky="e")

root.protocol("WM_DELETE_WINDOW", close_window)
root.mainloop()  # keeps window open


#todo get the pictures, std, check boxes/ however i will choose to veryify that each wall is in steady state
#todo neaten up
