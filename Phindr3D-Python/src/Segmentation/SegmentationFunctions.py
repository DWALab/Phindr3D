# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of src <https://github.com/DWALab/Phindr3D>.
#
# src is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# src is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with src.  If not, see <http://www.gnu.org/licenses/>.

import cv2 as cv
import numpy as np
import tifffile as tf
import skimage.io as io
from scipy import ndimage
from skimage import filters
from skimage import morphology as morph
from skimage import segmentation as seg

"""Functions for segmentation. Referenced from
https://github.com/DWALab/Phindr3D/tree/9b95aebbd2a62c41d3c87a36f1122a78a21019c8/Lib
and
https://github.com/SRI-RSST/Phindr3D-python/blob/ba588bc925ef72c72103738d17ea922d20771064/phindr_functions.py
"""
def imfinfo(filename):
    class info:
        pass
    info = info()
    tif = tf.TiffFile(filename)
    file = tif.pages[0]
    immetadata = {}
    for tag in file.tags.values():
        immetadata[tag.name] = tag.value
    info.Height = immetadata['ImageLength']
    info.Width = immetadata['ImageWidth']
    info.Format = 'tif'
    return info 

def stdfilt(img, kernel_size=5):
    #called in getfsImage
    """
    apparently this is a faster way to compute std deviation filter ( https://nickc1.github.io/python,/matlab/2016/05/17/Standard-Deviation-(Filters)-in-Matlab-and-Python.html )
    
    result is similar to matlab stdfilt function but not perfect match.
    """
    c1 = ndimage.filters.uniform_filter(img, size=kernel_size, mode='reflect')
    c2 = ndimage.filters.uniform_filter((img*img), size=kernel_size, mode='reflect')
    res = c2 - c1*c1
    res[res < 0] = 0
    return np.sqrt(res)

def smoothImage(IM, cutOff):
    #smooths image in frequency domain
    m = np.max(IM.shape)
    if cutOff > 0.99:
        cutOff = 0.99
    elif cutOff <= 0: #in matlab code is <. changed to <= because min value it is reset to is 0.1
        cutOff = 0.01
    m /= 2
    x, y = np.mgrid[ -(m-0.5):(m-0.5)+1, -(m-0.5):(m-0.5)+1 ] #might need to use actual meshgrid and define index locations with linspace or arange
    x /= m
    y /= m #shouldnt this be divided by n? who knows
    x = np.sqrt(x**2 + y**2)
    x = (x < cutOff).astype(np.float64)
    struct = np.ones((50,50))/(2500) #50 by 50 seems very big, but whatever
    x = cv.filter2D(x, -1, struct)
    x[x<0] = 0
    return np.abs(np.fft.ifft2(np.fft.fftshift(np.fft.fft2(IM))*x))

def imadjust(img, inrange=[0,1], outrange=[0,1], gamma=1):
    #convert image range from inrage to outrange # solution from ( https://stackoverflow.com/questions/39767612/what-is-the-equivalent-of-matlabs-imadjust-in-python )
    a, b = inrange
    c, d = outrange
    adjusted = (((img - a)/(b-a)) ** gamma) * (d-c) + c
    return adjusted

def bwareaopen(img, num, conn=8):
    """
    like morphological opening, but dont use a filter, just do connected components and remove small groups of connected components

    img: binary image
    num: number of components threshold for being allowed
    """
    #want fully connected components
    if conn == 8:
        struct = np.ones((3,3))
    elif conn == 4:
        struct = np.ones((3,3))
        struct[0, 0] = 0
        struct[-1, 0] = 0
        struct[0, -1] = 0
        struct[-1, -1] = 0 #take out corners
    labelled, dump = ndimage.label(img, structure = struct)
    labels = np.unique(labelled)
    for label in labels:
        if np.sum(labelled == label) < num:
            img[labelled == label] = 0 
    return img

def segmentImage(I, minArea):
    imthreshold = getImageThreshold(I.astype(np.float64))
    bw = bwareaopen(I>imthreshold, minArea, conn=8) #conn used to be 4 here
    struct = np.ones((3,3))
    L, N = ndimage.label(bw, structure = struct)
    #set border to 1
    nI = np.zeros(I.shape)
    nI[:, np.r_[0, nI.shape[1]-1]] = 1 #hopefully this is correct indexing
    nI[np.r_[0, nI.shape[0]-1], :] = 1
    nL = L * nI
    uL = np.unique(nL)
    for i in range(0, uL.size): #this is a little redundant, does same as bwareaopen, as a double check after we remove the outside boundary.
        ii = L==uL[i]
        areaVal = np.sum(ii)
        if areaVal < minArea:
            L[ii] = 0
    return L

