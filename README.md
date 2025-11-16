# Ollama Chat Application

Author: Tadeusz Puźniakwski

Generated using GitHub Copilot.

Prosty interfejs czatu do lokalnego API Ollama z frontendem w czystym JavaScript i backendem w Pythonie.

## Wymagania

- Python 3.8+
- Ollama zainstalowana lokalnie i uruchomiona
- Przynajmniej jeden model pobrany w Ollama (np. `ollama pull tinyllama`)

### Przetestowane modele

Następujące modele zostały przetestowane i działają poprawnie:

```
NAME                   ID              SIZE  
smallthinker:latest    945eb1864589    3.6 GB
tinyllama:latest       2644915ede35    637 MB
```

### Instalacja

1. **Sklonuj lub pobierz projekt**

2. **Zainstaluj zależności Pythona**
```bash
pip install -r requirements.txt
```

3. **Upewnij się, że Ollama działa lokalnie**
```bash
# Sprawdź czy Ollama działa
curl http://localhost:11434/api/tags

# Jeśli nie masz modeli, pobierz jeden z nich:
ollama pull tinyllama
# lub
ollama pull smallthinker
```

## ⚙️ Konfiguracja

### Podstawowa konfiguracja

1. **Skopiuj przykładową konfigurację:**
```bash
cp config/config.example.json config/config.json
```

2. **Edytuj plik `config/config.json`** aby skonfigurować domyślny model i inne opcje:

```json
{
  "model": "llama2",
  "ollama_url": "http://localhost:11434",
  "system_prompt": "Jesteś pomocnym asystentem AI. Odpowiadaj zwięźle i rzeczowo.",
  "temperature": 0.7,
  "stream": true
}
```

### Opcje konfiguracji:

- **model**: Nazwa modelu Ollama do użycia (np. "llama2", "mistral", "codellama")
- **ollama_url**: URL do lokalnej instancji Ollama
- **system_prompt**: Systemowy prompt dla asystenta AI
- **temperature**: Parametr temperatury (0.0 - 1.0) - wyższa wartość = bardziej kreatywne odpowiedzi
- **stream**: Czy streamować odpowiedzi (true/false)
- **context_directory**: (opcjonalnie) Ścieżka do katalogu z plikami kontekstu (.md)
- **context_header**: (opcjonalnie) Nagłówek dodawany przed kontekstem
- **context_footer**: (opcjonalnie) Stopka dodawana po kontekście
- **starter_message**: (opcjonalnie) Wiadomość powitalna wyświetlana użytkownikowi

### Zaawansowane: Dodawanie kontekstu osobistego

Aplikacja obsługuje automatyczne ładowanie kontekstu z plików Markdown, co pozwala utworzyć asystenta AI ze specjalistyczną wiedzą:

1. **Utwórz katalog kontekstu:**
```bash
mkdir context
```

2. **Dodaj pliki .md z informacjami:**
```bash
# Przykład: context/cv.md, context/projects.md, context/publications.md
```

3. **Zaktualizuj config.json:**
```json
{
  "model": "mistral:latest",
  "context_directory": "../context",
  "context_header": "--- Informacje kontekstowe ---\n\n",
  "context_footer": "\n\n--- Koniec kontekstu ---\n\n",
  "system_prompt": "Jesteś asystentem AI z dostępem do specjalistycznej wiedzy..."
}
```

**Uwaga:** Katalog `context/` i plik `config/config.json` są w `.gitignore` i nie będą commitowane do repozytorium. To pozwala na utrzymanie prywatności osobistych informacji podczas współdzielenia kodu.

## 🏃 Uruchomienie

1. **Uruchom backend Flask**
```bash
cd backend
python app.py
```

Serwer uruchomi się na `http://localhost:5000`

2. **Otwórz przeglądarkę**

Przejdź do `http://localhost:5000`

## 🧪 Testy

Projekt zawiera testy jednostkowe i integracyjne napisane w pytest.

### Uruchomienie wszystkich testów:
```bash
pytest
```

### Uruchomienie testów z pokryciem kodu:
```bash
pytest --cov=backend --cov-report=html
```

Raport pokrycia zostanie wygenerowany w folderze `htmlcov/`.

### Uruchomienie konkretnego pliku testowego:
```bash
pytest tests/test_config_loader.py
pytest tests/test_ollama_client.py
pytest tests/test_api.py
```

## 📁 Struktura projektu

```
demko/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # Główna aplikacja Flask
│   ├── ollama_client.py       # Klient API Ollama
│   └── config_loader.py       # Ładowanie konfiguracji
├── frontend/
│   ├── index.html             # Główny HTML
│   ├── app.js                 # Logika czatu (czysty JS)
│   └── styles.css             # Style CSS
├── config/
│   ├── config.json            # Aktywna konfiguracja
│   └── config.example.json    # Przykładowa konfiguracja
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Konfiguracja pytest
│   ├── test_config_loader.py  # Testy loadera konfiguracji
│   ├── test_ollama_client.py  # Testy klienta Ollama
│   └── test_api.py            # Testy API endpoints
├── requirements.txt           # Zależności Python
├── pytest.ini                 # Konfiguracja pytest
└── README.md                  # Ten plik
```

## 🔧 API Endpoints

### GET `/api/config`
Zwraca aktualną konfigurację.

### GET `/api/models`
Zwraca listę dostępnych modeli Ollama.

### POST `/api/chat`
Wysyła wiadomość do Ollama i zwraca odpowiedź.

**Request body:**
```json
{
  "messages": [
    {"role": "user", "content": "Cześć!"}
  ],
  "model": "llama2",
  "stream": true
}
```

### POST `/api/reload-config`
Przeładowuje konfigurację z pliku bez restartu serwera.

## Funkcje

- Czysty JavaScript (ECMAScript) + HTML5
- Streaming odpowiedzi w czasie rzeczywistym
- Wybór modelu z listy dostępnych
- Konfiguracja przez plik JSON
- Przeładowanie konfiguracji bez restartu
- Responsywny interfejs
- Wskaźnik pisania
- Historia konwersacji
- Obsługa błędów
- Formatowanie bloków kodu
- Testy jednostkowe i integracyjne

## 🛠️ Rozwiązywanie problemów

### Ollama nie odpowiada
```bash
# Sprawdź czy Ollama działa
ollama serve

# W nowym terminalu sprawdź status
curl http://localhost:11434/api/tags
```

### Model nie jest dostępny
```bash
# Zobacz listę zainstalowanych modeli
ollama list

# Pobierz nowy model
ollama pull llama2
```

### Błędy CORS
Upewnij się, że `flask-cors` jest zainstalowane:
```bash
pip install flask-cors
```

### Port zajęty
Zmień port w `backend/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Zmień na inny port
```

## 📝 Licencja

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🤝 Współpraca

Jeśli chcesz rozwinąć projekt:
1. Dodaj więcej opcji konfiguracji
2. Zaimplementuj zapisywanie historii czatu
3. Dodaj wsparcie dla wielu konwersacji
4. Dodaj eksport konwersacji do pliku
5. Zaimplementuj uwierzytelnianie użytkownika

## 📞 Wsparcie

W razie problemów sprawdź:
- [Dokumentacja Ollama](https://github.com/ollama/ollama)
- [Dokumentacja Flask](https://flask.palletsprojects.com/)
- [MDN Web Docs](https://developer.mozilla.org/) dla JavaScript
