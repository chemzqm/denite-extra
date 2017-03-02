# ============================================================================
# FILE: history.py
# AUTHOR: Qiming Zhao <chemzqm@gmail.com>
# License: MIT license
# ============================================================================
# pylint: disable=E0401,C0411
import os
import re
from .base import Base
from denite import util
from ..kind.base import Base as BaseKind
from operator import itemgetter

class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'history'
        self.kind = Kind(vim)


    def gather_candidates(self, context):
        args = dict(enumerate(context['args']))
        t = args.get(0, 'all')
        pattern = re.compile(r'\s*(\d+)\s+(.+)')
        type_pattern = re.compile(r'\s*#\s+(.+)\shistory')

        res = self.vim.call('execute', 'history %s' % t)
        htype = ''

        candidates = []
        for line in res.split("\n"):
            if not line:
                continue
            ms = type_pattern.match(line)
            if ms:
                htype = ms.group(1)
                continue
            else:
                m = pattern.match(line)
                if not m:
                    continue
            candidates.append({
                'word': '%s' % m.group(2),
                'source__nr': int(m.group(1)),
                'source__type': htype,
                'source__word': m.group(2),
                })

        candidates = sorted(candidates, key=itemgetter('source__nr'), reverse=True)
        return candidates

class Kind(BaseKind):
    def __init__(self, vim):
        super().__init__(vim)
        self.default_action = 'auto'
        self.name = 'history'
        self.persist_actions = ['delete']
        self.redraw_actions = ['delete']

    def action_auto(self, context):
        target = context['targets'][0]
        if target['source__type'] == 'search':
            self.action_search(context)
        else:
            self.action_feedkeys(context)

    def action_feedkeys(self, context):
        target = context['targets'][0]
        command = target['source__word']
        util.clear_cmdline(self.vim)
        self.vim.call('denite#extra#feedkeys', command)

    def action_search(self, context):
        target = context['targets'][0]
        util.clear_cmdline(self.vim)
        command = target['source__word']
        self.vim.call('denite#extra#feedkeys', command, '/')

    def action_delete(self, context):
        for target in context['targets']:
            nr = int(target['source__nr'])
            self.vim.call('histdel', target['source__type'], nr)
