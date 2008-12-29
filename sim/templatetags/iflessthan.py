from django.template import Node, NodeList, Template, Context, Variable
from django.template import TemplateSyntaxError
from django.template import Library, InvalidTemplateLibrary


register = Library()

class IfLessThanNode(Node):
    def __init__(self, var1, var2, nodelist_true, nodelist_false, negate):
        self.var1, self.var2 = Variable(var1), Variable(var2)
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfEqualNode>"

    def render(self, context):
        try:
            val1 = self.var1.resolve(context)
        except VariableDoesNotExist:
            val1 = None
        try:
            val2 = self.var2.resolve(context)
        except VariableDoesNotExist:
            val2 = None
        if (val1 < val2):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)

def do_iflessthan(parser, token, negate):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfLessThanNode(bits[1], bits[2], nodelist_true, nodelist_false, negate)

#@register.tag                                                                                                                       
def iflessthan(parser, token):
    """                                                                                                                              
    Outputs the contents of the block if arg1 is less than arg2                                                  
                                                                                                                                     
    Examples::                                                                                                                       
                                                                                                                                     
        {% iflessthan user.id comment.user_id %}                                                                                        
            ...                                                                                                                      
        {% endiflessthan %}                                                                                                             
                                                                                                                                     
        {% iflessthan user.id comment.user_id %}                                                                                     
            ...                                                                                                                      
        {% else %}                                                                                                                   
            ...                                                                                                                      
        {% endiflessthan %}                                                                                                          
    """
    return do_iflessthan(parser, token, False)

iflessthan = register.tag(iflessthan)
