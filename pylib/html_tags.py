# a collection of functions for outputting HTML

INDENT1 = "    "
INDENT2 = INDENT1 + INDENT1
INDENT4 = INDENT2 + INDENT2

    
def par(text=None, indent=INDENT4):
    s = indent + '<p>\n'
    if text is not None:
        s += text + '\n'
    s += indent + '</p>\n'
    return s
    
def figure(src="", caption=None, indent=INDENT4):
    # by default we get an empty figure tag
    s = indent + '<figure>\n'
    s += indent + INDENT1 + '<img src="' + src + '" width="40%">\n'
    s += indent + INDENT1 + '<figcaption>\n'
    if caption is not None:
        s += indent + INDENT1 + caption + "\n"
    s += indent + INDENT1 + '</figcaption>\n'
    s += indent + '</figure>\n'
    return s

def details(sumtext, level=1, indent=INDENT4, inc_par=False, inc_fig=False,
           inner_details=None):
    indent += INDENT1 * (level - 1)
    s = indent + '<details>\n'
    inner_indent = indent + INDENT1   # add one level indentation
    s += inner_indent + '<summary class="sum' + str(level) + '">\n'
    s += inner_indent + sumtext + "\n"
    s += inner_indent + '</summary>\n'
    if inc_fig:
        s += figure(indent=inner_indent)
    if inc_par:
        s += par(indent=inner_indent)
    if inner_details is not None:
        s += inner_details
    s += indent + '</details>\n'
    return s

def ulist(css_class=None, l=None, indent=INDENT4, level=1):
    return html_list(css_class=css_class, l=l,
                     indent=indent, level=level,
                     list_type='ol')

def olist(css_class=None, l=None, indent=INDENT4, level=1):
    return html_list(css_class=css_class, l=l,
                     indent=indent, level=level,
                     list_type='ol')

def html_list(css_class=None, l=None, indent=INDENT4, level=1,
              list_type='ul'):
    # represents modules in homepage
    indent += INDENT1 * (level - 1)
    inner_indent = indent + INDENT1   # add one level indentation
    s = indent + "<" + list_type
    if css_class is not None:
        s += " class=\"" + css_class + "\""
    s += ">\n"
    for item in l:
        # l is the content within li tag (in this case, anchor tags)
        s += inner_indent
        s += "<li>\n"
        s += inner_indent
        s += item + "\n"
        s += inner_indent
        s += "</li>\n"
    s += indent + "</" + list_type + ">\n"
    return s

def image(indent=INDENT4, src="", alt="", other_attr=""):
    s = indent + "<img src=" + src + "alt=" + alt + other_attr + ">\n"
    return s

def head(indent=INDENT4, title="", cssFile=None): # generate meta head
    s = "<head>\n"
    s += INDENT1 + "<title>\n\n"
    s += INDENT2 + title + "\n"
    s += INDENT1 + "</title>\n"
    if cssFile is not None:
        s += "<link rel='stylesheet' type='text/css' href="+cssFile+">\n"
    s += "</head>\n"
    return s


collapse_link = 'data-toggle="collapse" aria-expanded="false"'

def sidebar_links(padding=INDENT1, topic=None, tot_submenus=0,
                  is_url=False):
    s = "%s<li>\n" % padding
    if is_url:
        s += '%s<a href="%s">\n' % (padding, topic.url)
    else:
        s += ('%s<a href="#Submenu%d" %s >\n'
              % (padding, tot_submenus, collapse_link))
    if topic.glyphicon:
        s += '%s<i class="glyphicon %s"></i>\n' % (padding, topic.glyphicon)
    s += "%s%s\n" % (padding, topic.title)
    s += "%s</a>\n" % padding
    s += "%s</li>\n" % padding
    return s

def sidebar(title="", short_title="", menu_txt=""): # for create_menu.py
    s = "<!-- Sidebar Holder -->\n"
    s += '<nav id=\"sidebar\">\n'
    s += '<div id=\"sidebarCollapse\">\n'
    s += '<div class=\"sidebar-header\">\n'
    s += '<h1>\n'+title+'\n'+'</h1>\n'
    s += '<strong>'+short_title+'</strong>\n'
    s += '</div>\n</div>\n'
    s += menu_txt
    s += "</nav>\n" 
    return s 

