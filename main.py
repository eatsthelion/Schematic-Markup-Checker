import os
import pathlib
import pandas as pd
import tkinter as tk
import cv2

from tkinter import LEFT, W, NS, EW, NORMAL, DISABLED, CENTER, filedialog
from PIL import Image, ImageChops, ImageTk

from markup_checker import MarkupChecker

class MarkupCheckerGUI:
    def __init__(self, master:tk) -> None:
        self.master = master
        self.master.title("Markup Checker")
        bgcolor = "#7f007f"
        frame = tk.Frame(self.master, bg=bgcolor)
        labelfont=('arial',10,'bold')
        entryboxwidth = 60
        titlelabel = tk.Label(frame, text='MARKUP CHECKER', 
                              font = ('Helvetica', 20, 'bold'), 
                              bg = bgcolor, fg="white")
        
        self.markupfile = str()
        self.correctionfile = str()
        
        # Text Labels for Entry Boxes
        savefolderLabel    = tk.Label(frame, anchor=W, justify=LEFT, 
                                           text="Saving Folder:", font=labelfont, 
                                           bg=bgcolor)
        correctedLabel     = tk.Label(frame, anchor=W, justify=LEFT, 
                                           text='Correction Image:', font=labelfont, 
                                           bg=bgcolor, fg='white')
        markedLabel        = tk.Label(frame, anchor=W, justify=LEFT, 
                                           text='Marked Up Image:', font=labelfont, 
                                           bg=bgcolor, fg='white')

        # Entry Fields for file input
        self.correctedEntry     = tk.Entry(frame, exportselection=0, 
                                           width=entryboxwidth)
        self.markedEntry        = tk.Entry(frame, exportselection=0, 
                                           width=entryboxwidth)
        self.savefolderEntry    = tk.Entry(frame, exportselection=0, 
                                           width=entryboxwidth)
        
        # Buttons to browse directory for file selection
        self.browseButton1 = tk.Button(frame,cursor='hand2',
            text="SELECT", 
            command=lambda m = self.correctedEntry: self.get_file(m),
            font=('helvetica', 8, 'bold'))
        self.browseButton2      = tk.Button(frame,cursor='hand2',
            text="SELECT", 
            command=lambda m = self.markedEntry: self.get_file(m), 
            font=('helvetica', 8, 'bold'))
        
        # Initiates comparison
        self.checkButton = tk.Button(frame,cursor='hand2',
            text='Check Corrections', command=self.start_operation,
            bg='gold2', font=('helvetica', 12, 'bold'))        
        self.highlightButton      = tk.Button(frame,cursor='hand2',
            text='Highlight Markups', command=self.highlight_markups, 
            bg='gold2', font=('helvetica', 12, 'bold'))
        
        # Placement configuration of widgets
        titlelabel              .grid(row=0, column=0, columnspan=3, pady=5)
        correctedLabel          .grid(row=2, column=0, padx=5)
        self.correctedEntry     .grid(row=2, column=1, sticky = NS, pady=5)
        self.browseButton1      .grid(row=2, column=2, padx=5, pady=5, sticky=EW)
        markedLabel             .grid(row=1, column=0)
        self.markedEntry        .grid(row=1, column=1, sticky = NS, pady=5)
        self.browseButton2      .grid(row=1, column=2, padx=5, pady=5, sticky=EW)
        self.checkButton        .grid(row=6, column=0, columnspan=3, padx=5, pady=5,sticky=EW)
        self.highlightButton    .grid(row=7, column=0, columnspan=3, padx=5, pady=5,sticky=EW)

        self.markedEntry.config(state=DISABLED)
        self.correctedEntry.config(state=DISABLED)
        frame.pack()
        self.master.resizable(0,0)

    def get_file(self, entrybox:tk.Entry)->str:
        """Lets user select file from directory and store file path in Entrybox"""
        import_file_path= filedialog.askopenfilename(filetypes=(("JPEG","*.jpg"),("PDF","*.pdf"),("all files","*.*")))
        if not import_file_path:
            return False
        file_path = pathlib.Path(import_file_path)
        file_ext = file_path.suffix.lower()

        if file_ext not in [".jpg", ".jpeg", ".pdf", ".png", ".tiff"]:
            tk.messagebox.showwarning('Error','Not a supported file type',icon = 'error')
            return False  
        
        # Populates entry box
        entrybox.config(state=NORMAL)
        entrybox.delete(0,'end')
        entrybox.insert(0,file_path.name)
        entrybox.config(state=DISABLED)

        # Updates File variable
        if entrybox == self.correctedEntry:
            self.correctionfile = import_file_path
        else:
            self.markupfile = import_file_path
        return import_file_path

    def start_operation(self)->None:
        markup_file = self.markupfile
        correct_file = self.correctionfile

        if (not os.path.exists(markup_file)):
            tk.messagebox.showwarning('Error','File {} does not exist'.format(markup_file),icon = 'error')
            return
        if (not os.path.exists(correct_file)):
            tk.messagebox.showwarning('Error','File {} does not exist'.format(correct_file),icon = 'error')
            return
        
        self.aligned_img, matched_img = MarkupChecker.align_drawings(markup_file,correct_file)
        correct_df = MarkupChecker.find_markups(markup_file)
        if len(correct_df)<1:
            tk.messagebox.showwarning('Done',"No Markups found.")
            return 
        CheckerWindowGUI(self, correct_df)
        #MarkupChecker.draw_markup_highlights(aligned_img,correct_df, show=True)

    def highlight_markups(self)->None:
        markup_file = self.markupfile
        m_filename = pathlib.Path(markup_file).stem
        if (not os.path.exists(markup_file)):
            tk.messagebox.showwarning('Error','File {} does not exist'.format(markup_file),icon = 'error')
            return
        
        correct_df = MarkupChecker.find_markups(markup_file)
        markup_img = MarkupChecker.draw_markup_highlights(markup_file,correct_df)
        downloads = str(pathlib.Path.home()/"Downloads")
        highlight_output = str(pathlib.Path.home()/"Downloads"/"".join([m_filename,"_Highlighted.jpg"]))
        cv2.imwrite(highlight_output, markup_img)
        os.startfile(highlight_output)

