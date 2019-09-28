"""Custom feed functionality used by checks."""

from . import base


class QueryCache(base.Feed):

    @staticmethod
    def mangle_argparser(parser):
        group = parser.add_argument_group('query caching')
        group.add_argument(
            '--reset-caching-per', dest='query_caching_freq',
            choices=('version', 'package', 'category'), default='package',
            help='control how often the cache is cleared '
                 '(version, package or category)')

    @staticmethod
    def _version(item):
        return item

    @staticmethod
    def _package(item):
        return item.key

    @staticmethod
    def _category(item):
        return item.category

    def __init__(self, options):
        super().__init__(options)
        self.query_cache = {}
        self._keyfunc = getattr(self, f'_{options.query_caching_freq}')
        self._key = None

    def feed(self, item):
        key = self._keyfunc(item)
        # TODO: this should be logging debug info
        if key != self._key:
            self.query_cache.clear()
            self._key = key
        super().feed(item)


class EvaluateDepSet(base.Feed):

    def __init__(self, options, profiles):
        super().__init__(options)
        self.pkg_evaluate_depsets_cache = {}
        self.pkg_profiles_cache = {}
        self.profiles = profiles

    def feed(self, item):
        super().feed(item)
        self.pkg_evaluate_depsets_cache.clear()
        self.pkg_profiles_cache.clear()

    def _identify_common_depsets(self, pkg, depset):
        profile_grps = self.pkg_profiles_cache.get(pkg, None)
        if profile_grps is None:
            profile_grps = self.profiles.identify_profiles(pkg)
            self.pkg_profiles_cache[pkg] = profile_grps

        # strip use dep defaults so known flags get identified correctly
        diuse = frozenset(
            x[:-3] if x[-1] == ')' else x for x in depset.known_conditionals)
        collapsed = {}
        for profiles in profile_grps:
            immutable, enabled = profiles[0].identify_use(pkg, diuse)
            collapsed.setdefault((immutable, enabled), []).extend(profiles)

        return [(depset.evaluate_depset(k[1], tristate_filter=k[0]), v)
                for k, v in collapsed.items()]

    def collapse_evaluate_depset(self, pkg, attr, depset):
        depset_profiles = self.pkg_evaluate_depsets_cache.get((pkg, attr))
        if depset_profiles is None:
            depset_profiles = self._identify_common_depsets(pkg, depset)
            self.pkg_evaluate_depsets_cache[(pkg, attr)] = depset_profiles
        return depset_profiles
