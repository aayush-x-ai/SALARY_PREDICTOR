import csv
import hashlib
import random
from pathlib import Path


CITIES = {
    "Bangalore": 1.16,
    "Mumbai": 1.12,
    "Hyderabad": 1.08,
    "Delhi": 1.05,
    "Pune": 1.00,
    "Chennai": 0.96,
}

ROLES = {
    "Software Developer": ("Software Development", 400_000),
    "Web Developer": ("Web Development", 320_000),
    "Data Analyst": ("Data Science", 380_000),
    "Data Scientist": ("Data Science", 600_000),
    "ML Engineer": ("Artificial Intelligence", 650_000),
    "AI Engineer": ("Artificial Intelligence", 700_000),
}

EDUCATION_BONUS = {
    "Diploma": -50_000,
    "B.Sc": 0,
    "BCA": 20_000,
    "B.Tech": 80_000,
    "MCA": 120_000,
    "MBA": 100_000,
    "M.Tech": 180_000,
}

EXPERIENCE_LEVELS = [0, 1, 2, 4, 7, 10]
OUTPUT_PATH = Path(__file__).with_name("dataset.csv")


def stable_number(*values):
    text = "|".join(str(value) for value in values)
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def calculate_profile(city, role, education, experience):
    domain, role_base = ROLES[role]
    profile_number = stable_number(city, role, education, experience)

    skills_count = min(10, 2 + (experience // 2) + (profile_number % 3))
    experience_value = experience * 115_000 + (experience**2) * 9_000
    skills_value = max(0, skills_count - 2) * 28_000
    variation = ((profile_number % 19) - 9) * 5_000

    salary = (
        (role_base + EDUCATION_BONUS[education] + experience_value + skills_value)
        * CITIES[city]
        + variation
    )
    salary = max(250_000, int(round(salary / 5_000) * 5_000))

    return {
        "city": city,
        "domain": domain,
        "job_role": role,
        "education": education,
        "experience_years": experience,
        "skills_count": skills_count,
        "salary": salary,
    }


def generate_dataset():
    rows = [
        calculate_profile(city, role, education, experience)
        for city in CITIES
        for role in ROLES
        for education in EDUCATION_BONUS
        for experience in EXPERIENCE_LEVELS
    ]

    random.Random(42).shuffle(rows)

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as dataset:
        writer = csv.DictWriter(
            dataset,
            fieldnames=[
                "city",
                "domain",
                "job_role",
                "education",
                "experience_years",
                "skills_count",
                "salary",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


if __name__ == "__main__":
    count = generate_dataset()
    print(f"Generated {count} salary profiles in {OUTPUT_PATH}")
