from invoke import task
from export_tools import to_xml
from export_tools import to_sinc
from export_tools import to_markdown


@task
def xml(c):
    with open('PCode.xml', 'wt') as f:
        print(to_xml.run(), file=f)


@task
def sinc(c):
    with open('kh2ai.sinc', 'wt') as f:
        print(to_sinc.run(), file=f)


@task
def md(c):
    with open('kh2ai.md', 'wt') as f:
        print(to_markdown.run(), file=f)
