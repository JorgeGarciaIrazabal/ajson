import re

as_comment_regex = re.compile("@as{[\s\S]*?}")  # type: Pattern
find_attribute_regex = re.compile("self\.\w*")  # type: Pattern