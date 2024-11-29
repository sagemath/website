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
import html

load_dotenv()
GITHUB_PAT = os.getenv('GITHUB_PAT')
BASE_URL = r"https://api.github.com/repos/sagemath/sage"
HEADERS = {'Authorization': f'token {GITHUB_PAT}', }
AUTOMATED_BOTS = ['dependabot[bot]', 'github-actions', 'renovate[bot]']

# Maps the github username to contributor name
git_to_name = {}

# Stores unique names of contributors
all_contribs = set([])

# Stores unique names of first constributors
first_contribs = set([])

# Stores information for all the prs across all pre-releases
# Maps tag of pre-release to its info
all_info = {}

# Stores new names which didn't previously existed in conf/contributor.xml
new_names = []


def get_last_name(full_name):
    return full_name.split()[-1]


def merge_contributors(original_file, new_contributors):
    """
    Merge new contributors into the existing contributors XML file and sort alphabetically by last name.
    
    Args:
        original_file (str): Path to the existing contributors XML file.
        new_contributors (list): A list of tuples, each containing (full_name, github_username) 
                                of new contributors to be added.
    
    Side effects:
        - Modifies the original XML file in-place
    """
    with open(original_file, 'r',encoding='utf-8') as f:
        original_content = f.read()
    tree = ET.fromstring(original_content)

    for new_name, github in new_contributors:
        new_contributor = ET.Element('contributor')
        new_contributor.set('name', new_name)
        new_contributor.set('github', github)

        tree.append(new_contributor)
    
    sorted_contributors = sorted(
        tree.findall('contributor'),
        # Items which don't have a name attribute are placed at the end 
        key=lambda x: unidecode(get_last_name(x.get('name', '\x7F'))) # '\x7F' is highest ASCII value
    )

    for cont in tree.findall('contributor'):
        tree.remove(cont)

    for cont in sorted_contributors:
        tree.append(cont)

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8" ?>',
        '<!--',
        'Sage contributors',
        '',
        '+ mandatory / - optional',
        '',
        'contributor',
        ' + name = full name',
        ' - altnames = comma-separated list of alternate full names',
        ' - location = something which returns the correct location when entered in maps.google.com',
        ' - work = university, institute, ...',
        ' - description = <item>[;<item>]* ... delimiter ";" is converted into a break or list',
        ' - url = webpage, when clicking on name; no need to provide github profile URL',
        ' - pix = url to a small image (max 50x50 or something like that) .. subdirectory "./pix/people/" should store them locally',
        ' - jitter = float as string, multiplicated in jitter function, 0 to disable',
        ' - trac = trac nickname for the search (also searched for the name, but the trac name is often different!). comma-separated list of several trac account names ok. No need to provide "gh-..." names, provide a github attribute instead.',
        ' - github = github.com account name',
        ' - gitlab = gitlab.com account name',
        '',
        'Please keep the list in alphabetical order by last name!',
        '-->',
        '<contributors>'
    ]

    # Write contributors with precise formatting
    for contributor in sorted_contributors:
        contrib_line = '<contributor'
        for attr, value in contributor.attrib.items():
            contrib_line += f'\n {attr}="{html.escape(value,quote=False)}"'
        contrib_line += '/>'
        xml_lines.append(contrib_line)
    xml_lines.append('</contributors>')
    
    with open(original_file, 'w',encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))


def map_git_to_names():
    """
    Create a mapping between GitHub usernames and full names from the contributors XML file.
    
    Side effects:
        - Populates the global git_to_name dictionary with GitHub username to full name mappings
    """
    tree = ET.parse('conf/contributors.xml')
    root = tree.getroot()
    for c in root.findall('contributor'):
        name = c.get('name')
        git = c.get('github')
        if git and name:
            git_to_name[git] = unidecode(name)


def fetch_real_name(github_name):
    """
    Fetch the full name of a GitHub user via the GitHub API.
    
    Args:
        github_name (str): GitHub username to look up.
    
    Side effects:
        - Updates the global git_to_name dictionary if a full name is found
        - Adds the full name and GitHub username to the global new_names list
    """
    url = f"https://api.github.com/users/{github_name}"
    try:
        res = requests.get(url,headers=HEADERS)
        res.raise_for_status()
        user = res.json()
        if not user['name']:
            return
        name_parts = user['name'].split()
        if len(name_parts) < 2: # Full name is not available
            return
        git_to_name[github_name] = user['name']
        new_names.append((user['name'],github_name))
    except Exception as e:
        print(f"Failed to fetch real name for @{github_name} : {str(e)}")


