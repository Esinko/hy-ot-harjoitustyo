# Arkkitehtuurikuvaus

## Rakenne
![rakenne](./arkkitehtuuri-kuvat/rakenne.png)

Ohjelmassa on kolme keskeistä osaa: `ui`, `map_store` ja `map` -hakemistot.

`ui`-hakemisto sisältää alihakemistot `components` ja `views`.
`views`-hakemisto sisältää sovelluksen näkymät, jotka käyttävät käyttöliittymäkomponentteja `components`-hakemistosta.

`map`-hakemistossa on tiedosto `entity.py`, jonka tehtävän on karttojen käsittely ja muokkaaminen.
`map_store`-hakemistossa on tiedosto `store.py`, jopka hallinnoi karttatiedostoja ja huolehtii niiden pysyväistallentamisesta.

Huom. Tällä hetkellä `map`-hakemiston ohjelmakoodi muokkaa karttatiedostoja suoraan, ei `MapStore`-luokan kautta. Tämä on puute.

## Käyttöliittymä
Käyttöliittymässä on kaksi keskeistä näkymää, sekä muutama lisänäkymä.

**Keskeiset näkymät**
- `select`-näkymä
    - Käyttäjä voi valita, luoda uuden, poistaa tai nimetä uudelleen kartan
    - Käyttäjä voi viedä/tuoda karttoja
- `editor`-näkymä
    - 2D-editori, jossa kartan elementit
    - Käyttäjä voi lisätä objekteja kartalle yläpalkista raahamalla niitä kartalle
    - Klikkaamalla objekteja hiiren oikealla näppäimellä, aukeaa `properties`-sivupaneli objektin muokkaamista varten

**Lisänäkymät**
- `create`-näkymä (luo kartta)
- `rename`-näkymä (uudelleen nimeä kartta)
- `delete`-näkymä (are-you-sure tarkistus ennen kartan poistoa)

Kaikki näkymät on toteutettu omina tiedostoinaan `ui/views` kansioon. Näkymän pohjana on `View`-luokka, jonka näkmät perivät.
Näkymien vaihtamisesta vastaa `Application`-luokka, jonka `change_to_view`-metodi tarjotaan näkymille tarvittaessa.
Näkymät luodaan `BaseWindow`-luokassa omilla metodeillaan, jota `Application`-luokka käyttää (mikäli joskus tarvitaan useampi ikkuna).
Näkymistä voi olla esillä vain yksi kerrallaan.

Käyttöliittymä on erillinen sovelluslogiikasta ja vain kutsuu `MapStore`- tai `Map`-luokkien metodeja.

## Sovelluslogiikka
Sovelluksen loogisen tietomallin keskiössä ovat luokat `MapStore` ja `Map`. Päätoiminnallisuuden tarjoaa `MapStore`-luokan ainoa olio. Luokka tarjoaa kaikille sovelluksen osille metodit `Map`-olioiden muodostamiseen levyllä olevien `.dmap`-tiedostojen pohjalta.

`MapStore`-luokka tarjoaa keskeisiä metodeja, kuten:
- `list()`, joka listaa karttatiedostot ja muodostaa kaikille `Map`-oliot.
- `create_map(name: str, filename: str)`, jonka avulla voi luoda uuden kartan.
- jne.

Tämä pakkauskaavio kuvastaa sovelluksen luokkien hierarkiaa ja suhdetta toisiinsa.
![Pakkauskaavio](./arkkitehtuuri-kuvat/alustava-pakkauskaavio.png)

## Tietojen pysyväistallennus
Sovelluksen luokat `Map` ja `MapStore` huolehtivat tietojen pysyväistallennuksesta. `MapStore`-luokka käyttää tiedostojärjestelmää karttatiedostojen löytämiseen ja luontiin. `Map`-luokka vastaa tiedoston sisällön muokkaamisesta, uudelleennimeämisestä ja poistamisesta mikäli tarpeen.

