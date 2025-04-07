from ui.application import Application
from map.abstract import MapStore

def main():
    # Open map store
    new_store = MapStore("./data")

    # Open UI
    application = Application(new_store)
    application.open(800, 600)

if __name__ == "__main__":
    main()
