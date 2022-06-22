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

    @staticmethod
    def parseAndCompareRegex(sampleFile, regex):
        """Given a sample file name string and a regex string, parse the file name
            and find the fields specified in the regular expression. If no fields
            can be found, return empty dictionary. Otherwise, return a dictionary with the
            field names and their values. On re.error return empty dictionary. """
        outdict = {}
        # Check that both sampleFile and regex are strings
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
        for chan in channels:
            chandf = tmpdf[tmpdf['Channel']==chan].reset_index(drop=True)
            df[f'Channel_{chan}'] = chandf['_file']
        df.to_csv(metadatafilename, sep='\t', index=False)
        return True # return value to indicate success of function

    # end createMetadata

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
