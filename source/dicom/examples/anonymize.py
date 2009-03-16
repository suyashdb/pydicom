# anonymize.py
"""Read a dicom file (or directory of files), partially "anonymize" it (them), 
by replacing Person names, patient id, optionally remove curves 
and private tags, and write result to a new file (directory)
This is an example only; use only as a starting point."""
# Copyright (c) 2008 Darcy Mason
# This file is part of pydicom, relased under an MIT license.
#    See the file license.txt included with this distribution, also
#    available at http://pydicom.googlecode.com

usage = """
Usage:
python anonymize.py dicomfile.dcm outputfile.dcm
OR
python anonymize.py originalsdirectory anonymizeddirectory
"""

# Use at your own risk!!
# Many more items need to be addressed for proper anonymizing
# In particular, note that pixel data could have confidential data "burned in"

import os, os.path
import dicom

def anonymize(filename, output_filename, PersonName="anonymous",
              PatientID="id", RemoveCurves=True, RemovePrivate=True):
    """Replace data elements with VR="PN" with PersonName etc."""

	# Define call-back functions
    def PN_callback(ds, data_element):
        """Called from the dataset "walk" recursive function for all data elements."""
        if data_element.VR == "PN":
            data_element.value = PersonName
    def curves_callback(ds, data_element):
        """Called from the dataset "walk" recursive function for all data elements."""
        if data_element.tag.group & 0xFF00 == 0x5000:
            del ds[data_element.tag]
    
	# Load the current dicom file to anonymize
    dataset = dicom.read_file(filename)
    
	# Remove patient name and any other names
    dataset.walk(PN_callback)
    
	# Change ID
    dataset.PatientID = PatientID
	
	# Remove data elements (if DICOM type 3 optional) 
	# Use general loop so easy to add more later
    for name in ['OtherPatientIDs']:
        if name in dataset:
            tag = dataset.data_element(name).tag
            del dataset[tag]

	# Same as above but for blanking data elements that are type 2.
    for name in ['PatientsBirthDate']:
        if name in dataset:
            dataset.data_element(name).value = ''
	
	# Remove private tags if funcation argument says to do so. Same for curves
    if RemovePrivate:
        dataset.RemovePrivateTags()
    if RemoveCurves:
        dataset.walk(curves_callback)
		
	# write the 'anonymized' DICOM out under the new filename
    dataset.SaveAs(output_filename)   

# Can run as a script:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print usage
        sys.exit()
    arg1, arg2 = sys.argv[1:]

    if os.path.isdir(arg1):
        in_dir = arg1
        out_dir = arg2
        if os.path.exists(out_dir):
            if not os.path.isdir(out_dir):
                raise IOError, "Input is directory; output name exists but is not a directory"
        else: # out_dir does not exist; create it.
            os.makedirs(out_dir)

        filenames = os.listdir(in_dir)
        for filename in filenames:
            if not os.path.isdir(os.path.join(in_dir, filename)):
                print filename + "...",
                anonymize(os.path.join(in_dir, filename), os.path.join(out_dir, filename))
                print "done\r",
    else: # first arg not a directory, assume two files given
        in_filename = arg1
        out_filename = arg2
        anonymize(in_filename, out_filename)
    print
    