from pkgcheck import reporters, base

pkgcore_plugins = {
    'configurable': [
        reporters.json_reporter,
        reporters.xml_reporter,
        reporters.plain_reporter,
        reporters.fancy_reporter,
        reporters.multiplex_reporter,
        base.Whitelist,
        base.Blacklist,
        base.Suite,
        ],
    }
