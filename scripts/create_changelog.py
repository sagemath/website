#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script is used in 'Generate Changelog' workflow, defined in the 'generate_changelog.yml' file
to automate the process of creating changelogs after each stable release.

It fetches release data, extracts relevant pull request (PR) information, and generates a detailed changelog
and add it to src/changelogs.
The script uses the GitHub REST API to collect information about contributors, PR authors, and reviewers.

Additional Note:
- The script requires a GitHub personal access token (PAT) stored in an environment variable named `GITHUB_PAT`.
"""

import requests
import re
from dotenv import load_dotenv
import os
import argparse
import xml.etree.ElementTree as ET
from unidecode import unidecode

load_dotenv()
GITHUB_PAT = os.getenv('GITHUB_PAT')
BASE_URL = r"https://api.github.com/repos/sagemath/sage"
HEADERS = {'Authorization': f'token {GITHUB_PAT}', }
AUTOMATED_BOTS = ['dependabot[bot]', 'github-actions', 'renovate[bot]']

# Maps the github username to contributer name
git_to_name = {}

# Stores unique names of contributors
all_contribs = set([])

# Stores unique names of contributors
first_contribs = set([])

# Stores information for all the prs across all pre-releases
# Maps tag of pre-release to its info
all_info = {}


def map_git_to_names():
    tree = ET.parse('conf/contributors.xml')
    root = tree.getroot()
    for c in root.findall('contributor'):
        name = c.get('name')
        git = c.get('github')
        if git and name:
            git_to_name[git] = unidecode(name)


def update_names():
    """
    Replace the github usernames with real names. If name is not found in contributors.xml,
    then github usernames are used in the form @<github-username>
    """
    for tag in all_info:
        for pr in all_info[tag]:
            pr['creator'] = git_to_name.get(pr['creator'], f"@{pr['creator']}")
            pr['authors'] = [git_to_name.get(a, f"@{a}") for a in pr['authors']]
            pr['reviewers'] = [git_to_name.get(r, f"@{r}") for r in pr['reviewers']]
    global all_contribs
    global first_contribs
    all_contribs = set([git_to_name.get(c, f"@{c}") for c in all_contribs])
    first_contribs = set([git_to_name.get(c, f"@{c}") for c in first_contribs])


def get_release_data(tag):
    url = fr"{BASE_URL}/releases/tags/{tag}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 404:
        print(f"{tag} release not found")
        return None
    if res.status_code != 200:
        print(f"Failed to fetch release data: {res.status_code}")
        return None
    return res.json()


def get_release_date(release_data):
    if not release_data:
        return 'N/A'
    date_time = release_data.get('published_at', '')
    if not date_time:
        return 'Unavailable'
    return date_time.split('T')[0]


def extract_pr_info(release_data):
    body = release_data.get('body', '')
    pr_info = []
    pattern = r"\* (.*?) by (@\S+) in https://github.com/sagemath/sage/pull/(\d+)"
    matches = re.findall(pattern, body)
    for match in matches:
        title = match[0]
        creator = match[1][1::]
        pr_id = match[2]
        authors = get_authors(pr_id)
        reviewers = get_reviewers(pr_id, authors)
        pr_info.append({
            'title': title,
            'creator': creator,
            'pr_id': pr_id,
            'authors': authors,
            'reviewers': reviewers
        })
    return pr_info


def update_first_contribs(release_data):
    body = release_data.get('body', '')
    pattern = r"\* (@\S+) made their first contribution in"
    matches = re.findall(pattern, body)
    for match in matches:
        username = match[1::]
        first_contribs.add(username)


def get_authors(pr_id):
    url = f"{BASE_URL}/pulls/{pr_id}/commits"
    authors = []
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        commits = res.json()
        for commit in commits:
            if commit['commit']['committer']['name'] in AUTOMATED_BOTS:
                continue
            if 'author' in commit and 'login' and commit['author']:
                username = commit['author']['login']
                if username not in AUTOMATED_BOTS:
                    authors.append(username)
                    all_contribs.add(username)
    except Exception as e:
        print(f"Failed to fetch commits for PR {pr_id}: {e}")
    return list(set(authors))


def get_reviewers(pr_id, authors):
    url = f"{BASE_URL}/pulls/{pr_id}/reviews"
    reviewers = []
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        reviews = res.json()
        for review in reviews:
            if 'user' in review and 'login' in review['user']:
                username = review['user']['login']
                if username not in authors and username not in AUTOMATED_BOTS:
                    reviewers.append(username)
                    all_contribs.add(username)
    except Exception as e:
        print(f"Failed to fetch reviews for PR {pr_id}: {e}")
    return list(set(reviewers))


def get_latest_tags():
    url = f"{BASE_URL}/tags?per_page=100"  # If per_page is not specified then very few tags are fetched
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        tags = res.json()
        tags = [tag['name'] for tag in tags]
        return tags
    except Exception as e:
        print(f"Failed to fetch tags")
        return None


def sort_tags(tag):
    name = tag.lower()
    if "beta" in name:
        return (0, name)  # Beta comes first
    elif "rc" in name:
        return (1, name)  # RC comes next
    else:
        return (2, name)  # Stable versions come last


def save_to_file(filename, ver, date_of_release):
    with open(filename, 'w') as file:
        file.write(f"Sage {ver} was released on {date_of_release}. It is available from:\n\n")
        file.write(f"  * https://www.sagemath.org/download-source.html\n\n")
        file.write(f"Sage (http://www.sagemath.org) is developed by volunteers and\n")
        file.write(f"combines hundreds of open source packages.\n\n")
        file.write(f"The following {len(all_contribs)} people contributed to this release.\n")
        file.write(f"Of those, {len(first_contribs)} made their first contribution to Sage:\n\n")
        max_name_len = max([len(c) for c in all_contribs])
        for c in all_contribs:
            file.write(f"  - {c}{' '*(max_name_len - len(c)) + ' [First Contribution]' if c in first_contribs else ''}\n")
        pr_count = sum([len(all_info[tag]) for tag in all_info])
        file.write(f"\n* We merged {pr_count} pull requests in this release.\n\n")
        sorted_tags = sorted(all_info.keys(), key=sort_tags)
        for tag in sorted_tags:
            file.write(f"Merged in sage-{tag}:\n\n")
            for pr in all_info[tag]:
                file.write(f"#{pr['pr_id']}: {', '.join(pr['authors'])}: {pr['title']}")
                if pr['reviewers']:
                    file.write(f" [Reviewed by {', '.join(pr['reviewers'])}]")
                file.write('\n')
            file.write('\n')

    print(f"Saved changelog to {filename}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch release data from GitHub and extract PR info")
    parser.add_argument('version', type=str, help="The release version (e.g., 10.1)")
    args = parser.parse_args()
    ver = args.version
    is_stable = re.match(r'^\d+(\.\d+){0,3}$', ver)
    if not is_stable:
        print(f"{ver} is not a stable release. terminating....")
        exit()

    filepath = f"src/changelogs/sage-{ver}.txt"
    if os.path.exists(filepath):
        print(f"{filepath} already exists. Exiting without making changes.")
        exit()

    map_git_to_names()
    all_tags = get_latest_tags()
    tag_pattern = fr"^{ver}.(beta|rc)\d*$"
    valid_tags = set([ver,])
    for tag in all_tags:
        if re.match(tag_pattern, tag):
            valid_tags.add(tag)

    for tag in valid_tags:
        release_data = get_release_data(tag)
        if tag == ver:
            date_of_release = get_release_date(release_data)
        if release_data is None:
            continue
        pr_info = extract_pr_info(release_data)
        all_info[tag] = pr_info
        update_first_contribs(release_data)
        print(f"Fetched data for tag: {tag}")

    update_names()
    first_contribs = first_contribs.intersection(all_contribs)
    all_contribs = sorted(all_contribs, key=lambda x: (x[0].startswith('@'), x[0]))
    if all_info:
        save_to_file(filepath, ver, date_of_release)
    else:
        print("No information found.")
