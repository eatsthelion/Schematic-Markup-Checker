import os
import cv2
import pathlib
import numpy as np
import pandas as pd
import tkinter as tk

from PIL import Image, ImageTk
from tkinter import LEFT, W, NS, EW, NORMAL, DISABLED, filedialog, END

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
        self.checkButton        .grid(row=6, column=0, columnspan=3, padx=5, pady=5,
                                      sticky=EW)
        self.highlightButton    .grid(row=7, column=0, columnspan=3, padx=5, pady=5,
                                      sticky=EW)

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
        self.markupfile = MarkupChecker.convert2jpg(self.markupfile)
        self.correctionfile = MarkupChecker.convert2jpg(self.correctionfile)

        if (not os.path.exists(self.markupfile)):
            tk.messagebox.showwarning('Error','File {} does not exist'.format(self.markupfile),icon = 'error')
            return
        if (not os.path.exists(self.correctionfile)):
            tk.messagebox.showwarning('Error','File {} does not exist'.format(self.correctionfile),icon = 'error')
            return
        
        self.aligned_img, matched_img = MarkupChecker.align_drawings(self.markupfile,self.correctionfile)
        correct_df = MarkupChecker.find_markups(self.markupfile)
        if len(correct_df)<1:
            tk.messagebox.showwarning('Done',"No Markups found.")
            return 
        CheckerWindowGUI(self, correct_df, self.markupfile, self.aligned_img)

    def highlight_markups(self)->None:
        self.markupfile = self.markupfile
        m_filename = pathlib.Path(self.markupfile).stem
        if (not os.path.exists(self.markupfile)):
            tk.messagebox.showwarning('Error','File {} does not exist'.format(self.markupfile),icon = 'error')
            return
        
        correct_df = MarkupChecker.find_markups(self.markupfile)
        markup_img = MarkupChecker.draw_markup_highlights(self.markupfile,correct_df)
        downloads = str(pathlib.Path.home()/"Downloads")
        highlight_output = downloads + "/" + str("".join([m_filename,"_Highlighted.jpg"]))
        cv2.imwrite(highlight_output, markup_img)
        os.startfile(highlight_output)

