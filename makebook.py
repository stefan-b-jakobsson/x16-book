import sys
import mistletoe
from mistletoe.x16latex_renderer import X16LaTeXRenderer

with open(sys.argv[1], "r") as fin:
    rendered = mistletoe.markdown(fin, X16LaTeXRenderer)
    print (rendered)
