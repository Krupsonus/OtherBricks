# OtherBricks

Platforma agregująca oferty klocków konstrukcyjnych (COBI, Mega Construx, CaDA).

## Uruchomienie

```bash
docker compose up --build -d
docker compose exec backend python seed.py
```

Frontend dostępny pod `http://localhost:5173`, API pod `http://localhost:8000/docs`.

## Dane seedowane

Seed tworzy 6 kategorii produktów (wojsko, pojazdy, architektura, miasto, kosmos, historyczne), 22 produkty z ofertami cenowymi z 3 zewnętrznych sklepów (BrickBot Alpha/Beta/Gamma) oraz dwa konta:

| Konto | E-mail | Hasło |
|-------|--------|-------|
| Administrator | admin@otherbricks.com | admin123 |
| Użytkownik | user@otherbricks.com | user123 |
