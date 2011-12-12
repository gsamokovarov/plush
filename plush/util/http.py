def parse_content_type(raw_content_type):
    '''
    Parses HTTP _Content-Type_ header.

    Returns a tuple of the parsed type as a string, and a dictionary of the
    parsed parameters.
    '''

    type, _, params = (raw_content_type or '').partition(';')

    type = type.strip()

    params = filter(bool, params.split(';'))
    params = [param.strip() for param in params]
    params = [param.split('=') for param in params]
    params = dict([item for item in params if len(item) == 2])

    return (type, params)

def encode_content_type(type, params):
    '''
    Encodes `type` string and dictionary of parameters to HTTP _Content-Type_
    header friendly message.

    Does not escape the special characters at the moment, so keep that in mind.
    '''

    params = ['%s=%s' % (name, value) for name, value in params]
    params = ';'.join(params)

    return ';'.join([type, params])
