import os
import requests
import html

USERNAME = "Manas-Dikshit"
TOKEN = os.environ.get("GH_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def get_repositories():
    repositories = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/user/repos"
            f"?per_page=100&page={page}&affiliation=owner,collaborator,organization_member"
        )

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        data = response.json()

        if not data:
            break

        repositories.extend(data)
        page += 1

    return repositories


def count_commits(repo):
    owner = repo["owner"]["login"]
    name = repo["name"]

    # Ignore forks because they can contain duplicated commit history.
    if repo["fork"]:
        return 0

    count = 0
    page = 1

    while True:
        url = (
            f"https://api.github.com/repos/{owner}/{name}/commits"
            f"?author={USERNAME}&per_page=100&page={page}"
        )

        response = requests.get(url, headers=HEADERS)

        if response.status_code == 409:
            break

        if response.status_code == 404:
            break

        response.raise_for_status()

        commits = response.json()

        if not commits:
            break

        count += len(commits)
        page += 1

    return count


def create_svg(commits, repositories):
    commits_text = f"{commits:,}"
    repos_text = f"{repositories:,}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="495" height="195" viewBox="0 0 495 195">

<rect width="495" height="195"
rx="12"
fill="#0d1117"
stroke="#30363d"/>

<text x="24" y="38"
font-family="Arial, sans-serif"
font-size="22"
font-weight="bold"
fill="#007BFF">
GitHub Statistics
</text>

<line x1="24" y1="55"
x2="471" y2="55"
stroke="#30363d"/>

<text x="55" y="100"
font-family="Arial, sans-serif"
font-size="30"
font-weight="bold"
fill="#007BFF">
{commits_text}
</text>

<text x="55" y="125"
font-family="Arial, sans-serif"
font-size="14"
fill="#007BFF">
Total Commits
</text>

<text x="290" y="100"
font-family="Arial, sans-serif"
font-size="30"
font-weight="bold"
fill="#007BFF">
{repos_text}
</text>

<text x="290" y="125"
font-family="Arial, sans-serif"
font-size="14"
fill="#007BFF">
Repositories
</text>

<text x="24" y="165"
font-family="Arial, sans-serif"
font-size="12"
fill="#007BFF">
Manas-Dikshit
</text>

</svg>
"""

    with open("github-stats.svg", "w", encoding="utf-8") as file:
        file.write(svg)


def main():
    repositories = get_repositories()

    total_commits = 0

    for repo in repositories:
        try:
            commits = count_commits(repo)
            total_commits += commits

            print(
                f"{repo['full_name']}: {commits} commits"
            )

        except Exception as error:
            print(
                f"Skipping {repo['full_name']}: {error}"
            )

    create_svg(
        total_commits,
        len([repo for repo in repositories if not repo["fork"]])
    )

    print()
    print(f"Total commits: {total_commits}")


if __name__ == "__main__":
    main()
