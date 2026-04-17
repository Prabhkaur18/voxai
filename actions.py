import os

OUTPUT_FOLDER = "output"

def create_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)

    with open(path, "w") as f:
        pass

    return f"File '{filename}' created successfully."


def write_code(filename, code):
    path = os.path.join(OUTPUT_FOLDER, filename)

    with open(path, "w") as f:
        f.write(code)

    return f"Code written to '{filename}' successfully."