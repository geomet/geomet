How to Contribute
-----------------

Contributing to GeoMet is simple.

1.  Fork the repository
2.  Make changes in your fork
3.  Add yourself to CONTRIBUTORS.txt (only necessary for your first
    contribution)
4.  Submit a pull request

If the change satisfies the Hacking Guidelines (see below), it will be merged.


Hacking Guidelines
------------------

New code submissions must satisfy pyflakes and pep8 guidelines. Travis CI will
run these checks along with the test suite. (See `tox.ini` and `.travis.yml`
for details about the test procedures.) To run the tests yourself, just clone
the repository and type `tox` in a shell. You will of course need to install
`tox` using `pip` or your favorite package manager.

Each code submission should be no larger than ~500 lines of diff. If the change
is larger, it may still be accepted but please try to keep contributions as
small and concise as possible.

Each code submission should be reasonably well tested. Test coverage should be
near-perfect. It is acknowledged that perfect test coverage is not always
possible, but reasonable effort should be spent to make it so.


Reporting Bugs
--------------

Bugs should be reported using the GitHub issue tracker.
