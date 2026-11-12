"""Motifs de chemins : `*` reste dans un dossier, `**` traverse les dossiers, un `/` final désigne tout un dossier."""
import re
from functools import lru_cache


@lru_cache(maxsize=None)
def compile_pattern(pattern: str) -> 're.Pattern[str]':
    if pattern.endswith('/'):
        pattern += '**'
    regex = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if pattern.startswith('**/', index):
            regex.append('(?:.*/)?')
            index += 3
        elif pattern.startswith('**', index):
            regex.append('.*')
            index += 2
        elif char == '*':
            regex.append('[^/]*')
            index += 1
        elif char == '?':
            regex.append('[^/]')
            index += 1
        else:
            regex.append(re.escape(char))
            index += 1
    return re.compile('^' + ''.join(regex) + '$')


def matches(pattern: str, path: str) -> bool:
    return compile_pattern(pattern).match(path) is not None


def matches_any(patterns, path: str) -> bool:
    return any(matches(pattern, path) for pattern in patterns)
