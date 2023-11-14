def run():
    import os

    from chainlit.cli import run_chainlit

    dirname = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(dirname, "main2.py")
    run_chainlit(target)


if __name__ == "__main__":
    run()
