import re

as_comment_regex = re.compile("@aj\([\s\S]*?\)")  # type: Pattern
find_attribute_regex = re.compile("(self\.\w*)|(^(?!(def ))\w+)")  # type: Pattern