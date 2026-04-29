from configparser import ConfigParser


def load_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        return {key: value for key, value in parser.items(section)}

    raise Exception(f"Section {section} not found in {filename}")
