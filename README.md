# Ohjelmistotekniikka, harjoitustyö
> This repository contains course work. Contents in Finnish.

*"Dungeon-karttahallintaohjelmisto"*. Helppoon kartanpiirtoon **RolePlaying**-pelin aikana.

**Linkit**
- Laskarit
    - [vk1](./laskarit/viikko1.md)
    - [vk2](./laskarit/viikko2/)
    - [vk3](./laskarit/viikko3/)
        - [tehtävä-1](./laskarit/viikko3/tehtävä1.md)
        - [tehtävä-2](./laskarit/viikko3/tehtävä2.md)
- [Vaatimusmäärittely](./dokumentaatio/vaatimusmaarittely.md)
- [Työaikakirjanpito](./dokumentaatio/tyoaikakirjanpito.md)
- [Changelog](./dokumentaation/changelog.md)


## Projektista

### Käynnistys
1. Asenna riippuvuudet: `poetry install`
2. Suorita lähteestä: `poetry run invoke start`

## Paketointi
1. Asenna riippuvuudet: `poetry install`
    - Windowsilla varmista, että `dumpbin` on saatavilla.
2. Paketoi: `poetry run invoke build`

### Kehitysympäristö
**Käyttöönotto**
1. Luo venv `poetry install`
2. Aktivoi venv `poetry env activate` -> `"./.venv/Scripts/activate.bat"`
3. Aseta VSCodessa suositeltu Python interpreter (korjaa kirjastotyypitykset)

**Update checklist**
1. Tee muutokset
2. Commit
3. Päivitä työaikakirjanpito & changelog
