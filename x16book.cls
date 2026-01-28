% Class identification
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{x16book}[2026/01/20 Commander X16 book class]

% Load parent class
\LoadClass[10pt]{book}

% Pass options to parent class
\DeclareOption*
{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax

% Packages
\RequirePackage[english]{babel}
\RequirePackage{geometry}
\RequirePackage{xcolor}
\RequirePackage{afterpage}
\RequirePackage{titlesec}
\RequirePackage{enumitem, calc}
\RequirePackage{fancyhdr}
\RequirePackage{hyperref}
\RequirePackage{parskip}[parfill]
\RequirePackage{tcolorbox}
\RequirePackage{longtable}
\RequirePackage{tabu}
\RequirePackage{fontspec}
\RequirePackage{listings}
\RequirePackage{tabularray}

% Definitions
\geometry{a5paper, portrait}
\setmainfont{Poppins}
\definecolor{x16blue}{cmyk}{1.00, 0.50, 0.00, 0.00}
\definecolor{x16gray}{cmyk}{0.00, 0.00, 0.00, 0.20}
\titleformat{\chapter}[display]
    {\normalfont\sffamily\raggedleft\huge\bfseries\color{white}}
    {\chaptertitlename\ \thechapter}{20pt}{\Huge}
\titleformat{\section}
    {\normalfont\bfseries\huge\color{x16blue}}{\thesection}{20pt}{}
\titleformat{\subsection}
    {\normalfont\bfseries\large\color{x16blue}}{\thesection}{20pt}{}
\fancypagestyle{whitepagenum}{
    \fancyhf{}
    \renewcommand{\headrulewidth}{0pt}
    \renewcommand{\footrulewidth}{0pt}
    \fancyfoot[C]{\textcolor{white}{\thepage}}
}
\newcommand*\NoIndentAfterEnv[1]{%
  \AfterEndEnvironment{#1}{\par\@afterindentfalse\@afterheading}}
\makeatother

% Chapter environment
\newenvironment{chapterpage}[1]
    %begin
    {
        \color{white}
        \chapter{#1}
        \pagecolor{x16blue}
        \thispagestyle{whitepagenum}
    }
    %end
    {
        \color{black}
        \afterpage{\nopagecolor}
        \newpage
    }

% Chapter content list
\newenvironment{chapteritems}
    %begin
    {
        \begin{itemize}[labelwidth=0.5\textwidth, leftmargin=0.5\textwidth]
    }
    %end
    {
        \end{itemize}
    }

% Suppress indentation
%\NoIndentAfterEnv{chapterpage}

% TODO
\newenvironment{tightlist}{}{}
\newenvironment{Shaded}
    {
        \begin{tcolorbox}[colframe=x16blue,colback=x16gray,boxrule=0.5pt]
        \ttfamily\scriptsize
    }
    {
        \end{tcolorbox}
    }
\newenvironment{Highlighting}{}{} 
\newcommand{\NormalTok}[1]{\par #1}
