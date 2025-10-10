import requests, re
from howlongtobeatpy import HowLongToBeat
from difflib import SequenceMatcher
from  nintendeals import noa
from nintendeals.api import prices

# Using RAWG API to get game titles
RAWG_API_KEY = ''
# Using IsThereAnyDeal to get epic and xbox game price
ISTHEREANYDEAL_API_KEY = ''
# Using Plat Prices to get playsation game price
PLAT_PRICES_API_KEY = ''
# Dont need steam key yet
# Steam api Key: ''
#Domain Name: localhost

'''Some titles have been remastered and they include the year in the title 
   but some api dont like the year in the title so I also try removing the year if it fails.
'''
def _clean_title(title):
    search_titles = [title]
    new_title = re.sub(r'\(\d{4}\)', '', title).strip()
    if new_title != title:
        search_titles.append(new_title)
    return search_titles

''' If an api returns multiple games information based on name similiarty then 
    grab the one with the name that most closely matches the title searched.
    This returns a number between 0 and 1. 0 meaning not realted at all and 1 meaning completely matching
'''
def _similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Finds the steam id so I can search for the price
def _get_steam_id(game_name, country='US'):
    ID_URL = 'https://store.steampowered.com/api/storesearch/'
    params = {'term': game_name, 'cc': country}
    try:
        request_data = requests.get(ID_URL, params=params, timeout=10)
        request_data.raise_for_status()
    except requests.RequestException:
        return None
    
    id_data = request_data.json().get('items', [])
    if not id_data:
        return None
            
    best_item = max(id_data, key=lambda x: _similarity(game_name, x['name']))
    return best_item['id']

# Uses RAWG API to get list of games closest to user search input when adding games. Info: game title, platforms, rating, and release date
def search_games(query, max_results=10):
    RAWG_BASE_URL = 'https://api.rawg.io/api/games'
    params = {
        'key': RAWG_API_KEY,
        'search': query,
        'page_size': max_results
    }
    
    response = requests.get(RAWG_BASE_URL, params=params, timeout=10)
    if response.status_code != 200:
        return []
    data = response.json()
    if not data:
        return []
    
    results = []
    for g in data.get('results', []):
        platforms_list = g.get('platforms') or []
        results.append({
            'name': g['name'],
            'platforms': [p['platform']['name'] for p in platforms_list],
            'rating': g.get('rating', 0),
            'released': g.get('released', ''),
            'background_image': g.get('background_image')
            })
    return results

# From HowLongToBeat grabs the hours (main, extra, completionist, all styles) and the image url
def fetch_hltb_data(game_name):
    search_titles = _clean_title(game_name)    
    for game_title in search_titles:
        results = HowLongToBeat().search(game_title)
        # pick the closest results from user search input
        if results:
            # similarity is a built in attribute of howlongtobeat library
            best_match = max(results, key=lambda r: r.similarity) 
            
            data = {
                'name': best_match.game_name,
                'main_story_hours': best_match.main_story,
                'main_extras_hours': best_match.main_extra,
                'completionist_hours': best_match.completionist,
                'all_styles_hours': best_match.all_styles,
                'url': best_match.game_web_link
            }
            return data
    return None

# Returns the steam score of the game if it exists
def fetch_steam_review_score(game_name, country='US'):
    search_titles = _clean_title(game_name)
    
    for game_title in search_titles:
        game_id = _get_steam_id(game_title, country)
        if not game_id:
            continue
        
        review_url = f'https://store.steampowered.com/appreviews/{game_id}' 
        params = {
            'json': 1,
            'language': 'all',
            'purchase_type': 'all'
        }
        
        try:
            request_data = requests.get(review_url, params, timeout=10)
            request_data.raise_for_status()
        except:
            continue
        
        data = request_data.json()
        if not data:
            continue
        
        summary = data.get('query_summary', None)
        if not summary:
            continue
        
        positive_votes = summary.get('total_positive', 0)
        total_votes = summary.get('total_reviews', 0)
        
        if total_votes > 0:
            score = round((positive_votes / total_votes) * 5, 2)
            return score
        
    return None

