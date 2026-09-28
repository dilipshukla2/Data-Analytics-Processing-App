# processor/worker_bootstrap.py
"""
Bootstrap module for spawned multiprocessing workers.
IMPORTANT: This module must NOT import Django models at module level,
because spawned children import this module BEFORE django.setup() runs.
"""

def django_setup():
    import django
    django.setup()