from setuptools import setup

setup(
    name="Wriggler",
    version="1.0.0a1",

    packages=["wriggler", "test_wriggler"],
    scripts=["scripts/fetch_tweet.py", "scripts/fetch_user.py"],

    install_requires=[
        'logbook',
        'python-dateutil',
        'requests',
        'requests-oauthlib'
    ],

    author="Parantapa Bhattacharya",
    author_email="pb [at] parantapa [dot] net",

    description="Data crawler libraries for different APIs",

    license="MIT",
)
