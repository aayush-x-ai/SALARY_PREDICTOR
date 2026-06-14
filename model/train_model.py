import csv
from pathlib import Path

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


class SalaryPredictor:
    """Random Forest regression model trained from the salary dataset."""

    def __init__(self, dataset_path):
        path = Path(dataset_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[1] / path

        with path.open(encoding="utf-8", newline="") as dataset:
            self.rows = list(csv.DictReader(dataset))

        if not self.rows:
            raise ValueError("Salary dataset is empty.")

        features = [
            [
                row["city"],
                row["domain"],
                row["job_role"],
                row["education"],
                float(row["experience_years"]),
                int(row["skills_count"]),
            ]
            for row in self.rows
        ]
        salaries = [float(row["salary"]) for row in self.rows]

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "categories",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    [0, 1, 2, 3],
                ),
                ("numbers", "passthrough", [4, 5]),
            ]
        )

        forest = RandomForestRegressor(
            n_estimators=250,
            random_state=42,
            min_samples_leaf=1,
            n_jobs=-1,
        )

        self.model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", forest),
            ]
        )
        self.model.fit(features, salaries)

    @staticmethod
    def _skills_count(skills):
        return len({skill.strip().lower() for skill in skills.split(",") if skill.strip()})

    def predict(self, education, skills, experience_months, city, domain, job_role):
        profile = [
            [
                city,
                domain,
                job_role,
                education,
                experience_months / 12,
                self._skills_count(skills),
            ]
        ]

        raw_salary = self.model.predict(profile)[0]

        transformed_profile = self.model.named_steps["preprocessor"].transform(profile)
        forest = self.model.named_steps["regressor"]
        tree_predictions = np.array(
            [tree.predict(transformed_profile)[0] for tree in forest.estimators_]
        )

        salary = int(round(raw_salary / 1000) * 1000)
        lower_estimate = int(round(np.percentile(tree_predictions, 10) / 1000) * 1000)
        upper_estimate = int(round(np.percentile(tree_predictions, 90) / 1000) * 1000)
        minimum = min(lower_estimate, salary - 50_000)
        maximum = max(upper_estimate, salary + 50_000)

        return {
            "salary": salary,
            "minimum": max(0, minimum),
            "maximum": maximum,
            "training_records": len(self.rows),
            "trees": forest.n_estimators,
        }
