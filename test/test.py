def test_running():
    import subprocess as sp
    test_files={"./test/test_source/hello world.nyan": "Hello, World!"}
    for i in test_files:
        response=sp.check_output(["python","interpreter.py",i]).decode()
        assert response==test_files[i]

test_running()
