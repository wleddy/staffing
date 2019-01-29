"""Some utility functions to use with the staffing views"""


def pack_list_to_string(element_list,sep=':'):
    """Return a string represenation of the element list surounded and separated by sep"""
    
    if len(element_list) == 0:
        return ''
        
    s = ""
    for x in element_list:
        s += sep + str(x) 
    return s + sep
    
    
def un_pack_string(string,inSep=":",outSep=","):
    """Convert a previously "Packed" list to a 'outSep' separated string"""
    
    if not string:
        return '' #guard against None
    return string.strip(inSep).replace(inSep,outSep)