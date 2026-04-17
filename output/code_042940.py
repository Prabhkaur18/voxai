class CodeCreator:
    def __init__(self, name, language):
        """
        Initialize the CodeCreator class.

        Args:
            name (str): The name of the code.
            language (str): The programming language of the code.
        """
        self.name = name
        self.language = language
        self.code = ""

    def add_line(self, line):
        """
        Add a line of code.

        Args:
            line (str): The line of code to add.
        """
        self.code += line + "\n"

    def get_code(self):
        """
        Get the generated code.

        Returns:
            str: The generated code.
        """
        return self.code


def create_code(name, language):
    """
    Create a new code.

    Args:
        name (str): The name of the code.
        language (str): The programming language of the code.

    Returns:
        CodeCreator: The CodeCreator object.
    """
    return CodeCreator(name, language)


def main():
    code_name = "example"
    language = "python"
    creator = create_code(code_name, language)

    # Add lines of code
    creator.add_line("def main():")
    creator.add_line("    print('Hello, World!')")
    creator.add_line("if __name__ == '__main__':")
    creator.add_line("    main()")

    print(creator.get_code())


if __name__ == "__main__":
    main()