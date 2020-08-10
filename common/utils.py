def get_current_fullpath(filename):
    import os
    res = os.path.join(os.path.dirname(__file__), filename)
    return res