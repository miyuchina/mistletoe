__all__ = ['Token']

class Token(object):
    def tagify(tag, content):
        return "<{0}>{1}</{0}>".format(tag, content)

    def tagify_attrs(tag, attrs, content):
        attrs = [ "{}=\"{}\"".format(key, attrs[key]) for key in attrs ]
        attrs = ' '.join(attrs)
        return "<{0} {1}>{2}</{0}>".format(tag, attrs, content)
