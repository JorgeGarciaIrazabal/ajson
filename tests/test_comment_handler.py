import inspect
import unittest

from _comment_handler import CommentHandler


class TestCommentHandler(unittest.TestCase):
    def test_clears_single_comments(self):
        class B:
            def __init__(self):
                self.a = 2
                '''
                    this is a test
                '''
                self.b = 2
                '''
                    another test
                '''

        cleared_class = CommentHandler().format_class_source(inspect.getsource(B))

        self.assertEqual(cleared_class, """        class B:
            def __init__(self):
                self.a = 2
                
                self.b = 2
                \n""")

    def test_clears_double_comments(self):
        class C:
            def __init__(self):
                self.a = 3
                """
                    this is a test
                """
                self.b = 3
                """
                    another test
                """

        cleared_class = CommentHandler().format_class_source(inspect.getsource(C))

        self.assertEqual(cleared_class, """        class C:
            def __init__(self):
                self.a = 3
                
                self.b = 3
                \n""")

    def test_move_as_comment_to_inline_in_single(self):
        class D:
            def __init__(self):
                self.a = 4
                '''
                    @as{"group": 2}
                '''

        cleared_class = CommentHandler().format_class_source(inspect.getsource(D))

        self.assertEqual(cleared_class, """        class D:
            def __init__(self):
                self.a = 4  # @as{"group": 2}
                
""")

    def test_complex_case(self):
        class E:
            def __init__(self):
                self.a = 4
                '''
                    @as{"group": 0}
                '''
                self.b = 8  # type: List[int] @as{"group": 1}
                self.c = self.b
                """
                    this is a comment and then we have the as_comment 
                    __example__ @as{"group": 2}
                """

        cleared_class = CommentHandler().format_class_source(inspect.getsource(E))
        print(cleared_class)

        self.assertEqual(cleared_class, """        class E:
            def __init__(self):
                self.a = 4  # @as{"group": 0}
                
                self.b = 8  # type: List[int] @as{"group": 1}
                self.c = self.b  # @as{"group": 2}
                
""")
