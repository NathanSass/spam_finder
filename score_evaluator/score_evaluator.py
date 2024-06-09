import yaml

CONFIG_PATH = "score_evaluator/scoring_system.yml"


class ScoreEvaluator:
    def __init__(self):
        self._config = self.get_config()

    def load_config(self, file_path):
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def get_config(self):
        return self.load_config(CONFIG_PATH)

    def calculate_weighted_score(self, categories):
        score = 0.0
        for category, value in categories.items():
            if category in self._config["scoring_system"]["categories"]:
                weight = self._config["scoring_system"]["categories"][category][
                    "weight"
                ]
                score += weight * value
        return score

    def is_spam(self, categories):
        # Check if any category exceeds the single category threshold
        single_category_threshold = self._config["scoring_system"]["thresholds"][
            "single_category"
        ]
        for category, value in categories.items():
            if value > single_category_threshold:
                return True

        # Calculate weighted overall score
        overall_score = self.calculate_weighted_score(categories)
        overall_threshold = self._config["scoring_system"]["thresholds"][
            "overall_score"
        ]
        print("Overall Score is: " + str(overall_score))
        return overall_score > overall_threshold
