################################################################################
# markup_checker.py
# Created: 4/5/23
# Author: Ethan de Leon
# Last Modified: Ethan de Leon
# Module Installs: PIL (pillow), pandas, cv2 (opencv-python), pdf2image
################################################################################

import os
import cv2
import pathlib
import pandas as pd
import numpy as np

from PIL import Image, ImageChops, ImageTk

from pdf2image import convert_from_path

POPPLER = r"\poppler-21.03.0\Library\bin"
HIGHLIGHT_COLOR = (255,0,255)
COLOR_BOUNDARIES = {
    "red":{"lower":[0, 50, 50], "upper":[20, 255, 255]},
    "green":{"lower":[36, 40, 35], "upper":[102, 255, 255]},
    "blue":{"lower":[110,50,50], "upper":[140, 255, 255]},
    "yellow":{"lower":[20, 100, 100], "upper":[30, 255, 255]},
}
CONTOUR_BUFFER = 20
AREA_LIMIT = 10

class MarkupChecker():
    def __init__(self, markupfile:str) -> None:
        self.markupfile = markupfile
        self.markup_df = MarkupChecker.find_markups(self.markupfile)
        MarkupChecker.draw_markup_highlights(self.markupfile,self.markup_df)
        pass

    def convert2jpg(filepath:str)->str:
        file_name = pathlib.Path(filepath).stem
        file_ext = pathlib.Path(filepath).suffix.lower()
        print(file_name)

        if file_ext not in [".jpg", ".jpeg", ".pdf", ".png", ".tiff"]:
            return False
        
        if (file_ext == ".jpg") or (file_ext == ".jpeg"):
            return filepath
        elif (file_ext == ".pdf"):
            # If the file is a pdf, we only want the first page as an image
            images = convert_from_path(filepath,poppler_path=POPPLER)
            image = images[0]
        else:
            image = Image.open(filepath)
            image = image.convert('RGB')
        
        image.save(".".join([file_name, ".jpg"]))

    def find_markups(dwg:str)->list[str,pd.DataFrame]:
        image = cv2.imread(dwg)
        hsvImage=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        contour_dict = {"color":[], "coords":[]}

        # loop over the boundaries
        # finds the contours of each color
        for color in COLOR_BOUNDARIES:
            cimage = cv2.imread(dwg)
            lower = np.array(COLOR_BOUNDARIES[color]["lower"], dtype = "uint8")
            upper = np.array(COLOR_BOUNDARIES[color]["upper"], dtype = "uint8")
            mask = cv2.inRange(hsvImage, lower, upper)

            contours, hierarchy = cv2.findContours(
                mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            coord_lst = []
            for c in contours:
                x, y, w, h  = cv2.boundingRect(c)
                coord_lst.append([x, y, x+w, y+h])

            rects, _, _ = MarkupChecker.clusterize(coord_lst, buffer = CONTOUR_BUFFER)
            contour_dict["color"] += [color] * len(rects)
            contour_dict["coords"] += rects
            cv2.waitKey(0)

        # Draws rectangles around all contours
        rectangles, types, tags = MarkupChecker.clusterize(
            contour_dict["coords"], type_lst = contour_dict["color"], 
            tag_lst=contour_dict["color"], buffer = CONTOUR_BUFFER)

        return pd.DataFrame({"color":types, "coords":rectangles, "tags":tags}).reset_index()
    
    # region Rectangle Clustering
    def clusterize(rect_lst:list, type_lst:list = [], tag_lst:list = [], buffer:int=1)->list:
        """Creates a list of clusted rectangles"""
        clusters = []
        tags = []
        types = []
        
        matched_count = 0
        for num, rect in enumerate(rect_lst):
            matched = False
            for cnum, cluster in enumerate(clusters):
                # Checks if the cluster and rectangle are matching type
                if type_lst and types:
                    if type_lst[num] != types[cnum]: continue

                # Checks if the rectangles and cluster overlap
                if MarkupChecker.rect_overlaps(rect, cluster):
                    matched = True
                    matched_count += 1
                    
                    # Updates cluster size
                    # buffer is used to help catch neighbors that are close to rectangle area
                    cluster[0] = min(cluster[0], rect[0]-buffer)
                    cluster[1] = min(cluster[1], rect[1]-buffer)
                    cluster[2] = max(cluster[2], rect[2]+buffer)
                    cluster[3] = max(cluster[3], rect[3]+buffer)

                    if tag_lst:
                        if isinstance(tag_lst[num], list): tags[cnum] += tag_lst[num] 
                        else: tags[cnum].append(tag_lst[num])
                    
            # Creates new clusters
            if not matched:
                # Filters out rectangles that are too small
                if (rect[2]-rect[0])*(rect[3]-rect[1])<AREA_LIMIT: continue

                # Adds tags to the cluster
                if tag_lst: 
                    if isinstance(tag_lst[num], list): tags += [tag_lst[num]]
                    else: tags.append([tag_lst[num]])
                
                # Adds typing to cluster
                if type_lst: types.append(type_lst[num])

                clusters.append(rect)

        # Removes duplicate tags 
        if tag_lst: return_tag = [list(set(x)) for x in tags]
        else: return_tag = []

        # If there were matched clusters in this iteration, the function 
        # recurses to get rid of any overlaping existing clusters
        if matched_count>0:
            return MarkupChecker.clusterize(clusters, tag_lst=return_tag, type_lst=types)
        else:
            return clusters, types, return_tag
        
    def range_overlap(a_min, a_max, b_min, b_max)->bool:
        return (a_min <= b_max) and (b_min <a_max)
    
    def rect_overlaps(r1, r2):
        return MarkupChecker.range_overlap(r1[0], r1[2], r2[0], r2[2]) \
           and MarkupChecker.range_overlap(r1[1], r1[3], r2[1], r2[3])
    
    # endregion

    def draw_markup_highlights(img_file:str, markup_df:pd.DataFrame):
        image = cv2.imread(img_file)
        for row in markup_df.iloc:
            rect = row['coords']
            cv2.rectangle(image,(rect[0],rect[1]),(rect[2],rect[3]),HIGHLIGHT_COLOR, 2)
            cv2.putText(image,str(row["index"]+1),(rect[0]+5,rect[1]+20), 
                        cv2.FONT_HERSHEY_SIMPLEX, .5,HIGHLIGHT_COLOR,1,cv2.LINE_AA)
        
        cv2.imshow("Markups Highlighted", image)
        
        cv2.imwrite(pathlib.Path(img_file).stem + "Highlighted.jpg", image)
        cv2.waitKey(10000)

    def compare_drawings(dwg1:str, dwg2:str)->None:
        pass

MarkupChecker("SchematicTestMarkUp.jpg")