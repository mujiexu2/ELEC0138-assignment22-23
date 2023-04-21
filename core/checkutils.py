import re

def checkString(content):
    if re.search(r'[<>"\'%;()&+]', content):
        return False

    nums = re.findall(r'\d+', content)
    for i  in nums:
        if 0>int(i) or int(i)>10:
            return False

        # Check if there are links
    if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content):
        return False
    return True