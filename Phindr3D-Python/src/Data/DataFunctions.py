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

import os
import re
import tifffile as tf
import pandas as pd
import numpy as np
# import imageio.v2 as io
# import imagecodecs

class DataFunctions:
    """Static methods for Metadata handling. Referenced from
    https://github.com/DWALab/Phindr3D/tree/9b95aebbd2a62c41d3c87a36f1122a78a21019c8/Lib
    and
    https://github.com/SRI-RSST/Phindr3D-python/blob/ba588bc925ef72c72103738d17ea922d20771064/phindr_functions.py
    No constructor. All parameters and methods are static.
    """

    @staticmethod
    def parseAndCompareRegex(sampleFile, regex):
        """Given a sample file name string and a regex string, parse the file name
            and find the fields specified in the regular expression. If no fields
            can be found, return empty dictionary. Otherwise, return a dictionary with the
            field names and their values. On re.error return empty dictionary. """
        # Check that both sampleFile and regex are strings
        if not isinstance(sampleFile, str) or not isinstance(regex, str):
            return {}
        # else
        outdict = {}
        try:
            m = re.fullmatch(regex, sampleFile)
            if m is None:
                outdict = {}
            else:
                outdict = m.groupdict()
        except re.error:
            outdict = {}
        return outdict
    # end parseAndCompareRegex

    @staticmethod
    def directoryExists(theDir):
        """Check whether the directory specified by the string theDir exists.
            Raises TypeError if theDir is not a string.
            Returns True if the directory exists, False if it does not.
            """
        if not isinstance(theDir, str):
            raise TypeError("Wrong type in static method DataFunctions.directoryExists. Argument must be a string.")
        else:
            return os.path.exists(theDir)
    # end directoryExists

    @staticmethod
    def regexPatternCompatibility(regex):
        """Provides compatibility between MATLAB regular expressions and Python.
            Replaces '?<' patterns with '?P<' to make compatible with re.fullmatch function.
            It first checks if '?<' corresponds to a '?<=' or '?<!' pattern first before replacing
            part of Python specific regular expression syntax."""
        # set the default value if no modifications are necessary
        outstring = ""
        strlist = regex.split("?<")
        if len(strlist) <= 1:
            return regex
        else:
            for i in range(len(strlist)-1):
                outstring = outstring+strlist[i]
                try:
                    theSep = "?<" if (strlist[i+1][0] == '=' or strlist[i+1][0] == '!') else "?P<"
                except IndexError:
                    theSep = "?<"
                outstring = outstring + theSep
            outstring = outstring+strlist[len(strlist)-1]
        return outstring
    # end regexPatternCompatibility

    @staticmethod
    def createMetadata(folder_path, regex, mdatafilename='metadata_python.txt'):
        """
        This function creates a metadata txt file in the same format as used in the matlab Phindr implementation

        folder_path: path to image folder (full or relative)
        regex: regular expression matching image file names. must include named groups for all required image attributes (wellID, field, treatment, channel, stack, etc.)
        Matlab style regex can be adapted by adding P before group names. ex. : "(?P<WellID>\w+)__(?P<Treatment>\w+)__z(?P<Stack>\d+)__ch(?P<Channel>\d)__example.tiff"
        mdatafilename: filename for metadatafile that will be written.

        regex groups MUST INCLUDE Channel and Stack and at least one other image identification group
        regex groups CANNOT include ImageID or
        """

        f = os.listdir(folder_path)
        metadatafilename = f'{os.path.abspath(folder_path)}\\{mdatafilename}'
        #read images in folder
        rows = []
        for i, file in enumerate(f):
            m = re.fullmatch(regex, file)
            if m != None:
                d = m.groupdict()
                rows.append(d)
        #make sure rows is not empty and that Channel and Stack are in the groups.
        if len(rows) == 0:
            return False
        if ('Channel' not in rows[0].keys()) or ('Stack' not in rows[0].keys()):
            raise MissingChannelStackError
        tmpdf = pd.DataFrame(rows)
        #make new dataframe with desired colummns
        tags = tmpdf.columns
        channels = np.unique(tmpdf['Channel'])
        cols = []
        for chan in channels:
            cols.append(f'Channel_{chan}')
        for tag in tags:
            if tag not in ['Channel', 'Stack', '_file']:
                cols.append(tag)
        cols.append('Stack')
        cols.append('MetadataFile')
        df = pd.DataFrame(columns=cols)
        #add data to the new dataframe
        stacksubset = [tag for tag in tags if tag not in ['Channel', '_file']]
        idsubset = [tag for tag in tags if tag not in ['Channel', '_file', 'Stack']]
        df[stacksubset] = tmpdf.drop_duplicates(subset = stacksubset)[stacksubset]
        df.reset_index(inplace=True, drop=True)
        #add unique image ids based on the "other tags"
        idtmp = tmpdf.drop_duplicates(subset = idsubset)[idsubset].reset_index(drop=True)
        idtmp.reset_index(inplace=True)
        idtmp.rename(columns={'index':'ImageID'}, inplace=True)
        idtmp['ImageID'] = idtmp['ImageID'] + 1
        df = pd.merge(df, idtmp, left_on=idsubset, right_on=idsubset)
        #give metadatafilename
        df['MetadataFile'] = metadatafilename
        # fill in file paths for each channel
        fileparts = re.split(r'\(\?P<\w+>\.?\\?\w?\+?\)', regex) #split the regex around all the capturing groups.
        for index, row in df.iterrows(): #iterate through the rows of the df to re-get capturing group info 
            for chan in channels:        #also have to go through the channels to get channel info
                fname = ''
                for i, dkey in enumerate(d.keys()): #build the expected filename back up from the split regex.
                    fname += fileparts[i]
                    if dkey == 'Channel':
                        fname += str(chan)
                    else:
                        fname += row[dkey]
                fname += fileparts[i+1] #add the .tif(f)
                df.iat[index, df.columns.get_loc(f'Channel_{chan}')] = os.path.abspath(f'{folder_path}\\{fname}') #place the name at the right spot
        df.to_csv(metadatafilename, sep='\t', index=False)
        return True # return value to indicate success of function
    # end createMetadata

    @staticmethod
    def mat_dot(A, B, axis=0):
        """
        equivalent to dot product for matlab (can choose axis as well)
        """
        return np.sum(A.conj() * B, axis=axis)
    # end mat_dot

    # regexpi

    @staticmethod
    def im2col(img, blkShape):
        # this function is modified from https://github.com/Mullahz/Python-programs-for-MATLAB-in-built-functions/blob/main/im2col.py
        # provides same functionality as matlab's im2col builtin function in distinct mode
        # actuall tested and compared to matlab version this time. produces nice results.
        imgw = img.shape[0]
        imgh = img.shape[1]
        blk_sizew = blkShape[0]
        blk_sizeh = blkShape[1]

        mtx = img
        m1c = (imgw * imgh) // (blk_sizew * blk_sizeh)
        m1 = ((blk_sizew * blk_sizeh), m1c)
        blk_mtx = np.zeros(m1)

        itr = 0
        for i in range(1, imgw, blk_sizew):
            for j in range(1, imgh, blk_sizeh):
                blk = mtx[i - 1:i + blk_sizew - 1, j - 1:j + blk_sizeh - 1].ravel()
                itr = itr + 1
                blk_mtx[:, itr - 1] = blk
        return blk_mtx
    # end im2col

    @staticmethod
    def imfinfo(filename):
        class info:
            pass

        info = info()
        tif = tf.TiffFile(filename)
        file = tif.pages[0]
        metadata = {}
        for tag in file.tags.values():
            metadata[tag.name] = tag.value
        info.Height = metadata['ImageLength']
        info.Width = metadata['ImageWidth']
        info.Format = 'tif'
        return info
    # end imfinfo

    @staticmethod
    def rescaleIntensity(im, low=0, high=1):
        """Called in getIndividualChannelThreshold.
        Rescales intensity of image based on lower and upper bounds
        """
        im = im.astype(np.float64)
        diffIM = high - low
        im = (im - low) / diffIM
        im[im > 1] = 1
        im[im < 0] = 0
        return im
    # end rescaleIntensity

    @staticmethod
    def selectPixelsbyweights(x):
        """called in getTrainingPixels. x type is """
        n, bin_edges = np.histogram(x, bins=(int(1/0.025) + 1), range=(0,1), )
        q = np.digitize(x, bin_edges)
        n = n / np.sum(n)
        p = np.zeros(q.shape)
        for i in range(0, n.shape[0]):
            p[q==i] = n[i]
        p = 1 - p
        p = np.sum(p>np.random.random((q.shape)), axis=1) #q shape may or may not be correct
        p = p != 0
        p = x[p, :]
        return p
    # end selectPixelsbyweights

    @staticmethod
    def getImageThreshold(IM):
        """called in getIndividualChannelThreshold"""
        maxBins = 256
        freq, binEdges = np.histogram(IM.flatten(), bins=maxBins)
        binCenters = binEdges[:-1] + np.diff(binEdges) / 2
        meanIntensity = np.mean(IM.flatten())
        numThresholdParam = len(freq)
        binCenters -= meanIntensity
        den1 = np.sqrt((binCenters ** 2) @ freq.T)
        numAllPixels = np.sum(
            freq)  # freq should hopefully be a 1D vector so summ of all elements should be right.
        covarMat = np.zeros(numThresholdParam)
        for iThreshold in range(numThresholdParam):
            numThreshPixels = np.sum(freq[binCenters > binCenters[iThreshold]])
            den2 = np.sqrt((((numAllPixels - numThreshPixels) * (numThreshPixels)) / numAllPixels))
            if den2 == 0:
                covarMat[iThreshold] = 0  # dont want to select these, also want to avoid nans
            else:
                covarMat[iThreshold] = (binCenters @ (freq * (binCenters > binCenters[iThreshold])).T) / (
                            den1 * den2)  # i hope this is the right mix of matrix multiplication and element-wise stuff.
        imThreshold = np.argmax(covarMat)  # index makes sense here.
        imThreshold = binCenters[imThreshold] + meanIntensity
        return imThreshold
    # end getImageThreshold

    @staticmethod
    def getImageWithSVMVOverlay(IM, param, type):
        """
        I assume this means get image with superVoxel or megaVoxel overlay.
        % param.tileX = 10;
        % param.tileY = 10;
        % param.megaVoxelTileX = 5;
        % param.megaVoxelTileY = 5;
        """
        xOffset = np.mod(IM.shape[0], param.tileX)
        yOffset = np.mod(IM.shape[1], param.tileY)
        param.croppedX = IM.shape[0] - xOffset
        param.croppedY = IM.shape[1] - yOffset
        superVoxelXOffset = np.mod(param.croppedX/ param.tileX, param.megaVoxelTileX)
        superVoxelYOffset = np.mod(param.croppedY/ param.tileY, param.megaVoxelTileY)
        spX = int((param.croppedX/ param.tileX))
        spY = int((param.croppedY/ param.tileY))
        tmpX = int((param.croppedX/ param.tileX) + superVoxelXOffset)
        tmpY = int((param.croppedY/ param.tileY) + superVoxelYOffset)

        if type == 'SV':
            IM[range(0,IM.shape[0],int(spX/param.megaVoxelTileX)), :,:] = (0.7, 0.7, 0.7, 1.0)
            IM[:, range(0,IM.shape[1], int(spY/param.megaVoxelTileY)),:] = (0.7, 0.7, 0.7, 1.0)
            IM[range(1,IM.shape[0],int(spX/param.megaVoxelTileX)), :,:] = (0.7, 0.7, 0.7, 1.0)
            IM[:, range(1,IM.shape[1], int(spY/param.megaVoxelTileY)),:] = (0.7, 0.7, 0.7, 1.0)

        else:
            IM[range(0,IM.shape[0],tmpX), :,:] = (1.0, 1.0, 1.0, 1.0)
            IM[:, range(0,IM.shape[1],tmpY),:] = (1.0, 1.0, 1.0, 1.0)
            IM[range(1,IM.shape[0],tmpX), :,:] = (1.0, 1.0, 1.0, 1.0)
            IM[:, range(1,IM.shape[1],tmpY),:] = (1.0, 1.0, 1.0, 1.0)

        return IM
    # end getImageWithSVMVOverlay


