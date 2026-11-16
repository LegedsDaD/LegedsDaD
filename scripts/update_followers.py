
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
    """Fetch all GitHub followers using API pagination."""

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
    """Generate an aligned HTML followers gallery."""

    if not followers:
        return "<p>No followers yet!</p>"

    # Sort followers alphabetically.
    # Avatar and username always come from the same object.
    followers = sorted(
        followers,
        key=lambda follower: follower["login"].lower()
    )

    columns = 6
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
<td align="center" valign="top" width="16.66%">
    <a href="{profile_url}">
        <img
            src="{avatar_url}"
            width="80"
            height="80"
            alt="@{username}"
            style="border-radius:50%;"
        />
        <br />
        <sub><b>@{username}</b></sub>
    </a>
</td>
"""

            cells.append(cell)

        # Fill empty cells to maintain six-column alignment.
        while len(cells) < columns:
            cells.append(
                '<td width="16.66%"></td>'
            )

        rows.append(
            "<tr>\n"
            + "\n".join(cells)
            + "\n</tr>"
        )

    gallery = f"""
<div align="center">

<p>
    <b>🌟 {len(followers)} amazing people are following me!</b>
</p>

<table>
{''.join(rows)}
</table>

</div>
"""

    # Remove unwanted indentation.
    return textwrap.dedent(gallery).strip()


def update_readme(gallery):
    """Replace only the followers section in README.md."""

    with open(
        README_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        readme = file.read()

    if START_MARKER not in readme:
        raise ValueError(
            "FOLLOWERS:START marker not found in README.md"
        )

    if END_MARKER not in readme:
        raise ValueError(
            "FOLLOWERS:END marker not found in README.md"
        )

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)

    if start > end:
        raise ValueError(
            "Invalid followers marker order!"
        )

    # Ensure HTML does not become a Markdown code block.
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
