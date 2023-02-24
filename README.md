# Surge type glacier data

Code for figures: `surge_data.py`

## data
Here you find the following files (everything that is necessary for running `surge_data.py`):

`00_rgi60_attribs/XX_rgi60_Region.csv`
This is what is currently in RGI60. If you look at surges-RGI60.png (and compare to the other two figures) you will notice that there are quite a 
number of points missing, largely in Alaska. 

`ST_November.csv`
This is the file that Heidi sent me a back in 2021. It contains a similar number of points, but more for Alaska, which is how I noticed that something in RGI-6 was off.

`GeodatabaseSTglaciers.csv`
I can't recreate how I got this file, but I presume it came from Heidi. It contains more points than the other two, but the spatial pattern is quite similar to what is in the file from Heidi. It has the nice advantage that it contains GLIMS IDs, which might be quite useful for linking. The number of entries in this files seems to match what is described Sevestre & Benn
2015. The original file (in 'xlsx_docx') contains two extra sheets, but those seem less useful. A description of sorts can also be found as a .docx in that same directory. 

## xlsx_docx
Just a collection of the original files. 