class CheckerWindowGUI:
    def __init__(self, master, df:pd.DataFrame) -> None:
        self.master = master
        self.df = df

        bgcolor = "#7f007f"
        
        self.compareWindow=tk.Toplevel(self.master.master)
        self.compareWindow.title("Comparing Marks")
        #compareWindow.geometry("810x550")
        self.compareWindow.grab_set()
        self.compareWindow.config(bg=bgcolor)

        self.cur_c= 0

        checkFrame=tk.Frame(self.compareWindow,bg=bgcolor)
        checkFrame.pack()

        reference_frame = tk.Frame(checkFrame, bg = bgcolor)

        imageframe1=tk.Frame(reference_frame,bg=bgcolor,width=400,height=400)
        imageframe2=tk.Frame(reference_frame,bg=bgcolor,width=400,height=400)

        panel2_label=tk.Label(reference_frame,text="Corrected Image",bg=bgcolor,font=('arial black', 12))
        panel1_label=tk.Label(reference_frame,text="Marked Image",bg=bgcolor,font=('arial black', 12))

        self.image_cont1=tk.Label(imageframe1)
        self.image_cont2=tk.Label(imageframe2)
        self.prompt_label=tk.Label(checkFrame,
                                   text="Have the corrections in this section been made?", bg=bgcolor,font=('arial black', 18))
        self.correction_label=tk.Label(checkFrame, bg=bgcolor,font=('arial black', 18))
        
        self.inputbox = tk.Entry(checkFrame, exportselection=0)

        self.submitButton=tk.Button(checkFrame,text='Submit', 
                                    command=None, bg='yellow', fg='black', 
                                    font=('helvetica', 12, 'bold'))
        self.cancelButton=tk.Button(checkFrame,text='Cancel', command=None, 
                                    bg='gray', fg='white', 
                                    font=('helvetica', 12, 'bold'))
        self.confirmButton = tk.Button(checkFrame,text='       Yes        ', 
                                       command=self.next_mark, bg='Green', 
                                       fg='white', font=('helvetica', 12, 'bold'))
        self.declineButton = tk.Button(checkFrame,text='        No        ', 
                                       command=None, bg='Red', fg='white',
                                       font=('helvetica', 12, 'bold'))
        
        panel1_label.grid(row=0,column=0)
        panel2_label.grid(row=0,column=1)

        imageframe1.grid(row=1, column=0)
        imageframe2.grid(row=1, column=1)

        self.image_cont1.pack()
        self.image_cont2.pack()

        reference_frame.grid(row=0,column=0,columnspan=2)

        self.prompt_label.grid(row=3, column=0, columnspan=2)
        self.correction_label.grid(row=2, column=0, columnspan=2)
        self.confirmButton.grid(row=4,column=0)
        self.declineButton.grid(row=4,column=1)

        self.next_mark()

    def next_mark(self):
        if self.cur_c >= len(self.df):
            return
        rect = self.df.iloc[self.cur_c][2]
        rect = (rect[0]-20, rect[1]-20, rect[2]+20, rect[3]+20)
        
        # Opens and crops images for display
        r_img=Image.open(self.master.markupfile)
        
        # Converts cv2 image to PIL image
        b,g,r = cv2.split(self.master.aligned_img)
        c_img = cv2.merge((r,g,b))
        c_img = Image.fromarray(c_img)

        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        ratio = width/height
        new_width = 250
        new_height = 250/ratio

        if new_height>250:
            new_height = 250
            new_width = 250*ratio

        new_size = (int(new_width),int(new_height))

        r_img = r_img.crop(rect)
        r_img = r_img.resize(new_size)
        r_img = ImageTk.PhotoImage(r_img)

        c_img = c_img.crop(rect)
        c_img = c_img.resize(new_size)
        c_img = ImageTk.PhotoImage(c_img)

        self.image_cont1.config(image=r_img)
        self.image_cont1.photo = r_img
        self.image_cont2.config(image=c_img)
        self.image_cont2.photo = c_img

        self.correction_label.config(text="Correction Number: {}".format(self.cur_c+1))

        self.cur_c += 1

        

if __name__ == "__main__":
    root = tk.Tk()
    MarkupCheckerGUI(root)
    tk.mainloop()