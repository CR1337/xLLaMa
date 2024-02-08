from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from typing import List


class CodeHighlighter:

    STYLE: str = 'github-dark'
    CLICKABLE_HTML: str = (
        '><b><u><a class="{clickable_class}" {on_click_attribute}='
        '"{click_handler_name}(\'{code_snippet_id}\', \'{name}\')">{name}'
        '</a></u></b><'
    )

    @classmethod
    def highlight(
        cls,
        code: str,
        clickable_names: List[str],
        clickable_class: str,
        on_click_attribute: str,
        click_handler_name: str,
        code_snippet_id: str
    ) -> str:
        formatter = HtmlFormatter(style=cls.STYLE)
        html = highlight(code, PythonLexer(), formatter)
        for name in clickable_names:
            print(name, flush=True)
            html = html.replace(
                f">{name}<",
                cls.CLICKABLE_HTML.format(
                    clickable_class=clickable_class,
                    on_click_attribute=on_click_attribute,
                    click_handler_name=click_handler_name,
                    code_snippet_id=code_snippet_id,
                    name=name
                )
            )
        return html
