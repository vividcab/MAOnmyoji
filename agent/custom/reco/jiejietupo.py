# [x0, y0, delta_x, delta_y] [146,143,332,135]
import json
from typing import Any, Dict, List, Union, Optional

from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
from maa.define import RectType
from utils.logger import logger


@AgentServer.custom_recognition("InitTuPoStatus")
class InitTuPoStatus(CustomRecognition):
    """
    参数：
    """

    x0, y0, delta_x, delta_y = 146, 143, 332, 135
    topu_status = [0 for i in range(9)]

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        params = json.loads(argv.custom_recognition_param)

        for i in range(3):
            for j in range(3):
                reco_detail1 = context.run_recognition(
                    "RCO-检测突破成功",
                    argv.image,
                    {
                        "RCO-检测突破成功": {
                            "roi": [403, 169, 54, 54],
                            "roi_offset": [self.delta_x * i, self.delta_y * j, 0, 0],
                            "template": "突破/突破成功.png",
                        }
                    },
                )
                # logger.debug(reco_detail1)
                if reco_detail1.best_result:
                    self.topu_status[i + 3 * j] = 1
                    continue

                reco_detail2 = context.run_recognition(
                    "RCO-检测突破失败",
                    argv.image,
                    {
                        "RCO-检测突破失败": {
                            "roi": [398, 142, 70, 40],
                            "roi_offset": [self.delta_x * i, self.delta_y * j, 0, 0],
                            "template": "突破/突破失败.png",
                        }
                    },
                )
                # logger.debug(reco_detail2)
                if reco_detail2.best_result:
                    self.topu_status[i + 3 * j] = -1
                    continue
                else:
                    self.topu_status[i + 3 * j] = 0

        # 0表示未进攻、1突破成功、-1突破失败
        logger.debug(self.topu_status)
        return CustomRecognition.AnalyzeResult(box=[0, 0, 10, 10], detail={})

    @classmethod
    def get_next_tupo(self):
        index = -1
        for i, v in enumerate(self.topu_status):
            if v != 1:
                index = i
                break

        if index < 0:
            return None
        j = index // 3
        i = index % 3
        roi = [307 + i * self.delta_x, 170 + j * self.delta_y, 123, 74]
        logger.debug(roi)
        logger.debug(f"row: {j+1}, col: {i+1}")
        return CustomRecognition.AnalyzeResult(roi, {"row": j + 1, "col": i + 1})


@AgentServer.custom_recognition("IsLastTuPo")
class IsLastTuPo(InitTuPoStatus):
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        if self.topu_status.count(1) >= 8:
            return self.get_next_tupo()
        else:
            return None


@AgentServer.custom_recognition("GetNextTuPo")
class GetNextTuPo(InitTuPoStatus):
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        return self.get_next_tupo()
