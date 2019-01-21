"""Some utility functions to use with the staffing views"""


def pack_list_to_string(element_list,sep=':'):
    """Return a string represenation of the element list surounded and separated by sep"""
    
    return sep + sep.join(str(element_list)) + sep
    
    
def un_pack_string(string,inSep=":",outSep=","):
    """Convert a previously "Packed" list to a 'outSep' separated string"""
    
    
    return string.strip(inSep).replace(inSep,outSep)