class CheckerWindowGUI:
    def __init__(self, master, df:pd.DataFrame, markup:str,
                 correctfile:str or Image or np.ndarray) -> None:
        self.master = master
        self.markupfile = markup
        self.correctfile = correctfile
        self.df = df

        bgcolor = "#7f007f"
        
        self.compareWindow=tk.Toplevel(self.master.master)
        self.compareWindow.title("Comparing Marks")
        #compareWindow.geometry("810x550")
        self.compareWindow.grab_set()
        self.compareWindow.config(bg=bgcolor)

        checkFrame=tk.Frame(self.compareWindow,bg=bgcolor)
        checkFrame.pack()

        reference_frame = tk.Frame(checkFrame, bg = bgcolor)

        imageframe1=tk.Frame(reference_frame,bg=bgcolor,width=400,height=400)
        imageframe2=tk.Frame(reference_frame,bg=bgcolor,width=400,height=400)

        panel2_label=tk.Label(reference_frame,text="Corrected Image",
                              bg=bgcolor,font=('arial black', 12))
        panel1_label=tk.Label(reference_frame,text="Marked Image",
                              bg=bgcolor,font=('arial black', 12))

        self.image_cont1=tk.Label(imageframe1)
        self.image_cont2=tk.Label(imageframe2)
        self.prompt_label=tk.Label(checkFrame,bg=bgcolor,font=('arial black', 18),
                                   text="Was this correction picked up?")
        self.correction_label=tk.Label(checkFrame, bg=bgcolor,font=('arial black', 18))
        
        self.inputbox = tk.Entry(checkFrame, exportselection=0)

        self.nextButton=tk.Button(checkFrame,text='Next', 
                                    command=self.go_next, bg='gold2', fg='black', 
                                    font=('helvetica', 12, 'bold'))
        self.backButton=tk.Button(checkFrame, command=self.go_back, 
                                    bg='gold2', fg='black', text = "Back",
                                    font=('helvetica', 12, 'bold'))
        self.confirmButton = tk.Button(checkFrame,text='Yes', 
                                       command=lambda m=True: self.confirm_correction(m),
                                       bg='Green', fg='white', font=('helvetica', 12, 'bold'))
        self.declineButton = tk.Button(checkFrame,text='No', 
                                       command=lambda m=False: self.confirm_correction(m), 
                                       bg='Red', fg='white', font=('helvetica', 12, 'bold'))
        
        comment_label = tk.Label(checkFrame, bg=bgcolor,font=('arial black', 18), 
                                 text="Comments:")
        
        self.comment_entry = tk.Text(checkFrame, font=('helvetica', 10, 'bold'),
                                     height = 5)
        
        panel1_label.grid(row=0,column=0)
        panel2_label.grid(row=0,column=1)

        imageframe1.grid(row=1, column=0)
        imageframe2.grid(row=1, column=1)

        self.image_cont1.pack()
        self.image_cont2.pack()

        reference_frame.grid(row=0,column=0,columnspan=2)

        #self.nextButton.grid(row=2,column=1, sticky=tk.E, padx=(0,5))
        self.backButton.grid(row = 2, column=0, sticky=W, padx=(5,0))
        self.correction_label.grid(row=2, column=0, columnspan=2, pady = (5,0))
        self.prompt_label.grid(row=3, column=0, columnspan=2, padx = 5)

        self.confirmButton.grid(row=4,column=0, padx=5, sticky=EW)
        self.declineButton.grid(row=4,column=1, padx=5, sticky=EW)

        comment_label.grid(row=5, column = 0, padx = 5, pady=(5,0), sticky = W)
        self.comment_entry.grid(row=6, column=0, columnspan=2, padx = 5, pady = 5, sticky = EW)

        # Initializes object attributes
        self.cur_c = 0
        self.correct_list = [''] * len(self.df)
        self.comments_list = [''] * len(self.df)

        self.compareWindow.update()
        self.show_mark()

    def show_mark(self):
        rect = self.df.iloc[self.cur_c][2]
        rect = (rect[0]-20, rect[1]-20, rect[2]+20, rect[3]+20)
        
        r_img, c_img = MarkupChecker.crop_images(self.markupfile, self.correctfile, rect)
        
        r_img = ImageTk.PhotoImage(r_img)
        c_img = ImageTk.PhotoImage(c_img)

        self.image_cont1.config(image=r_img)
        self.image_cont1.photo = r_img
        self.image_cont2.config(image=c_img)
        self.image_cont2.photo = c_img

        self.correction_label.config(text="Correction: {}/{}".format(self.cur_c+1,
                                                                     len(self.df)))
        self.comment_entry.delete("1.0", END)
        self.comment_entry.insert(END, self.comments_list[self.cur_c])
        return

    def confirm_correction(self, outcome:bool):
        # Updates the correction
        self.correct_list[self.cur_c] = outcome
        self.comments_list[self.cur_c] = self.comment_entry.get("1.0", "end-1c")
        self.cur_c += 1

        if self.cur_c >= len(self.df):
            if tk.messagebox.askquestion("Submit", "Submit results?") == 'yes':
                self.end_comparison()
            else:
                self.cur_c -= 1
        else:
            self.show_mark()

    def go_back(self):
        """Reverts back to a previous correction"""
        if self.cur_c<=0:
            self.cur_c = 0
            return
        self.comments_list[self.cur_c] = self.comment_entry.get("1.0", "end-1c")
        self.cur_c -= 1
        self.show_mark()

    def go_next(self):
        if self.cur_c >= len(self.df)-1:
            self.cur_c = len(self.df)-1
            return
        self.comments_list[self.cur_c] = self.comment_entry.get("1.0", "end-1c")
        self.cur_c += 1
        self.show_mark()

    def end_comparison(self):
        # Renumbers corrections
        self.df.index = np.arange(1, len(self.df) + 1)
        
        # Removes columns
        self.df.drop(['index', 'coords'], inplace=True, axis=1)
        self.df["Picked Up"] = self.correct_list
        self.df["Comments"] = self.comments_list

        # Names output columns
        outputfile = str(pathlib.Path.home()/"Downloads")
        outputfile += "/" + str("".join([pathlib.Path(self.markupfile).stem,
                                         "_CorrectionResults.xlsx"]))
        
        # Exports data to Excel
        self.df.to_excel(outputfile)
        os.startfile(outputfile)
        self.compareWindow.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    MarkupCheckerGUI(root)
    tk.mainloop()