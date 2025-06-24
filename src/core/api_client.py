"""
Module: api_client
This module provides functions to interact with the HH.ru API
for retrieving job vacancy data and generating suggestions
based on job titles.
"""

import time
from src.settings.constants import BASE_URL
import requests
from bs4 import BeautifulSoup
from src.settings.config import get_max_results_per_request


def get_vacancy_skills(url: str) -> list[str]:
    """
    Returns a list of key skills from a vacancy page on hh.ru by its URL.

    Args:
        url (str): The URL of the hh.ru vacancy page.

    Returns:
        list: A list of key skills found in the vacancy description.

    Raises:
        ValueError: If there is an error loading the page (e.g., a non-200 HTTP response).
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Error loading page: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    skills_elements = soup.find_all("li", attrs={"data-qa": "skills-element"})

    return [el.get_text(strip=True) for el in skills_elements]


def get_exchange_rate(currency: str = "RUR") -> float:
    """
    Fetches the exchange rate to RUB for the specified currency.

    Args:
        currency (str): Currency code (e.g., "USD", "EUR"). Default is "RUR" (for Rubles).

    Returns:
        float: The exchange rate to RUB.
    """
    if currency == "RUR":
        return 1.0

    url = f"https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if currency in data["rates"]:
        return data["rates"][currency]
    else:
        raise ValueError(f"Currency {currency} not found in exchange rates.")


def convert_salary_to_rub(salary_value: float, currency: str) -> float:
    """
    Converts the salary to RUB based on the exchange rate of the specified currency.

    Args:
        salary_value (float): Salary value in the original currency.
        currency (str): The currency code of the salary.

    Returns:
        float: The salary converted to RUB.
    """
    if currency == "RUR":
        return salary_value
    if currency == "BYR":
        currency = "BYN"

    exchange_rate = get_exchange_rate(currency)
    return salary_value / exchange_rate


def search_vacancies(query: str, per_page: int = 50) -> list:
    """
    Searches for job vacancies on HH.ru based on the query, searching only in the description.

    Args:
        query (str): The job title or keyword to search for.
        per_page (int): The number of results per page (max 100).

    Returns:
        list: A list of job vacancies matching the query.
    """
    total_vacancies = get_max_results_per_request()
    all_vacancies = []
    page = 0
    while len(all_vacancies) < total_vacancies:
        url = f"{BASE_URL}/vacancies"
        params = {
            "text": query,
            "per_page": per_page,
            "page": page,
            "search_field": "name",
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        vacancies = data.get("items", [])
        all_vacancies.extend(vacancies)

        if len(all_vacancies) >= total_vacancies or not data.get("pages", 1) > page:
            break

        page += 1
        time.sleep(1)

    return all_vacancies[:total_vacancies]
