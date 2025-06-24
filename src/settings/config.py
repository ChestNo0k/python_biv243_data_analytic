import os
import json

CONFIG_FILE = os.path.join("src", "settings", "config.json")


def load_config():
    """Load configuration from the config.json file."""
    if not os.path.exists(CONFIG_FILE):
        save_config(
            {
                "window_size": (600, 400),
                "salary_calculation_method": "average",
                "max_results_per_request": 50,
                "top_skills_count": 5,
                "top_regions_count": 5,
            }
        )

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    """Save configuration to the config.json file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_window_size():
    """Get the window size configuration."""
    config = load_config()
    return config.get("window_size", (600, 400))


def set_window_size(width, height):
    """Set the window size in the configuration."""
    config = load_config()
    config["window_size"] = (width, height)
    save_config(config)


def get_salary_calculation_method():
    """Get the salary calculation method from the configuration."""
    config = load_config()
    return config.get("salary_calculation_method", "average")


def set_salary_calculation_method(method):
    """Set the salary calculation method in the configuration."""
    config = load_config()
    config["salary_calculation_method"] = method
    save_config(config)


def get_max_results_per_request():
    """Get the maximum number of results per request."""
    config = load_config()
    return config.get("max_results_per_request", 50)


def set_max_results_per_request(count):
    """Set the maximum number of results per request in the configuration."""
    config = load_config()
    config["max_results_per_request"] = count
    save_config(config)


def get_top_skills_count():
    """Get the number of top skills to return."""
    config = load_config()
    return config.get("top_skills_count", 5)


def set_top_skills_count(count):
    """Set the number of top skills to return in the configuration."""
    config = load_config()
    config["top_skills_count"] = count
    save_config(config)


def get_top_regions_count():
    """Get the number of top regions to return."""
    config = load_config()
    return config.get("top_regions_count", 5)


def set_top_regions_count(count):
    """Set the number of top regions to return in the configuration."""
    config = load_config()
    config["top_regions_count"] = count
    save_config(config)
