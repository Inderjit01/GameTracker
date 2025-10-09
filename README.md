# GameTracker

## Screenshots

<img width="450" height="338" alt="image" src="https://github.com/user-attachments/assets/e4b44f5f-760d-4b7b-9860-6a367c106ae5" />
<img width="450" height="338" alt="image" src="https://github.com/user-attachments/assets/c4b80477-19d0-4683-bd06-dff82b203e34" />
<img width="450" height="338" alt="image" src="https://github.com/user-attachments/assets/773759c5-562c-42f1-8ff4-5f5fa9d05916" />
<img width="450" height="338" alt="image" src="https://github.com/user-attachments/assets/0c4420f9-b51b-47bb-b4a6-00ebb921cbd2" />

**GameTracker** is a desktop application for tracking your video game library, backlog, and wishlist. It fetches **game info, completion times, and prices** from multiple platforms, including Steam, Epic Games, Xbox, PlayStation, and Nintendo. Built with **Python and PyQt5**, it features a modern dark-themed interface and an **auto-update mechanism**.

---

## Features

- **Backlog & Wishlist Management**
  - Add games to backlog or wishlist.
  - Mark games as owned, favorite, or completed.
  - Track completion dates automatically.

- **Game Info Integration**
  - Fetch game details from **RAWG**.
  - Fetch **HowLongToBeat** stats (main story, extras, completionist, all-styles hours).

- **Price Tracking**
  - Current game prices from **Steam, Epic Games, Xbox, PlayStation, Nintendo**.
  - Full price, sale price, and subscriptions (Game Pass, PS Extra, PS Premium).
  - Detect free games and discounts.

- **Custom Game Cards**
  - Cover art, platforms, review score, hours, dates, and price info.
  - Interactive buttons for favorite, owned, completed status.

- **Filtering & Sorting**
  - Filter by backlog, wishlist, favorites, completed, score, or completion hours.
  - Sort by name, score, hours, or completion date.

- **Auto Update**
  - Checks GitHub for new versions and downloads updates automatically.

- **Dark Theme**
  - Clean, modern interface using `styles.qss`.

---

## Installation

### From Installer (Windows)

1. Download the latest [GameTrackerInstaller.exe](https://github.com/Inderjit01/GameTracker/releases).  
2. Run the installer and follow the prompts.  
3. The application will be installed to your selected folder.  

### From Source

> **Note:** The `api.py` file does **not include API keys**. If you want to use the source code, you must add your own keys for RAWG, IsThereAnyDeal, and PlatPrices.
> **Note:** Only need `src\GameTracker` if you don't want updates through Git.

1. Download /src/GameTracker.
2. pip install -r requirements.txt
3. Edit /controllers/api.py with your api keys.
4. Edit version.py with your own version number.
5. If you want remote updates through git edit /controllers/update_checker.py with the url to your git, otherwise you can remove the call to update_checker in app.py.
6. Run app.py.
