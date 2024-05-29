import traceback
from typing import Union
# import logging
import logging.config
from config import FASTAPI_LOG_CONFIG




def eval_log_msgs(log_msgs: list) -> list:
    seen = []
    final = [] 
    def _eval(msg_num, msg):
        same = []
        sentence = msg.split(" ")
        
        for idx, word in enumerate(sentence):
            if word not in seen:
                seen.append(word)
            else:
                same.append(word)
        if msg_num == len(log_msgs)-1:
            same = ' '.join(same)
            final.append(same)
            [ final.append(x.split(same)[1].strip()) for x in log_msgs ]

    if len(log_msgs) > 1:
        [ _eval(msg_num, msg) for msg_num, msg in enumerate(log_msgs) ]
    else:
        final = log_msgs
    return final


def grammar_join(words: Union[list, tuple]):
    if type(words) not in (list, tuple):
        ERROR_MSG = f"Please enter a list or tuple for 'grammar_join', got an unexpected input value of {type(words)}."
        raise ValueError(ERROR_MSG)

    if len(words) == 1:
        return words[0]
    elif len(words) == 2:
        return f"{words[0]} and {words[1]}"
    elif len(words) > 2:
        sentence = f"{', '.join(words[0:len(words)-1])}, and {words[-1]}"
        return sentence
    else:
        return ""


def make_log_sentence(msg_parts: list) -> str:
    parts = eval_log_msgs(msg_parts)
    if len(parts) > 0:
        if len(parts) == 1:
            parts = f"{parts[0]}."
        elif len(parts) == 2:
            # parts = parts[0] + ' and ' + parts[1] + '.'
            parts = f"{grammar_join(parts)}."
        # elif len(parts) == 3:
        #     # parts = parts[0] + 's ---> ' + parts[1] + ' and ' + parts[2] + '.'
        #     parts = f"{parts[0]}'s ---> {grammar_join(parts[1:])}."
        else:
            # parts = parts[0] + 's ---> ' + ', '.join(parts[1:len(parts)-1]) + ', and ' + parts[len(parts)-1] + '.'
            parts = f"{parts[0]}'s ---> {grammar_join(parts[1:])}."
    return parts


def config_logging_instance(module):
    logging.config.dictConfig(FASTAPI_LOG_CONFIG)
    logger = logging.getLogger(module)
    logger.handlers
    return logger


def verbose_error_info(msg, include_custom_msg=False):
    if include_custom_msg:
        verbose_msg = f"{traceback.format_exc()}: {msg}"
    else:
        verbose_msg = f"{traceback.format_exc()}"
    return verbose_msg


def handle_info_msg(logging, msg: str, function_name: str = "") -> None:
    # info_msg = "INFO: Process " + ("'" + function_name + "' status message -- " if function_name else "") + msg
    info_msg = verbose_error_info(msg=msg, include_custom_msg=False)
    logging.info(info_msg)


def handle_warn_msg(logging, msg: str, function_name: str = "") -> None:
    # warn_msg = "WARNING: Process " + ("'" + function_name + "' yielded -- " if function_name else "") + msg
    warn_msg = verbose_error_info(msg=msg, include_custom_msg=False)
    logging.warn(warn_msg)


def handle_error_msg(logging, msg: str, function_name: str = "") -> None:
    # error_msg = "ERROR:" msg + " " + traceback.format_exc() # + sys.exc_info()[2]
    error_msg = verbose_error_info(msg=msg, include_custom_msg=False)
    logging.error(error_msg)
