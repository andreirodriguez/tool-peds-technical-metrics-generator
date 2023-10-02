import json
import csv
from pathlib import Path
import pandas as pd

def get_repository_data(project, repo_name, repo_data):
    specialty = ""
    if repo_data.get("type", "") == "android-kotlin":
        specialty = "FRONTEND ANDROID"
    elif repo_data.get("type", "") == "ios-swift":
        specialty = "FRONTEND IOS"
    elif repo_data.get("type", "") == "web-javascript":
        specialty = "FRONTEND WEB"
    elif repo_data.get("type", "") == "atlas":
        specialty = "BACKEND JAVA"
    return {
        "project": project,
        "repository_name": repo_name.lower(),
        "technology": repo_data.get("type", ""),
        "specialty": specialty,
        "application_type":""
    }

def write_to_csv(output_path, repo_data_list):
    with open(output_path, "w", newline="") as f:
        fieldnames = ["project", "repository_name", "technology", "specialty","application_type"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repo_data_list)

def get_all_repo_data(json_files):
    unique_repos = set()
    all_repo_data = []
    for json_file in json_files:
        with open(json_file, "r") as f:
            json_data = json.load(f)
            project = json_data["project"]
            repositories = json_data["repositories"]
            for repo_name, repo_data in repositories.items():
                repo_key = (project, repo_name.lower())
                if repo_key not in unique_repos:
                    unique_repos.add(repo_key)
                    repo_data = get_repository_data(project, repo_name, repo_data)
                    repo_data["repository_name"] = repo_data["repository_name"].lower()
                    all_repo_data.append(repo_data)
    return all_repo_data

df = pd.read_excel('input/Legacy/Legacy.xlsx') 

legacy = df.values       

if __name__ == "__main__":
    directory_path = Path("input")
    json_files = [f for f in directory_path.glob("*.json")]

    all_repo_data = get_all_repo_data(json_files)

for item in legacy:
    for all_item in all_repo_data:
        if item[0]  ==  all_item['project'] and item[1] == all_item['repository_name']:
            all_item['application_type'] = "LEGACY"
            break
        else:
            new_repo = {"project": item[0], "repository_name": item[1], "technology": "", "specialty": "", "application_type": "LEGACY"}
            all_repo_data.append(new_repo)
            break
            
output_path = "output/specialty-file.csv"
write_to_csv(output_path, all_repo_data)
print("Success!")