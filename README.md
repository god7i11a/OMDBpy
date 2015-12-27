# OMDBpy
python interface to OMDB

takes as input an xlsx file with the following columns:

   Title Year Series/Episode/ID B-R Runtime DLed Director Actors
   tomatoMeter imdbRating Plot tomatoConsensus Genre Website Awards
   Language Country BoxOffice

and if DLed is not an 'x' will retrieve info from OMDB using info in
the Title, Year, and Series/Episode/ID columns.

Series/Episode/ID can be of the form SiEj or ttNNNNNNNN for imdb key.

see http://www.omdbapi.com/ for details. 

