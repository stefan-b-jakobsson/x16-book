NOTES

XeLaTeX is used to build the x16book.tex document that includes
the chapters.

The following three manual fixes are needed to build the first
three chapters:

chapter_02.tex:249
    Text: \subsection*{WHAT IS \verb|PC  RA RO AC XR YR SP NV#BDIZC|?}
     Fix: The \verb command might not work in a header
          If removed, the # must be escaped with \

chapter_03.tex:250
    Text: (The X16 logo is code point \xad, SHY, soft-hyphen.)
     Fix: The glyph \xad doesn't exist and must be replaced/removed

chapter_03.tex:367
    Text: Shift+Alt+\verb|s| & \verb|␣| & \xa0 \\
     Fix: The glyph \xa0 doesn't exist and must be replaced/removed


