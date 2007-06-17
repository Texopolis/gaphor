"""
Support for editable text, a part of a diagram item, i.e. name of named
item, guard of flow item, etc.
"""

from gaphor.diagram.style import Style
from gaphor.diagram.style import ALIGN_CENTER, ALIGN_TOP

from gaphas.geometry import distance_rectangle_point, Rectangle
from gaphas.util import text_extents, text_align, text_multiline


class EditableTextSupport(object):
    """
    Editable text support to allow display and edit text parts of a diagram
    item.

    Attributes:
     - _texts:       list of diagram item text elements
     - _text_groups: grouping information of text elements (None -
                     ungrouped) 
    """
    def __init__(self):
        self._texts = []
        self._text_groups = { None: [] }


    def texts(self):
        """
        Return list of diagram item text elements.
        """
        return self._texts


    def add_text(self, attr, style = None, pattern = None, when = None):
        """
        Create and add a text element. See also TextElement class
        description.

        Parameters:
         - attr:  attribute name of diagram item subject
         - style: align information

        If style information contains 'text-align-group' data, then text
        element is grouped.

        Returns created text element.
        """
        txt = TextElement(attr, style=style, pattern=pattern, when=when)
        self._texts.append(txt)

        # try to group text element
        gname = style.get('text-align-group')
        if gname not in self._text_groups:
            self._text_groups[gname] = []
        group = self._text_groups[gname]
        group.append(txt)

        return txt


    def _align_text_group(self, context, group):
        """
        Align group of text elements making vertical stack of strings.

        Parameters:
         - list of text elements to group
        """
        cr = context.cairo

        # find displayable texts
        texts = [ txt for txt in group if txt.display() ]

        # nothing to stack
        if len(texts) == 0:
            return

        # calculate text dimensions
        dimensions = [ text_extents(cr, txt.text, multiline=True) \
                for txt in texts ]

        # find maximum width and total height
        width = max(ext[0] for ext in dimensions)
        height = sum(ext[1] for ext in dimensions)

        extents = (width, height)
        width, height = map(max, extents, (15, 10))

        # align according to style of first text
        style = texts[0]._style
        x, y = self.text_align(extents, style.text_align,
                style.text_padding, style.text_outside)

        # stack all displayable texts
        dy = 0
        for i, txt in enumerate(texts):
            dw, dh  = dimensions[i]

            # center stacked texts
            txt.bounds.x0 = x + (width - dw) / 2.0
            txt.bounds.y0 = y + dy
            txt.bounds.width = dw
            txt.bounds.height = dh
            dy += dh + 3


    def update(self, context):
        """
        Calculate position and dimensions of all text elements of a diagram
        item.
        """
        cr = context.cairo
        for gname in self._text_groups:
            if gname is not None:
                group = self._text_groups[gname]
                self._align_text_group(context, group)

        # align ungrouped text elements
        for txt in self._text_groups[None]:
            if not txt.display():
                continue

            extents = text_extents(cr, txt.text, multiline=True)
            width, height = map(max, extents, (15, 10))
            extents = (width, height)

            style = txt._style
            x, y = self.text_align(extents, style.text_align,
                    style.text_padding, style.text_outside)

            txt.bounds.x0 = x
            txt.bounds.y0 = y
            txt.bounds.width = width
            txt.bounds.height = height


    def point(self, x, y):
        """
        Return the distance to the nearest text element.
        """
        distances = [10000.0]
        for txt in self._texts:
            if not txt.display():
                continue
            distances.append(distance_rectangle_point(txt.bounds, (x, y)))
        return min(distances)


    def draw(self, context):
        """
        Draw all text elements of a diagram item.
        """
        cr = context.cairo
        for txt in self._texts:
            if not txt.display():
                continue
            bounds = txt.bounds
            x, y = bounds.x0, bounds.y0
            width, height = bounds.width, bounds.height

            if self.subject:
                text_multiline(cr, x, y, txt.text)

            if context.hovered or context.focused or context.draw_all:
                cr.set_line_width(0.5)
                cr.rectangle(x, y, width, height)
                cr.stroke()



class TextElement(object):
    """
    Representation of an editable text, which is part of a diagram item.

    Text element is aligned according to style information.
        
    It also displays and allows to edit value of an attribute of UML
    class (DiagramItem.subject). Attribute name can be recursive, all
    below attribute names are valid:
     - name (named item name)
     - guard.value (flow item guard)

    Attributes and properties:
     - attr:    name of displayed and edited UML class attribute
     - bounds:  text bounds
     - _style:  text style (i.e. align information, padding)
     - text:    rendered text to be displayed
     - pattern: print pattern to display text

    See also EditableTextSupport.add_text.
    """

    bounds = property(lambda self: self._bounds)

    def __init__(self, attr, style = None, pattern = None, when = None):
        """
        Create new text element with bounds (0, 0, 10, 10) and empty text.

        Parameters:
         - when: function, which evaluates to True/False determining if text
                 should be displayed
        """
        super(TextElement, self).__init__()

        self._bounds = Rectangle(0, 0, width=10, height=0)

        # create default style for a text element
        self._style = Style()
        self._style.add('text-padding', (2, 2, 2, 2))
        self._style.add('text-align', (ALIGN_CENTER, ALIGN_TOP))
        self._style.add('text-outside', False)
        if style:
            self._style.update(style)

        self.attr = attr
        self._text = ''

        if when:
            self.display = when

        if pattern:
            self._pattern = pattern
        else:
            self._pattern = '%s'


    def _set_text(self, value):
        self._text = self._pattern % value


    text = property(lambda s: s._text, _set_text)


    def display(self):
        """
        Display text by default.
        """
        return True


# vim:sw=4:et:ai