# Return the current steam price of game if it exists
def steam_prices(game_name, country='US'):
    search_titles = _clean_title(game_name)
    
    for game_title in search_titles:
        game_id = _get_steam_id(game_title, country)
        if not game_id:
            continue
        
        GAME_URL = 'https://store.steampowered.com/api/appdetails'
        params = {
            'appids': str(game_id), 
            'cc':country, 
            'filters': 'price_overview'
        }
        
        try:
            request_data = requests.get(GAME_URL, params=params, timeout=10)
            request_data.raise_for_status()
        except requests.RequestException:
            continue
        
        store_data = request_data.json()
        game_info = store_data.get(str(game_id))
        if not game_info or not game_info.get('success', False):
            continue
        
        game_data = game_info.get('data', None)
        if game_data == []:
            return 'Free'
        if not game_data or not isinstance(game_data, dict):
            continue
        
        game_prices = game_data.get('price_overview', None)
        if not game_prices:
            return 'Free'
        
        return {
            'currency': game_prices['currency'],
            'initial': game_prices['initial'] / 100.0,
            'final': game_prices['final'] / 100.0,
            'discount_percent': game_prices['discount_percent']
        }
    return None

# Returns the current epic store price if it exists
def epic_prices(game_name, country='US'):
    search_titles = _clean_title(game_name)
    
    for game_title in search_titles:
        url = "https://api.isthereanydeal.com/lookup/id/title/v1"
        try:
            request_data = requests.post(
                url,
                json=[game_title],
                headers={"Content-Type": "application/json"}
            )
            request_data.raise_for_status()
        except requests.RequestException:
            continue
        
        lookup_data = request_data.json()
        game_id = lookup_data.get(game_title)
        if not game_id:
            continue

        prices_url = f"https://api.isthereanydeal.com/games/prices/v3?key={ISTHEREANYDEAL_API_KEY}&country={country}"
        try:
            prices_request = requests.post(
                prices_url,
                json=[game_id],
                headers={"Content-Type": "application/json"}
            )
            prices_request.raise_for_status()
        except requests.RequestException:
            continue
        
        prices_data = prices_request.json()
        if not prices_data or not isinstance(prices_data, list):
            continue
        
        game_prices = prices_data[0].get("deals", [])
        
        # Filter for Epic Games Store (shop ID 16)
        epic_deals = [d for d in game_prices if d.get("shop", {}).get("id") == 16]
        if not epic_deals:
            continue
        
        deal = epic_deals[0]
        regular = deal.get("regular", {})
        price = deal.get("price", {})
        cut = deal.get("cut", 0)
        
        regular_amount = regular.get("amount", 0.0)
        price_amount = price.get("amount", 0.0)
        
        if price_amount == 0 or regular_amount == 0:
            return "Free"
        
        return {
            "currency": price.get("currency") or regular.get("currency", "USD"),
            "initial": regular_amount,
            "final": price_amount,
            "discount_percent": cut
        }
    
    return None

