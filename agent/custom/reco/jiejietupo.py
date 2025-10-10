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
                            "roi_offset": [self.delta_x * i, self.delta_y * j, 0, 0]
                        }
                    },
                )
                # logger.debug(reco_detail1)
                if reco_detail1:
                    InitTuPoStatus.topu_status[i + 3 * j] = 1
                    continue

                # try:
                #     result1 = reco_detail1.best_result
                #     logger.debug(result1)
                # except:
                #     pass

                reco_detail2 = context.run_recognition(
                    "RCO-检测突破失败",
                    argv.image,
                    {
                        "RCO-检测突破失败": {
                            "roi_offset": [self.delta_x * i, self.delta_y * j, 0, 0]
                        }
                    },
                )
                # logger.debug(reco_detail2)
                if reco_detail2:
                    InitTuPoStatus.topu_status[i + 3 * j] = -1
                    continue
                else:
                    InitTuPoStatus.topu_status[i + 3 * j] = 0
                # try:
                #     result2 = reco_detail2.best_result
                #     logger.debug(result2)
                # except:
                #     pass
        logger.debug(InitTuPoStatus.topu_status)
        return CustomRecognition.AnalyzeResult(box=[0, 0, 0, 0], detail="")

    @classmethod
    def get_next_tupo(self):
        index = None
        for i, v in enumerate(self.topu_status):
            if v != 1:
                index = i
                break

        j = index // 3
        i = index % 3
        roi = [307 + i * self.delta_x, 170 + j * self.delta_y, 123, 74]
        # logger.debug(roi)
        # logger.debug(f"{i}, {j}")
        return CustomRecognition.AnalyzeResult(roi, f"({i}, {j})")


@AgentServer.custom_recognition("IsLastTuPo")
class IsLastTuPo(InitTuPoStatus):
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        if IsLastTuPo.topu_status.count(1) >= 8:
            return IsLastTuPo.get_next_tupo()
        else:
            return None


@AgentServer.custom_recognition("GetNextTuPo")
class GetNextTuPo(InitTuPoStatus):
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        return GetNextTuPo.get_next_tupo()
