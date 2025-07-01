import re
tags = ["1.0.0-dev", "1.0.1-dev", "1.0.10-dev", "1.0.2-dev", "1.0.3-dev", "1.0.4-dev", "1.0.5-dev", "1.0.6-dev", "1.0.7-dev", "1.0.8-dev", "1.0.9-dev"]
suffix = "dev"

# print(hyphenatedSuffix)
tags_without_suffix = [tag.replace("-dev", "") for tag in tags]

print(tags_without_suffix)
sorted_tags = sorted(tags_without_suffix, key=lambda x: [int(num) if num.isdigit() else num for num in x.split('.')])
print(sorted_tags)

tags_with_suffix = [tag + "-dev" for tag in sorted_tags]

print(tags_with_suffix)
suffixRegexHyphen = re.compile(r'^([0-9]\d*\.[0-9]\d*\.[0-9]\d*)\-([a-zA-z]+)$') #1.2.3-snapshot
suffixRegexHyphenMajorMinor = re.compile(r'^([0-9]\d*\.[0-9]\d*)\-([a-zA-z]+)$') #1.2-snapshot
suffixRegexDot = re.compile(r'^([0-9]\d*\.[0-9]\d*\.[0-9]\d*)\.([a-zA-z]+)$') #11.23.0.alpha
current_tag = "1.0-dev"
latest_tag = current_tag.split("-")[0]
print(latest_tag)
if re.match(suffixRegexHyphenMajorMinor, current_tag):
    tagGroup = suffixRegexHyphenMajorMinor.search(current_tag)
    tag = tagGroup.group(1)
    print(tag)
else:
    print("none")    