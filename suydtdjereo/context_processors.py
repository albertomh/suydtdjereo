from suydtdjereo import __version__


def metadata(request):
    return {"suydtdjereo": {"meta": {"version": __version__}}}
