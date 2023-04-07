
import os
import cv2
import shutil
import xlsxwriter
import numpy as np
import tkinter as tk
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image, ImageChops, ImageTk
from tkinter import Entry, filedialog, messagebox, Toplevel, W, CENTER, DISABLED, NORMAL, LEFT
from program import Program
from savelocs import OUTPUTLOC, POPPLER

MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15

class QualityChecker(Program):
    programtitle='Quality Checker'
    description="\t\t        %s\
            \n\nThis program checks for corrections of a marked up drawing. The program will create a list of all the corrections that were picked up or missed.\
            \n\nThe User must input two images, an image of the drawing with the Corrections made which is called the Correction Image, and an image where all the colored mark ups are drawn which is called the Marked Image.\
            \n\nThe Correction Image and the Marked Image should be of similar size in order for the program to work properly.\
            \n\nThe User should also provide a save folder for results to be saved in.\
            \n\nThe program first aligns the images so that shared features and keypoints are lined up properly.\
            \n\nThe program then identifies all correcetions by searching for any colored pixels in the Marked Up Image.\
            \n\nThen the program shows the user the area where each correction is located on both the Corrected and Marked Images and asks if the correction was picked up.\
            \n\nIf the correction was not picked up, the user should provide a comment to help idenify what was incorrect.\
            \n\nThe program then provides a list of corrections that were and weren't picked up in the form of an Excel Sheet, located within the save folder.\
            \n\n-------------------------------------------------------------------------------------------\
            \n\nFor more help with how this program works, please contact the Program Designer for assistance.\
            \n\nProgram Designer: Ethan de Leon\
            \n\nRelease Date: September 28, 2021\
            \n\nThis software was made for the purposes of Ocampo-Esta Corporation only. Any usesage of this program outside of the company workplace is strictly prohibited.\
            "%programtitle
    bgcolor='white'
    refFilename=None
    imFilename=None
    boundaries = [
        ([0, 20, 20], [20, 255, 255]),    #red 
        ([36, 25, 25], [102, 255, 255]),  #green
        ([100, 150, 0], [140, 255, 255]), #blue
        ([0, 100, 100], [30, 255, 255])  #yellow
        ]


    def __init__(self, master,user):
        super(QualityChecker,self).__init__(master,user,width=350,height=200,programtitle='OEC Quality Checker')
        Program.programInfo(self,self.frame, self.description, self.w_width, 0)

        self.titlelabel = tk.Label(self.frame, text='Quality Checker', bg = self.bgcolor)
        self.titlelabel.config(font=('Helvetica', 20, 'bold'))

        labelfont=('arial',9,'bold')
        entryboxwidth=30


        self.savefolderLabel    = tk.Label(self.frame, anchor=W, justify=LEFT, text="Saving Folder:", font=labelfont, bg=self.bgcolor)
        self.correctedLabel     = tk.Label(self.frame, anchor=W, justify=LEFT, text='Corrected Image:', font=labelfont, bg=self.bgcolor)
        self.markedLabel        = tk.Label(self.frame, anchor=W, justify=LEFT, text='Marked Up Image:', font=labelfont, bg=self.bgcolor)
  
        self.correctedEntry     = Entry(self.frame, exportselection=0, width=entryboxwidth)
        self.markedEntry        = Entry(self.frame, exportselection=0, width=entryboxwidth)
        self.savefolderEntry    = Entry(self.frame, exportselection=0, width=entryboxwidth)
        
        self.browseButton1      = tk.Button(self.frame,cursor='hand2',text="Select", command=lambda m='corrected': self.getFile(m), font=('helvetica', 8, 'bold'))
        self.browseButton2      = tk.Button(self.frame,cursor='hand2',text="Select", command=lambda m='marked': self.getFile(m),  font=('helvetica', 8, 'bold'))
        self.openButton         = tk.Button(self.frame,cursor='hand2',text='Select', command=self.getSaveLoc, bg='blue', fg='white', font=('helvetica', 8, 'bold'))
        self.checkButton        = tk.Button(self.frame,cursor='hand2',text='Check Corrections', command=lambda m=master: self.startChecking(m), bg='gray', fg='white', font=('helvetica', 12, 'bold'))        
        self.compareButton      = tk.Button(self.frame,cursor='hand2',text='Compare Images', command=lambda m=master: self.compareImages(m), bg='gray', fg='white', font=('helvetica', 12, 'bold'))


        self.terminal           =tk.StringVar()
        self.terminalLabel      =tk.Label(self.frame,font=labelfont, bg=self.bgcolor,textvariable=self.terminal)


        self.titlelabel         .grid(row=0, column=0, columnspan=3, pady=5)
        self.correctedLabel     .grid(row=1, column=0, padx=5)
        self.correctedEntry     .grid(row=1, column=1)
        self.browseButton1      .grid(row=1, column=2, padx=5, pady=5)
        self.markedLabel        .grid(row=2, column=0)
        self.markedEntry        .grid(row=2, column=1)
        self.browseButton2      .grid(row=2, column=2, padx=5, pady=5)
        #self.savefolderLabel    .grid(row=4, column=0)
        #self.savefolderEntry    .grid(row=4, column=1)
        #self.openButton         .grid(row=4, column=2, padx=5, pady=5)
        self.checkButton        .grid(row=6, column=0, columnspan=3, pady=5)
        self.compareButton      .grid(row=7, column=0, columnspan=3, pady=5)
        #self.terminalLabel      .grid(row=8, column=0, columnspan=3, pady=5)

        self.loadtrigger=True

    def getFile(self,pathway):
        import_file_path= filedialog.askopenfilename(filetypes=(("JPEG","*.jpg"),("PDF","*.pdf"),("all files","*.*")))
        if (import_file_path==""):
            return

        split_path=os.path.splitext(import_file_path)
        file_extension=split_path[1]
        file_ext=file_extension.lower()

        isJPG=(file_ext=='.jpg')or(file_ext=='.jpeg')
        isPDF=(file_ext=='.pdf')
        isPNG=(file_ext=='.png')
        isTIF=(file_ext=='.tif')

        if not (isJPG or isPDF or isPNG or isTIF):
            #wrong file selected/ nothing is selected
            if file_extension!="":
                MsgBox = tk.messagebox.showwarning('Error','Not a supported file type',icon = 'error')
                file_extension=""
            return
        
        if pathway=='corrected':
            self.correctedEntry.config(state=NORMAL)
            self.correctedEntry.delete(0,'end')
            self.correctedEntry.insert(0,import_file_path)
            self.correctedEntry.config(state=DISABLED)
            self.refFilename = import_file_path
        elif pathway=='marked':
            self.markedEntry.config(state=NORMAL)
            self.markedEntry.delete(0,'end')
            self.markedEntry.insert(0,import_file_path)
            self.markedEntry.config(state=DISABLED)
            self.imFilename = import_file_path

        #savecheck=self.savefolderEntry.get().replace(" ","")
        if (self.refFilename!=None)and(self.imFilename!=None):
            self.checkButton.configure(bg='green')
            self.compareButton.configure(bg='green')
        return

    def getSaveLoc(self):
        msg=tk.messagebox.askyesno("Save Results?","Would you like to save your results?")
        if not msg:
            return

        downloadspath = str(Path.home() / "Downloads")
        output_path = filedialog.askdirectory(initialdir=downloadspath)
        if output_path=="":
            self.getSaveLoc()
            return

        oSaveName="QC Compare -%s"%(os.path.basename(self.refFilename))
        self.path=os.path.join(output_path, oSaveName)
        fileCount=0
        while (os.path.exists(self.path)):
            if fileCount==0:
                savedName=oSaveName
            else:
                savedName=oSaveName+" (%s)"%(str(fileCount))
            fileCount+=1
            self.path=os.path.join(output_path, savedName)
        os.mkdir(self.path)
        for file in os.listdir(self.imagepath):
            fileLoc=os.path.join(self.imagepath,file)
            saveLoc=os.path.join(self.path,file)
            shutil.copy(fileLoc,saveLoc)
        
        return

        #self.savefolderEntry.config(state=NORMAL)
        #self.savefolderEntry.delete(0,'end')
        #self.savefolderEntry.insert(0,output_path)
        #self.savefolderEntry.config(state=DISABLED)
 
        #savecheck=self.savefolderEntry.get().replace(" ","")
        #if (self.refFilename!=None)and(self.imFilename!=None)and(savecheck!=""):
        #    self.checkButton.configure(bg='green')
        #    self.compareButton.configure(bg='green')
           
    def startChecking(self, master):
        if (self.refFilename==None)or(self.imFilename==None):
            
            return
        #output_path=self.savefolderEntry.get()
        
        #if not os.path.exists(output_path):
        #    msg=tk.messagebox.showerror("Error", "Folder not found.") 
        #    return

        
        #oSaveName="QC Output -%s"%(os.path.basename(self.refFilename))
        #self.path=os.path.join(output_path, oSaveName)
        #fileCount=0
        #while (os.path.exists(self.path)):
        #    if fileCount==0:
        #        savedName=oSaveName
        #    else:
        #        savedName=oSaveName+" (%s)"%(str(fileCount))
        #    fileCount+=1
        #    self.path=os.path.join(output_path, savedName)
        #os.mkdir(self.path)

        #folder="images"
        #self.imagepath=os.path.join(self.path,folder)
        self.imagepath=os.path.join(OUTPUTLOC,'Quality Checker')
        self.imagepath=os.path.join(self.imagepath,'Checking')

        if (not os.path.exists(self.imagepath)):
            os.mkdir(self.imagepath)
        self.imagepath=os.path.join(self.imagepath,self.user.name)
        if (not os.path.exists(self.imagepath)):
            os.mkdir(self.imagepath)

        self.refFilename=QualityChecker.convert2jpg(self.refFilename,self.imagepath)
        if self.refFilename==False:
            self.refFilename=None
            self.checkButton.configure(bg='gray')
            self.compareButton.configure(bg='gray')
            self.correctedEntry.config(state=NORMAL)
            self.correctedEntry.delete(0,'end')
            return
        self.imFilename=QualityChecker.convert2jpg(self.imFilename,self.imagepath)
        if self.imFilename==False:
            self.imFilename=None
            self.checkButton.configure(bg='gray')
            self.compareButton.configure(bg='gray')
            self.markedEntry.config(state=NORMAL)
            self.markedEntry.delete(0,'end')
            return

        master.grab_set()
        self.executeAlign()
        self.findCorrections()
        self.createCropping()
            
        self.checkWindow()
        self.cropDisplay()          
            
        self.updateTerminal("Finished!")        

    def compareImages(self,master):
        #output_path=self.savefolderEntry.get()
        if (self.refFilename==None)or(self.imFilename==None):
            return
        #if not os.path.exists(output_path):
        #    msg=tk.messagebox.showerror("Error", "Folder not found.") 
        #    return

        #oSaveName="QC Compare -%s"%(os.path.basename(self.refFilename))
        #self.path=os.path.join(output_path, oSaveName)
        #fileCount=0
        #while (os.path.exists(self.path)):
        #    if fileCount==0:
        #        savedName=oSaveName
        #    else:
        #        savedName=oSaveName+" (%s)"%(str(fileCount))
        #    fileCount+=1
        #    self.path=os.path.join(output_path, savedName)
        #os.mkdir(self.path)

        #folder="images"
        #self.imagepath=os.path.join(self.path,folder)
        self.imagepath=os.path.join(OUTPUTLOC,'Quality Checker')
        self.imagepath=os.path.join(self.imagepath,'Comparing')
        if (not os.path.exists(self.imagepath)):
            os.mkdir(self.imagepath)
        self.imagepath=os.path.join(self.imagepath,self.user.name)
        if (not os.path.exists(self.imagepath)):
            os.mkdir(self.imagepath)

        self.refFilename=QualityChecker.convert2jpg(self.refFilename,self.imagepath)
        if self.refFilename==False:
            self.refFilename=None
            self.checkButton.configure(bg='gray')
            self.compareButton.configure(bg='gray')
            self.correctedEntry.config(state=NORMAL)
            self.correctedEntry.delete(0,'end')
            return
        self.imFilename=QualityChecker.convert2jpg(self.imFilename,self.imagepath)
        if self.imFilename==False:
            self.imFilename=None
            self.checkButton.configure(bg='gray')
            self.compareButton.configure(bg='gray')
            self.markedEntry.config(state=NORMAL)
            self.markedEntry.delete(0,'end')
            return

        master.grab_set()
        self.executeAlign()
        self.alignedImage=os.path.join(self.imagepath, "aligned.jpg")
        self.contrastImage=os.path.join(self.imagepath,"differences.jpg")
        img1=Image.open(self.refFilename)
        img2=Image.open(self.alignedImage)
        diff=ImageChops.difference(img1,img2)

        img_copy=diff.copy()
        img_copy.paste(diff)
        img_copy.save(self.contrastImage,'JPEG')

        self.getSaveLoc()
        os.startfile(self.contrastImage)

        self.clearFiles()
        self.updateTerminal("Finished!")     
        #(red, green, blue) = img_copy.split()
        #colorMerge=Image.merge("RGB",(blue,red,green))
        #contrast=ImageEnhance.Contrast(colorMerge)
        #contrast=contrast.enhance(1.25)
        #contrast.show()

    def clearFiles(self):
        self.refFilename=None
        self.imFilename=None
        self.checkButton.configure(bg='gray')
        self.compareButton.configure(bg='gray')
        self.correctedEntry.config(state=NORMAL)
        self.markedEntry.config(state=NORMAL)
        self.correctedEntry.delete(0,'end')
        self.markedEntry.delete(0,'end')

    def convert2jpg(filepath,loc):
        split_path=os.path.splitext(filepath)
        file_extension=split_path[1]
        file_ext=file_extension.lower()

        isJPG=(file_ext=='.jpg')or(file_ext=='.jpeg')
        isPDF=(file_ext=='.pdf')
        isPNG=(file_ext=='.png')
        isTIFF=(file_ext=='.tiff')
        if isJPG:
            return filepath

        if isPDF:
            images = convert_from_path(filepath,poppler_path=POPPLER)
            if len(images)>1:
                MsgBox = tk.messagebox.showwarning('Error','PDF has more than one page.',icon = 'error')
                return False
            image = images[0]
            
        elif isPNG or isTIFF:
            image = Image.open(filepath)
            image = image.convert('RGB')
        
        img_file=os.path.basename(filepath)
        img_file=img_file.replace(file_ext,"")
        img_file=img_file.replace(file_ext.upper(),"")
        jpeg_file=img_file+".jpg"
        jpgLoc=os.path.join(loc,jpeg_file)
        image.save(jpgLoc,'JPEG')
        return jpgLoc


    #HOMOGRAPHY IMPLEMENT
    def alignImages(self,im1, im2):
        # Convert images to grayscale
        im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

        # Detect ORB features and compute descriptors.
        orb = cv2.ORB_create(MAX_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
        keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # Draw top matches
        imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
        matchLocation=os.path.join(self.imagepath,"matches.jpg")
        cv2.imwrite(matchLocation, imMatches)

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # Find homography
        h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

        # Use homography
        height, width, channels = im2.shape
        im1Reg = cv2.warpPerspective(im1, h, (width, height))

        return im1Reg, h

    def executeAlign(self):

        #self.updateTerminal("Reading reference image: "+self.refFilename)
        #self.refFilename=QualityChecker.convert2jpg(self.refFilename,self.imagepath)
        imReference = cv2.imread(self.refFilename, cv2.IMREAD_COLOR)
        imRefHeight, imRefWidth, imRefChannels = imReference.shape

        #self.updateTerminal("Reading image to align:  "+self.imFilename)
        #self.imFilename=QualityChecker.convert2jpg(self.imFilename,self.imagepath)
        im = cv2.imread(self.imFilename, cv2.IMREAD_COLOR)
        (imHeight, imWidth, imChannels) = im.shape

        #self.updateTerminal("Reference Img:")
        #self.updateTerminal(" Width: "+imRefWidth+"\n Height: "+imRefHeight)
        #print("Im:")
        #print(" Width:",imWidth," Height:",imHeight)

        self.updateTerminal("Aligning images ...")
        # Registered image will be resotred in imReg.
        # The estimated homography will be stored in h.
        imReg, h = self.alignImages(im, imReference)

        # Write aligned image to disk.
        outFilename = "aligned.jpg"
        outputLocation=os.path.join(self.imagepath,outFilename)
        self.updateTerminal("Saving aligned image : "+outFilename)
        cv2.imwrite(outputLocation, imReg)

        # #print estimated homography
        #self.updateTerminal("Estimated homography : \n"+  h)

    def contourShift(self, cList): #cList = [[x,y,w,h],...]
        c1_count=0
        changes=0
        for c1 in cList:
            if c1==[]:
                c1_count+=1
                continue 
            #first rectangle
            x1Left=c1[0]            #left side
            y1Top=c1[1]             #top side
            x1Right=c1[0]+c1[2]     #right side
            y1Bottom=c1[1]+c1[3]    #bottom side

            rec1=(x1Right-x1Left)*(y1Bottom-y1Top)

            c2_count=0
            for c2 in cList:
                if (c1==c2)or(c2==[]):
                    c2_count+=1
                    continue
                
                #second rectangle
                x2Left=c2[0]            #left side
                y2Top=c2[1]             #top side
                x2Right=c2[0]+c2[2]     #right side
                y2Bottom=c2[1]+c2[3]    #bottom side

                rec2=(x2Right-x2Left)*(y2Bottom-y2Top)

                prevChanges=changes
                #when a contour is inside a contour
                #       Left        Right        Top        Bottom
                if (((x2Left>=x1Left)and(x2Right<=x1Right))and((y2Top>=y1Top)and(y2Bottom<=y1Bottom))):
                    cList[c2_count]=[]
                    changes+=1
                else:
                    if ((y2Top>=y1Top)and(y2Top<=y1Bottom))or((y2Bottom>=y1Top)and(y2Bottom<=y1Bottom)):
                        #Right shift
                        if (x2Left<=x1Right)and(x2Right>x1Right):
                            dif=x2Right-x1Right
                            c1[2]=c1[2]+dif
                            changes+=1
                        #Left shift
                        if (x2Left<x1Left)and(x2Right>=x1Left):
                            c1[0]=x2Right
                            changes+=1
                    if ((x2Left>=x1Left)and(x2Left<x1Right))or((x2Right>=x1Left)and(x2Right<=x1Right)):
                        #Top shift
                        if (y2Top<y1Top)and(y2Bottom>=y1Top):
                            c1[1]=y2Top
                            changes+=1
                        #Bottom shift
                        if (y2Top<=y1Bottom)and(y2Bottom>y1Bottom):
                            dif=y2Bottom-y1Bottom
                            c1[3]=c1[3]+dif
                            changes+=1
                    if (changes!=prevChanges)and(rec1>rec2):
                        cList[c2_count]=[]
                c2_count+=1
            c1_count+=1

        outputList=[]
        for i in cList:
            if i!=[]:
                outputList.append(i)

        #print(outputList)
        #print("changes:", changes)
        return outputList
        
    def findCorrections(self):

        self.alignedImage=os.path.join(self.imagepath, "aligned.jpg")
        image = cv2.imread(self.alignedImage)
        hsvImage=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        save_path=os.path.join(self.imagepath,"hsvImage.jpg")
        cv2.imwrite(save_path,hsvImage)

        width,height,_ = image.shape
        imArea=width*height
        if imArea<1_000_000:
            imScale=50
            self.frameSize=4
            boarderSpace=10
        else:
            imScale=100
            self.frameSize=7
            boarderSpace=30

        #print("Image size:",imArea)
        #print("Image Area Limit:", imScale)
        self.updateTerminal("Finding corrections...")

        ###
        # loop over the boundaries
        count=0
        contourList=[]
        
        for (lower, upper) in self.boundaries:
        
            image = cv2.imread(self.alignedImage)

            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")
            mask = cv2.inRange(hsvImage, lower, upper)
            output = cv2.bitwise_and(hsvImage, hsvImage, mask = mask)     
            """
            count+=1
            if count==1:
                fileName="red_output.jpg"
            elif count==2:
                fileName="blue_output.jpg"
            elif count==3:
                fileName="yellow_output.jpg"
            elif count==4:
                fileName="green_output.jpg"
            """
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            for c in contours:
                area = cv2.contourArea(c)
                if area>(imScale):
                    #cv2.drawContours(image, c, -1, (200,0,255), 3)
                    ##print(area)
                    x,y,w,h = cv2.boundingRect(c)
                    x-=boarderSpace
                    y-=boarderSpace
                    w+=boarderSpace*2
                    h+=boarderSpace*2
                    contourList.append([x,y,w,h])
                    #cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,255),frameSize)
            
            contourList=self.contourShift(contourList)
            
            #save_path = os.path.join(imagepath, fileName)	
            #cv2.imwrite(save_path, image)
            #cv2.imshow(save_path, np.hstack([image, output]))
            cv2.waitKey(0)
        
        self.correctionList=self.contourShift(contourList)

    def createCropping(self):
        self.rectList=[]
        self.rect_limit=200
        image=cv2.imread(self.alignedImage)
        imRef=cv2.imread(self.refFilename)
        width, height, _ = image.shape
        num_count=0
        keypoint_font=cv2.FONT_HERSHEY_SIMPLEX
        scale=.75
        bgr=(255,0,100)
        for cr in self.correctionList:
            x=cr[0]
            y=cr[1]
            w=cr[2]
            h=cr[3]
            centerx=x+(w/2)
            centery=y+(h/2)
            leftSide=(centerx-self.rect_limit)
            topSide=(centery-self.rect_limit)
            rightSide=(centerx+self.rect_limit)
            bottomSide=(centery+self.rect_limit)

            if leftSide>x:
                leftSide=x
            #if leftSide<0:
            #    leftSide=0
            if topSide>y:
                topSide=y
            #if topSide<0:
            #    topSide=0
            if rightSide<(x+w):
                rightSide=x+w
            #if rightSide>width:
            #    rightSide=width
            if bottomSide<(y+h):
                bottomSide=y+h
            #if bottomSide>height:
            #    bottomSide=height
            
            crop_rect=[leftSide,topSide,rightSide,bottomSide]
            self.rectList.append(crop_rect)
            cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,255),self.frameSize)
            cv2.rectangle(imRef,(x,y),(x+w,y+h),(255,0,255),self.frameSize)

            num_count+=1
            num_counter=str(num_count)
            
            cv2.putText(image,num_counter,(x+10,y+22),keypoint_font,scale,(255,255,255))
            cv2.putText(image,num_counter,(x+11,y+23),keypoint_font,scale,bgr)
            cv2.putText(imRef,num_counter,(x+10,y+22),keypoint_font,scale,(255,255,255))
            cv2.putText(imRef,num_counter,(x+11,y+23),keypoint_font,scale,bgr)
        
        self.markedsavepath=os.path.join(self.imagepath,"marked_Ref.jpg")
        cv2.imwrite(self.markedsavepath, imRef)


        self.correctedsavepath=os.path.join(self.imagepath, "corrections.jpg")
        cv2.imwrite(self.correctedsavepath, image)

    def cropDisplay(self):
        if self.r_count<self.rectNum:
            r=self.rectList[self.r_count]
            r_img=Image.open(self.markedsavepath)
            c_img=Image.open(self.correctedsavepath)
            leftSide=r[0]
            rightSide=r[1]
            upSide=r[2]
            downSide=r[3]

            sizeLimit=400

            croping=(leftSide,rightSide,upSide,downSide)
            width=rightSide-leftSide
            height=downSide-upSide
            print('leftSide: '+str(leftSide))
            print('rightSide: '+str(rightSide))
            print('upSide: '+str(upSide))
            print('downSide: '+str(downSide))
            print('Width: '+str(width))
            print('Height: '+str(height))

            ratio=width/height
            new_height=sizeLimit
            new_width=int(ratio*new_height)
            if new_width>sizeLimit:
                ratio=width/height
                new_width=sizeLimit
                new_height=int(new_width/ratio)
            newSize=(new_width,new_height)
            print(str(new_width))
            print(str(new_height))

            self.imR=r_img.crop(croping)
            self.imR=self.imR.resize(newSize)
            self.imR=ImageTk.PhotoImage(self.imR)

            self.imC=c_img.crop(croping)
            self.imC=self.imC.resize(newSize)
            self.imC=ImageTk.PhotoImage(self.imC)

            self.panel1.configure(image=self.imR)
            self.panel2.configure(image=self.imC)
            self.r_count+=1
            self.correctionNumberLabel.config(text="Correction Number: %s"%self.correctionNum)
        else: 
            self.compareWindow.destroy()
            self.checkResults()
            self.clearFiles()

    #CHECKING WINDOW
    def checkWindow(self):
        bgcolor=self.bgcolor
        if bgcolor=='white':
            bgcolor='gray90'
        self.compareWindow=Toplevel(self.master)
        self.compareWindow.title("Comparing Marks")
        self.compareWindow.geometry("810x550")
        self.compareWindow.resizable(0,0)

        self.checkFrame=tk.Frame(self.compareWindow,bg=bgcolor)
        self.checkFrame.place(relwidth=1,relheight=1, relx=0, rely=0)

        self.correctionNum=1
        self.correct_count=0
        self.missed_count=0
        self.rectNum=len(self.rectList)
        self.r_count=0
        self.correctList=[]
        self.missedList=[]

        self.panelTitle1=tk.Label(self.checkFrame,text="Corrected Image",bg=bgcolor,font=('arial black', 12))
        self.panelTitle2=tk.Label(self.checkFrame,text="Marked Image",bg=bgcolor,font=('arial black', 12))
        
        self.imageframe1=tk.Frame(self.checkFrame,bg=bgcolor,width=400,height=400)
        self.imageframe2=tk.Frame(self.checkFrame,bg=bgcolor,width=400,height=400)
        self.panel1=tk.Label(self.imageframe1)
        self.panel2=tk.Label(self.imageframe2)
        self.questionLabel=tk.Label(self.checkFrame,text="Have the corrections in this section been made?", bg=bgcolor,font=('arial black', 18))
        self.correctionNumberLabel=tk.Label(self.checkFrame,text="Correction Number: %s"%self.correctionNum, bg=bgcolor,font=('arial black', 18))
        
        self.comments=Entry(self.checkFrame, exportselection=0)

        self.submitButton=tk.Button(self.checkFrame,text='Submit', command=self.submit, bg='yellow', fg='black', font=('helvetica', 12, 'bold'))
        self.cancelButton=tk.Button(self.checkFrame,text='Cancel', command=self.restoreYN, bg='gray', fg='white', font=('helvetica', 12, 'bold'))
        self.confirmButton = tk.Button(self.checkFrame,text='       Yes        ', command=self.checkConfirm, bg='Green', fg='white', font=('helvetica', 12, 'bold'))
        self.declineButton = tk.Button(self.checkFrame,text='        No        ', command=self.checkDecline, bg='Red', fg='white', font=('helvetica', 12, 'bold'))
        
        self.panelTitle1.grid(row=0,column=0)
        self.panelTitle2.grid(row=0,column=1)
        self.imageframe1.grid(row=1, column=0)
        self.imageframe2.grid(row=1, column=1)
        self.questionLabel.grid(row=2, column=0, columnspan=2)
        self.correctionNumberLabel.grid(row=3, column=0, columnspan=2)
        self.confirmButton.grid(row=4,column=0)
        self.declineButton.grid(row=4,column=1)

        self.panel1.place(relx=.5,rely=.5,anchor=CENTER)
        self.panel2.place(relx=.5,rely=.5,anchor=CENTER)

        self.workbookName = os.path.join(self.imagepath,"CorrectionList.xlsx")
        self.workbook=xlsxwriter.Workbook(self.workbookName)
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.write("A1","Correction")
        self.worksheet.write("B1", "Corrected IMG")
        self.worksheet.write("C1", "Marked IMG")
        self.worksheet.write("D1", "Result")
        self.worksheet.write("E1", "Comments")
        self.worksheet.set_column('A:A',10)
        self.worksheet.set_column('B:C',60)
        self.worksheet.set_column('D:D',10)
        self.worksheet.set_column('E:E',60)
        cell_format_green=self.workbook.add_format()
        cell_format_green.set_bg_color('green')
        cell_format_red=self.workbook.add_format()
        cell_format_red.set_bg_color('red')

    def checkConfirm(self):
        self.worksheet.write("A"+str(1+self.correctionNum), str(self.correctionNum))
        self.worksheet.write("B"+str(1+self.correctionNum), self.refFilename)
        self.worksheet.write("C"+str(1+self.correctionNum), self.imFilename)
        self.worksheet.write("D"+str(1+self.correctionNum), "Corrected")
        self.correctList.append(self.correctionNum)
        self.correctionNum+=1
        self.correct_count+=1
        self.cropDisplay()

    def restoreYN(self):
        self.comments.grid_forget()
        self.submitButton.grid_forget()
        self.cancelButton.grid_forget()
        self.questionLabel.config(text="Have the corrections in this section been made?")
        self.correctionNumberLabel.grid(row=3, column=0, columnspan=2)
        self.confirmButton.grid(row=4,column=0)
        self.declineButton.grid(row=4,column=1)

    def submit(self):
        self.worksheet.write("A"+str(1+self.correctionNum), str(self.correctionNum))
        self.worksheet.write("B"+str(1+self.correctionNum), self.refFilename)
        self.worksheet.write("C"+str(1+self.correctionNum), self.imFilename)
        self.worksheet.write("D"+str(1+self.correctionNum), "Missed")
        self.worksheet.write("E"+str(1+self.correctionNum), self.comments.get())
        self.comments.delete(0,'end')
        self.missedList.append(self.correctionNum)
        self.correctionNum+=1
        self.missed_count+=1
        self.restoreYN()
        self.cropDisplay()
        return

    def checkDecline(self):
        
        self.confirmButton.grid_forget()
        self.declineButton.grid_forget()
        self.correctionNumberLabel.grid_forget()
        self.questionLabel.config(text="What was missed?")
        self.comments.grid(row=3,column=0,columnspan=2)
        self.submitButton.grid(row=4, column=0)
        self.cancelButton.grid(row=4, column=1)   

    def checkResults(self):
        #print("Corrections picked up:", self.correct_count)
        #print("Corrections missed:", self.missed_count)
        correct_count=str(self.correct_count)
        missed_count=str(self.missed_count)
        self.master.grab_release()
        self.workbook.close()

        #workbook formating
        '''
        wb=openpyxl.load_workbook(workbookName)
        ws=wb['Sheet1']
        fill_pattern_red= PatternFill(patternType='solid', fgColor='C64747')
        fill_pattern_green= PatternFill(patternType='solid', fgColor='228B22')
        for i in correctList:
            row='A'+str(i)+':E'+str(i)
            ws[row].fill=fill_pattern_green
        for j in missedList:
            row='A'+str(j)+':E'+str(j)
            ws[row].fill=fill_pattern_red
        wb.save(workbookName)'''
        messagebox.showinfo("Correction Results", "Corrections picked up: "+correct_count+"\nCorrections missed: "+missed_count)
        self.getSaveLoc()
        
    def updateTerminal(self,text):
        self.terminal.set(text)

def main():
    from testscript import testscript
    testscript(QualityChecker)

if __name__=='__main__':
    main()
