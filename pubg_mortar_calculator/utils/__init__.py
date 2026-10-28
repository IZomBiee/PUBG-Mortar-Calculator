from pubg_mortar_calculator.utils import imgpr, paths
from pubg_mortar_calculator.utils.screenshot import take_screenshot


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance
