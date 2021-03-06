# -*- coding: utf-8 -*-
"""
    renoir_haml.elements
    --------------------

    Processes haml files and creates nodes

    :copyright: 2017 Giovanni Barillari

    Based on the code of hamlpy (https://github.com/jessemiller/HamlPy)
    :copyright: 2011 Jesse Miller

    :license: BSD-3-Clause
"""

import re

from .elements import Element

ELEMENT = '%'
ID = '#'
CLASS = '.'
DOCTYPE = '!!!'

HTML_COMMENT = '/'
CONDITIONAL_COMMENT = '/['
HAML_COMMENTS = ['-#', '=#']

VARIABLE = '='
TAG = '-'

INLINE_VARIABLE = re.compile(r'(?<!\\)([#=]\{\s*(.+?)\s*\})')
ESCAPED_INLINE_VARIABLE = re.compile(r'\\([#=]\{\s*(.+?)\s*\})')

COFFEESCRIPT_FILTERS = [':coffeescript', ':coffee']
JAVASCRIPT_FILTER = ':javascript'
CSS_FILTER = ':css'
STYLUS_FILTER = ':stylus'
PLAIN_FILTER = ':plain'
MARKDOWN_FILTER = ':markdown'
CDATA_FILTER = ':cdata'
PYGMENTS_FILTER = ':highlight'
RENOIR_FILTER = '---'

ELEMENT_CHARACTERS = (ELEMENT, ID, CLASS)

HAML_ESCAPE = '\\'


def create_node(haml_line):
    stripped_line = haml_line.strip()

    if len(stripped_line) == 0:
        return None

    if (
        re.match(INLINE_VARIABLE, stripped_line) or
        re.match(ESCAPED_INLINE_VARIABLE, stripped_line)
    ):
        return PlaintextNode(haml_line)

    if stripped_line == RENOIR_FILTER:
        return RenoirFilterNode(haml_line)

    if stripped_line[0] == HAML_ESCAPE:
        return PlaintextNode(haml_line)

    if stripped_line.startswith(DOCTYPE):
        return DoctypeNode(haml_line)

    if stripped_line[0] in ELEMENT_CHARACTERS:
        return ElementNode(haml_line)

    if stripped_line[0:len(CONDITIONAL_COMMENT)] == CONDITIONAL_COMMENT:
        return ConditionalCommentNode(haml_line)

    if stripped_line[0] == HTML_COMMENT:
        return CommentNode(haml_line)

    for comment_prefix in HAML_COMMENTS:
        if stripped_line.startswith(comment_prefix):
            return HamlCommentNode(haml_line)

    if stripped_line[0] == VARIABLE:
        return VariableNode(haml_line)

    if stripped_line[0] == TAG:
        return TagNode(haml_line)

    if stripped_line == JAVASCRIPT_FILTER:
        return JavascriptFilterNode(haml_line)

    if stripped_line in COFFEESCRIPT_FILTERS:
        return CoffeeScriptFilterNode(haml_line)

    if stripped_line == CSS_FILTER:
        return CssFilterNode(haml_line)

    if stripped_line == STYLUS_FILTER:
        return StylusFilterNode(haml_line)

    if stripped_line == PLAIN_FILTER:
        return PlainFilterNode(haml_line)

    if stripped_line == CDATA_FILTER:
        return CDataFilterNode(haml_line)

    return PlaintextNode(haml_line)


class TreeNode:
    def __init__(self):
        self.parent = None
        self.children = []

    def left_sibling(self):
        siblings = self.parent.children
        index = siblings.index(self)
        return siblings[index - 1] if index > 0 else None

    def right_sibling(self):
        siblings = self.parent.children
        index = siblings.index(self)
        return siblings[index + 1] if index < len(siblings) - 1 else None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


class RootNode(TreeNode):
    def __init__(self, attr_wrapper="'"):
        super().__init__()
        self.indentation = -2
        # Number of empty lines to render after node
        self.newlines = 0
        # Rendered text at start of node, e.g. "<p>\n"
        self.before = ''
        # Rendered text at end of node, e.g. "\n</p>"
        self.after = ''
        # Indicates that a node does not render anything
        self.empty_node = False

        # Options
        self.attr_wrapper = attr_wrapper

    def add_child(self, child):
        '''Add child node, and copy all options to it'''
        super(RootNode, self).add_child(child)
        child.attr_wrapper = self.attr_wrapper

    def render(self):
        # Render (sets self.before and self.after)
        self._render_children()
        # Post-render (nodes can modify the rendered text of other nodes)
        self._post_render()
        # Generate HTML
        return self._generate_html()

    def render_newlines(self):
        return '\n' * (self.newlines + 1)

    def parent_of(self, node):
        if self._should_go_inside_last_node(node):
            ret = self.children[-1].parent_of(node)
            return ret
        return self

    def inside_filter_node(self):
        if self.parent:
            return self.parent.inside_filter_node()
        return False

    def _render_children(self):
        for child in self.children:
            child._render()

    def _post_render(self):
        for child in self.children:
            child._post_render()

    def _generate_html(self):
        output = []
        output.append(self.before)
        for child in self.children:
            output.append(child.before)
            output += [gc._generate_html() for gc in child.children]
            output.append(child.after)
        output.append(self.after)
        return ''.join(output)

    def add_node(self, node):
        if self._should_go_inside_last_node(node):
            self.children[-1].add_node(node)
        else:
            self.add_child(node)

    def _should_go_inside_last_node(self, node):
        return (
            len(self.children) > 0 and (
                node.indentation > self.children[-1].indentation or (
                    node.indentation == self.children[-1].indentation and
                    self.children[-1].should_contain(node))))

    def should_contain(self, node):
        return False

    def debug_tree(self):
        return '\n'.join(self._debug_tree([self]))

    def _debug_tree(self, nodes):
        output = []
        for n in nodes:
            output.append('%s%s' % (' ' * (n.indentation + 2), n))
            if n.children:
                output += self._debug_tree(n.children)
        return output

    def __repr__(self):
        return '(%s)' % (self.__class__)


class HamlNode(RootNode):
    def __init__(self, haml):
        super().__init__()
        self.haml = haml.strip()
        self.raw_haml = haml
        self.indentation = (len(haml) - len(haml.lstrip()))
        self.spaces = ''.join(haml[0] for i in range(self.indentation))

    def replace_inline_variables(self, content):
        content = re.sub(INLINE_VARIABLE, r'{{=\2}}', content)
        content = re.sub(ESCAPED_INLINE_VARIABLE, r'\1', content)
        return content

    def __repr__(self):
        return '(%s in=%d, nl=%d: %s)' % (
            self.__class__, self.indentation, self.newlines, self.haml)


class PlaintextNode(HamlNode):
    def _render(self):
        text = self.replace_inline_variables(self.haml)
        # Remove escape character unless inside filter node
        if text and text[0] == HAML_ESCAPE and not self.inside_filter_node():
            text = text.replace(HAML_ESCAPE, '', 1)

        self.before = '%s%s' % (self.spaces, text)
        if self.children:
            self.before += self.render_newlines()
        else:
            self.after = self.render_newlines()
        self._render_children()


class ElementNode(HamlNode):
    def __init__(self, haml):
        super().__init__(haml)
        self.renoir_variable = False

    def _render(self):
        self.element = Element(self.haml, self.attr_wrapper)
        self.before = self._render_before(self.element)
        self.after = self._render_after(self.element)
        self._render_children()

    def _render_before(self, element):
        '''Render opening tag and inline content'''
        start = ["%s<%s" % (self.spaces, element.tag)]
        if element.id:
            start.append(
                " id=%s" % self.element.attr_wrap(
                    self.replace_inline_variables(element.id)))
        if element.classes:
            start.append(
                " class=%s" % self.element.attr_wrap(
                    self.replace_inline_variables(element.classes)))
        if element.attributes:
            start.append(
                ' ' + self.replace_inline_variables(element.attributes))

        content = self._render_inline_content(self.element.inline_content)

        if element.nuke_inner_whitespace and content:
            content = content.strip()

        if element.self_close and not content:
            start.append(" />")
        elif content:
            start.append(">%s" % (content))
        elif self.children:
            start.append(">%s" % (self.render_newlines()))
        else:
            start.append(">")
        return ''.join(start)

    def _render_after(self, element):
        '''Render closing tag'''
        if element.inline_content:
            return "</%s>%s" % (element.tag, self.render_newlines())
        elif element.self_close:
            return self.render_newlines()
        elif self.children:
            return "%s</%s>\n" % (self.spaces, element.tag)
        return "</%s>\n" % (element.tag)

    def _post_render(self):
        # Inner whitespace removal
        if self.element.nuke_inner_whitespace:
            self.before = self.before.rstrip()
            self.after = self.after.lstrip()

            if self.children:
                node = self
                # If node renders nothing, do removal on first child instead
                if node.children[0].empty_node == True:
                    node = node.children[0]
                if node.children:
                    node.children[0].before = node.children[0].before.lstrip()

                node = self
                if node.children[-1].empty_node == True:
                    node = node.children[-1]
                if node.children:
                    node.children[-1].after = node.children[-1].after.rstrip()

        # Outer whitespace removal
        if self.element.nuke_outer_whitespace:
            left_sibling = self.left_sibling()
            if left_sibling:
                # If node has left sibling, strip whitespace after left sibling
                left_sibling.after = left_sibling.after.rstrip()
                left_sibling.newlines = 0
            else:
                # If not, whitespace comes from it's parent node,
                # so strip whitespace before the node
                self.parent.before = self.parent.before.rstrip()
                self.parent.newlines = 0

            self.before = self.before.lstrip()
            self.after = self.after.rstrip()

            right_sibling = self.right_sibling()
            if right_sibling:
                right_sibling.before = right_sibling.before.lstrip()
            else:
                self.parent.after = self.parent.after.lstrip()
                self.parent.newlines = 0

        super(ElementNode, self)._post_render()

    def _render_inline_content(self, inline_content):
        if inline_content is None or len(inline_content) == 0:
            return None

        if self.renoir_variable:
            content = "{{=" + inline_content.strip() + "}}"
            return content
        return self.replace_inline_variables(inline_content)


class CommentNode(HamlNode):
    def _render(self):
        self.after = "-->\n"
        if self.children:
            self.before = "<!-- %s" % (self.render_newlines())
            self._render_children()
        else:
            self.before = "<!-- %s " % (self.haml.lstrip(HTML_COMMENT).strip())


class ConditionalCommentNode(HamlNode):
    def _render(self):
        conditional = self.haml[1: self.haml.index(']') + 1]

        if self.children:
            self.before = "<!--%s>\n" % (conditional)
        else:
            content = self.haml[
                len(CONDITIONAL_COMMENT) + len(conditional) - 1:]
            self.before = "<!--%s>%s" % (conditional, content)

        self.after = "<![endif]-->\n"
        self._render_children()


class DoctypeNode(HamlNode):
    def _render(self):
        doctype = self.haml.lstrip(DOCTYPE).strip()

        parts = doctype.split()
        if parts and parts[0] == "XML":
            encoding = parts[1] if len(parts) > 1 else 'utf-8'
            self.before = "<?xml version=%s1.0%s encoding=%s%s%s ?>" % (
                self.attr_wrapper, self.attr_wrapper,
                self.attr_wrapper, encoding, self.attr_wrapper,
            )
        else:
            types = {
                "": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
                "Strict": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',
                "Frameset": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">',
                "5": '<!DOCTYPE html>',
                "1.1": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
            }

            if doctype in types:
                self.before = types[doctype]

        self.after = self.render_newlines()


class HamlCommentNode(HamlNode):
    def _render(self):
        self.after = self.render_newlines()[1:]

    def _post_render(self):
        pass


class VariableNode(ElementNode):
    def __init__(self, haml):
        super().__init__(haml)
        self.renoir_variable = True

    def _render(self):
        tag_content = self.haml.lstrip(VARIABLE)
        self.before = "%s%s" % (
            self.spaces, self._render_inline_content(tag_content))
        self.after = self.render_newlines()

    def _post_render(self):
        pass


class TagNode(HamlNode):
    self_closing = ['for', 'if', 'with']
    need_fixtures = ['for', 'if', 'elif', 'else', 'with']
    may_contain = {'if': ['else', 'elif'], 'with': 'with'}

    def __init__(self, haml):
        super().__init__(haml)
        self.tag_statement = self.haml.lstrip(TAG).strip()
        self.tag_name = self.tag_statement.split(' ')[0]
        self.fix_statement = (
            not self.tag_statement.split(' ')[-1].endswith(":"))

        if self.tag_name == self.self_close:
            raise TypeError(
                "Do not close Renoir tags manually. "
                "It will be done for you.")

    @property
    def self_close(self):
        return 'pass'

    def _render(self):
        fixture = (
            ':' if self.tag_name in self.need_fixtures and self.fix_statement
            else '')
        self.before = "%s{{%s%s}}" % (self.spaces, self.tag_statement, fixture)
        if self.tag_name in self.self_closing:
            self.before += self.render_newlines()
            self.after = '%s{{%s}}%s' % (
                self.spaces, self.self_close, self.render_newlines())
        else:
            if self.children:
                self.before += self.render_newlines()
            else:
                self.after = self.render_newlines()
        self._render_children()

    def should_contain(self, node):
        return (
            isinstance(node, TagNode) and
            node.tag_name in self.may_contain.get(self.tag_name, ''))


class FilterNode(HamlNode):
    def add_node(self, node):
        self.add_child(node)

    def inside_filter_node(self):
        return True

    def _render_children_as_plain_text(self, remove_indentation=True):
        if self.children:
            initial_indentation = len(self.children[0].spaces)
        for child in self.children:
            child.before = ''
            if not remove_indentation:
                child.before = child.spaces
            else:
                child.before = child.spaces[initial_indentation:]
            child.before += child.haml
            child.after = child.render_newlines()

    def _post_render(self):
        # Don't post-render children of filter nodes as we don't want them
        # to be interpreted as HAML
        pass


class PlainFilterNode(FilterNode):
    def __init__(self, haml):
        super().__init__(haml)
        self.empty_node = True

    def _render(self):
        self._render_children_as_plain_text()


class RenoirFilterNode(FilterNode):
    def _render(self):
        if self.children:
            self.before = (
                ' ' * len(self.spaces) + '{{' + self.render_newlines()[1:])
            indent_offset = len(self.children[0].spaces)
            code = (
                "\n".join(
                    [node.raw_haml[indent_offset:] for node in self.children]
                ) + '}}\n')
            self.before += code
        else:
            self.after = self.render_newlines()


class JavascriptFilterNode(FilterNode):
    def _render(self):
        self.before = '<script type=%(attr_wrapper)stext/javascript%(attr_wrapper)s>\n// <![CDATA[%(new_lines)s' % {
            'attr_wrapper': self.attr_wrapper,
            'new_lines': self.render_newlines(),
        }
        self.after = '// ]]>\n</script>\n'
        self._render_children_as_plain_text(remove_indentation=False)


class CoffeeScriptFilterNode(FilterNode):
    def _render(self):
        self.before = '<script type=%(attr_wrapper)stext/coffeescript%(attr_wrapper)s>\n#<![CDATA[%(new_lines)s' % {
            'attr_wrapper': self.attr_wrapper,
            'new_lines': self.render_newlines(),
        }
        self.after = '#]]>\n</script>\n'
        self._render_children_as_plain_text(remove_indentation=False)


class CssFilterNode(FilterNode):
    def _render(self):
        self.before = '<style type=%(attr_wrapper)stext/css%(attr_wrapper)s>\n/*<![CDATA[*/%(new_lines)s' % {
            'attr_wrapper': self.attr_wrapper,
            'new_lines': self.render_newlines(),
        }
        self.after = '/*]]>*/\n</style>\n'
        self._render_children_as_plain_text(remove_indentation=False)


class StylusFilterNode(FilterNode):
    def _render(self):
        self.before = '<style type=%(attr_wrapper)stext/stylus%(attr_wrapper)s>\n/*<![CDATA[*/%(new_lines)s' % {
            'attr_wrapper': self.attr_wrapper,
            'new_lines': self.render_newlines(),
        }
        self.after = '/*]]>*/\n</style>\n'
        self._render_children_as_plain_text()


class CDataFilterNode(FilterNode):
    def _render(self):
        self.before = self.spaces + '<![CDATA[%s' % (self.render_newlines())
        self.after = self.spaces + ']]>\n'
        self._render_children_as_plain_text(remove_indentation=False)
