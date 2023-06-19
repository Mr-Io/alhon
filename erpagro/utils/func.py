
def __merge(a, b, path=None):
    '''merges b into a'''
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                __merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def convert_dotted_json(dottedJson):
    '''
    parameter
        dottedJson : dict type
    '''
    root = {}

    for key in dottedJson:
        split_key = key.split(".");
        split_key.reverse()
        value = dottedJson [key]
        curr = {split_key[0]: value};
        for ind in range(1, len(split_key)):
            curr = {split_key[ind]:curr}
        root = __merge(root, curr)

    return root
