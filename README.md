# ALECS WhatsApp Pro

O aplicație desktop pentru automatizarea trimiterii de mesaje WhatsApp, cu interfață grafică modernă și funcționalități avansate.

![ALECS WhatsApp Pro Logo](screenshots/logo.png)

## Funcționalități

- 📱 Trimitere mesaje către contacte individuale sau grupuri
- 📎 Suport pentru atașamente (imagini și documente)
- ⏰ Programare mesaje la ore specifice
- 🔄 Trimitere mesaje multiple cu interval personalizat
- 📝 Sistem de șabloane pentru mesaje
- 👥 Import contacte din CSV
- 📋 Istoric complet al operațiunilor
- 🌙 Mod întunecat/luminos
- 💾 Salvare/încărcare setări

## Cerințe

- Python 3.8+
- WhatsApp Web activ în browser
- Conexiune la internet

## Instalare

1. Clonați repository-ul:
```bash
git clone https://github.com/arian222/alecs-whatsapp-pro.git
cd alecs-whatsapp-pro
```

2. Instalați dependențele:
```bash
pip install -r requirements.txt
```

## Utilizare

1. Rulați aplicația:
```bash
python whatsapp_sender.py
```

2. Asigurați-vă că sunteți conectat la WhatsApp Web în browser

3. Introduceți numărul de telefon sau selectați un grup

4. Scrieți mesajul și setați ora de trimitere

5. Opțional, atașați fișiere sau folosiți șabloane

6. Apăsați "Trimite Mesaj"

## Configurare

- Fișierele de configurare sunt salvate automat în directorul aplicației:
  - `templates.json` - șabloane de mesaje
  - `settings.pkl` - setări generale
  - `logs/` - istoricul operațiunilor

## Contribuții

Contribuțiile sunt binevenite! Vă rugăm să:

1. Fork repository-ul
2. Creați un branch pentru feature (`git checkout -b feature/AmazingFeature`)
3. Commit modificările (`git commit -m 'Add some AmazingFeature'`)
4. Push la branch (`git push origin feature/AmazingFeature`)
5. Deschideți un Pull Request

## Licență

Distribuit sub licența MIT. Vezi `LICENSE` pentru mai multe informații.

## Contact

Numele Dvs. - https://wa.me/40732159658?text=Salut!%20Cum%20te%20pot%20ajuta?

Link proiect: [https://github.com/arian222/alecs-whatsapp-pro](https://github.com/arian222/alecs-whatsapp-pro)
