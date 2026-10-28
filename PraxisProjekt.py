import datetime
from datetime import date

class LagerbestandNichtAusreichendError(Exception):
    pass

sortiment = {}
versandtarife = {
    "standard": 4.90,
    "express": 12.50
}

class Produkt:
    def __init__(self, produkt_id: str, name: str, preis: float, lagerbestand: int):
        self.produkt_id = produkt_id
        self.name = name
        self.preis = preis
        self.lagerbestand = lagerbestand

    def __str__(self):
        return f"{self.produkt_id}: {self.name} {self.preis:.2f} € | Lager: {self.lagerbestand}"


class Kunde:
    def __init__(self, kunden_id: str, name: str, ist_premium: bool):
        self.kunden_id = kunden_id
        self.name = name
        self.ist_premium = ist_premium

    def __str__(self):
        return f"Kunde: {self.name} (ID: {self.kunden_id}, Premium: {self.ist_premium})"


def registriere_produkt(produkt_id: str, name: str, preis: float, lagerbestand: int):
    produkt = Produkt(produkt_id, name, preis, lagerbestand)
    sortiment[produkt_id] = produkt


def berechne_gesamtsumme(warenkorb: list, kunde: Kunde, rabattcode: str = None, versandart: str = "standard") -> dict:
    nettbetrag = 0.0
    
    for produkt_id, menge in warenkorb:
        if produkt_id in sortiment:
            produkt = sortiment[produkt_id]
            nettbetrag += produkt.preis * menge
        else:
            raise ValueError(f"Produkt {produkt_id} ist nicht im Sortiment.")

    mwst = nettbetrag * 0.19
    zwischensumme = nettbetrag + mwst

    versandkosten = versandtarife.get(versandart, 0.0)
    if nettbetrag >= 100.0:
        versandkosten = 0.0

    rabatt = 0.0
    if rabattcode:
        bereinigter_code = rabattcode.strip().upper()
        if bereinigter_code == "SOMMER2026":
            rabatt = (nettbetrag + mwst) * 0.10
        elif bereinigter_code == "START10":
            rabatt = 10.0
    
    gesamtsumme = nettbetrag + mwst - rabatt + versandkosten

    return {
        "nettbetrag": round(nettbetrag, 2),
        "mwst": round(mwst, 2),
        "versand": round(versandkosten, 2),
        "rabatt": round(rabatt, 2),
        "gesamtsumme": round(gesamtsumme, 2)
    }


def bestell_menge_eingeben(produkt_id: str) -> int:
    while True:
        try:
            eingabe = input(f"Menge für Produkt {produkt_id} eingeben: ")
            menge = int(eingabe)

            if menge <= 0:
                print("Fehler: Menge muss größer als 0 sein.")
                continue

            if produkt_id in sortiment:
                if sortiment[produkt_id].lagerbestand < menge:
                    raise LagerbestandNichtAusreichendError(
                        f"Nicht ausreichend Lagerbestand für {produkt_id}. "
                        f"Verfügbar: {sortiment[produkt_id].lagerbestand}"
                    )
            else:
                raise ValueError(f"Produkt {produkt_id} nicht gefunden.")

            return menge

        except ValueError as e:
            if "Produkt" in str(e):
                print(f"Fehler: {e}")
                return None
            print("Fehler: Bitte geben Sie eine gültige ganze Zahl ein.")

        except LagerbestandNichtAusreichendError as e:
            print(f"Lagerfehler: {e}")
            neu = input("Möchten Sie eine andere Menge eingeben? (j/n): ")
            if neu.lower() == 'j':
                continue
            else:
                return 0

        finally:
            pass


def interaktive_bestellung():
    if not sortiment:
        registriere_produkt("P001", "Laptop", 999.00, 10)
        registriere_produkt("P002", "Maus", 29.90, 50)
        registriere_produkt("P003", "Tastatur", 59.90, 30)

    print("\nInteraktive Bestellung")
    print("Verfügbare Produkte:")
    for pid, prod in sortiment.items():
        print(prod)

    kunde = Kunde("K001", "Max Mustermann", False)
    print(f"\nAngemeldet als: {kunde}")
    
    warenkorb = []

    while True:
        produkt_id = input("Produkt-ID eingeben (oder 'f' für fertig): ").strip()
        if produkt_id.lower() == 'f':
            break

        if produkt_id not in sortiment:
            print(f"Produkt {produkt_id} nicht gefunden.")
            continue

        menge = bestell_menge_eingeben(produkt_id)
        
        if menge is None:
            continue
        elif menge == 0:
            continue
        else:
            warenkorb.append((produkt_id, menge))
            print(f"{menge}x {produkt_id} zum Warenkorb hinzugefügt.")

    if not warenkorb:
        print("Warenkorb ist leer. Bestellung abgebrochen.")
        return

    versandart = input("Versandart wählen (standard/express) [standard]: ").strip().lower()
    if versandart not in versandtarife:
        versandart = "standard"

    rabattcode = input("Rabattcode eingeben (optional): ").strip()

    ergebnis = berechne_gesamtsumme(warenkorb, kunde, rabattcode, versandart)
    
    print(f"\n--- Rechnung für {kunde.name} ---")
    print(f"Netto: {ergebnis['nettbetrag']:.2f} €")
    print(f"MwSt (19%): {ergebnis['mwst']:.2f} €")
    print(f"Rabatt: -{ergebnis['rabatt']:.2f} €")
    print(f"Versand ({versandart}): {ergebnis['versand']:.2f} €")
    print(f"Gesamtsumme: {ergebnis['gesamtsumme']:.2f} €")

    bestellzeitpunkt = datetime.datetime.now()
    bestell_datum = bestellzeitpunkt.strftime("%d.%m.%Y %H:%M:%S")
    liefer_datum = (bestellzeitpunkt + datetime.timedelta(days=3)).strftime("%d.%m.%Y")

    print(f"\nBestellt am: {bestell_datum}")
    print(f"Voraussichtliche Lieferung: {liefer_datum}")


if __name__ == "__main__":
    interaktive_bestellung()
