################################################################################
# markup_checker.py
# Created: 4/5/23
# Author: Ethan de Leon
# Last Modified: Ethan de Leon
# Module Installs: PIL (pillow), pandas, cv2 (opencv-python), pdf2image
################################################################################

import cv2
import fitz
import pathlib
import pandas as pd
import numpy as np
from PIL import Image

POPPLER = r"\poppler-21.03.0\Library\bin"
HIGHLIGHT_COLOR = (255,0,255)
COLOR_BOUNDARIES = {
    "red1":{"lower":[0, 50, 50], "upper":[10, 255, 255]},
    "red2":{"lower":[170, 50, 50], "upper":[180, 255, 255]},
    "green":{"lower":[40, 50, 50], "upper":[85, 255, 255]},
    "blue":{"lower":[86,50,50], "upper":[140, 255, 255]},
    "yellow":{"lower":[20, 50, 50], "upper":[35, 255, 255]},
}
CONTOUR_BUFFER = 20
AREA_LIMIT = 10

# Alignment Macros
MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15

class MarkupChecker():
    def convert2jpg(filepath:str, save=True)->str:
        file_name = pathlib.Path(filepath).stem
        file_ext = pathlib.Path(filepath).suffix.lower()

        if file_ext not in [".jpg", ".jpeg", ".pdf", ".png", ".tiff"]:
            return False
        
        if (file_ext == ".jpg") or (file_ext == ".jpeg"):
            return filepath
        
        outputfile = "".join([file_name, ".jpg"])
        if not save:
            return outputfile
        
        if (file_ext == ".pdf"):
            # If the file is a pdf, we only want the first page as an image
            doc = fitz.open(filepath)
            zoom = 1
            mat = fitz.Matrix(zoom, zoom)
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix = mat)
            pix.save(outputfile)
            doc.close()
        else:
            image = Image.open(filepath)
            image = image.convert('RGB')
            image.save(outputfile)
        return outputfile

    def find_markups(dwg:str)->pd.DataFrame:
        """Finds the markups and outputs a dataframe of ROI data"""
        dwg = MarkupChecker.convert2jpg(dwg)
        image = cv2.imread(dwg)
        hsvImage=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        contour_dict = {"color":[], "coords":[]}

        # loop over the boundaries
        # finds the contours of each color
        for color in COLOR_BOUNDARIES:
            lower = np.array(COLOR_BOUNDARIES[color]["lower"], dtype = "uint8")
            upper = np.array(COLOR_BOUNDARIES[color]["upper"], dtype = "uint8")
            mask = cv2.inRange(hsvImage, lower, upper)

            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, 
                                                   cv2.CHAIN_APPROX_SIMPLE)
            coord_lst = []
            for c in contours:
                x, y, w, h  = cv2.boundingRect(c)
                coord_lst.append([x, y, x+w, y+h])

            # Creating ROIs for clusters
            rects, _, _ = MarkupChecker.clusterize(
                coord_lst, type_lst=[color] * len(contours), buffer = CONTOUR_BUFFER)
            contour_dict["color"] += [color] * len(rects)
            contour_dict["coords"] += rects

        return pd.DataFrame({"color":contour_dict["color"], 
                             "coords":contour_dict["coords"]}).reset_index()
    
    # region ROI Clustering
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
                    cluster[0] = min(cluster[0], rect[0]-buffer) #x1
                    cluster[1] = min(cluster[1], rect[1]-buffer) #y1
                    cluster[2] = max(cluster[2], rect[2]+buffer) #x2
                    cluster[3] = max(cluster[3], rect[3]+buffer) #y2

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

    def draw_markup_highlights(img_file:str or np.ndarray, markup_df:pd.DataFrame, show=False):
        if isinstance(img_file, np.ndarray):
            image = img_file
        else: 
            img_file = MarkupChecker.convert2jpg(img_file, save = False)
            image = cv2.imread(img_file)

        for row in markup_df.iloc:
            rect = row['coords']
            cv2.rectangle(image,(rect[0],rect[1]),(rect[2],rect[3]),HIGHLIGHT_COLOR, 2)
            cv2.putText(image,str(row["index"]+1),(rect[0]+5,rect[1]+20), 
                        cv2.FONT_HERSHEY_SIMPLEX, .5,HIGHLIGHT_COLOR,1,cv2.LINE_AA)
        
        if show:
            cv2.imshow("Markups Highlighted", image)
        return image        

    def compare_drawings(dwg1:str, dwg2:str)->None:
        pass

    def align_drawings(dwg1:str, dwg2:str)->cv2:
        """Aligns two similar images together
        @dwg1: reference image, the image that stays the same
        @dwg2: the image that will be aligned"""

        ref_img = cv2.imread(dwg1, cv2.IMREAD_COLOR)
        input_img = cv2.imread(dwg2, cv2.IMREAD_COLOR)

        # Detect ORB features and compute descriptors.
        orb = cv2.ORB_create(MAX_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(
            cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY), None)
        keypoints2, descriptors2 = orb.detectAndCompute(
            cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY), None)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors2, descriptors1, None)

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove bad matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # Draw top matches
        img_matches = cv2.drawMatches(ref_img, keypoints2, input_img, keypoints1, matches, None)

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points2[i, :] = keypoints2[match.queryIdx].pt
            points1[i, :] = keypoints1[match.trainIdx].pt

        # Find homography
        h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

        # Use homography to warp and align input image
        height, width, _ = ref_img.shape
        output_img = cv2.warpPerspective(input_img, h, (width, height))

        return output_img, img_matches



if __name__ == "__main__":
    pass