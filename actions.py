def create_file(filename):
    try:
        with open(filename, "w") as f:
            f.write("File created successfully!")
        return f"{filename} created successfully."
    except Exception as e:
        return str(e)


def write_code(filename, code):
    try:
        with open(filename, "w") as f:
            f.write(code)
        return f"{filename} written successfully."
    except Exception as e:
        return str(e)