# GameTracker

![image_placeholder](image_placeholder)

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

## Screenshots

![image_placeholder](image_placeholder)  
*Game library view.*

![image_placeholder](image_placeholder)  
*Add game dialog with search suggestions.*

---

## Installation

### From Installer (Windows)

1. Download the latest [GameTrackerInstaller.exe](image_placeholder).  
2. Run the installer and follow the prompts.  
3. The application will be installed to your selected folder.  

### From Source

> **Note:** The `api.py` file does **not include API keys**. If you want to use the source code, you must add your own keys for RAWG, IsThereAnyDeal, and PlatPrices.

1. Clone the repository:

```bash
git clone https://github.com/YourUsername/GameTracker.git
cd GameTracker
