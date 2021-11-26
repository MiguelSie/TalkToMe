import socket
import threading
import tkinter
from tkinter import *
import tkinter.scrolledtext
import pyaudio

PORT = 9090


class Client:
    
    def __init__(self, host, port, nickname):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
        except socket.gaierror:
            print("Ingrese una IP correcta")
            exit(1)
            
        self.nickname = nickname
        
        self.p = pyaudio.PyAudio()
        
        self.Format = pyaudio.paInt16
        self.Chunks = 4096
        self.Channels = 1
        self.Rate = 48000
        
        self.input_stream = self.p.open(format = self.Format,
                                        channels = self.Channels,
                                        rate = self.Rate,
                                        input = True,
                                        frames_per_buffer = self.Chunks)
        
        self.output_stream = self.p.open(format = self.Format,
                                         channels = self.Channels,
                                         rate = self.Rate,
                                         output = True,
                                         frames_per_buffer=self.Chunks)

        
        
        self.gui_done = False    
        self.running = True
        self.mute = False
        
        self.gui_thread = threading.Thread(target = self.gui_loop)
        self.receive_thread = threading.Thread(target = self.receive)
        self.audio_thread = threading.Thread(target = self.sendAudio)
        
        self.gui_thread.start()
        self.receive_thread.start()
        self.audio_thread.start()
        
        
    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.config(bg = "#00BFFF" )
        self.win.title("TalkToMe")
        
        self.chat_label = tkinter.Label(self.win, text = "Chat", bg = "#00BFFF")
        self.chat_label.config(font = ("Arial", 12))
        self.chat_label.pack(padx = 20, pady = 5)
        
        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx = 20, pady = 5)
        self.text_area.insert("end", self.nickname + " se ha conectado al chat\n")
        self.text_area.config(state="disabled", font = ("Arial", 12))
        
        self.msg_label = tkinter.Label(self.win, text = "Mensaje: ", bg = "#00BFFF")
        self.msg_label.config(font = ("Arial", 12))
        self.msg_label.pack(padx = 20, pady = 5)
        
        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.config(font = ("Arial", 12))
        self.input_area.pack(padx = 20, pady = 5)
        
        
        self.send_button = tkinter.Button(self.win,
                                          bg = "white", 
                                          text = "Enviar", 
                                          command = self.write,
                                          borderwidth=0,
                                          highlightthickness=0,
                                          relief="flat")
        self.send_button.pack(padx = 20, pady = 5)
        self.send_button.config(font = ("Arial", 12))
        self.send_button.pack(padx = 20, pady = 5)
        

        self.audio_button = tkinter.Button(self.win, 
                                           bg="white",
                                           text="Audio On",
                                           command = self.toggleAudio,
                                           borderwidth=0,
                                           highlightthickness=0,
                                           relief="flat")
        self.audio_button.config(font = ("Arial", 12))
        self.audio_button.pack(padx = 20, pady = 5)
        
        self.users_button = tkinter.Button(self.win, 
                                           bg="white",
                                           text="Participantes",
                                           command = self.showUsers,
                                           borderwidth=0,
                                           highlightthickness=0,
                                           relief="flat")
        self.users_button.config(font = ("Arial", 12))
        self.users_button.pack(padx = 20, pady = 5)
        
        self.gui_done = True
        
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        
        self.win.mainloop()
        
    def showUsers(self):
        self.sock.send("showParticipantes".encode("utf-8"))
        
        
    def toggleAudio(self):
        if self.mute == False:
            self.mute = True
            self.audio_button.config(text = "Audio Off")
        else:
            self.mute = False
            self.audio_button.config(text = "Audio On")
            
        
    def sendAudio(self):
        while True:
            if self.mute == False:
                try:
                    message = self.input_stream.read(self.Chunks)
                    self.sock.send(message)
                except:
                    break
        
    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode("utf-8"))
        self.input_area.delete("1.0", "end")
        self.writeSelf(message)
            
    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        self.input_stream.close()
        self.output_stream.close()
        self.p.terminate()
        exit(0)        
    
    def receive(self):
        while self.running:
            message = self.sock.recv(self.Chunks)
            try:
                message = message.decode("utf-8")
                if message == "Nickname":
                    self.sock.send(self.nickname.encode("utf-8"))
                elif message.find("@") == 0:
                    self.writeSelf(message+"\n")
                else:
                    self.writeSelf(message)
            except ConnectionAbortedError:
                self.sock.close()
            except:
                self.output_stream.write(message)
            
    def writeSelf(self, message):
        if self.gui_done:
            self.text_area.config(state="normal")
            self.text_area.insert("end", message)
            self.text_area.yview("end")
            self.text_area.config(state="disabled")
            
    
            
def openChat():
    nickname = nickname_Input.get()
    host = host_Input.get()
    client = Client(host, PORT, nickname)
    window.destroy()
            
window = Tk()
window.title("TalkToMe")
window.geometry("900x465")
window.configure(bg = "#FFFFFF")
canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 465,
    width = 900,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.place(x = 0, y = 0)

background_img = PhotoImage(file = f"background.png")
background = canvas.create_image(
    450.0, 232.5,
    image=background_img)

img0LB = PhotoImage(file = f"img0.png")
login_Button = Button(
    image = img0LB,
    borderwidth = 0,
    highlightthickness = 0,
    command = openChat,
    relief = "flat")

login_Button.place(
    x = 366, y = 400,
    width = 168,
    height = 42)

nickname_Input_img = PhotoImage(file = f"img_textBox0.png")
nickname_Input_bg = canvas.create_image(
    450.0, 222.5,
    image = nickname_Input_img)

nickname_Input = Entry(
    bd = 0,
    bg = "#fef7f7",
    highlightthickness = 0)

nickname_Input.place(
    x = 250.0, y = 205,
    width = 400.0,
    height = 33)

host_Input_img = PhotoImage(file = f"img_textBox1.png")
host_Input_bg = canvas.create_image(
    450.0, 345.5,
    image = host_Input_img)

host_Input = Entry(
    bd = 0,
    bg = "#fef7f7",
    highlightthickness = 0)

host_Input.place(
    x = 250.0, y = 328,
    width = 400.0,
    height = 33)

window.resizable(False, False)
window.mainloop()

