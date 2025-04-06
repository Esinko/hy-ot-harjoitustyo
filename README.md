# Ohjelmistotekniikka, harjoitustyö
> This repository contains course work. Contents in Finnish.

*"Dungeon-karttahallintaohjelmisto"*. Helppoon kartanpiirtoon **RolePlaying**-pelin aikana.

Sovelluksella voi luoda karttoja ja tuoda kartoille monimuotoisia grid-järjestelmään sovitettuja elementtejä. Sovellus tallentaa muutokset automaattisesti ja muokattavaa karttaa on helppo vaihtaa. Lisää ominaisuuksia tulossa.

## Dokumentaatio ja linkit
- [Vaatimusmäärittely](./dokumentaatio/vaatimusmaarittely.md)
- [Työaikakirjanpito](./dokumentaatio/tyoaikakirjanpito.md)
- [Changelog](./dokumentaation/changelog.md)


## Projektista
Sovelluksen tarvitsema Python versio ja tiedot riippuvuuksista löytyvät `pyproject.toml`-tiedostosta.

### Asennus ja käynnistys
1. Asenna riippuvuudet: `poetry install`
2. Suorita lähteestä: `poetry run invoke start`

**Poetry:n asennus tarvittaessa**

`pipx install poetry`

## Paketointi
1. Asenna riippuvuudet: `poetry install`
    - Windowsilla varmista, että `dumpbin` on saatavilla.
2. Paketoi: `poetry run invoke build`

### Kehitysympäristö

**Käyttöönotto**
1. Luo venv `poetry install`
2. Aktivoi venv `poetry env activate` -> `"./.venv/Scripts/activate"`
3. Aseta VSCodessa suositeltu Python interpreter (korjaa kirjastotyypitykset)

**Update checklist**
1. Tee muutokset
2. Commit
3. Päivitä työaikakirjanpito & changelog

## Komentorivitoiminnot
Kommennot on toteuttu invoke-kirjastolla.

### `poetry run invoke start`
Suorittaa sovelluksen.

### `poetry run invoke test`
Suorittaa sovelluksen testit.

### `poetry run invoke coverage-report`
Luo sovellukselle testikattavuusraportin `htmlcov`-kansioon ja avaa sen selaimessa.

### `poetry run invoke lint`
Suorittaa `pylint` koodin laaduntarkastusohjelmiston sovelluksen koodikantaa vasten. Tyylisäännöt on määritelty `.pylintrc`-tiedostossa.