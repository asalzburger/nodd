"""Allowlist user-visible items from an explicitly selected Codex app turn.

This module does not read client stores or grant access to other conversations.
Call curate_turn with read_thread data in memory, then review before committing.
"""

import re

PUBLIC_HOSTS = {'github.com', 'raw.githubusercontent.com',
                'user-images.githubusercontent.com', 'openai.com',
                'platform.openai.com', 'developers.openai.com', 'arxiv.org',
                'cds.cern.ch', 'root.cern', 'geant4.web.cern.ch', 'pdg.lbl.gov'}


def redact(text):
    for pattern in (r'/Users/[^\s`\"\'<>]+',
                    r'\b(?:sk-[A-Za-z0-9_-]{15,}|gh[pousr]_[A-Za-z0-9_]{20,})\b',
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'):
        text = re.sub(pattern, '[redacted]', text)
    text = re.sub(r'<in-app-browser-context\b[\s\S]*?</in-app-browser-context>', '', text)

    def public(match):
        url = match.group()
        return url if url.split('/')[2].lower() in PUBLIC_HOSTS else '[external URL redacted; see source journal]'

    return re.sub(r'https?://[^\s<>)\"\'`]+', public, text).strip()


def curate_turn(thread_id, turn, accounts):
    """Never serialize reasoning, outputs, arbitrary tool arguments or images."""
    messages, operations, children = [], {}, []
    for item in turn.get('items', []):
        kind = item.get('type')
        if kind in ('userMessage', 'agentMessage'):
            user = kind == 'userMessage'
            text = ('\n'.join(c['text'] for c in item.get('content', []) if c['type'] == 'text')
                    if user else item.get('text', ''))
            if user and text.strip().startswith('<environment_context>'):
                continue
            cleaned = redact(text)
            if cleaned:
                messages.append({'id': item['id'], 'role': 'user' if user else 'assistant',
                                 'phase': item.get('phase'), 'text': cleaned,
                                 'redacted': 'yes' if cleaned != text else 'no'})
            if user:
                for index, part in enumerate(item.get('content', [])):
                    if part['type'] != 'text':
                        messages.append({'id': item['id'] + f':upload:{index}', 'role': 'user',
                                         'phase': 'upload', 'text': 'User upload (' + part['type']
                                         + '); binary and private URL omitted.', 'redacted': 'yes'})
        elif kind in ('commandExecution', 'mcpToolCall', 'subAgentActivity',
                      'fileChange', 'imageView', 'webSearch', 'collabAgentToolCall', 'sleep'):
            name = item['server'] + '.' + item['tool'] if kind == 'mcpToolCall' else kind
            op = operations.setdefault(name, {'name': name, 'calls': 0, 'failures': 0})
            op['calls'] += 1
            if item.get('status') == 'failed' or item.get('exitCode', 0):
                op['failures'] += 1
            if kind == 'subAgentActivity':
                children.append({'thread_id': item.get('agentThreadId'),
                                 'name': item.get('agentPath'), 'activity': item.get('kind')})
    return {'schema_version': 1, 'thread_id': thread_id, 'turn_id': turn['id'],
            'status': turn['status'], 'started_at': turn.get('startedAt'),
            'completed_at': turn.get('completedAt'), 'token_accounts': accounts,
            'source': 'Codex app read_thread; exact recorded thread/turn match',
            'messages': messages, 'native_tools': list(operations.values()),
            'subagents': children, 'limitations': [
                'Only userMessage and agentMessage text retained; reasoning, tool arguments/results and private state excluded.',
                'Conservative path, credential, email and URL redaction is not a privacy guarantee; review retained text.',
                'Exposed operation counts are per retained turn; journal counts can describe the same invocations and must not be added.']}
