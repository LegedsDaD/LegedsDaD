
import os
import requests
import html
import textwrap

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

README_FILE = "README.md"

START_MARKER = "<!-- FOLLOWERS:START -->"
END_MARKER = "<!-- FOLLOWERS:END -->"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


def fetch_followers():
    """Fetch all GitHub followers."""

    followers = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/"
            f"{USERNAME}/followers"
            f"?per_page=100&page={page}"
        )

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        batch = response.json()

        if not batch:
            break

        followers.extend(batch)

        if len(batch) < 100:
            break

        page += 1

    return followers


def generate_gallery(followers):
    """Generate a professional five-column followers gallery."""

    if not followers:
        return "<p align='center'>No followers yet!</p>"

    # Alphabetical sorting
    followers = sorted(
        followers,
        key=lambda follower: follower["login"].lower()
    )

    columns = 5
    rows = []

    for i in range(0, len(followers), columns):

        cells = []

        for follower in followers[i:i + columns]:

            username = html.escape(
                follower["login"],
                quote=True
            )

            profile_url = html.escape(
                follower["html_url"],
                quote=True
            )

            avatar_url = html.escape(
                follower["avatar_url"],
                quote=True
            )

            cell = f"""
<td align="center" valign="middle" width="20%"
    style="padding:22px 8px; border:1px solid #30363d;">

    <a href="{profile_url}" style="text-decoration:none;">

        <img
            src="{avatar_url}"
            width="88"
            height="88"
            alt="@{username}"
            style="
                width:88px;
                height:88px;
                border-radius:50%;
                object-fit:cover;
                border:3px solid #58a6ff;
            "
        />

        <br /><br />

        <strong>@{username}</strong>

    </a>

</td>
"""

            cells.append(cell)

        # Keep every row exactly five columns.
        while len(cells) < columns:
            cells.append(
                '<td width="20%" style="padding:22px 8px; border:1px solid #30363d;"></td>'
            )

        rows.append(
            "<tr>\n"
            + "\n".join(cells)
            + "\n</tr>"
        )

    gallery = f"""
<div align="center">

<h3>✦ THE PEOPLE BEHIND THE SUPPORT ✦</h3>

<p>
    <strong>{len(followers)} FOLLOWERS</strong>
    &nbsp; • &nbsp;
    <sub>THANK YOU FOR BEING HERE</sub>
</p>

<table width="100%" align="center">
<tbody>
{''.join(rows)}
</tbody>
</table>

<p>
    <sub>BUILT WITH ♥ AND THE GITHUB API</sub>
</p>

</div>
"""

    return textwrap.dedent(gallery).strip()


def update_readme(gallery):
    """Update only the followers section in README."""

    with open(
        README_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        readme = file.read()

    if START_MARKER not in readme:
        raise ValueError("FOLLOWERS:START marker not found!")

    if END_MARKER not in readme:
        raise ValueError("FOLLOWERS:END marker not found!")

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)

    if start > end:
        raise ValueError("Invalid followers marker order!")

    gallery = textwrap.dedent(gallery).strip()

    updated_readme = (
        readme[:start]
        + "\n\n"
        + gallery
        + "\n\n"
        + readme[end:]
    )

    with open(
        README_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(updated_readme)


if __name__ == "__main__":

    print(f"Fetching followers for {USERNAME}...")

    followers = fetch_followers()

    print(f"Found {len(followers)} followers.")

    gallery = generate_gallery(followers)

    update_readme(gallery)

    print("Followers gallery updated successfully!")
