import json
import os
import time
import threading
import tkinter as tk
from tkinter.constants import CENTER, N, NE, RAISED, SUNKEN
import webbrowser
from tkinter import ttk, Menu, filedialog, DISABLED, NORMAL,WORD, RIGHT,Y, NW
from PIL import ImageTk, Image

from savelocs import VERSIONFILE,USERFILE,ASSETSFILE,LOGO,LOGOJPG,SAVEDRIVE,BACKGROUND,INFOSYMBOL 

VERSION="v.2.5"
CREDITS="\t\t             Credits\
            \n\nProgramers: Ethan de Leon, Wilfred Nono \
            \n\nLead Designer: Ethan de Leon\
            \n\nDebuggers: Allen Poniente\
            \n\nExecutive Producer: Russel Ocampo\
            \n\nInitial Release Date: September 28, 2021\
            \n\nLatest Update Release: September 28, 2021\
            \n\nThis software was made for the purposes of Ocampo-Esta Corporation only. Any usesage of this program outside of the company workplace is strictly prohibited.\
            "

class Program:
    programlist=['Home','File Search','Database Input','Multi-Drawing Input',
        'Quality Checker','Drawing Organizer',
        'Ampacity','Voltage Clearances','Settings']
    adminlist=['admin','ethan','wilfred']
    def __init__(self,master,user,width=350,height=390,programtitle="Program",
        personalize=True,menu=True,logo=True, bgpattern=BACKGROUND,
        screen_center=False,animation=True,toplevel=False):

        self.master=master
        self.user=user
        self.w_width=width
        self.w_height=height

        if toplevel==False:
            if menu:
                Program.add_menu(self.master,user,self.programtitle)
                
            master.title(programtitle)
            if screen_center:
                master.geometry('%dx%d+%d+%d'%(self.w_width,self.w_height,(master.winfo_screenwidth()-self.w_width)/2,(master.winfo_screenheight()-self.w_height)/2-50))
            else:
                master.geometry('%dx%d'%(self.w_width,self.w_height))
        else:
            self.master=tk.Toplevel()
            self.master.resizable(0,0)
        master.minsize(width,height)
        master.maxsize(1920,1080)
        master.iconbitmap(LOGO)
        
        self.b_frame=tk.Frame(master,bg='black')
        self.frame=tk.Frame(master,bg=self.bgcolor,width=width,height=height)
        
        Program.bgpatterning(self,master,imgfile=bgpattern)
        
        
        Program.cornorLogo(self,master)

        Program.fullscreenMode(self,master)
        self.b_frame_buffer=10
        if animation:
            self.loadtrigger=False
            openingthread=threading.Thread(daemon=True,target=self.opening_sequence).start()
        else:
            
            self.frame.place(width=width,height=height, relx=.5, rely=.5,anchor=CENTER)
            self.b_frame.place(width=width+self.b_frame_buffer,height=height+self.b_frame_buffer, relx=.5, rely=.5,anchor=CENTER)
    
    def checkupdate(master):
        f=open(VERSIONFILE,"r")
        currentVersion=f.readline()
        if currentVersion == VERSION:
            return
        
        msg=tk.messagebox.showinfo("UPDATE","An update for this program has been found. The program will now close for installation.")
        master.destroy()
        exit()

    def totalUnbind(widget):
        widget.unbind("<F11>")
        widget.unbind("<Escape>")
        widget.unbind("<Configure>")
        widget.unbind("<MouseWheel>")
        widget.unbind("<Shift-MouseWheel>")
        widget.unbind("<KeyPress-Up>")
        widget.unbind("<space>")
        widget.unbind("<FocusIn>")
        widget.unbind("<FocusOut>")
        widget.unbind("<Enter>")
        widget.unbind("<Leave>")
        widget.unbind("<KeyPress-Right>")
        widget.unbind("<KeyRelease-Right>")
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Shift-MouseWheel>")
        
    def switchprogram(master,user, Class=None,classname=None,startup=False,timesheet=None):
        for child in master.winfo_children():
            #wont delete toplevel processes
            if child.winfo_class()=='Toplevel':
                continue
            Program.totalUnbind(child)
            child.destroy()
        Program.totalUnbind(master)

        if classname!=None:
            if classname=='Home':
                from home import Home
                program=Home(master,user,startup=startup)
                return
            # region Drawings
            #elif classname=='DLInput':
            #    from DwgDatabase.drawinglist_input import DLInput
            #    Class=DLInput
            elif classname=='DBinput':
                from DwgDatabase.insert_drawing import InputDWG
                Class=InputDWG
            elif classname=='DBSearch':
                from DwgDatabase.search_drawing import DrawingSearch
                Class=DrawingSearch
            # endregion
            # region References
            elif classname=='Ampacity':
                from References.ampacity import Ampacity
                Class=Ampacity
            elif classname=='voltageClearance':
                from References.voltage_clearance import voltageClearance
                Class=voltageClearance
            # endregion
            # region Tools
            elif classname=='Settings':
                from account.oec_settings import Settings
                Class=Settings
            elif classname=='QualityChecker':
                from tools.quality_checker import QualityChecker
                Class=QualityChecker
            elif classname=='DLOrganize':
                from tools.drawinglist_organizer import DLOrganize
                Class=DLOrganize
            elif classname=='QuickBind':
                from tools.quickbind import QuickBind
                Class=QuickBind
            # endregion
            # region Project Database
            elif classname=='PDHome':
                from ProjectDatabase.PDHome import PDHome
                Class=PDHome
            elif classname=='fourWeekAhead':
                from ProjectDatabase.fourWeekAhead import fourWeekAhead
                Class=fourWeekAhead
            elif classname=='addProject':
                from ProjectDatabase.addproject import addProject
                Class=addProject
            elif classname=='ProjectList':
                from ProjectDatabase.projectlist import ProjectList
                program=ProjectList(master,user,view='all')
                return
            elif classname=='ProjectView':
                from ProjectDatabase.projectlist import ProjectList
                program=ProjectList(master,user,view='user')
                return
            elif classname=='StatusBudget':
                from ProjectDatabase.statuswork import StatusWork
                program=StatusWork(master,user,view='budget')
                return
            elif classname=='StatusWork':
                from ProjectDatabase.statuswork import StatusWork
                program=StatusWork(master,user,view='work')
                return
            elif classname=='StatusProject':
                from ProjectDatabase.statuswork import StatusWork
                program=StatusWork(master,user,view='whole')
                return
            elif classname=='SubstationList':
                from ProjectDatabase.substationlist import SubstationList
                Class=SubstationList
            # endregion
            # region Reports
            elif classname=='TimesheetList':
                from ReportForms.timesheetlist import TimesheetList
                Class=TimesheetList
            
            elif classname=='Timesheet':
                from ReportForms.timesheet import Timesheet
                program=Timesheet(master,user,timesheet=timesheet)
                return
            # endregion
            elif classname=='AdminAccess':
                from account.oec_user_login import AdminAccess
                Class=AdminAccess

        program=Class(master,user)
        return

    def add_menu(master,user, dontadd):
        from tools.quickbind import QuickBind

        menubar=Menu(master)
        account=Menu(menubar, tearoff=0)
        program=Menu(menubar, tearoff=0)
        references=Menu(menubar,tearoff=0)
        menubar.add_command(label='Home',command=lambda m=master: Program.switchprogram(m,user,classname='Home'))
        menubar.add_cascade(label='Database',menu=program)
        menubar.add_cascade(label='References',menu=references)
        menubar.add_cascade(label='Account',menu=account)

        if dontadd!='File Search':
            program.add_command(label='File Search',command=lambda m=master: Program.switchprogram(m,user,classname="DBSearch"))
        if dontadd!='Database Input':
            program.add_command(label='Database Input',command=lambda m=master: Program.switchprogram(m,user,classname="DBinput"))
        if dontadd!='Multi-Drawing Input':
            program.add_command(label='Multi-Drawing Input',command=lambda m=master: Program.switchprogram(m,user,classname="DLInput"))
        
        references.add_command(label='Calculator',command=lambda m='https://www.desmos.com/scientific': webbrowser.open(m))
        references.add_command(label='Multi-Printing',command=Program.multiprint)
        references.add_command(label='Quick Binder', command=lambda m=user:QuickBind(m))
        references.add_separator()
        if dontadd!='Quality Checker':
            references.add_command(label='Quality Checker',command=lambda m=master: Program.switchprogram(m,user,classname="QualityChecker"))
        if dontadd!='Drawing List Organizer':
            references.add_command(label='Drawing List Organizer',command=lambda m=master: Program.switchprogram(m,user,classname="DLOrganize"))
        if dontadd!='Ampacity':
            references.add_command(label='Ampacity',command=lambda m=master: Program.switchprogram(m,user,classname="Ampacity"))
        if dontadd!='voltageClearance':
            references.add_command(label='Voltage Clearances',command=lambda m=master: Program.switchprogram(m,user,classname="voltageClearance"))
        
        #if dontadd!='CBD':
        #    references.add_command(label='CBD',command=lambda m=master: Program.switchprogram(m,CBD))
        references.add_separator()
        feExam=Menu(references,tearoff=0)
        feExam.add_command(label='FE Handbook',command=lambda m=r'G:\PROFESSIONAL LICENCE\STANDARDS\FE EXAM\fe-handbook-10-1.pdf':os.startfile(m))
        references.add_cascade(label='FE Exam Prep',menu=feExam)
        references.add_separator()
        #references.add_command(label="Credits",command=lambda m=master: Program.popuptextwindow(DB,"Credits",CREDITS,'blue'))
        
        account.add_command(label=user,command=None)
        if dontadd!='Settings':
            account.add_separator()
            account.add_command(label='Settings',command=lambda m=master: Program.switchprogram(m,user,classname="Settings"))
        if user in Program.adminlist:
            
            account.add_command(label='ADMIN ACCESS',command=lambda m=master: Program.switchprogram(m,user, classname="AdminAccess"))
            account.add_separator()
            account.add_command(label='Pyoro', command=lambda m=r"O:\pythonprograms\Database\Assets\Pyoro-master\Pyoro.exe":os.startfile(m))
        account.add_separator()
        account.add_command(label='Log Out', command=lambda m=master: Program.logout(m,user,menubar))
        account.add_command(label='Exit',command=lambda m=master: Program.exitconfirm(m,user))

        master.config(menu=menubar)

    def logout(master,user,menu=None):
        msg=tk.messagebox.askyesno("Log Out?","Are you sure you want to log out?")
        if msg:
            if menu!=None:
                menu.destroy()
            from account.oec_user_login import UserLogin
            user=None
            Program.switchprogram(master,user,UserLogin)

    def exitconfirm(master,user):
        msg=tk.messagebox.askyesno("Quit?","Are you sure you want to quit?")
        if msg:
            master.destroy()

    def popuptextwindow(title,texts,bgcolor):
        resultswindow=tk.Toplevel()
        resultswindow.grab_set()
        resultswindow.wm_title(title)
        w_width=500
        w_height=600
        resultswindow.geometry('%dx%d'%(w_width,w_height))
        resultswindow.resizable(0,0)
        resultswindow.iconbitmap(LOGO)
        bgcolorset=bgcolor
        if bgcolor=='white':
            bgcolorset='gray90'
        resultswindow.configure(bg=bgcolorset)

        scrollbarWidth=20
        boarder=20

        resultbox=tk.Text(resultswindow,font=('helvetica',12),wrap=WORD)
        resultbox.place(x=10,y=10,width=w_width-boarder-scrollbarWidth,height=w_height-boarder)
        resultbox.insert('1.0',texts)
        resultbox.configure(state=DISABLED)
        if title=="Credits":
            resultswindow.configure(bg="purple")
            img=Image.open(LOGOJPG)
            img_rsize=img.resize((140,100), Image.ANTIALIAS)
            img=ImageTk.PhotoImage(img_rsize)
            logolabel=tk.Label(resultswindow,image=img)
            logolabel.place(relx=.46,rely=.65,anchor=CENTER)

        scrollbar=ttk.Scrollbar(resultswindow, orient='vertical',command=resultbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        resultbox['yscrollcommand']=scrollbar.set

    def bgpatterning(self,master,imgfile=BACKGROUND):
        bgpattern=Image.open(imgfile)
        bgpattern=bgpattern.resize((master.winfo_screenwidth(),master.winfo_screenheight()), Image.ANTIALIAS)
        bgpattern=ImageTk.PhotoImage(bgpattern)
        bgpatternlabel=tk.Label(master,image=bgpattern)
        bgpatternlabel.lower()
        bgpatternlabel.place(relwidth=1,relheight=1,relx=0.5,rely=0,anchor=N)
        self.bgpattern = bgpattern
        return bgpatternlabel

    def cornorLogo(self,master,x=0,y=0,resize=(65,40),anchor=NW):
        img=Image.open(LOGOJPG)
        img_rsize=img.resize(resize, Image.ANTIALIAS)
        self.img=ImageTk.PhotoImage(img_rsize)
        self.logolabel=tk.Label(master,image=self.img, relief=RAISED)
        self.logolabel.place(x=x,y=y,anchor=anchor)

    def programInfo(self, master, info, place_x, place_y):
        self.infoimg=Image.open(INFOSYMBOL)
        self.infoimg=self.infoimg.resize((20,20))
        self.infoimg=ImageTk.PhotoImage(self.infoimg)
        self.infolabel=tk.Label(master, image=self.infoimg, cursor='hand2', bg=self.bgcolor)
        self.infolabel.place(x=place_x,y=place_y,anchor=NE)
        #self.infolabel.bind("<Button-1>",lambda m=self: DB.popuptextwindow(m,self.programtitle, info, self.bgcolor))

    def multiprint():
        pdf=filedialog.askopenfilenames(title="Please Select the Associated Files")
        if pdf!="":
            from widgets.printer import Printing
            Printing(pdf)
    
    def opening_sequence(self):
        #while not self.loadtrigger:
        #    pass
        self.master.configure(bg='purple4')
        b_pos=0+self.b_frame_buffer
        pos=0
        openspd=15
        while b_pos<self.w_height+self.b_frame_buffer:
            pos+=openspd
            b_pos+=openspd
            if pos>self.w_height:pos=self.w_height
            if b_pos>self.w_height+self.b_frame_buffer:b_pos=self.w_height+self.b_frame_buffer
            self.frame.place(width=self.w_width,height=pos, relx=.5, y=(self.master.winfo_height()-self.w_height)/2,anchor=N)
            self.b_frame.place(width=self.w_width+self.b_frame_buffer,height=b_pos, relx=.5, y=(self.master.winfo_height()-self.w_height-self.b_frame_buffer)/2,anchor=N)
            self.master.update()
            time.sleep(.001)

        self.master.bind("<Configure>",self.on_resize)

    def on_resize(self,event):
        self.frame.place(width=self.w_width,height=self.w_height, relx=.5, y=(self.master.winfo_height()-self.w_height)/2,anchor=N)
        self.b_frame.place(width=self.w_width+self.b_frame_buffer,height=self.w_height+self.b_frame_buffer, relx=.5, y=(self.master.winfo_height()-self.w_height-self.b_frame_buffer)/2,anchor=N)
        return

    def fullscreenMode(Class,master):
        Class.fullScreenState=False
        master.bind("<F11>", lambda m=True: Program.toggleFullScreen(Class,m))
        master.bind('<Escape>', lambda m=True: Program.quitFullScreen(Class,m))

    def toggleFullScreen(self,event):
        print(event)
        self.fullScreenState=True
        self.master.attributes('-fullscreen',self.fullScreenState)

    def quitFullScreen(self,event):
        self.fullScreenState=False
        self.master.attributes('-fullscreen',self.fullScreenState)