def update_names():
    """
    Update contributor names by replacing GitHub usernames with real names 
    or formatted usernames (in the form @<github_username>).
    
    Side effects:
        - Attempts to fetch real names for contributors not already in global git_to_name
        - Modifies global all_contribs and global first_contribs to use real names or formatted usernames
        - Updates PR information in global all_info with real names or formatted usernames
    """
    global all_contribs
    global first_contribs
    for c in all_contribs:
        if c not in git_to_name:
            fetch_real_name(c)
    for tag in all_info:
        for pr in all_info[tag]:
            pr['creator'] = git_to_name.get(pr['creator'],f"@{pr['creator']}")
            pr['authors'] = [git_to_name.get(a,f"@{a}")  for a in pr['authors']]
            pr['reviewers'] = [git_to_name.get(r,f"@{r}") for r in pr['reviewers']]
    all_contribs = set([git_to_name.get(c,f"@{c}") for c in all_contribs])
    first_contribs = set([git_to_name.get(c,f"@{c}") for c in first_contribs])


def get_release_data(tag):
    """
    Fetch release data for a specific GitHub tag.
    
    Args:
        tag (str): The release tag to fetch data for.
    
    Returns:
        dict or None: Release data if found, otherwise None.
    """
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
    """
    Extract the publication date from release data.
    
    Args:
        release_data (dict): Release data from GitHub API.
    
    Returns:
        str: Formatted date of release (YYYY-MM-DD) or 'Unavailable' if no date is found.
    """
    date_time = release_data.get('published_at', '')
    if not date_time:
        return 'Unavailable'
    return date_time.split('T')[0]


def extract_pr_info(release_data):
    """
    Extract pull request information from release body text.
    
    Args:
        release_data (dict): Release data from GitHub API.
    
    Returns:
        list: A list of dictionaries, each containing PR details:
              - title: PR title
              - creator: GitHub username of PR creator
              - pr_id: Pull request Id
              - authors: List of PR authors
              - reviewers: List of PR reviewers
    """
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
    """
    Update the set of first-time contributors from release body text.
    
    Args:
        release_data (dict): Release data from GitHub API.
    
    Side effects:
        - Adds newly identified first-time contributors to the global first_contribs set
    """
    body = release_data.get('body', '')
    pattern = r"\* (@\S+) made their first contribution in"
    matches = re.findall(pattern, body)
    for match in matches:
        username = match[1::]
        first_contribs.add(username)


def get_authors(pr_id):
    """
    Retrieve the authors of commits for a specific pull request.
    
    Args:
        pr_id (str): Pull request ID.
    
    Returns:
        list: Unique GitHub usernames of PR commit authors, excluding automated bot accounts.
    
    Side effects:
        - Updates the global all_contribs set with discovered authors
    """
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
    """
    Retrieve the reviewers of a specific pull request.
    
    Args:
        pr_id (str): Pull request ID.
        authors (list): List of PR authors to exclude from reviewers.
    
    Returns:
        list: Unique GitHub usernames of PR reviewers, 
              excluding PR authors and automated bot accounts.
    
    Side effects:
        - Updates the global all_contribs set with discovered reviewers
    """
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
    """
    Custom sorting key for release tags to prioritize in order: beta, RC, and stable versions.
    
    Args:
        tag (str): Tag name to be sorted.
    """
    name = tag.lower()
    if "beta" in name:
        return (0, name)  # Beta comes first
    elif "rc" in name:
        return (1, name)  # RC comes next
    else:
        return (2, name)  # Stable versions come last


def save_to_file(filename, ver, date_of_release):
    """
    Generate and save the changelog to a text file.
    
    Args:
        filename (str): Path to the output changelog file.
        ver (str): Sage version number.
        date_of_release (str): Date of the release.
    
    Side effects:
        - Creates a changelog file with contributor and PR information
    """
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
        file.write(f"\n* We merged {pr_count} pull requests in this release.")
        sorted_tags = sorted(all_info.keys(), key=sort_tags)
        for tag in sorted_tags:
            file.write(f"\n\nMerged in sage-{tag}:\n")
            for pr in all_info[tag]:
                file.write(f"\n#{pr['pr_id']}: {', '.join(pr['authors'])}: {pr['title']}")
                if pr['reviewers']:
                    file.write(f" [Reviewed by {', '.join(pr['reviewers'])}]")

    print(f"Saved changelog to {filename}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch release data from GitHub and extract PR info")
    parser.add_argument('version', type=str, help="The release version (e.g., 10.1)")
    args = parser.parse_args()
    ver = args.version
    is_stable = re.match(r'^\d+(\.\d+){0,3}$', ver)
    if not is_stable:
        print(f"{ver} is not a stable release. terminating....")
        exit(1)

    filepath = f"src/changelogs/sage-{ver}.txt"
    if os.path.exists(filepath):
        print(f"{filepath} already exists. Exiting without making changes.")
        exit(1)

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
            if release_data:
                date_of_release = get_release_date(release_data)
            else:
                date_of_release = "N/A"
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
        exit(1)
    
    if new_names:
        merge_contributors('conf/contributors.xml',new_names)
        print("Added new contributors to conf/contributors.xml")
    else:
        print("No new contributors found.")