def imfill(img):
    """
    similar to matlab imfill('holes')
    flood fill holes in binary image that are separate from the border. 
    algo:
    padd outer borders to ensure flooding from corner goes all around
    flood from border, invert
    combine inverted flooded with binary map (OR operation)
    
    img should be binary map 
    """
    rows, cols = img.shape
    tmp = np.zeros((rows+2, cols+2))
    tmp[1:-1, 1:-1] = img #make a copy of img padded on all sides by zeros
    flooded = seg.flood_fill(tmp, (0,0), 1, in_place=True) #default is already full connectivity including diagonals as desired.
    inverted = flooded*(-1) + 1
    inverted = inverted[1:-1, 1:-1] #get rid of padding
    return np.logical_or(img, inverted) #works!

def imextendedmax(img, H):
    """
    pick out regional maxima of H maxima transform

    analog to imextendedmaxima function from matlab
    """
    foot = np.ones((3,3))
    h_maxed = HMAX(img, H)
    return morph.local_maxima(h_maxed, footprint=foot, allow_borders=True)

def HMAX(f, h):
    """
    H-maxima transform (reconstruction by dilation of image, using (image - H) as the seed/marker)
    """
    img = f.copy().astype(np.float64)
    seed = img - h
    seed[seed<0] = 0
    return morph.reconstruction(seed, img, method='dilation')

def imimposemin(img, minima):
    """
    assume integer img values starting at 0
    """
    marker = np.full(img.shape, np.inf)
    marker[minima == 1] = 0
    mask = np.minimum((img + 1), marker)
    return morph.reconstruction(marker, mask, method='erosion')

def imcomplement(image):
    """Equivalent to matlabs imcomplement function"""
    if image.dtype == 'float64':
        max_type_val = 1
    else:
        max_type_val = np.finfo(image.dtype).max
    return max_type_val - image

def watershed(img):
    """
    img should be the distance transform already flipped to be "deep" where objects are
    """
    # coords = peak_local_max((-img), footprint=np.ones((3,3)))
    struct = np.ones((3,3)) #structure was 3,3
    dilated = cv.dilate(-img, struct)
    mask = ((-img) >= dilated).astype('uint8') #both used to be -img
    # # mask = np.zeros(img.shape, dtype=bool)
    # # mask[tuple(coords.T)] = True
    markers, ret = ndimage.label(mask)
    return seg.watershed(img, markers=markers, watershed_line=True)

def removeBorderObjects(L, dis):
    """
    remove objects touching border of image
    """
    borderimage = np.zeros(L.shape)
    borderimage[:, :dis] = 1
    borderimage[:, -dis:] = 1
    borderimage[:dis, :] = 1
    borderimage[-dis:, :] = 1
    L2 = borderimage * L
    uL = np.unique(L2)
    for borderL in uL:
        L[L == borderL] = 0
    L = resetLabelImage(L)
    return L

def resetLabelImage(L):
    """
    rename labels in a labelled image from 1 to # of labels
    """
    uL = np.unique(L)
    uL = uL[uL > 0] #remove background
    for i, label in enumerate(uL):
        ii = (L == label)
        L[ii] = i+1
    return L.astype('uint8')

def regionprops(watershed_img, final_im, IM11):
    """
    regionprops:
    area of each labelled region
    mean intensity of final_im in each labelled region
    mean intensity of entropy_filter on IM11 in each labelled region
    """
    labels = np.unique(watershed_img)
    if labels[0] == 0:
        labels = labels[1:]
    areas = np.zeros(labels.shape)
    final_im_intensities = np.zeros(labels.shape)
    entropy = np.zeros(labels.shape)
    ent = filters.rank.entropy(IM11, footprint=np.ones((5,5)))
    for i, label in enumerate(labels):
        areas[i] = np.sum((watershed_img == label))
        final_im_intensities[i] = np.mean(final_im[watershed_img == label])
        entropy[i] = np.mean(ent[watershed_img == label])
    return labels, areas, final_im_intensities, entropy

