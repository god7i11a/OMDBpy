"""
>>> import requests
>>> r = requests.get('https://github.com/timeline.json')
>>> r.json()


    r = requests.get('http://www.omdbapi.com/?t=Batman&page=1&r=xml')
    print dir(r)
    print r.text

"""

from requests import get as rget
from openpyxl import load_workbook
from openpyxl import Workbook

_VERBOSE=True

irvXLS = '/home/godzilla/Desktop/OMDBpy/dvd-list.xlsx'
infoXLS= '/home/godzilla/Desktop/OMDBpy/dvd-info.xlsx'
badF = '/home/godzilla/Desktop/OMDBpy/bad-movie-names.txt'

keyL = [u'Title', u'Year', u'Series / Episode / ID', u'B-R',
        u'Runtime', u'DLed', u'Director', u'Actors', u'tomatoMeter',
        u'imdbRating', u'Plot', u'tomatoConsensus', u'Genre',
        u'Website', u'Awards', u'Language', u'Country', u'BoxOffice']


def make_not_found(movieN):
    theD = {field: ''  for field in keyL}
    theD[u'Title']= '%s'%movieN
    return theD

def getData(movieL):
    movieN, seid, br, omdb = movieL
    if type(movieN) is type(3):
        movieN = '%s'%movieN
    elif movieN.lower().endswith(' a'):
         movieN='A '+movieN[:-1]
    elif movieN.lower().endswith(' the'):
        movieN='The '+movieN[:-3]
        
    if not movieN.startswith('%%'):
        # need to add in epise=, season=, y= etc
        r = rget('http://www.omdbapi.com/?t=%s&r=json&tomatoes=true'%movieN)
        res=r.json()
        # check for {"Response":"False","Error":"Movie not found!"}
        if res['Response'] == "False":
            print 'not found!!!'
            badFP.write(movieN+'\n')
            res=make_not_found(movieN)
            res['DLed']=''
        else:
            res['DLed']='x'
        res[u'Series / Episode / ID'] = seid
        res[u'B-R'] = br
    else:
        res=make_not_found(movieN)
        
    return res

def getDiscL():
    wb = load_workbook(filename=irvXLS, read_only=True)
    ws = wb['Sheet1'] # ws is now an IterableWorksheet

    titleL=[]
    for row in ws.rows:
        valL = [ row[i].value for i in range(3)]
        valL.append('')
        titleL.append( valL )

    return titleL

def add_dataD(rowD):
    ws.append(   [rowD[key]  for key in keyL] )

wb = Workbook()
ws=wb.active
ws.title='AllInfo'
ws.append(keyL)

badFP = open(badF, 'w')
titleL = getDiscL()
for title in titleL[1:]:
    print 'getting info for %s ...'%title[0]
    res=getData(title)
    if res is None: continue
    add_dataD( res)
        
wb.save(infoXLS)
badFP.close()
