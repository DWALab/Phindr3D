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
import pandas as pd
import numpy as np

class DataFunctions:
    """Static methods for Metadata handling. Referenced from
    https://github.com/DWALab/Phindr3D/tree/9b95aebbd2a62c41d3c87a36f1122a78a21019c8/Lib
    and
    https://github.com/SRI-RSST/Phindr3D-python/blob/ba588bc925ef72c72103738d17ea922d20771064/phindr_functions.py
    No constructor. All parameters and methods are static.
    """

    # replace this with a single comparison for one file to make a dictionary with the
    # Well, Stack, Channel, etc. to display in a window after clicking "Evaluate Regular Expression"

    @staticmethod
    def parseAndCompareRegex(sampleFile, regex):
        """Given a sample file name string and a regex string, parse the file name
            and find the fields specified in the regular expression. If no fields
            can be found, return None. Otherwise, return a dictionary with the
            field names and their values."""

        # Check that both sampleFile and regex are strings

        m = re.fullmatch(regex, sampleFile)
        if m != None:
            pass
            # ...



    # end parseAndCompareRegex


    @staticmethod
    def parseAndSearchRegex(folderPath, regex, numResults=-1, useAbsPath=True):
        """This function returns an empty list if the folderPath cannot be found,
            or if the regular expression returns no results.
            It returns a list of file name strings on success,
            where the number of list elements will be all the file names
            in the directory if numResults is less than 0.
            If numResults is less than the number of files in the directory,
            numResults elements are returned. If numResults is greater, then
            the list will contain all the file names in the directory."""

        # Error handling
        # directoryExists(folderPath)
        #

        regexResults = []
        f = os.listdir(folderPath)
        #read images in folder
        for i, file in enumerate(f):
            m = re.fullmatch(regex, file)
            if m != None:
                d = m.groupdict()
                d['_file'] = os.path.abspath(f'{folderPath}\\{file}') if useAbsPath else file
                regexResults.append(d)

        if len(regexResults) == 0 or numResults == 0:
            return []
        elif numResults < 0:
            return regexResults
        elif len(regexResults) > numResults:
            return regexResults[:numResults]
        else:
            return regexResults
    # end parseAndSearchRegex




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
    def createMetadata(folder_path, regex, mdatafilename='metadata_python.txt'):
        """
        This function creates a metadata txt file in the same format as used in the matlab Phindr implementation

        folder_path: path to image folder (full or relative)
        regex: regular expression matching image file names. must include named groups for all required image attributes (wellID, field, treatment, channel, stack, etc.)
        Matlab style regex can be adapted by adding P before group names. ex. : "(?P<WellID>\w+)__(?P<Treatment>\w+)__z(?P<Stack>\d+)__ch(?P<Channel>\d)__example.tiff"
        mdatafilename: filename for metadatafile that will be written.

        regex groups MUST INCLUDE Channel and Stack and at least one other image identification group
        regex groups CANNOT include ImageID or _file.
        """

        f = os.listdir(folder_path)
        metadatafilename = f'{os.path.abspath(folder_path)}\\{mdatafilename}'
        #read images in folder
        rows = []
        for i, file in enumerate(f):
            m = re.fullmatch(regex, file)
            if m != None:
                d = m.groupdict()
                d['_file'] = os.path.abspath(f'{folder_path}\\{file}')
                rows.append(d)
        #make sure rows is not empty and that Channel and Stack are in the groups.
        if len(rows) == 0:
            print('\nFailed to create metadata. No regex matches found in folder.\n')
            return False
        if ('Channel' not in rows[0].keys()) or ('Stack' not in rows[0].keys()):
            print('\nFailed to create metadata. regex must contain "Channel" and "Stack" groups.')
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
        for chan in channels:
            chandf = tmpdf[tmpdf['Channel']==chan].reset_index(drop=True)
            df[f'Channel_{chan}'] = chandf['_file']
        df.to_csv(metadatafilename, sep='\t', index=False)
        print(f'Metadata file created at \n{metadatafilename}')
        return True # return value to indicate success of function

    # end createMetadata

# end DataFunctions





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

# end test_parseAndCompareRegex

# error classes

class MissingChannelStackError(Exception):
    pass

if __name__ == '__main__':
    """Tests of the static methods that can be run directly."""
    #test_directoryExists()

    test_parseAndCompareRegex()



# end if main
