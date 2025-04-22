# for f in examples/*.ttl ; do python scripts/convert_to_dot.py $f > ${f/.ttl/.dot} ; done
from rdflib.namespace import RDF
from rdflib import Graph, URIRef, BNode
import sys
import re

print(sys.argv[1], file=sys.stderr)
g = Graph()
g.parse(sys.argv[1], format="turtle")

roots = set([s for s, p, o in g if len(list(g.subjects(None, s))) == 0])


def make_name(n):
    print(n, file=sys.stderr)
    s = str(n)
    i = 0
    if '#' in s:
        i = s.rindex('#')
    if '/' in s:
        i = max(i, s.rindex('/'))
    if s[0] == "n" and all('0' <= c <= '9' or 'a' <= c <= 'f' for c in s[1:]):
        return "node" + s[1:4]
    if i + 1 < len(s) and s[i + 1].isdigit():
        return "Synset " + s[i + 1:]
    t = s[i + 1:]
    if t == "":
        return "_node"
    else:
        return s[i + 1:]


def write_obj(o):
    if isinstance(o, URIRef):
        return "<%s>" % str(o)
    elif isinstance(o, BNode):
        return "[]"
    elif o.language:
        return "%s@%s" % (str(o), o.language)
    else:
        return str(o)

seen_node = set([])


def gen(s):
    name = make_name(s)
    class_of = None
    if s not in seen_node:
        seen_node.add(s)
        for o in g.objects(s, RDF.type):
            if not class_of:
                class_of = o
        args = []
        for p, o in g.predicate_objects(s):
            if p != RDF.type and isinstance(o, URIRef) or isinstance(o, BNode):
                o2 = gen(o)
                print("%s -> %s [ label=\"%s\" ] " %
                      (re.sub(r"[\W^-]", "", name), o2, make_name(p)))
            elif p != RDF.type:
                prop_name = make_name(p)
                args.append("%s=%.30s" % (prop_name, write_obj(o)))
        if class_of:
            class_of_name = make_name(class_of)
            if args:
                print("%s [ label=\"{%s : %s|%s}\" ]" %
                      (re.sub(r"[\W^-]", "", name), name,
                       class_of_name, "\\l".join(args)))
            else:
                print("%s [ label=\"{%s : %s}\" ]" %
                      (re.sub(r"[\W^-]", "", name), name, class_of_name))
        else:
            if args:
                print("%s [ label=\"{%s|%s}\" ]" %
                      (re.sub(r"[\W^-]", "", name), name, "\\l".join(args)))
            else:
                print("%s [ label=\"{%s}\" ]" %
                      (re.sub(r"[\W^-]", "", name), name))
    return re.sub(r"[\W^-]", "", name)


print("digraph G {")
print("  fontname = \"Bitstream Vera Sans\"")
print("    fontsize = 8")
print("")
print("    node [")
print("      fontname = \"Bitstream Vera Sans\"")
print("      fontsize = 8")
print("      shape = \"record\"")
print("    ]")
print("")
print("    edge [")
print("      fontname = \"Bitstream Vera Sans\"")
print("      fontsize = 8")
print("    ]")
print(" ")
if roots:
    for s in roots:
        gen(s)
else:
    s1 = next(g.subjects())
    gen(s1)
print("}")