# end DataFunctions

# error classes
class MissingChannelStackError(Exception):
    pass


def test_directoryExists():
    """A set of tests of the static method directoryExists"""
    success = "Success in test_directoryExists test "
    failure = "Failure in test_directoryExists test "
    # Test 1
    tnum = 1
    inVal1 = 5
    try:
        print(failure+str(tnum) if DataFunctions.directoryExists(inVal1) else failure+str(tnum))
    except TypeError:
        print(success+str(tnum))

    # Test 2
    tnum = 2
    # Only works on Windows
    inVal2 = "C://Windows//System32"
    try:
        print(success+str(tnum) if DataFunctions.directoryExists(inVal2) else failure+str(tnum))
    except TypeError:
        print(failure+str(tnum))

    # Test 3
    tnum = 3
    inVal3 = "C://nowhere_but_here"
    try:
        print(failure+str(tnum) if DataFunctions.directoryExists(inVal3) else success+str(tnum))
    except TypeError:
        print(failure+str(tnum))
# end test_directoryExists


def test_parseAndCompareRegex():
    """A set of tests of the static method parseAndCompareRegex"""
    success = "Success in test_parseAndCompareRegex test "
    failure = "Failure in test_parseAndCompareRegex test "
    # Test 1
    tnum = 1
    t1expected = {'Well': 'r03c19', 'Field': '01', 'Stack': '15', 'Channel': '2'}
    t1file = "r03c19f01p15-ch2sk1fk1fl1.tiff"
    t1regex = "(?<Well>\w+)f(?<Field>\d+)p(?<Stack>\d+)-ch(?<Channel>\d).*.tif(f)?"
    t1regex = DataFunctions.regexPatternCompatibility(t1regex)
    t1out = DataFunctions.parseAndCompareRegex(t1file, t1regex)
    print(success + str(tnum) if t1out == t1expected else failure + str(tnum))

# end test_parseAndCompareRegex


if __name__ == '__main__':
    """Tests of the static methods that can be run directly."""

    test_directoryExists()
    test_parseAndCompareRegex()

# end if main
