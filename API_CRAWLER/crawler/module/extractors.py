from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from crawler.libs.util import get_path, flatten_dictionaries,kurs
import json
from time import sleep
import re
import inspect
import operator

DRIVER_PATH = {"chrome": get_path('chromedriver'),
               "firefox": get_path('geckodriver')}
elementFilterTool = {"id": By.ID,
                     "xpath": By.XPATH,
                     "link_text": By.LINK_TEXT,
                     "partial_link_text": By.PARTIAL_LINK_TEXT,
                     "name": By.NAME,
                     "tag_name": By.TAG_NAME,
                     "class_name": By.CLASS_NAME,
                     "css_selector": By.CSS_SELECTOR}


class Extractors(object):
    value_name = None
    is_postprocessed = False
    _pre_actions = None
    is_preaction = False
    _preactions_chains = None
    static = False

    def __init__(self, **kwargs):
        self.postprocess = list()
        self.extractor = SeleniumElementsExtractor(**kwargs)
        self.postprocessed_value = list()

    def _configure_preactions(self,action,driver):
        action_chains = list()
        chain = self._pre_actions
        for i in chain:
            tmp = ActionsHandler(action,driver,
                                 i['chain'],i['chain_name'])
        action_chains.append(tmp)
        self._preactions_chains = action_chains

    def dump_value(self):
        key = self.value_name
        if self.is_preaction:
            for act in self._preactions_chains:
                act.run()
            values = self.extractor.run()
        else:
            if self.extractor.static:
                values = [{"static": self.extractor.run()[0]}]
            else:
                values = self.extractor.run()
        if values and self.is_postprocessed:
            postprocessed_value = list()
            for i in values:
                val = self.generate_postprocess(i)
                postprocessed_value.append(val)
            values = postprocessed_value
        return {key: values}

    def generate_postprocess(self, value):
        postprocess_ = self.postprocess
        postprocess = list()
        for i in postprocess_:
            kwargs = self.post_process_kwargs(i)
            kwargs['value'] = value
            process = PostProcess(**kwargs)
            process_ = process.extractor(**process.kkwargs)
            value = process_.result
        return value

    def post_process_kwargs(self, data):
        d = {}
        if isinstance(data, dict):
            for key, val in data.items():
                d['type_'] = key
                d = {**d, **data}
        else:
            raise TypeError("YAML Configuration must be list of dictionary")
        return d


class SeleniumElementExtractor(object):
    filter_ = None

    def __init__(self, type_, value, driver):
        self.driver = driver
        type_ = type_.lower()
        self.filter_ = elementFilterTool[type_]
        self.value = value

    def run(self):
        return driver.find_element(self.filter_, self.value).text


class SeleniumElementsExtractor(object):
    filter_ = None
    attribute = None
    current_height = 0
    max_height = None
    cycle = 0

    def __init__(self, type_, static, value, driver, attribute=None):
        self.driver = driver
        self.attribute = attribute
        type_ = type_.lower()
        self.filter_ = elementFilterTool[type_]
        self.value = value
        self.static = static

    def run(self):
        driver = self.driver
        if not self.max_height:
            self.get_page_height()
            self.get_steps()
        text_result = []
        self.cycle = 0
        while "" in text_result or not text_result:
            self.scroll_page()
            result = driver.find_elements(self.filter_, self.value)
            text_result = [i.text for i in result]
            if self.cycle < 3:
                self.reset_scroll()
            else:
                print("Unable To Obtain Data: {}".format(self.value))
                break
        if self.attribute:
            result = [i.get_attribute(self.attribute) for i in result]
        else:
            result = [i.text for i in result]
        return result

    def get_page_height(self):
        driver = self.driver
        script = "window.scrollTo(0,document.body.scrollHeight);"
        driver.execute_script(script)
        height = driver.execute_script("return window.scrollY")
        self.max_height = int(height)
    
    def scroll_page(self, cycle=0, startswith=0):
        driver = self.driver
        delta = self.max_height - self.current_height
        step_scroll = self.step_scroll + self.current_height
        if delta < self.step_scroll:
            step_scroll = self.max_height
        script = "document.documentElement.scrollTo(0,{});".format(step_scroll)
        driver.execute_script(script)
        self.current_height = self.get_current_height()

    def reset_scroll(self):
        self.current_height = 0
        driver = self.driver
        script = "window.scrollTo(0,0);"
        driver.execute_script(script)
        self.cycle = self.cycle + 1

    def get_current_height(self):
        driver = self.driver
        script = "return document.documentElement.scrollTop"
        return driver.execute_script(script)

    def get_steps(self):
        driver = self.driver
        script = "return window.innerHeight"
        steps = driver.execute_script(script)
        self.step_scroll = steps


