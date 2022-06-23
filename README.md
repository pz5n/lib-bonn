# Crawler for the OPAC catalog of lib.bonn.de

## Installation

```sh
pip install -r requirements.txt
```

## Configuration

### Examples

Search for all Game of Thrones movies published between 2010 and 2015

```sh
scrapy crawl lib.bonn.de -a "search=Game of Thrones" -a media=11 -a year=2010:2015
```

Crawl the whole catalog

> Don't do this! This takes quite a bit and puts some load on the OPAC site

```sh
for MEDIA in 22 19 12 36 20 31 11 15 21 32 37
do 
    scrapy crawl lib.bonn.de -O "target/$MEDIA-%(batch_id)04d-%(batch_time)s.json" -a media="$MEDIA" -s FEED_EXPORT_BATCH_ITEM_COUNT="100"     
done

```

### Search

```text
-a search=[[category]:]<search>
-a search2=[[operator][category]:]<search>
-a search2=[[operator][category]:]<search>
```

#### Operators

`&`
: und

`|`
: oder

`^`
: und nicht

#### Categories

`100`
: Autorin/Autor

`331`
: Titel/Stichwort

`902`
: Schlagwort_1

`14`
: Signatur

`700`
: Notation

`412`
: Verlag

`540`
: ISBN / ISSN

`451`
: Serie/Reihe

`425`
: Ersch.-Jahr

`712`
: Stoffkreis

### Location

```text
-a location=<location>
```

`0`
: Zentralbibliothek Tel. 772277

`1`
: onleihe:Bonn

`2`
: Dottendorf Tel. 776532

`6`
: Tannenbusch  Tel. 776042/776041

`7`
: Zentralbibl./Cassius-Bastei. 774570

`9`
: Musikbibliothek     Tel. 773656

`10`
: Auerberg Tel. 98929003

`11`
: Endenich            Tel. 772320

`12`
: Bad Godesberg  Tel. 776046

`13`
: Beuel               Tel. 774780

`14`
: Beuel-Ost           Tel. 774787

`17`
: Brüser Berg       Tel. 77 89 010

`20`
: Stadtbibliothek Bonn, Fernleihe

`21`
: Bibliobike

### Media

```text
-a media=<media>
```

`22`
: Zeitung/Zeitschrift

`19`
: Audio

`12`
: Buch

`36`
: Comic, Cartoon, Manga, Graphic Novel

`20`
: CD-ROM/DVD-ROM

`31`
: einzelne Notenstücke und Lieder

`11`
: Film

`15`
: Spiel

`21`
: Noten

`32`
: eMedien

`37`
: eTutorial

### Language

```text
-a language=<language>
```

`33`
: Arabisch

`29`
: Spanisch

`23`
: Englisch

`24`
: Französisch

`25`
: Italienisch

`26`
: Niederländisch

`27`
: Persisch

`34`
: Polnisch

`28`
: Russisch

`30`
: Türkisch

`35`
: mehrsprachig

### Year

```text
-a year=<year_start>[:<year_end>]
```

### Sort

```text
-a sort=<sort>
```

`1`
: Sortierung nach Zweigstelle

`2`
: Sortierung nach Status

## Crawler logic

1. Get `/webOPACClient/start.do?Lang=de&Login=web00&BaseURL=this` to create a new session and get a session token.

2. Set search restrictions and call `/webOPACClient/search.do?methodToCall=submit&methodToCallParameter=searchPreferences&callingPage=searchParameters` to store search restrictions for this session. On the web interface this switches from *Suche eingrenzen* to *Sucheinstellungen* tab.

3. Set search preferences and run search by calling `webOPACClient/search.do?methodToCall=submit&methodToCallParameter=submitSearch&submitSearch=Suchen&callingPage=searchPreferences`. On the web interface this relates to pushing the *Suchen* button

4. Parse received hitlist and for each item extract media type (not present on the detail page) and call `webOPACClient/singleHit.do?methodToCall=showHit` to receive the detail page. We only grab the media item data from this page as it only has partial and semi-structured data about the record.

5. Call `webOPACClient/singleHit.do?methodToCall=activateTab&tab=showTitleActive` to get record attributes from the *mehr zum Titel* tab.

6. Repeat steps 4 and 5 for all items on the current page.

7. When there are no more items on the page call next page link `webOPACClient/hitList.do?methodToCall=pos` and repeat steps 4, 5 and 6.

8. We are done when ther are no more pages.

The crawler needs to run sequentially as the search an current result are both stored for the current session on the server side. Crawling search results in parallel does reset the current selected item and messes up the extracted results.

## Data output

Output data structure is dynamic and depends on all attributes found on the *mehr zum Titel* tab. It is possible for some attributes to be specified multiple times for the same record. Therefore all attributes are arrays of items. Special attributes are `Medientyp` and `Exemplare`. `Medientyp` isn't visible at all on the single hit page, we're grabbing this from the title attribute of the image shown on hitlist page. `Exemplare` is parsed from all entries on the *Exemplare* tab on single hit page. An example item looks like this:

```json
{
        "Medientyp": "DVD",
        "Titel": [
            "2 guns",
            "[Two] guns"
        ],
        "Einheitssacht.": [
            "2 guns"
        ],
        "Verfasser": [
            "nach dem Buch von Steven Grant. Regie: Baltasar Kormákur. Drehb.: Blake Masters. Kamera: Oliver Wood. Musik: Clinton Shorter. Darst.: Denzel Washington ; Mark Wahlberg ; Paula Patton ..."
        ],
        "Verlagsort": [
            "München"
        ],
        "Verlag": [
            "Sony Pictures Home Entertainment"
        ],
        "Preis/Einband": [
            "14,99 €"
        ],
        "Ersch.-Jahr": [
            "[2014]"
        ],
        "Produktionsland": [
            "USA, 2013"
        ],
        "Umfangsangabe": [
            "105 Min."
        ],
        "Ill_Angabe": [
            "farb."
        ],
        "Allg. Fussnoten": [
            "FSK ab 16 Jahren - Sprachen: Deutsch, Englisch, Italienisch / Untertitel: Deutsch, Englisch, Dänisch, Finnisch, Italienisch, Norwegisch, Schwedisch / Mit Bonusmaterial"
        ],
        "Ang. zum Inhalt": [
            "1 DVD"
        ],
        "Bestnr. Musik.": [
            "0373049"
        ],
        "Signatur": [
            "DVD-VS Abenteuer/Action TWO"
        ],
        "Ersch. Form": [
            "m"
        ],
        "Aufnahme": [
            "21.02.2014"
        ],
        "Kat.-Datum": [
            "03.09.2019"
        ],
        "ASIN": [
            "B00FF4KOWK"
        ],
        "Exemplare": {
            "Mediennummer": "14392416",
            "Signatur": "DVD-VS Abenteuer/Action TWO",
            "Zweigstelle": "Brüser Berg       Tel. 77 89 010",
            "Status": "bestellbar"
        }
    }
```
