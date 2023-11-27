# Bikila Data Dive

Bikila Data Dive ist ein Streamlit-basiertes Projekt, das Wettkampfresultate grafisch aufbereitet anzeigt.

## Installation

### Lokale Installation

1. Klone das Repository:

    ```bash
    git clone https://github.com/axel-bruening/streamlit-bikila.git
    cd streamlit-bikila
    ```

2. Installiere die erforderlichen Pakete mit pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Führe die Anwendung aus:

    ```bash
    streamlit run app.py
    ```

    Öffne deinen Webbrowser und gehe zu [http://localhost:8501](http://localhost:8501), um die Wettkampfresultate grafisch aufbereitet zu sehen.

### Verwendung mit Docker

1. Baue das Docker-Image:

    ```bash
    docker build -t bikila-app .
    ```

2. Starte den Docker-Container:

    ```bash
    docker run -p 8501:8501 bikila-app
    ```

    Öffne deinen Webbrowser und gehe zu [http://localhost:8501](http://localhost:8501), um die Wettkampfresultate grafisch aufbereitet zu sehen.

## Beitrag

Wenn Sie zur Entwicklung beitragen möchten, lesen Sie bitte unsere [Beitragshinweise](CONTRIBUTING.md).

## Anforderungen

Alle erforderlichen Pakete und deren Versionen sind in der `requirements.txt`-Datei aufgeführt. Sie können sie mit dem folgenden Befehl installieren:

```bash
pip install -r requirements.txt
```

## Lizenz

Dieses Projekt ist unter der GPL-Lizenz lizenziert - siehe die Datei [LICENSE](LICENSE) für weitere Details.

## Kontakt

Bei Fragen oder Anregungen kontaktieren Sie uns unter [bruening.axel@gmail.com].
