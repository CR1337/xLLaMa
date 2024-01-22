from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from typing import List


class CodeHighlighter:

    STYLE: str = 'github-dark'
    CLICKABLE_HTML: str = (
        '<b><u><a class="{clickable_class}" {on_click_attribute}='
        '"{click_handler_name}(\'{code_snippet_id}\', \'{name}\')">{name}'
        '</a></u></b>'
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


if __name__ == "__main__":
    code = """
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from typing import List


class CodeHighlighter:

    STYLE: str = 'github-dark'

    @classmethod
    def highlight(
        cls,
        code: str,
        clickable_names: List[str],
        click_handler_name: str
    ) -> str:
        formatter = HtmlFormatter(style=cls.STYLE)
        html = highlight(code, PythonLexer(), formatter)
        for name in clickable_names:
            html = html.replace(
                f">{name}<",
                '><u><a class="clickable" onClick="'
                f'{click_handler_name}(\'{name}\')">{name}</a></u><'
            )
        return html
"""
    clickable_class = 'clickable'
    click_handler_name = 'clickHandler'
    highlighted_code = CodeHighlighter.highlight(
        code,
        ['highlight', 'HtmlFormatter', 'replace', 'PythonLexer'],
        clickable_class,
        'onClick',
        click_handler_name
    )
    form = HtmlFormatter(style='github-dark')
    css = form.get_style_defs('.highlight')

    content = f"""
<html>
<head>
<style>
{css}
.{clickable_class} {{
    cursor: pointer;
}}
</style>
<script>
function {click_handler_name}(name) {{
    alert('You clicked ' + name);
}}
</script>
</head>
<body>
{highlighted_code}
</body>
</html>
"""

    with open('test.html', 'w') as f:
        f.write(content)
