import requests
from bs4 import BeautifulSoup
import re

def extract_drug_info(title):
    brand_match = re.search(r"taking\s+([A-Za-z0-9]+)", title)
    ingredient_match = re.search(r"\((.*?)\)", title)
    brand = brand_match.group(1) if brand_match else ""
    ingredient = ingredient_match.group(1) if ingredient_match else ""
    return brand, ingredient

def extract_action_and_population(title):
    action_match = re.search(r"(requires warning|recommend|update|remove|add warning|adds Boxed Warning)", title, re.IGNORECASE)
    population_match = re.search(r"for (.*?) taking", title)
    action = action_match.group(1) if action_match else "N/A"
    population = population_match.group(1) if population_match else "N/A"
    return action, population

def get_fda_current_communications():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    current_section = soup.find("h2", string="Current Drug Safety Communications")
    previous_section = soup.find("h2", string="Previous Drug Safety Communications")

    items = []
    if current_section and previous_section:
        ul = current_section.find_next("ul")
        while ul and ul != previous_section.find_previous("ul"):
            for li in ul.find_all("li"):
                text_parts = li.get_text(strip=True).split(" ", 1)
                date_text = text_parts[0] if len(text_parts) > 0 else ""
                link = li.find("a")
                if link:
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    full_url = href if href.startswith("http") else f"https://www.fda.gov{href}"

                    brand, ingredient = extract_drug_info(title)
                    action, population = extract_action_and_population(title)

                    items.append({
import requests
from bs4 import BeautifulSoup
import re

def extract_drug_info(title):
    brand_match = re.search(r"taking\s+([A-Za-z0-9]+)", title)
    ingredient_match = re.search(r"\((.*?)\)", title)
    brand = brand_match.group(1) if brand_match else ""
    ingredient = ingredient_match.group(1) if ingredient_match else ""
    return brand, ingredient

def extract_action_and_population(title):
    action_match = re.search(r"(requires warning|recommend|update|remove|add warning|adds Boxed Warning)", title, re.IGNORECASE)
    population_match = re.search(r"for (.*?) taking", title)
    action = action_match.group(1) if action_match else "N/A"
    population = population_match.group(1) if population_match else "N/A"
    return action, population

def get_fda_current_communications():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    current_section = soup.find("h2", string="Current Drug Safety Communications")
    previous_section = soup.find("h2", string="Previous Drug Safety Communications")

    items = []
    if current_section and previous_section:
        ul = current_section.find_next("ul")
        while ul and ul != previous_section.find_previous("ul"):
            for li in ul.find_all("li"):
                text_parts = li.get_text(strip=True).split(" ", 1)
                date_text = text_parts[0] if len(text_parts) > 0 else ""
                link = li.find("a")
                if link:
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    full_url = href if href.startswith("http") else f"https://www.fda.gov{href}"

                    brand, ingredient = extract_drug_info(title)
                    action, population = extract_action_and_population(title)

                    items.append({
                        "date": date_text,
                        "title": title,
                        "brand": brand,
                        "ingredient": ingredient,
                        "population": population,
                        "action": action,
                        "url": full_url
                    })
            ul = ul.find_next("ul")

    return items

                        "date": date_text,
                        "title": title,
                        "brand": brand,
                        "ingredient": ingredient,
                        "population": population,
                        "action": action,
                        "url": full_url
                    })
            ul = ul.find_next("ul")

    return items