class PostProcess(object):

    def __init__(self, type_, **kwargs):
        extractor = ExtractorPostProcess[type_]
        if type_ == 'math':
            kkwargs = self.generate_math_args(**kwargs)
        kkwargs = self.parse_arguments(extractor, **kwargs)
        self.extractor = extractor
        self.kkwargs = kkwargs

    def parse_arguments(self, extractor=None, **kwargs):
        func = getattr(extractor, '__init__')
        argspecs = inspect.getargspec(func)
        args = argspecs.args
        args.remove('self')
        extractor_args = {'value': kwargs.pop('value')}
        args.remove('value')
        keys = list(kwargs.keys())
        if args:
            for k1, k2 in zip(args, keys):
                extractor_args[k1] = kwargs.pop(k2)
        return extractor_args

    def generate_math_args(self,**kwargs):
        d = {'query': kwargs['math'], 'value': kwargs['value']}
        return d

class RegexExtractBefore(PostProcess):

    def __init__(self, value, character):
        regex = '(.*)\{}'.format(character)
        result = re.search(regex, repr(value))
        if not result:
            self.result = value
        else:
            result = result.group(1)
            result = result.replace("'","").replace('"','')
            self.result = result


class RegexExtractAfter(PostProcess):
    
    def __init__(self, value, character):
        regex = "\{}(.*)".format(character)
        result = re.search(regex, repr(value))
        if not result:
            result = value
            self.result = value
        else:
            result = result.group(1)
            result = result.replace("'","").replace('"','')
            self.result = result

class RemoveExtendedAscii(PostProcess):

    def __init__(self,value):
        pass

class RegexRaw(PostProcess):
    def __init__(self, value, raw_regex):
        result = re.search(raw_regex, value)
        try:
            result_ = result.group(1)
        except IndexError:
            result_ = result.group(0)
        except AttributeError:
            if not result:
                result_ = value
        self.result = result_


class ExtractNumbers(PostProcess):
    def __init__(self, value):
        result = re.sub("\D", "", value)
        if not result:
            result = value
        self.result = result


class ExtractConvertInt(PostProcess):
    def __init__(self, value):
        num = re.sub("\D", "", value)
        if not num:
            self.result = value
        else:
            self.result = int(num)


class ExtractConvertFloat(PostProcess):
    def __init__(self, value):
        num = re.sub("\D", "", value)
        if not num:
            self.result = value
        else:
            self.result = float(num)

class ConvertCurrency(PostProcess):
    def __init__(self,value,currency):
        try:
            tmp=int(value)
            result = kurs(tmp,currency.upper(),"IDR")
            self.result = int(result)
        except Exception:
            self.result = value

class InsertStringAfter(PostProcess):
    def __init__(self,value,string):
        tmp = str(value)+" {}".format(string)
        self.result = tmp

class InsertStringBefore(PostProcess):
    def __init__(self,value,string):
        tmp = "{} ".format(string)+str(value)
        self.result = tmp


class MathProcess(PostProcess):
    OPERATIONS = {
        "+": lambda x, y: operator.add(x, y),
        "-": lambda x, y: operator.sub(x, y),
        "/": lambda x, y: operator.truediv(x, y),
        "//": lambda x, y: operator.floordiv(x, y),
        "*": lambda x, y: operator.mul(x, y),
        "x": lambda x, y: operator.mul(x, y)
    }

    def __init__(self, query, value, *args, **kwargs):
        self.operator = query['operator']
        self.x = value
        self.y = query['y']

    @property
    def result(self):
        """ Query Model : {x: x, y:y, operation: (+-/*)}
        If x or y is using obtained data, use key::key_name"""
        try:
            x = float(self.x)
            y = float(self.y)
            operator = self.operator
            result_ = self.OPERATIONS[operator](x,y)
            return round(result_,2)
        except Exception:
            return self.x

class RemoveStrings(PostProcess):
    def __init__(self,value,character):
        value = str(value)
        result = value.strip(character)
        self.result = result


ExtractorPostProcess = {
    'extract_before': RegexExtractBefore,
    'extract_after': RegexExtractAfter,
    'raw_regex':    RegexRaw,
    'extract_numbers': ExtractNumbers,
    'extract_convert_int': ExtractConvertInt,
    'extract_convert_float': ExtractConvertFloat,
    'math': MathProcess,
    'convert_currency': ConvertCurrency,
    'remove_strings': RemoveStrings,
    'insert_string_after': InsertStringAfter,
    'insert_string_before': InsertStringBefore
}


