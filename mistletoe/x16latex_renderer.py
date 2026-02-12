"""
LaTeX renderer for mistletoe.
"""
import re
from pprint import pprint
import string
from itertools import chain
from urllib.parse import quote
import mistletoe.latex_token as latex_token
from mistletoe.base_renderer import BaseRenderer, URI_SAFE_CHARACTERS
from mistletoe.block_token import HtmlBlock
from mistletoe.span_token import HtmlSpan
from mistletoe.block_tokenizer import tokenize
from mistletoe.block_token import _token_types
from bs4 import BeautifulSoup

# (customizable) delimiters for inline code
verb_delimiters = string.punctuation + string.digits
for delimiter in '*':  # remove invalid delimiters
    verb_delimiters.replace(delimiter, '')
for delimiter in reversed('|!"\'=+'):  # start with most common delimiters
    verb_delimiters = delimiter + verb_delimiters.replace(delimiter, '')


class X16LaTeXRenderer(BaseRenderer):
    def __init__(self, *extras, **kwargs):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
            **kwargs: additional parameters to be passed to the ancestor's
                      constructor.
        """
        #tokens = self._tokens_from_module(latex_token)
        tokens = (HtmlBlock, HtmlSpan)
        self.packages = {}
        self.verb_delimiters = verb_delimiters
        super().__init__(*tokens, **kwargs)

    def render_strong(self, token):
        return '\\textbf{{{}}}'.format(self.render_inner(token))

    def render_emphasis(self, token):
        return '\\textit{{{}}}'.format(self.render_inner(token))

    def render_inline_code(self, token):
        content = self.render_raw_text(token.children[0], escape=False)

        # search for delimiter not present in content
        for delimiter in self.verb_delimiters:
            if delimiter not in content:
                break

        if delimiter in content:  # no delimiter found
            raise RuntimeError('Unable to find delimiter for verb macro')

        escaped = content.replace('\\', '\\textbackslash ').replace('$', '\\$').replace('#', '\\#').replace('{', '\\{').replace('}', '\\}').replace('&', '\\&').replace('_', '\\_').replace('%', '\\%').replace('^', '\\^{}')

        template = '\\texttt{{{content}}}'
        return template.format(content=escaped)

    def render_strikethrough(self, token):
        self.packages['ulem'] = ['normalem']
        return '\\sout{{{}}}'.format(self.render_inner(token))

    def render_image(self, token):
        self.packages['graphicx'] = []
        return '\n\\includegraphics{{{}}}\n'.format(token.src)

    def render_link(self, token):
        #self.packages['hyperref'] = []
        #template = '\\href{{{target}}}{{{inner}}}'
        #inner = self.render_inner(token)
        #return template.format(target=self.escape_url(token.target),
        #                       inner=inner)
        return self.render_inner(token)

    def render_auto_link(self, token):
        self.packages['hyperref'] = []
        return '\\url{{{}}}'.format(self.escape_url(token.target))

    def render_math(self, token):
        self.packages['amsmath'] = []
        self.packages['amsfonts'] = []
        self.packages['amssymb'] = []
        return token.content

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token, escape=True):
        return (token.content.replace('\\', '\\textbackslash ')
                             .replace('$', '\\$').replace('#', '\\#')
                             .replace('{', '\\{').replace('}', '\\}')
                             .replace('&', '\\&').replace('_', '\\_')
                             .replace('%', '\\%').replace('^', '\\^{}')
               ) if escape else token.content

    def render_heading(self, token):
        inner = self.render_inner(token)
        if token.level == 1:
            return ''
        elif token.level == 2:
            return '\n\\subsection*{{{}}}\n'.format(inner)
        return '\n\\subsubsection*{{{}}}\n'.format(inner)

    def render_quote(self, token):
        self.packages['csquotes'] = []
        template = '\\begin{{displayquote}}\n{inner}\\end{{displayquote}}\n'
        return template.format(inner=self.render_inner(token))

    def render_paragraph(self, token):
        return '\n{}\n'.format(self.render_inner(token))

    def render_block_code(self, token):
        self.packages['listings'] = []
        template = ('\n\\begin{{lstlisting}}\n'
                    '{}'
                    '\\end{{lstlisting}}\n')
        inner = self.render_raw_text(token.children[0], False)
        return template.format(inner)

    def render_list(self, token):
        self.packages['listings'] = []
        template = '\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n'
        tag = 'enumerate' if token.start is not None else 'itemize'
        inner = self.render_inner(token)
        return template.format(tag=tag, inner=inner)

    def render_list_item(self, token):
        inner = self.render_inner(token)
        return '\\item {}\n'.format(inner)

    def render_table(self, token):
        def render_align(column_align):
            if column_align != [None]:
                cols = ""
                index = 0
                for col in token.column_align:
                    try:
                        w = self.x16_colwidths[index]
                    except:
                        w = 1
                    index += 1
                    c = ('X[' + str(w) + ',{align}] ').format(align=get_align(col))
                    cols += c
                return cols
            else:
                return ''
        
        def render_hidden_columns():
            if self.x16_colwidths == None:
                return ""
            else:
                out = ""
                for index in range(0,len(self.x16_colwidths)):
                    if self.x16_colwidths[index] == 0:
                        out += "column{" + str(index+1) + "} = {cmd=\\discardcol,colsep=0pt},\n"
                return out

        def get_align(col):
            if col is None:
                return 'l'
            elif col == 0:
                return 'c'
            elif col == 1:
                return 'r'
            raise RuntimeError('Unrecognized align option: ' + col)

        template =  ('\\begin{{longtblr}}{{'
                     'colspec = {{{colspec}}},\n'
                     '{hidecol}'
                     'width = \\linewidth,\n'
                     'rowhead = 1,\n'
                     'rowfoot = 0}}\n'
                     '{inner}\n'
                     '\\end{{longtblr}}\n'
                    )
        
        if hasattr(token, 'header'):
            head_template = '{inner}\\hline\n'
            head_inner = self.render_table_row(token.header)
            head_rendered = head_template.format(inner=head_inner)
        else:
            head_rendered = ''
        inner = self.render_inner(token)
        colspec = render_align(token.column_align)
        return template.format(inner=head_rendered + inner, colspec=colspec, hidecol=render_hidden_columns())

    def render_table_row(self, token):
        cells = [self.render(child) for child in token.children]
        return ' & '.join(cells) + ' \\\\\n'

    def render_table_cell(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_thematic_break(token):
        return '\n\\hrulefill\n'

    @staticmethod
    def render_line_break(token):
        return '\n' if token.soft else '\\newline\n'

    def render_packages(self):
        pattern = '\\usepackage{options}{{{package}}}\n'
        return ''.join(pattern.format(options=options or '', package=package)
                         for package, options in self.packages.items())

    def render_document(self, token):
        chaptername = "?"
        itemcount = 0
        chaptercontent = "\\begin{chapteritems}\n"
        for c in token._children:
            if c.__class__.__name__ == "Heading":
                if c.level == 1:
                    chaptername = re.search(r":\s*(.*)", c._children[0].content).group(1)
                    itemcount=0
                elif c.level == 2:
                    try:
                        chaptercontent += "\\item " + c._children[0].content + "\n"
                    except:
                        pass
                    itemcount+=1
        if itemcount > 0:
            chaptercontent += "\\end{chapteritems}"
        else:
            chaptercontent = ""
        
        template = ('\\begin{{chapterpage}}{{{chapter}}}\n'
                    '{chapteritems}\n'
                    '\\end{{chapterpage}}\n'
                    '{inner}\n')
        self.footnotes.update(token.footnotes)
        return template.format(chapter=chaptername, inner=self.render_inner(token), chapteritems=chaptercontent)

    def render_inner(self, token) -> str:
        s = super().render_inner(token)
        return s

    @staticmethod
    def escape_url(raw: str) -> str:
        """
        Quote unsafe chars in urls & escape as needed for LaTeX's hyperref.

        LaTeX-escapes '%' and '#' for hyperref's \\url{} to also
        work if used within macros like \\multicolumn. if \\url{} with urls
        containing '%' or '#' is used outside of multicolumn-macros, they work
        regardless of whether these characters are escaped, and the result
        remains the same (at least for pdflatex from TeX Live 2019).
        """
        quoted_url = quote(raw, safe=URI_SAFE_CHARACTERS)
        return quoted_url.replace('%', '\\%') \
                         .replace('#', '\\#')

    x16_colwidths = None
    def render_html_span(self, token) -> str:
        content = token.content.lower()
        if re.search(r"^<mark\s*>", content):
            return "\\markbox{\\strut "
        elif re.search(r"^</mark\s*>", content):
            return "}"
        
        colwidths = re.search(r"^<span.*data-x16-colwidths=([\"'])(.+)\1", content)
        if colwidths:
            self.x16_colwidths = list(map(int, colwidths.group(2).split(",")))
            return ""
        
        return ""
    
    def render_html_block(self, token) -> str:
        response = ""

        # Render HTML <summary>
        match_summary = re.search(r"<summary[^>]*>(.*?)</summary>",token.content, re.DOTALL)
        if match_summary:
            response = "\\par " + match_summary.group(1)
        
        # Render HTML <table>
        match_table = re.search(r"<table[^>]*>.*?</table>",token.content, re.DOTALL)
        if match_table:
            table_struct = "\\hline\n"
            table_colspec = ""
            currow = 1
            curcol = 1

            table = BeautifulSoup(match_table.group(0), "html.parser")
            for row in table.find_all("tr"):
                for cell in row.find_all(re.compile("td|th")):
                    # Headers
                    if currow == 1:
                        if curcol >1:
                            table_colspec += " "
                        else:
                            table_colspec += "| "
                        table_colspec += "X[1,l] |"

                    # Cells
                    if curcol > 1:
                        table_struct += " & "
                    
                    if "colspan" in cell.attrs:
                        colspan = int(cell.attrs["colspan"])
                    else:
                        colspan = None
                    if "align" in cell.attrs:
                        align = cell.attrs["align"][0]
                        if not colspan: colspan = 1
                    else:
                        if colspan:
                            align = "l"
                        else: 
                            align = None

                    if colspan:
                        table_struct += "\\SetCell[c={cspan}]{{{halign}}} ".format(cspan=colspan, halign=align)
                    
                    table_struct += escape_string(cell.contents[0].string.strip())
                    if colspan:
                        for i in range(1,int(colspan)):
                            table_struct += " &"
                    curcol += 1
                
                table_struct += " \\\\\n\\hline\n"
                currow += 1
                curcol = 1

            template =  ('\\begin{{longtblr}}{{'
                         'colspec = {{{colspec}}},\n'
                         '{hidecol}'
                         'width = \\linewidth,\n'
                         'rowhead = 1,\n'
                         'rowfoot = 0}}\n'
                         '{inner}\n'
                         '\\end{{longtblr}}\n'
                        )
            response += "\n\n" + template.format(colspec=table_colspec, hidecol="", inner=table_struct)

        return response

def escape_string(s):
    return s.replace('\\', '\\textbackslash ').replace('$', '\\$').replace('#', '\\#').replace('{', '\\{').replace('}', '\\}').replace('&', '\\&').replace('_', '\\_').replace('%', '\\%').replace('^', '\\^')
