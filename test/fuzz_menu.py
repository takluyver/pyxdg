import os
import sys
import atheris

with atheris.instrument_imports(enable_loader_override=False):
    import xdg.Menu
    from xdg.Exceptions import ParsingError

@atheris.instrument_func
def TestOneInput(input_bytes):
    # We need to make the file an absolute path
    testfile_path = os.path.join(os.getcwd(), "test.menu")
    with open(testfile_path, "wb") as f:
	f.write(input_bytes)
    try:
	xdg.Menu.parse(filename = testfile_path)
    except ParsingError:
	None
    os.remove(testfile_path)

def main():
    atheris.instrument_all()
    atheris.Setup(sys.argv, TestOneInput, enable_python_coverage=True)
    atheris.Fuzz()


if __name__ == "__main__":
    main()

