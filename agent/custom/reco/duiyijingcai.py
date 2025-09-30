import json
from typing import Any, Dict, List, Union, Optional

from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
from maa.define import RectType
from utils.logger import logger


@AgentServer.custom_recognition("DuiYiJingCai")
class DuiYiJingCai(CustomRecognition):
    """
    参数：
    {
        "zhengya": bool
    }
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        params = json.loads(argv.custom_recognition_param)
        zhengya = params.get("zhengya", True)

        reco_detail1 = context.run_recognition("J-OCR红方押注人数", argv.image)
        reco_detail2 = context.run_recognition("J-OCR蓝方押注人数", argv.image)
        # logger.debug(reco_detail1)

        red_num, red_box, blue_num, blue_box = 0, None, 0, None
        try:
            red_num = int(reco_detail1.best_result.text)
            red_box = reco_detail1.best_result.box
        except:
            pass
        try:
            blue_num = int(reco_detail2.best_result.text)
            blue_box = reco_detail2.best_result.box
        except:
            pass

        if zhengya:
            if red_num >= blue_num:
                rt_detail = str(red_num)
                rt_box = red_box
            else:
                rt_detail = str(blue_num)
                rt_box = blue_box
        else:
            if red_num < blue_num:
                rt_detail = str(red_num)
                rt_box = red_box
            else:
                rt_detail = str(blue_num)
                rt_box = blue_box

        return CustomRecognition.AnalyzeResult(box=rt_box, detail=rt_detail)
