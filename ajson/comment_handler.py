from ajson.regex import as_comment_regex
from ajson.singleton import Singleton


class CommentHandler(object, metaclass=Singleton):
    def format_class_source(self, source: str) -> str:
        single = source.find("'''")
        double = source.find('"""')

        single = single if single != -1 else len(source) + 1
        double = double if double != -1 else len(source) + 1

        first_pos = min(single, double)
        if first_pos == len(source) + 1:
            return source

        if single == first_pos:
            end_of_comment = source.find("'''", first_pos + 3) + 3
            source = self._add_as_comment_as_inline(source, first_pos, end_of_comment)

        if double == first_pos:
            end_of_comment = source.find('"""', first_pos + 3) + 3
            source = self._add_as_comment_as_inline(source, first_pos, end_of_comment)

        return self.format_class_source(source)

    def _add_as_comment_as_inline(self, source: str, first_pos: int, end_of_comment: int):
        comment = source[first_pos: end_of_comment]
        as_comments = as_comment_regex.findall(comment)
        if len(as_comments) >= 1:
            source = source[:first_pos] + source[end_of_comment:]
            previous_line_pos = source[:first_pos].rfind("\n")
            source = source[:previous_line_pos] + "  # " + as_comments[0] + source[previous_line_pos:]
        else:
            source = source[:first_pos] + source[end_of_comment:]
        return source