class ActionsHandler(object):
    action = None
    name = 'Default'
    repeat = 1

    def __init__(self, action, driver, query, name=None):
        self.action = action
        self.driver = driver
        self.query = query
        for i in query:
            if 'run' in i:
                self.config_run(i['run'])

    def config_run(self, data):
        if isinstance(data, str) or isinstance(data, int):
            self.repeat = int(data)
        elif isinstance(data, dict):
            extractor = data['extractor']
            pass

    @property
    def act(self):
        return self.action

    def run(self):
        self.generate_actions(self.query)
        self.execute()

    def execute(self):
        for i in self.action_chains:
            i.run()
            self.action.reset_actions()

    def generate_actions(self, data):
        action_chains = list()
        for i in data:
            if 'run' in i:
                pass
            else:
                query = self.parse_action(i)
                act_ = self.generate_action(query)
                action_chains.append(act_)
        self.action_chains = action_chains

    def parse_action(self, data):
        d = {}
        for key, value in data.items():
            d = {'action': key}
            d_ = {}
            if value:
                for child_key, child_value in value.items():
                    d_[child_key] = child_value
                d.update(d_)
        return d

    def generate_action(self, query):
        action = self.action
        driver = self.driver
        act_ = Actions(action, driver, query)
        return act_


class Actions(ActionsHandler):
    action = None
    query = None
    action_execute = None
    move_to_center = False

    def __init__(self, action, driver, query):
        self.action = action
        self.driver = driver
        self.action_type = query.pop('action')
        query['driver'] = driver
        query['action'] = action
        try:
            self.move_to_center = query['move_to_window_center']
        except Exception:
            self.move_to_center = False
        self.query = self.parse_arguments(self.action_type, query)

    def run(self):
        return self.__getattribute__(self.action_type)(**self.query)


    def parse_arguments(self, action_type, query):
        func = getattr(self, action_type)
        argspecs = inspect.signature(func)
        param = list(argspecs.parameters.keys())
        q = {}
        for i in param:
            if argspecs.parameters[i].default is None:
                q[i] = flatten_dictionaries(query.get(i, {}))
            else:
                q[i] = flatten_dictionaries(query[i])
        return q

    def click(self, action, on_element=None):
        if on_element:
            on_element = self.get_element(on_element)
            if self.move_to_center:
                self._move_element_to_center(on_element)
        d = {'on_element': on_element}
        return action.click(**d).perform()

    def click_and_hold(self, action,  on_element=None):
        if on_element:
            on_element = self.get_element(element)
            if self.move_to_center:
                self._move_element_to_center(on_element)
        d = {'on_element': on_element}
        return action.click_and_hold(**d).perform()

    def context_click(self, action, on_element=None):
        if on_element:
            on_element = self.get_element(element)
            if self.move_to_center:
                self._move_element_to_center(on_element)
        d = {'on_element': on_element}
        return action.context_click(**d).perform()

    def double_click(self, action, on_element=None):
        if on_element:
            on_element = self.get_element(element)
            if self.move_to_center:
                self._move_element_to_center(on_element)
        d = {'on_element': on_element}
        return action.double_click(**d).perform()

    def drag_and_drop(self, action, source, target):
        source = self.get_element(source)
        target = self.get_element(target)
        if self.move_to_center:
            self._move_element_to_center(source)
        d = {'source': source, 'target': target}
        return action.drag_and_drop(**d).perform()

    def drag_and_drop_by_offset(self, action, source, xoffset, yoffset):
        driver = self.driver
        source = self.get_element(source)
        if self.move_to_center:
            self._move_element_to_center(source)
        d = {'source': source, 'xoffset': xoffset, 'yoffset': yoffset}
        return action.drag_and_drop_by_offset(**d).perform()

    def key_down(self, action, value, element=None):
        value_ = self.modifier_key(value)
        if element:
            element = self.get_element(element)
            if self.move_to_center:
                self._move_element_to_center(element)
        if value == value_:
            return 0
        else:
            d = {'value': value, 'element': element}
            return action.key_down(**d).perform()

    def key_up(self, action, value, element=None):
        value_ = self.modifier_key(value)
        if element:
            element = self.get_element(element)
            if self.move_to_center:
                self._move_element_to_center(element)
        if value_ == value:
            return 0
        else:
            d = {'value': value, 'element': element}
            return action.key_up(**d).perform()

    def move_by_offset(self, action, xoffset, yoffset):
        d = {'xoffset': xoffset, 'yoffset': yoffset}
        return action.move_by_offset(**d).perform()

    def move_to_element(self, action, to_element):
        driver = self.driver
        to_element = self.get_element(to_element)
        if self.move_to_center:
            self._move_element_to_center(to_element)
        d = {'to_element': to_element}
        return action.move_to_element(**d).perform()

    def move_to_element_with_offset(self, action, to_element, xoffset, yoffset):
        driver = self.driver
        to_element = self.get_element(to_element)
        if self.move_to_center:
            self._move_element_to_center(to_element)
        d = {'xoffset': xoffset, 'yoffset': yoffset, 'to_element': to_element}
        return action.move_to_element_with_offset(**d).perform()
    
    def pause(self, action, seconds):
        d = {'seconds': seconds}
        return action.pause(**d).perform()

    def release(self, action, on_element=None):
        if on_element:
            on_element = self.get_element(element)
        d = {'on_element': on_element}
        return action.release(**d).perform()
    
    def perform(self, action):
        return action.perform()

    def reset_actions(self, action):
        return action

    def send_keys(self, action, value):
        if value['type'] == 'modifier':
            key_to_send = self.modifier_key(value['key'])
        else:
            key_to_send = value['key']
        return action.send_keys(key_to_send).perform()
    
    def send_keys_to_element(self, action, element, value):
        if value['type'] == 'modifier':
            key_to_send = self.modifier_key(value['key'])
        else:
            key_to_send = value['key']
        element = self.get_element(element)
        if self.move_to_center:
            self._move_element_to_center(element)
        d = [element, key_to_send]
        return action.send_keys_to_element(*d).perform()

    def get_element(self, elements):
        driver = self.driver
        to_element = None
        for locator_, value in elements.items():
            delay = 3
            type_ = elementFilterTool[locator_]
            try:
                myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((type_,value)))
            except TimeoutException:
                print ("Loading took too much time!")
            to_element = driver.find_element(type_, value)
        return to_element

    def _move_element_to_center(self, element):
        driver = self.driver
        x = element.location['x']
        y = element.location['y']
        windowHeight = driver.execute_script("return window.innerHeight")
        centerHeightY = (y-(windowHeight/3))
        driver.execute_script("return window.scrollTo(0,{});".format(centerHeightY))
        sleep(0.1)

    def modifier_key(self, value):
        mod_key =  {'ADD': "u'\ue025'",
                    'ALT': "u'\ue00a'",
                    'ARROW_DOWN': "u'\ue015'",
                    'ARROW_LEFT': "u'\ue012'",
                    'ARROW_RIGHT': "u'\ue014'",
                    'ARROW_UP': "u'\ue013'",
                    'BACKSPACE': "u'\ue003'",
                    'BACK_SPACE': "u'\ue003'",
                    'CANCEL': "u'\ue001'",
                    'CLEAR': "u'\ue005'",
                    'COMMAND': "u'\ue03d'",
                    'CONTROL': "u'\ue009'",
                    'DECIMAL': "u'\ue028'",
                    'DELETE': "u'\ue017'",
                    'DIVIDE': "u'\ue029'",
                    'DOWN': "u'\ue015'",
                    'END': "u'\ue010'",
                    'ENTER': "u'\ue007'",
                    'EQUALS': "u'\ue019'",
                    'ESCAPE': "u'\ue00c'",
                    'F1': "u'\ue031'",
                    'F10': "u'\ue03a'",
                    'F11': "u'\ue03b'",
                    'F12': "u'\ue03c'",
                    'F2': "u'\ue032'",
                    'F3': "u'\ue033'",
                    'F4': "u'\ue034'",
                    'F5': "u'\ue035'",
                    'F6': "u'\ue036'",
                    'F7': "u'\ue037'",
                    'F8': "u'\ue038'",
                    'F9': "u'\ue039'",
                    'HELP': "u'\ue002'",
                    'HOME': "u'\ue011'",
                    'INSERT': "u'\ue016'",
                    'LEFT': "u'\ue012'",
                    'LEFT_ALT': "u'\ue00a'",
                    'LEFT_CONTROL': "u'\ue009'",
                    'LEFT_SHIFT': "u'\ue008'",
                    'META': "u'\ue03d'",
                    'MULTIPLY': "u'\ue024'",
                    'NULL': "u'\ue000'",
                    'NUMPAD0': "u'\ue01a'",
                    'NUMPAD1': "u'\ue01b'",
                    'NUMPAD2': "u'\ue01c'",
                    'NUMPAD3': "u'\ue01d'",
                    'NUMPAD4': "u'\ue01e'",
                    'NUMPAD5': "u'\ue01f'",
                    'NUMPAD6': "u'\ue020'",
                    'NUMPAD7': "u'\ue021'",
                    'NUMPAD8': "u'\ue022'",
                    'NUMPAD9': "u'\ue023'",
                    'PAGE_DOWN': "u'\ue00f'",
                    'PAGE_UP': "u'\ue00e'",
                    'PAUSE': "u'\ue00b'",
                    'RETURN': "u'\ue006'",
                    'RIGHT': "u'\ue014'",
                    'SEMICOLON': "u'\ue018'",
                    'SEPARATOR': "u'\ue026'",
                    'SHIFT': "u'\ue008'",
                    'SPACE': "u'\ue00d'",
                    'SUBTRACT': "u'\ue027'",
                    'TAB': "u'\ue004'",
                    'UP': "u'\ue013"}
        
        if value in mod_key:
            return mod_key[value]
        else:
            return value


