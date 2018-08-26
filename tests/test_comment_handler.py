import inspect
import unittest

from ajson.comment_handler import CommentHandler


class TestCommentHandler(unittest.TestCase):
    def test_clears_single_comments(self):
        class CHB:
            def __init__(self):
                self.a = 2
                '''
                    this is a test
                '''
                self.b = 2
                '''
                    another test
                '''

        cleared_class = CommentHandler().format_class_source(inspect.getsource(CHB))

        self.assertEqual(cleared_class, """        class CHB:
            def __init__(self):
                self.a = 2
                
                self.b = 2
                \n""")

    def test_clears_double_comments(self):
        class CHC:
            def __init__(self):
                self.a = 3
                """
                    this is a test
                """
                self.b = 3
                """
                    another test
                """

        cleared_class = CommentHandler().format_class_source(inspect.getsource(CHC))

        self.assertEqual(cleared_class, """        class CHC:
            def __init__(self):
                self.a = 3
                
                self.b = 3
                \n""")

    def test_move_as_comment_to_inline_in_single(self):
        class CHD:
            def __init__(self):
                self.a = 4
                '''
                    @aj(group=2)
                '''

        cleared_class = CommentHandler().format_class_source(inspect.getsource(CHD))

        self.assertEqual(cleared_class, """        class CHD:
            def __init__(self):
                self.a = 4  # @aj(group=2)
                
""")

    def test_complex_case(self):
        class CHE:
            def __init__(self):
                self.a = 4
                '''
                    @aj(group=0)
                '''
                self.b = 8  # ANOTHER TEST @aj(group=1)
                self.c = self.b
                """
                    this is a comment and then we have the as_comment 
                    __example__ @aj(group=2)
                """

        cleared_class = CommentHandler().format_class_source(inspect.getsource(CHE))

        self.assertEqual(cleared_class, """        class CHE:
            def __init__(self):
                self.a = 4  # @aj(group=0)
                
                self.b = 8  # ANOTHER TEST @aj(group=1)
                self.c = self.b  # @aj(group=2)
                
""")