def getImageThreshold(IM):
    maxBins = 256
    freq, binEdges = np.histogram(IM.flatten(), bins=maxBins)
    binCenters = binEdges[:-1] + np.diff(binEdges)/2
    meanIntensity = np.mean(IM.flatten())
    numThresholdParam = len(freq)
    binCenters -= meanIntensity
    den1 = np.sqrt((binCenters**2) @ freq.T)
    numAllPixels = np.sum(freq) #freq should hopefully be a 1D vector so summ of all elements should be right.
    covarMat = np.zeros(numThresholdParam)
    for iThreshold in range(numThresholdParam):
        numThreshPixels = np.sum(freq[binCenters > binCenters[iThreshold]])
        den2 = np.sqrt( (((numAllPixels - numThreshPixels)*(numThreshPixels))/numAllPixels) )
        if den2 == 0:
            covarMat[iThreshold] = 0 #dont want to select these, also want to avoid nans
        else:
            covarMat[iThreshold] = (binCenters @ (freq * (binCenters > binCenters[iThreshold])).T) / (den1*den2) #i hope this is the right mix of matrix multiplication and element-wise stuff.
    imThreshold = np.argmax(covarMat) #index makes sense here.
    imThreshold = binCenters[imThreshold] + meanIntensity
    return imThreshold

def getfsimage(imstack, segchannel):
    """
    % getfsimage - Outputs best focussed image from a set of 3D image slices
    % Input:
    % imdata: metadata for a single image id
    % channel: segmentation channel column header
    % Output:
    % final_image: Best focussed image
    """
    stackLayers = imstack.stackLayers
    zVals = list(stackLayers.keys())
    imInfo = imfinfo( stackLayers[zVals[0]].channels[segchannel].channelpath )
    prevImage = np.full((imInfo.Height, imInfo.Width), -1*np.inf)
    focusIndex = np.zeros((imInfo.Height, imInfo.Width))
    finalImage = np.zeros((imInfo.Height, imInfo.Width))
    for z in zVals:
        IM = io.imread( stackLayers[zVals[0]].channels[segchannel].channelpath ).astype(np.float64)
        imtmp = stdfilt(IM, kernel_size=5)
        xgrad = ndimage.sobel(imtmp, axis=0) #directional gradients
        ygrad = ndimage.sobel(imtmp, axis=1)
        tmp = np.sqrt( (xgrad*xgrad) + (ygrad*ygrad) ) #gradient magnitude
        ii = (tmp >= prevImage)
        focusIndex[ii] = z
        finalImage[ii] = IM[ii]
        prevImage = np.maximum(tmp, prevImage)
    return finalImage, focusIndex

def getfsimage_multichannel(imstack):
    """
    % getfsimage - Outputs best focussed image from a set of 3D image slices (using multichannel max intensity.)
    % Input:
    % imdata: metadata for a single image id
    % Output:
    % final_image: Best focused image
    """
    stackLayers = imstack.stackLayers
    zVals = list(stackLayers.keys())
    chans = list(stackLayers[zVals[0]].channels.keys())
    #want to end up with fnames == images from single channel being read in stack order.
    imInfo = imfinfo( stackLayers[zVals[0]].channels[chans[0]].channelpath )
    prevImage = np.full((imInfo.Height, imInfo.Width), -1*np.inf)
    focusIndex = np.zeros((imInfo.Height, imInfo.Width))
    finalImage = np.zeros((imInfo.Height, imInfo.Width))
    for z in zVals:
        for i, c in enumerate(chans):
            if i == 0:
                IM = io.imread(stackLayers[z].channels[c].channelpath).astype(np.float64)
            else:
                IM = np.maximum(IM, io.imread(stackLayers[z].channels[c].channelpath).astype(np.float64))
        imtmp = stdfilt(IM, kernel_size=5)
        xgrad = ndimage.sobel(imtmp, axis=0) #directional gradients
        ygrad = ndimage.sobel(imtmp, axis=1)
        tmp = np.sqrt( (xgrad*xgrad) + (ygrad*ygrad) ) #gradient magnitude
        ii = (tmp >= prevImage)
        focusIndex[ii] = z
        finalImage[ii] = IM[ii]
        prevImage = np.maximum(tmp, prevImage)
    return finalImage, focusIndex

