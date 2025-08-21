from ruamel.yaml import YAML


def main():

    yaml = YAML()
    project = {"version": '4.0', "actions": {}}

    needs_list = []
    # 5 years
    for year in range(2020, 2025):
        project["actions"][f"generate_dataset_minimal_{year}"] = {
                "run": (
                    "ehrql:v1 generate-dataset analysis/dataset_definition_minimal.py "
                    f"--output output/dataset_min_{year}.arrow "
                    f"-- --year={year}"
                ),
                "outputs": {
                    "highly_sensitive": {
                        "dataset": f"output/dataset_min_{year}.arrow"
                    }
                }
            }
        needs_list.append(f"generate_dataset_minimal_{year}")

    # minimal python actions to accumulate lots of jobs (2500 total)
    for i in range(500):
        for needs in needs_list:    
            project["actions"][f"copy_to_txt_{needs}_{i}"] = {
                    "run": (
                        f"python:v2 analysis/copy_to_txt.py {needs} {i}"
                    ),
                    "needs": [needs],
                    "outputs": {
                        "moderately_sensitive": {
                            "report": f"output/{needs}_{i}.txt"
                        }
                    }
                }

    with open("project.yaml", "w") as outfile:
        yaml.dump(project, outfile)


if __name__ == "__main__":
    main()
