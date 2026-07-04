"""Convenience entry point. The real composition root is ``studyguard.cli``.

Run ``python app.py`` or, once installed, the ``studyguard`` console script or
``python -m studyguard``.
"""
from studyguard.cli import main

if __name__ == "__main__":
    main()