def getSegmentedOverlayImage(final_im, pdict):
    #min_area_spheroid, radius_spheroid, smoothin_param, entropy_thresh, intensity_threshold, scale_spheroid):
    # newfim = final_im.copy()
    SE = morph.disk(2*pdict['radius_spheroid'])
    IM2 = cv.morphologyEx(final_im.astype('uint16'), cv.MORPH_TOPHAT, SE).astype('float64')
    IM4 = smoothImage(IM2, pdict['smoothin_param'])
    minIM = np.min(IM4)
    maxIM = np.max(IM4)
    IM4 = (IM4 - minIM)/(maxIM - minIM) #rescale 0-1
    IM4 = imadjust(IM4, gamma=0.5)
    # #im4 is float image from 0 to 1
    IM6 = segmentImage(IM4, pdict['min_area_spheroid'])
    IM6 = (IM6 > 0).astype('uint8')
    IM6 = cv.morphologyEx(IM6, cv.MORPH_CLOSE, np.ones((3,3))) #this operation is iterated 3 times in matlab script. No reason to do this because morphological closing is idempotent.
    IM6 = imfill(IM6)
    IM6 = bwareaopen(IM6, 20) #open sets of connected components with less than 20 members 
    #im6 is binary image
    IM7 = ndimage.distance_transform_edt(IM6)# matlab bwdist gives euclidean distance transform from non-zero elements. use on binary inverse of IM6 so distance transform from zero-elements. ndimage.distance_transform_edt is already distance from zero elements
    #im7 is float image
    if pdict['scale_spheroid'] > 1:
        pdict['scale_spheroid'] = 1
    elif pdict['scale_spheroid'] <= 0:
        pdict['scale_spheroid'] = 0.1
    splitFactor = pdict['scale_spheroid'] * pdict['radius_spheroid']
    IM9 = imextendedmax(IM7, splitFactor)
    bw = np.logical_or(np.logical_not(IM6), IM9)
    IM10 = imimposemin(imcomplement(IM4*IM7),bw)
    L = watershed(IM10)
    L = np.maximum(L-1, 0) #background label is 1, so replace with 0.
    if pdict['remove_border_objects'] == True:
        L = removeBorderObjects(L, 30) #used to be 10.
    IM11 = (final_im - np.min(final_im)) / (np.max(final_im) - np.min(final_im))
    labels, areas, final_im_means, entropies = regionprops(L, final_im, IM11)
    # return L, labels, areas, final_im_means, entropies
    if np.sum(areas) != 0:
        i2 = areas >= pdict['min_area_spheroid']
        i3 = final_im_means >= pdict['intensity_threshold']
        i4 = entropies >= pdict['entropy_threshold']
        ii = ((i2*i3*i4) == 0) #ii is True at the indices of all the labels that we want to discard
        for l in labels[np.nonzero(ii)]:
            L[L==l] = 0
    L = resetLabelImage(L)
    return L 

def getFocusplanesPerObjectMod(labelImage, fIndex, numZ=None):
    """
    computes optimal focus plane for each object in a 3d stack

    labelImage: bool image indicating presence of object
    """
    if numZ == None:
        numZ = np.max(fIndex)
    try:
        ll = np.zeros(2)
        ii = fIndex[labelImage]
        bins = np.append(np.linspace(0.5, numZ-0.5, num=int(numZ), endpoint=True), [numZ-0.5]) #this weird bin format gives a repeated final bin edge value, replicates histc function bin behaviour from matlab.
        n = np.histogram(ii, bins=bins)[0] #1d histogram array.
        n = n/np.sum(n)
        rndPoint = 1/numZ
        p = np.argwhere(n > rndPoint)+1 #find returns linear indices, so does argwhere, except starting at 0. for matlab , indices corresponds 1-1 to z-planes. need +1 to get proper z-planes values.
        if p.size == 0:
            minN = 1
            maxN = numZ
        else:
            minN = max([1, np.min(p)-2])
            maxN = min([numZ, np.max(p)+2])

        ll[0] = int(minN)
        ll[1] = int(maxN)
    except Exception as e:
        print('\nexception found')
        print(e)
        print()
    return ll #want ll to be zplane values, corresponding to fIndex values.

# end SegmentationFunctions
