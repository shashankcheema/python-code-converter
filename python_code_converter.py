import ast
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
from lib2to3.pgen2.parse import ParseError

class PythonCodeConverter:
    def __init__(self, code, target_version):
        self.code = '#!/usr/bin/env python\n' + ast.literal_eval(code).strip()
        self.target_version = target_version

    def convert_code(self):
        if self.target_version.startswith('3'):
            return self.convert_to_python3()
        else:
            return self.code

    def convert_to_python3(self):
        fixers = get_fixers_from_package('lib2to3.fixes')
        tool = RefactoringTool(fixers)
        try:
            tree = tool.refactor_string(self.code, "<string>")
            return str(tree)
        except ParseError:
            return "Syntax error in the input code."
