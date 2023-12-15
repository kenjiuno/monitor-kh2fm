from invoke import task
from export_tools import to_xml
from export_tools import to_sinc
from export_tools import to_markdown
from export_tools import to_cs
from export_tools import fixup as fixup_module
import os


@task
def xml(c):
    with open("PCode.xml", "wt") as f:
        print(to_xml.run(), file=f)


@task
def sinc(c):
    with open("kh2ai.sinc", "wt") as f:
        print(to_sinc.run(), file=f)


@task
def md(c, out_file="docs/kh2ai.md"):
    with open(out_file, "wt") as f:
        print(to_markdown.run(), file=f)


@task
def cs_enum(c, out_file="out.cs"):
    with open(out_file, "wt") as f:
        print(to_cs.enums(), file=f)


@task
def cs(c, out_file="out.cs"):
    with open(out_file, "wt") as f:
        print(to_cs.descs(), file=f)


@task
def cs_trap(c, out_file="trap.cs"):
    with open(out_file, "wt") as f:
        print(to_cs.traps(), file=f)


@task
def fixup(c, out_file="fixup.json"):
    with open(out_file, "wt") as f:
        print(fixup_module.ver3(), file=f)