Luokkien valmistelussa on pyritty noudattamaan [Repository](https://en.wikipedia.org/wiki/Data_access_object)-mallia, joten niiden toteutukset voidaan tarvittaessa korvata. Ne tarjoavat korkean tason abstraktion tiedostojärjestelmän käyttöön ja karttojen sisällön muokkaamiseen.

### Karttatiedostot
Karttatiedostot tallennetaan lähtökohtaisesti `./data`-kansioon uniikeilla `uuidv4`-tunnisteilla. Karttojen käyttäjäystävällien nimi, sekä muut tiedot, on tallennettu itse karttaan.

Karttatiedoston rakenne selviää `src/map_store/schemal.sql`-tiedostosta.

**Lyhyesti**
- Tiedostopääte: `.dmap`
- Formaatti: `SQLite`-tietokanta

**Taulut**
- `Text`: teksti-objektit
- `Elements`: kartan elementit
- `Meta`: taulu, jossa vain yksi rivi, jossa kartan metatiedot


## Päätoiminnallisuus
Sovelluksen päätoiminnallisuus on karttatiedostojen muokkaaminen.

**Kartan luominen**
```mermaid
sequenceDiagram
    actor User
    participant UI
    participant MapStore
    participant Map

    UI->>UI: initialize `select_view`
    UI->>MapStore: .list()
    MapStore->>UI: []
    User->>UI: click "Create Map"
    UI->>UI: open `create`-view
    User->>UI: input map name
    User->>UI: click "Create"
    UI->>UI: pick random uuidv4
    UI->>MapStore: .create_map("new map", uuidv4)
    MapStore->>Map: Map(...)
    Map->>MapStore: created_map
    UI->>UI: open `select`-view
```

**Kartan valinta ja avaaminen**
```mermaid
sequenceDiagram
    actor User
    participant UI
    participant MapStore
    participant Map

    UI->>UI: initialize `select_view`
    UI->>MapStore: .list()
    MapStore->>UI: [created_map]
    User->>UI: Click created_map on the map list
    UI->>UI: initialize editor
    UI-->>Map: created_map.get_elements()
    Map-->>UI: elements_list
    UI-->>Map: created_map.get_text_list()
    Map-->>UI: text_list
    UI->>UI: begin rendering editor
```

**Kartan sisällön muokkaaminen**
Esimerkkinä ruudun nimen muokkaaminen.
Editor näkymä jo auki.

```mermaid
sequenceDiagram
    actor User
    participant UI
    participant MapStore
    participant Map

    User->>UI: right click tile in editor
    UI->>UI: focus right clicked tile (id)
    UI->>UI: open tile properties sidebar
    User->>UI: input new tile name "cool tile"
    UI-->>Map: .edit_element(id, {..., "name": "cool tile"})
    UI->>Map: .get_elements()
    Map-->>UI: elements_list
    UI->>UI: update editor graphics
```


**Muu toiminnallisuus**
Lähtökohtaisesti kaikki muu toiminnallisuus seuraa vastaavaa mallia. Käyttäjä tekee jotain, joka johtaa tapahtuman käsittelyyn käyttöliittymän toimesta, joka kutsuu MapStore ja Map luokkia tapahtuman edellytyksien mukaisesti.

## Sekvenssikaavio: kartan luonti, elementin lisäys ja kartan sulku
Tämä sekvenssikaavio kuvastaa sovelluksen ohjelmallista toimintaa.
```mermaid
sequenceDiagram
    %% Add columns
    participant main
    participant map_store
    participant created_map
    participant first_map_element

    %% Create map
    main->>map_store: MapStore(path="./store/", init_path="./init.sql", schema_path="./schema.sql")
    map_store-->>main: store
    main->>map_store: store.create_map(name="cool map name", filename="very-random-name-here")
    map_store->>created_map: Map(map_file: Path, connection: sqlite3.Connection)
    created_map-->>map_store: map
    map_store->>created_map: map.set_name(name)
    map_store-->>main: map

    %% Add element
    main->>created_map: map.create_element({ "name": "cool-element , "x": 0, "y": 0, "width": 1, "height": 1})
    created_map-->>created_map: element_id
    created_map->>created_map: get_element(element_id)
    created_map-->>first_map_element: Element(id=element_id, ...)
    first_map_element-->>created_map: element
    created_map-->>main: element

    %% Close
    main->>created_map: map.close()
```

## Puutteet
Tällä hetkellä kartan objektien käsittely on koodissa jaettu erikseen Elements ja MapText osiin, joita käsitellään erikseen. Mielekkäämpää olisi käsitellä yhtä suurta MapObject-tyyppiä, joka vähentäisi koodissa toistoa.

Arkkitehtuurillisia poikkeamia on käyttöliittymän MapStore- ja Map-luokkien käsittelyssä. Tavoitteena oli rajata näkymille pääsy vain Map-luokkaan, mutta MapStore on tietyissä tilanteissa tarpeellinen. Käyttöliittymän rakenteen yksinkertaistaminen voisi poistaa nämä edellytykset. Lisäksi kartan poisto tapahtuu Map-luokan kautta, sillä tietokantayhteyden sulkeminen on sen kauttaa mielekkäämpää.
