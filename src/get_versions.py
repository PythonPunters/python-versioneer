import os, sys # --STRIP DURING BUILD
def get_config(): pass # --STRIP DURING BUILD
def versions_from_file(): pass # --STRIP DURING BUILD
def versions_from_parentdir(): pass # --STRIP DURING BUILD
def render(): pass # --STRIP DURING BUILD
class NotThisMethod(Exception): pass  # --STRIP DURING BUILD

class VersioneerBadRootError(Exception):
    pass

def get_root():
    # we require that all commands are run from the project root, i.e. the
    # directory that contains setup.py, setup.cfg, and versioneer.py .
    root = os.path.realpath(os.path.abspath(os.getcwd()))
    setup_py = os.path.join(root, "setup.py")
    versioneer_py = os.path.join(root, "versioneer.py")
    if not (os.path.exists(setup_py) or os.path.exists(versioneer_py)):
        # allow 'python path/to/setup.py COMMAND'
        root = os.path.dirname(os.path.realpath(os.path.abspath(sys.argv[0])))
        setup_py = os.path.join(root, "setup.py")
        versioneer_py = os.path.join(root, "versioneer.py")
    if not (os.path.exists(setup_py) or os.path.exists(versioneer_py)):
        err = ("Versioneer was unable to run the project root directory. "
               "Versioneer requires setup.py to be executed from "
               "its immediate directory (like 'python setup.py COMMAND'), "
               "or in a way that lets it use sys.argv[0] to find the root "
               "(like 'python path/to/setup.py COMMAND').")
        raise VersioneerBadRootError(err)
    try:
        # Certain runtime workflows (setup.py install/develop in a setuptools
        # tree) execute all dependencies in a single python process, so
        # "versioneer" may be imported multiple times, and python's shared
        # module-import table will cache the first one. So we can't use
        # os.path.dirname(__file__), as that will find whichever
        # versioneer.py was first imported, even in later projects.
        me = os.path.realpath(os.path.abspath(__file__))
        if os.path.splitext(me)[0] != os.path.splitext(versioneer_py)[0]:
            print("Warning: build in %s is using versioneer.py from %s"
                  % (os.path.dirname(me), versioneer_py))
            #print("\n", file=sys.stderr)
            #print("me:", me, file=sys.stderr)
            #print("vp:", versioneer_py, file=sys.stderr)
            #print("os.getcwd():", os.getcwd(), file=sys.stderr)
            #print("sys.argv[0]:", sys.argv[0], file=sys.stderr)
            #print("__file__:", __file__, file=sys.stderr)
    except NameError:
        pass
    return root

def vcs_function(vcs, suffix):
    return getattr(sys.modules[__name__], '%s_%s' % (vcs, suffix), None)


def get_versions():
    # returns dict with two keys: 'version' and 'full'
    cfg = get_config()
    assert cfg.VCS is not None, "please set versioneer.VCS"
    verbose = cfg.verbose
    assert cfg.versionfile_source is not None, \
        "please set versioneer.versionfile_source"
    assert cfg.tag_prefix is not None, "please set versioneer.tag_prefix"

    # I am in versioneer.py, which must live at the top of the source tree,
    # which we use to compute the root directory. py2exe/bbfreeze/non-CPython
    # don't have __file__, in which case we fall back to sys.argv[0] (which
    # ought to be the setup.py script). We prefer __file__ since that's more
    # robust in cases where setup.py was invoked in some weird way (e.g. pip)
    root = get_root()
    versionfile_abs = os.path.join(root, cfg.versionfile_source)

    get_keywords_f = vcs_function(cfg.VCS, "get_keywords")
    versions_from_keywords_f = vcs_function(cfg.VCS, "versions_from_keywords")
    pieces_from_vcs_f = vcs_function(cfg.VCS, "pieces_from_vcs")

    # extract version from first of: _version.py, VCS command (e.g. 'git
    # describe'), parentdir. This is meant to work for developers using a
    # source checkout, for users of a tarball created by 'setup.py sdist',
    # and for users of a tarball/zipball created by 'git archive' or github's
    # download-from-tag feature or the equivalent in other VCSes.

    if get_keywords_f and versions_from_keywords_f:
        try:
            vcs_keywords = get_keywords_f(versionfile_abs)
            ver = versions_from_keywords_f(vcs_keywords, cfg.tag_prefix,
                                           verbose)
            if verbose:
                print("got version from expanded keyword %s" % ver)
            return ver
        except NotThisMethod:
            pass

    try:
        ver = versions_from_file(versionfile_abs)
        if verbose:
            print("got version from file %s %s" % (versionfile_abs, ver))
        return ver
    except NotThisMethod:
        pass

    if pieces_from_vcs_f:
        try:
            pieces = pieces_from_vcs_f(cfg.tag_prefix, root, verbose)
            ver = render(pieces, cfg.style)
            if verbose:
                print("got version from VCS %s" % ver)
            return ver
        except NotThisMethod:
            pass

    try:
        if cfg.parentdir_prefix:
            ver = versions_from_parentdir(cfg.parentdir_prefix, root, verbose)
            if verbose:
                print("got version from parentdir %s" % ver)
            return ver
    except NotThisMethod:
        pass

    if verbose:
        print("unable to compute version")

    return {"version": "0+unknown", "full-revisionid": None,
            "dirty": None, "error": "unable to compute version"}


def get_version():
    return get_versions()["version"]
