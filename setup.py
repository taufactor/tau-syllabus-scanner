import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="syllabus_scanner",
    version="1.0.0",
    author="Tau-Factor",
    author_email="factor.tau@gmail.com",
    description="Tel-Aviv University syllabus scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/taufactor/tau-syllabus-scanner',
    project_urls={
        "Bug Tracker": "https://github.com/taufactor/tau-syllabus-scanner/issues"
    },
    license="MIT",
    packages=["syllabus_scanner"],
    install_requires=(
        "BeautifulSoup4>=4.10.0",
        "types-beautifulsoup4>=4.10.0",
        "aiohttp>=3.8.0",
    ),
)
