import re
from collections import defaultdict, Counter

def parse_comments(text):
    """
    Parses Instagram-comment text where each comment looks like:

    username's profile picture
    username
      2d
    @tag1 @tag2 ...

    Returns dict: {username: set(of tagged users)}
    """

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    user_tag_map = defaultdict(set)

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect profile picture line
        if line.endswith("'s profile picture"):
            # Next line = username
            commenter = lines[i + 1].strip()

            # Skip time (i+2)
            comment_text = lines[i + 3]  # The actual comment line

            # Extract all @tags (case-insensitive), then dedupe within this comment
            tags = set(re.findall(r'@[\w\.\_]+', comment_text.lower()))

            # Add unique tags for this commenter (dedupe across all their comments)
            user_tag_map[commenter].update(tags)

            # Move pointer 4 lines forward
            i += 4
        else:
            i += 1

    return user_tag_map


def count_tags_unique(user_tag_map):
    """
    Convert user→unique tags into global tag counts.
    Each user only counts once per tag (no duplicate votes).
    """
    tag_counter = Counter()

    for user, tags in user_tag_map.items():
        for tag in tags:
            tag_counter[tag] += 1

    return tag_counter


def count_tags_with_duplicates(text):
    """
    Count every single @tag occurrence in the entire text.
    - Duplicates in the same comment are counted
    - Same user tagging the same person in multiple comments is counted every time
    """
    tags = re.findall(r'@[\w\.\_]+', text.lower())
    return Counter(tags)


if __name__ == "__main__":
    # Load your txt file
    with open("comments.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # WITHOUT duplicates (what you have now: unique voters per tag)
    user_tag_map = parse_comments(text)
    tag_counts_unique = count_tags_unique(user_tag_map)

    # WITH duplicates (raw mentions)
    tag_counts_all = count_tags_with_duplicates(text)

    print("\n=== Top 10 WITH duplicates (raw mentions, every tag occurrence) ===")
    for tag, count in tag_counts_all.most_common(10):
        print(f"{tag}: {count}")

    print("\n=== Top 10 WITHOUT duplicates (unique voters per tag) ===")
    for tag, count in tag_counts_unique.most_common(10):
        print(f"{tag}: {count}")

    # === Target artists ===
    target_artists = ["@vesummusic", "@kakashi_dubz", "@jovasdubz"]

    print("\n=== Total Tag Summary for Selected Artists ===")
    for artist in target_artists:
        total_with_dupes = tag_counts_all.get(artist, 0)
        total_unique = tag_counts_unique.get(artist, 0)
        print(f"{artist} → total tags (with duplicates): {total_with_dupes}, unique voters: {total_unique}")