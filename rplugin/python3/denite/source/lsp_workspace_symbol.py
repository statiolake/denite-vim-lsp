import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.resolve()))

from denite_lsp_symbol.symbol_base import SymbolBase


class Source(SymbolBase):
    def __init__(self, vim):
        super().__init__(vim, 'lsp_workspace_symbol')

    def start_lookup(self, query):
        self.vim.call('denite_vim_lsp#workspace_symbol', query)
