from setuptools import setup
setup(
    name="Test",
    packages=["Widget"],
    package_data={"Widget": ["icons/*.svg"]},
    classifiers=["Spectroscopy :: Invalid"],
    entry_points={"orange.widgets": "Test = Widget"},
)
