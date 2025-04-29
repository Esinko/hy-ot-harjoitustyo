## Viikko 3 (28.3.2025)
- Käyttäjä voi luoda ja poistaa karttoja
    - Lisätty MapStore-luokka karttatiedostojen käsittely varten
    - Lisätty Map-luokka karttatiedon hyödyntämistä ja muokkaamista varten
- Lisätty testejä karttojen luonnin, listaamisen ja poistamisen testaamiseen

## Viikko 4 (6.4.2025)
- Lisätty editorinäkymä
- Suunniteltu ja osittain toteutettu visuaalinen ilme
- Lisätty pylint ja siistitty koodia
- Lisätty karttojen elementtien lisäys ja muokkaaminen
- Parannettu viansietoa
- Päivitetty projektin `README.md`

## Viikko 4 (7.4.2025)
- Luotu alustava pakkauskaavio
- Muokattu näkymät käsittelemään vain Map-luokkia (ei MapStore-luokkaa)
- Lisätty kartan elementtien nimien ja taustakuvan lisäys ja muokkaus
- Lisätty kartan elementtien poisto
- Lisätty liitetiedostojen käsittely
- Lisätty elementtien kierto

## Viikko 4 (8.4.2025)
- Korjattu readme

## Viikko 5 (15.4.2025)
- Refaktoiroitu editorin renderöintiprosessi tukemaan monityyppisiä objekteja
- Lisätty teksti-objektien lisäys kartalle, sisältää:
    - Tietokantamuutoksia
    - Isomman teksti-inputin
    - Värinvalinta-inputin
- Lisätty poista taustakuva -nappi kartan elementtien taustakuville
- Korjattu bugi, joka johti elementin taustan katoamiseen siirrettäessä
- Lisätty ominaisuus muokata kartan nimiä valintanäkymästä
- Siistitty valintanäkymän ulkonäköä

# Viikko 6 (28.4.2025)
- Refakotoritu application.py useammaksi View-luokan pohjalta tehdyiksi view-tiedostoiksi views-kansioon
- Lisätty import & export ominaisuus kartoille
- Lisätty tyylit kaikille näkymille

## Viikko 6 (29.4.2025)
- Dokumentoinnin parantamista (esim. docstring)
- Korjattu virhe kartan valintanäkymässä
- Refaktoroitu `map/abstract.py` erillisiksi kansioksi `map` ja `map_store` koodin kasvamisen ja rakenteellisen selkeyden vuoksi.
- Lisätty käyttöhje
