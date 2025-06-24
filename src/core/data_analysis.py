import numpy as np
from src.settings.config import get_salary_calculation_method
from src.core.api_client import convert_salary_to_rub
from collections import Counter
from src.core.api_client import get_vacancy_skills
from src.settings.config import get_top_skills_count


def get_top_skills(vacancies: list) -> list:
    """
    Get the top X most common skills across a list of vacancies.

    Args:
        vacancies (list): List of job vacancies (already retrieved).

    Returns:
        list: A list of tuples with the skill and its frequency, sorted by popularity.
    """
    top_x = get_top_skills_count()

    all_skills = []

    for vacancy in vacancies:
        skills = get_vacancy_skills(vacancy["alternate_url"])
        all_skills.extend(skills)

    skills_counter = Counter(all_skills)

    return skills_counter.most_common(top_x)


def get_top_regions(vacancies: list, top_x: int) -> list:
    """
    Determines the most popular regions for job vacancies.

    Args:
        vacancies (list): List of job vacancies.
        top_x (int): The number of top regions to return.

    Returns:
        list: A list of tuples with the region name and its frequency, sorted by popularity.
    """
    regions = [
        vacancy.get("area", {}).get("name")
        for vacancy in vacancies
        if vacancy.get("area")
    ]
    region_counts = Counter(regions)
    return region_counts.most_common(top_x)


def calculate_salary(vacancies: list, method: str = None) -> float:
    """
    Calculates the salary based on the method (average or median).

    Args:
        vacancies (list): List of job vacancies.
        method (str): Calculation method ("average" or "median").

    Returns:
        float: The calculated salary (average or median).
    """
    salary_values = []

    for vacancy in vacancies:
        salary = vacancy.get("salary")
        if not salary:
            continue

        salary_from = salary.get("from")
        salary_to = salary.get("to")
        currency = salary.get("currency", "RUR")

        if salary_from is not None and salary_to is None:
            salary_values.append(convert_salary_to_rub(salary_from, currency))
        elif salary_to is not None and salary_from is None:
            salary_values.append(
                convert_salary_to_rub(salary_to, currency)
            )
        elif salary_from is not None and salary_to is not None:
            avg_salary = (salary_from + salary_to) / 2
            salary_values.append(convert_salary_to_rub(avg_salary, currency))

    if not salary_values:
        return 0

    if method == "average":
        return np.mean(salary_values)
    elif method == "median":
        return np.median(salary_values)
    else:
        raise ValueError("Invalid calculation method: choose 'average' or 'median'.")


def get_salary_statistics(vacancies: list) -> float:
    """
    Calculate the salary statistic (average or median) for a list of vacancies.

    The calculation method is retrieved from the application configuration.

    Args:
        vacancies (list): A list of vacancy dictionaries.

    Returns:
        float: The computed salary value in RUB based on the selected method.
    """
    method = get_salary_calculation_method()
    stat_salary = calculate_salary(vacancies, method)
    return stat_salary


def get_salary_distribution(vacancies: list) -> list:
    """
    Extract a list of salary values from vacancies for distribution analysis.

    :param vacancies: List of vacancy dictionaries.
    :return: List of float salary values.
    """
    salaries = []
    for vacancy in vacancies:
        salary = vacancy.get("salary")
        if salary and salary.get("from") and salary.get("to"):
            average = (salary["from"] + salary["to"]) / 2
            salaries.append(average)
        elif salary and salary.get("from"):
            salaries.append(salary["from"])
        elif salary and salary.get("to"):
            salaries.append(salary["to"])
    return salaries
