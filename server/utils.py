from rest_framework.response import Response


def required_data(required_fields, data):
    missing_values = []
    for field in required_fields:
        value = data.get(field,  None)
        if not value:
            missing_values.append(field)

    return Response(resp_fail(f'{missing_values} is required'), status=422)


def resp_success(message, data={}, code=200):

    return {
        'success': True,
        'message': message,
        'results': data,
        'code': code
    }


def resp_fail(error_msg, data={}, error_code=401):

    return {
        'success': False,
        'message': error_msg,
        'results': data,
        'code': error_code
    }
