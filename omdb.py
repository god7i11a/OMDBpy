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

OMDBdir = '/home/godzilla/Desktop/OMDBpy'
irvXLS = '%s/dvd-list.xlsx'%OMDBdir
infoXLS= '%s/dvd-info.xlsx'%OMDBdir
backXLS = '%s/dvd-info-bak.xlsx'%OMDBdir
badF = '%s/bad-movie-names.txt'%OMDBdir

keyL = [u'Title', u'Year', u'Series / Episode / ID', u'B-R',
        u'Runtime', u'DLed', u'Director', u'Actors', u'tomatoMeter',
        u'imdbRating', u'Plot', u'tomatoConsensus', u'Genre',
        u'Website', u'Awards', u'Language', u'Country', u'BoxOffice']

TYPE='movie'   # default search mode

def make_not_found(movieN):
    theD = {field: ''  for field in keyL}
    theD[u'Title']= '%s'%movieN
    return theD

def _getData(movieN, yr, seid):
    # need to add in epise=, season=, y= etc
    reqStr = '?t=%s&r=json&tomatoes=true&type=%s'%(movieN, TYPE)
    if not seid:
        pass
    elif seid.startswith('tt'):
        reqStr = reqStr+'&i=%s'%seid
    else:
        # parse the string
        x = seid.split('E')
        theS = x[0][1:]
        if len(x) == 1:
            theE = None
        elif len(x)==2:
            theE = x[1]
            
    if yr: reqStr = reqStr+'&year=%s'%year
    if _VERBOSE: print reqStr
    r = rget('http://www.omdbapi.com/'+reqStr)
    res=r.json()
    return res

def getData(movieL, ws):
    global TYPE

    movieN, yr, seid, br, run, dled = movieL[0:6]
    if type(movieN) is type(3):
        movieN = '%s'%movieN
    elif movieN.lower().endswith(' a'):
         movieN='A '+movieN[:-1]
    elif movieN.lower().endswith(' the'):
        movieN='The '+movieN[:-3]

    if dled=='x':                   # we have the data already, doanatouch
        res = movieL
    elif movieN.startswith('%%'):   # placeholder
        res=make_not_found(movieN)
        # switch modes
        TYPE=movieN[2:]
    else:                           # we need to get data
        res=_getData(movieN, yr, seid)
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


    if type(res) is type({}):
        res=[rowD[key]  for key in keyL] 
        
    ws.append(res)

def getDiscLold():
    wb = load_workbook(filename=irvXLS, read_only=True)
    ws = wb['Sheet1'] # ws is now an IterableWorksheet

    titleL=[]
    for row in ws.rows:
        valL = [ row[i].value for i in range(4)]
        valL.append('')
        titleL.append( valL )

    return titleL

def getDiscL():
    wb = load_workbook(filename=infoXLS, read_only=False)
    ws = wb['AllInfo'] # ws is now an IterableWorksheet

    titleL=[]
    for row in ws.rows:
        valL = [ row[i].value for i in range(len(keyL))]
        titleL.append( valL )
    
    wb.save(backXLS)
    return titleL

def main():
    
    titleL = getDiscL()

    wb = Workbook()
    ws=wb.active
    ws.title='AllInfo'
    ws.append(keyL)
    badFP = open(badF, 'w')
    
    for title in titleL[1:]:
        print 'getting info for %s ...'%title[0]
        getData(title, ws)
        
    wb.save(infoXLS)
    badFP.close()

if __name__ == '__main__':

    import re
    SEIDre= re.compile('^S\d+E\S+')

    
    seidL = ('S1', 'S1E1', 'S1E#1.2') 
    for seid in seidL:
        print SEIDre.match(seid)
