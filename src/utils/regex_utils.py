import re


def group_and_split(text, group_re, split_re):
    groups = re.findall(group_re, text, re.MULTILINE)
    splits = [(split.strip(), group) for group, split in zip(groups, re.split(split_re, text)) if split.strip()]
    return groups, splits
