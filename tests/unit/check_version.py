import re
tags = ["1.0.0-dev", "1.0.1-dev", "1.0.10-dev", "1.0.2-dev", "1.0.3-dev", "1.0.4-dev", "1.0.5-dev", "1.0.6-dev", "1.0.7-dev", "1.0.8-dev", "1.0.9-dev"]
print(tags)
moduleRegex = re.compile(r'^([0-9]\d*\.[0-9]\d*\.[0-9]\d*)\-([a-zA-z]+)$')
# sorted_tags = sorted(tags, key=lambda x: [int(i) if i.isdigit() else i for i in x.split('.')])
sorted_tags = sorted(tags, key=lambda x: [int(num) if num.isdigit() else num for num in x.split('.')])

print(sorted_tags)
print(sorted_tags)
current_tag = sorted_tags[-1]
print("current tag is ", current_tag)
tag = moduleRegex.search(current_tag)
semver_tag = tag.group(1)
print(semver_tag)