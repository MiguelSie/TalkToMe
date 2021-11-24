import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
import pyaudio

HOST = "127.0.0.1"
PORT = 9090

class Client:
    
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        
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

        
        msg = tkinter.Tk()
        msg.withdraw()
        
        self.nickname = simpledialog.askstring("Nickname", "Ingresa tu nickname: ", parent = msg)
        
        self.gui_done = False    
        self.running = True
        
        gui_thread = threading.Thread(target = self.gui_loop)
        receive_thread = threading.Thread(target = self.receive)
        audio_thread = threading.Thread(target = self.sendAudio)
        
        gui_thread.start()
        receive_thread.start()
        audio_thread.start()

        
    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.config(bg = "lightgray")
        
        self.chat_label = tkinter.Label(self.win, text = "Chat", bg = "lightgray")
        self.chat_label.config(font = ("Arial", 12))
        self.chat_label.pack(padx = 20, pady = 5)
        
        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx = 20, pady = 5)
        self.text_area.insert("end", self.nickname + " se ha conectado al chat\n")
        self.text_area.config(state="disabled", font = ("Arial", 12))
        
        self.msg_label = tkinter.Label(self.win, text = "Mensaje: ", bg = "lightgray")
        self.msg_label.config(font = ("Arial", 12))
        self.msg_label.pack(padx = 20, pady = 5)
        
        self.input_area = tkinter.Text(self.win, height=3)
        self.msg_label.config(font = ("Arial", 12))
        self.input_area.pack(padx = 20, pady = 5)
        
        self.send_button = tkinter.Button(self.win, text = "Enviar", command = self.write)
        self.send_button.config(font = ("Arial", 12))
        self.send_button.pack(padx = 20, pady = 5)
        
        self.audio_button = tkinter.Button(self.win, text = "Audio")
        self.audio_button.config(font = ("Arial", 12))
        self.audio_button.pack(padx = 20, pady = 5)
        
        self.gui_done = True
        
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        
        self.win.mainloop()
        
    def sendAudio(self):
        while True:
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
                else:
                    self.writeSelf(message)
            except:
                self.output_stream.write(message)
            
    def writeSelf(self, message):
        if self.gui_done:
            self.text_area.config(state="normal")
            self.text_area.insert("end", message)
            self.text_area.yview("end")
            self.text_area.config(state="disabled")
            
client = Client(HOST, PORT)