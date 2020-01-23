from urllib.parse import urlparse
from collections.abc import Iterable
import logging
import os
from denite.source.base import Base

LOGGING_ENABLED = False

LSP_SYMBOL_KINDS = [
    'File',
    'Module',
    'Namespace',
    'Package',
    'Class',
    'Method',
    'Property',
    'Field',
    'Constructor',
    'Enum',
    'Interface',
    'Function',
    'Variable',
    'Constant',
    'String',
    'Number',
    'Boolean',
    'Array',
    'Object',
    'Key',
    'Null',
    'EnumMember',
    'Struct',
    'Event',
    'Operator',
    'TypeParameter',
]

if LOGGING_ENABLED:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler('denitevimlsp.log')
    fmt = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    handler.setFormatter(fmt)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)


def info(s):
    if LOGGING_ENABLED:
        logger.info(s)


class SymbolBase(Base):
    def __init__(self, vim, name):
        super().__init__(vim)
        self.name = name
        self.kind = 'file'
        self.reinit()

    def gather_candidates(self, context):
        if context['event'] == 'gather':
            self.reinit()
            context['is_async'] = True

        query = context['input']

        if query != self.prev_query:
            # Search for new query
            self.vim.call('denite_vim_lsp#prepare_for_next_query')
            self.start_lookup(query)
            self.prev_query = query
            return []

        results = self.vim.call('denite_vim_lsp#try_get_results')
        if results is None:
            return []

        return self.get_newly_added(results)

    def reinit(self):
        self.prev_query = None
        self.result = set()
        self.vim.call('denite_vim_lsp#set_current_server')

    def get_newly_added(self, results):
        results = make_candidates(results)
        newly_added = []
        for cand in results:
            cand_str = candidate_to_str(cand)
            if cand_str not in self.result:
                newly_added.append(cand)
                self.result.add(cand_str)
        info(newly_added)
        return newly_added

    def start_lookup(self, query):
        # self.vim.call('denite_vim_lsp#workspace_symbol', query)
        raise NotImplementedError()


def candidate_to_str(cand):
    return '{}: {}@L{}C{}'.format(cand['word'], cand['action__path'],
                                  cand['action__line'], cand['action__col'])


def make_candidates(symbols):
    if not symbols:
        return []
    if not isinstance(symbols, Iterable):
        return []
    return [_parse_candidate(symbol) for symbol in symbols]


def _parse_candidate(symbol):
    candidate = {}
    loc = symbol['location']
    fp = _uri_to_path(urlparse(loc['uri']))

    candidate['word'] = symbol['name']
    candidate['abbr'] = '{} [{}] {}'.format(
        symbol['name'],
        LSP_SYMBOL_KINDS[symbol['kind'] - 1],
        fp,
    )

    candidate['action__path'] = fp
    candidate['action__line'] = loc['range']['start']['line'] + 1
    candidate['action__col'] = loc['range']['start']['character'] + 1
    return candidate


def _uri_to_path(uri):
    if os.name == 'nt' and uri.path.startswith('/') and uri.path[2] == ':':
        abspath = uri.path[1:]
    else:
        abspath = os.path.abspath(uri.path)

    if uri.netloc != '':
        return os.path.join(uri.netloc, abspath)
    else:
        return abspath
