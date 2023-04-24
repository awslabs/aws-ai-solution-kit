class _const(object):
    class ConstError(TypeError):
        def __init__(self, msg):
            super().__init__(msg)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            err = self.ConstError("Can't change const.%s" % name)
            raise err
        if not name.isupper():
            err = self.ConstError('Const name "%s" is not all uppercase' % name)
            raise err
        self.__dict__[name] = value


const = _const()

const.SOLUTION_FULL_NAME = "AIGC Stable Diffusion SageMaker"
const.SOLUTION_NAME = "AIGC_SAGEMAKER"

const.LOGGER_API = "api"

const.RESPONSE_SUCCESS = "success"
const.RESPONSE_FAIL = "fail"
