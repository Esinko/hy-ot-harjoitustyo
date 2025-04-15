# Vaatimusmäärittely

## Sovelluksen Tarkoitus
Sovelluksen avulla voi luoda, tallentaa ja muokata grid-järjestelmää hyödyntäviä karttoja(tiedostoja) helppoa yksinkertaisen kartan piirtämistä varten RolePlaying-pelien aikana.

## Käyttäjät
Sovelluksessa ei ole erilaisia käyttäjätyyppejä.

## Perusversion Suunnitellut Toiminnallisuudet
- `tehty` Tiedostojen hallinta
    - `tehty` Käyttäjä voi luoda uuden kartan ja asettaa sille nimen
    - `tehty` Käyttäjä voi poistaa kartan
    - `tehty` Käyttäjä voi nimetä uudelleen kartan
    - Käyttäjä voi viedä kartan valitsemaansa sijaintiin
    - Käyttäjä voi tuoda kartan valitsemastaan sijainnista
- Muokkaaminen ja luonti (editori)
    - Käyttäjä voi muokata kartan elementtien väriä ja taustakuvaa
        - `tehty` Neliöiden taustakuva
        - `tehty` Tekstin väri
    - Käyttäjä voi lisätä kartalle erilaisia muotoja ja viivoja (neliö, pallo, kolmio ja viiva)
        - `tehty` Neliöt
        - Pallo
        - Kolmio
        - Viiva
    - `tehty` Käyttäjä voi lisätä karttalle tekstiä
    - Käyttäjä voi määrittää muotojen ja merkintöjen sijainnin ja koon
        - `tehty` Neliöiden sijainti
        - `tehty` Tekstin koko ja sijainti
    - Käyttäjä voi poistaa elementtejä, muotoja ja muita merkintöjä
        - `tehty` Neliöt
        - `tehty` Tekstit
    - Käyttäjä näkee kaikki muodot ja merkinnät listauksesta editorissa ja voi valita ne muokattaviksi listalta
    - Käyttäjä voi peruuttaa tekemänsä muutokset
    - Editorissa on valmiita esimerkkitaustoja kartan elementeille
    
## Käyttöliittymäluonnoksia
Kun sovellus avataan, käyttäjä voi valita aikaisemman, tuoda, viedä tai luoda uuden kartan:
![alkunäkymä](valinta-luonnos.png)

Kartan muokkausnäkymän idea:
![editori-idea](editori-luonnos.png)

## Jatkokehitysiedoita
- Katselunäkymä
    - Käyttäjä voi avata katselunäkymän, jossa näkyy vain kartta ja sen sisältö
    - Katselunäkymän voi avata toiseen ikkunaan ja editorin toiseen
- Käyttäjä voi asettaa kartalle pikkukuvan
- Automaattinen karttojen varmuuskopiointi virheiden varalta
- Käyttäjä voi valita kartassa olevan tekstin fontin
- Käyttäjä voi tuoda vektoripiirroksia karttoihin
- Ohjelmisto pakkaa kartat tallentaessaan
- Tallenna kartat Google-Drive App-kansioon 
