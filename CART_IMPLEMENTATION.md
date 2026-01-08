# Shopping Cart Implementation ✅

## Status: COMPLETE 🎉

Die Shopping Cart Funktionalität ist jetzt vollständig implementiert!

## Implementierte Features

### 1. **Cart anzeigen** (`gurkerlcli cart list`)
- Zeigt alle Produkte im Warenkorb
- Inkl. Menge, Preis, Rabatte
- Warnung bei Mindestbestellwert nicht erreicht
- JSON-Export möglich

### 2. **Produkt hinzufügen** (`gurkerlcli cart add`)
- Fügt Produkt zum Warenkorb hinzu
- Erkennt bereits vorhandene Produkte und aktualisiert Menge
- Zeigt Produktname und neue Menge an

### 3. **Produkt entfernen** (`gurkerlcli cart remove`)
- Entfernt Produkt komplett aus Warenkorb
- Prüft ob Produkt überhaupt im Warenkorb ist

### 4. **Warenkorb leeren** (`gurkerlcli cart clear`)
- Entfernt alle Produkte auf einmal
- Optional mit Sicherheitsabfrage (--force überspringt diese)

## API Endpoints

Verifizierte und verwendete Endpoints:

```
✅ GET  /services/frontend-service/v2/cart-review/check-cart
   → Warenkorb abrufen

✅ PUT  /services/frontend-service/v2/cart-review/item/{orderFieldId}
   → Produkt hinzufügen/aktualisieren: {"quantity": X}
   → Produkt entfernen: {"quantity": 0}
```

## Datenmodelle

### Response-Struktur
```json
{
  "status": 200,
  "messages": [],
  "data": {
    "cartId": 12363005,
    "totalPrice": 9.86,
    "totalSavings": 0.19,
    "minimalOrderPrice": 39.00,
    "submitConditionPassed": false,
    "items": {
      "4659": {
        "productId": 4659,
        "orderFieldId": 84365053,
        "productName": "nöm Waldviertler BIO-Vollmilch",
        "quantity": 2,
        "price": 1.70,
        "salePercents": 10,
        "originalPrice": 1.89,
        ...
      }
    }
  }
}
```

### Pydantic Models

1. **CartResponseDTO** - Volle API Response
2. **CartDataDTO** - Warenkorb-Daten
3. **CartItemDTO** - Einzelnes Produkt (roh)
4. **Cart** - Vereinfachtes Modell für CLI
5. **CartItem** - Einzelnes Produkt (vereinfacht)

## Dateien geändert

- ✅ `src/gurkerlcli/models.py` - Neue Cart-Models
- ✅ `src/gurkerlcli/commands/cart_cmd.py` - Implementierung
- ✅ `src/gurkerlcli/utils/formatting.py` - Cart-Tabelle
- ✅ `README.md` - Dokumentation aktualisiert

## Testing

```bash
# Parse Test (funktioniert!)
uv run python test_cart_parsing.py

# Output:
✓ Parsed CartResponseDTO (status: 200)
✓ Created Cart model (cart_id: 12363005)
  - Items: 2
  - Total: €9.86
  - Savings: €0.19
  - Minimal order: €39.00

✓ Cart items:
  - nöm Waldviertler BIO-Vollmilch (nöm Waldviertler)
    2x 1 l @ €1.70 = €3.40
    💰 10% off! Was: €1.89
```

## Beispiel-Usage

```bash
# Warenkorb anzeigen
gurkerlcli cart list

# Produkt hinzufügen (2 Stück)
gurkerlcli cart add 4659 --quantity 2

# Produkt entfernen
gurkerlcli cart remove 4659

# Warenkorb leeren
gurkerlcli cart clear --force

# JSON Export
gurkerlcli cart list --json
```

## Features der Tabelle

- ✅ Produktname und Brand
- ✅ Menge mit Einheit (z.B. "2x 1 l")
- ✅ Preis mit Rabatt-Anzeige (durchgestrichen → grün)
- ✅ Zwischensummen
- ✅ Gesamt-Ersparnis
- ✅ Gesamtsumme
- ✅ Warnung bei Mindestbestellwert

## Besonderheiten

### Product ID vs Order Field ID
- **productId**: Identifiziert das Produkt im Katalog
- **orderFieldId**: Identifiziert den Eintrag im Warenkorb
- Für API-Calls wird `orderFieldId` verwendet!

### Items als Dictionary
Die API gibt Items als Dictionary zurück (nicht als Array):
```json
"items": {
  "4659": { ... },  // Key ist productId
  "2471": { ... }
}
```

### Quantity = 0 zum Löschen
Es gibt keinen DELETE-Endpoint - stattdessen:
```bash
PUT /cart-review/item/{orderFieldId}
{"quantity": 0}
```

## Nächste Schritte

- ⏳ Order History implementieren
- ⏳ Checkout-Flow (extern im Browser)
- ⏳ Integration Tests mit echter API
- ⏳ Unit Tests mit Mocks

## Credits

API-Discovery und Implementation: 2026-01-08