def xbox_prices(game_name, country="US"):
    search_titles = _clean_title(game_name)
    
    for game_title in search_titles:
        lookup_url = "https://api.isthereanydeal.com/lookup/id/title/v1"
        try:
            request_data = requests.post(
                lookup_url,
                json=[game_title],
                headers={"Content-Type": "application/json"}
            )
            request_data.raise_for_status()
        except requests.RequestException:
            continue
        
        lookup_data = request_data.json()
        game_id = lookup_data.get(game_title)
        if not game_id:
            continue

        prices_url = f"https://api.isthereanydeal.com/games/prices/v3?key={ISTHEREANYDEAL_API_KEY}&country={country}"
        try:
            prices_request = requests.post(
                prices_url,
                json=[game_id],
                headers={"Content-Type": "application/json"}
            )
            prices_request.raise_for_status()
        except requests.RequestException:
            continue
        
        prices_data = prices_request.json()
        if not prices_data or not isinstance(prices_data, list):
            continue
        
        game_prices = prices_data[0].get("deals", [])
        
        ms_deals = [d for d in game_prices if d.get("shop", {}).get("id") == 48]  # Microsoft Store
        price_info = None
        if ms_deals:
            deal = ms_deals[0]
            regular = deal.get("regular", {})
            price = deal.get("price", {})
            cut = deal.get("cut", 0)
            
            regular_amount = regular.get("amount", 0.0)
            price_amount = price.get("amount", 0.0)
            
            if price_amount == 0 and regular_amount == 0:
                price_info = "Free"
            else:
                price_info = {
                    "currency": price.get("currency") or regular.get("currency", "USD"),
                    "initial": regular_amount,
                    "final": price_amount,
                    "discount_percent": cut,
                    'game_pass': False
                }
        
        subs_url = f"https://api.isthereanydeal.com/games/subs/v1?key={ISTHEREANYDEAL_API_KEY}"
        try:
            subs_request = requests.post(
                subs_url,
                json=[game_id],
                headers={"Content-Type": "application/json"}
            )
            subs_request.raise_for_status()
        except requests.RequestException:
            return {"price": price_info, "game_pass": None}
        
        subs_data = subs_request.json()
        game_pass = None
        if subs_data and isinstance(subs_data, list) and "subs" in subs_data[0]:
            subs = subs_data[0]["subs"]
            game_pass = [s for s in subs if "Game Pass" in s.get("name", "")]
            if game_pass:
                price_info['game_pass'] = True
        
        return price_info
    
    return None

# Grabs the current price of playstation prices
def playstation_prices(game_name, country='US'):
    search_titles = _clean_title(game_name)
    
    for title in search_titles:
        ppid_url = 'https://platprices.com/api.php'
        params = {
            'key': PLAT_PRICES_API_KEY,
            'mode': 'search',
            'name': game_name
        }
        ppid_request = requests.get(ppid_url, params=params)
        if ppid_request.status_code != 200:
            continue
        
        data = ppid_request.json()
        if not data:
            continue
        
        currency = data.get('Region', None)
        discount = data.get('DiscPerc', None)
        initial = data.get('BasePrice', None)
        sale = data.get('SalePrice', None)
        if initial:
            initial = int(initial) / 100
        if sale:
            sale = int(sale) / 100
            
        if initial == 0:
            return 'Free'
        
        price_info = {
            'currency': currency,
            'initial': initial,
            'final': sale,
            'discount_percent': discount,
            'playstation_extra': True if data.get('PSPExtra', '0') == '1' else False,
            'playstation_premium': True if data.get('PSPPremium', '0') == '1' else False
        }
        return price_info
         
    return None

# Grabs the current price of nintendo games
def nintendo_prices(game_name, country='US'):
    search_titles = _clean_title(game_name)

    best_game = None
    for title in search_titles:
        # noa is North America
        search_results = list(noa.search_switch_games(query=title))
        if not search_results:
            continue
        
        # pick the best match by similarity
        try:
            best_game_candidate = max(search_results, key=lambda g: _similarity(title, g.title))
        except ValueError:
            continue
        
        if best_game is None or _similarity(title, best_game_candidate.title) > _similarity(title, best_game.title):
            best_game = best_game_candidate

    if not best_game:
        return None

    # Get price 
    price_obj = prices.get_price(best_game, country)
    if not price_obj:
        return None

    # Safely get values
    initial = getattr(price_obj, "value", None)
    final = getattr(price_obj, "discounted_value", initial)
    currency = getattr(price_obj, "currency", "USD")
    discount_percent = getattr(price_obj, "discount_percent", 0)

    # Detect free game
    if initial in (0, 0.0, None):
        return "Free"

    return {
        "currency": currency,
        "initial": float(initial),
        "final": float(final),
        "discount_percent": int(discount_percent)
    }    