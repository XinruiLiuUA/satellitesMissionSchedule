# import pandas as pd
from interval import Interval
#关于action：若接收任务，action=1,拒绝任务，action=0
import globalVariableLocalWorker3
import RemainingTimeTotalModule
#self.state = np.array([Storage,TaskNumber,label])
import sys

def get_env_feedback(S, A):
    a_omega=0.2 #平均角加速度°/s^2
    maxOmega=2 #最大角速度 °/s
    ms_b=15 #秒s
    ms_e=5 #秒s

    done=0

    rollAngle=S[3]
    # satStateTable=globalVariableLocal.get_value_satState()
    globalVariableLocalWorker3.taskListMove(S[1]) #更新完global值后要取出来
    taskList=globalVariableLocalWorker3.get_value_taskList()
    TaskTotal=globalVariableLocalWorker3.get_value_TaskTotal() #返回整个task字典变量
    # This is how agent will interact with the environment
    Tasknum = S[1]
    TaskRequirement=globalVariableLocalWorker3.get_value_Task(str(Tasknum)).copy()
    # S[2]=taskList[0]
    # RemainingTime = S[1]

    RemainingTimeTotal=RemainingTimeTotalModule.get_value_RemainingTimeTotal()

    RemainingTime = RemainingTimeTotal[S[2]].copy()

    '''
    根据当前卫星的roll angle，以及当前来临任务的roll angle,计算需要的
    机动时间，将时间添加进来临Task的时间窗口内
    '''

    taskRollAngle = TaskRequirement[4] #roll angle of incoming task
    deltaRollAngle=abs(taskRollAngle-rollAngle)#需要机动的角度
    if deltaRollAngle <= pow(maxOmega,2)/a_omega:

        attitudeManeuverTimeSeconds= 2*pow(deltaRollAngle/a_omega,0.5)+ms_b+ms_e

    else:

        attitudeManeuverTimeSeconds=(a_omega*deltaRollAngle-pow(maxOmega,2))/(a_omega*maxOmega)+ms_b+ms_e

    # attitudeManeuverTimeJulian= attitudeManeuverTimeSeconds/86400.0
    # print(attitudeManeuverTimeJulian)
    #修改incoming task的起始时间
    TaskRequirement[0] = TaskRequirement[0]-attitudeManeuverTimeSeconds





    NumTW = None  #初始化一下,免得有warning
    # print(RemainingTime)
    # print(TaskRequirement)
    for i in range(0, len(RemainingTime)):

        if (TaskRequirement[0] in RemainingTime[i]) and (TaskRequirement[1] in RemainingTime[i]):


            NumTW = i
            # print(NumTW)

            break


    if NumTW== None:

        print('Error in NumTW')
        sys.exit()

    if A == 1: #Accept=1

        R = float(TaskRequirement[3])
        S[3]= taskRollAngle #更新卫星姿态
        S[0] = S[0] - TaskRequirement[2]
        # 更新可用时间窗口
        # a=S[1]
        NewTW_1 = Interval(RemainingTime[NumTW].lower_bound, TaskRequirement[0], closed=True)
        NewTW_2 = Interval(TaskRequirement[1], RemainingTime[NumTW].upper_bound, closed=True)
        if NewTW_1.upper_bound - NewTW_1.lower_bound == 0:

            if NewTW_2.upper_bound - NewTW_2.lower_bound == 0:

                RemainingTime.pop(NumTW)


            else:

                RemainingTime.insert(NumTW + 1, NewTW_2)
                RemainingTime.pop(NumTW)

        else:

            if NewTW_2.upper_bound - NewTW_2.lower_bound == 0:

                RemainingTime.insert(NumTW, NewTW_1)
                RemainingTime.pop(NumTW + 1)

            else:

                RemainingTime.insert(NumTW, NewTW_1)
                RemainingTime.insert(NumTW + 2, NewTW_2)
                RemainingTime.pop(NumTW + 1)

        #更新下一个任务分配，如果下一个任务有冲突就跳到再下一个任务,一直验证到不冲突的任务再把任务给出去

        for i in range(0,len(taskList)):

            if taskList[0] == 0:

                S[1] = taskList[0]

                done=1

                break

            else:

                Counter=0
                #计算预分配任务是否拥有足够的机动时间，如果没有，则不分配
                rollAngleNew = S[3]
                taskRollAngleNew = TaskTotal[str(taskList[0])][4] # roll angle of incoming task
                # attitudeManeuverTimeSeconds = abs(taskRollAngle - rollAngleNew ) / omega  # /s
                # attitudeManeuverTimeJulian = attitudeManeuverTimeSeconds / 86400.0
                deltaRollAngle = abs(taskRollAngleNew - rollAngleNew)  # 需要机动的角度
                if deltaRollAngle <= pow(maxOmega, 2) / a_omega:

                    attitudeManeuverTimeSeconds = 2 * pow(deltaRollAngle / a_omega, 0.5) + ms_b + ms_e

                else:

                    attitudeManeuverTimeSeconds = (a_omega * deltaRollAngle - pow(maxOmega, 2)) / (
                                a_omega * maxOmega) + ms_b + ms_e


                for j in range(0, len(RemainingTime)):

                    if ((TaskTotal[str(taskList[0])][0]-attitudeManeuverTimeSeconds) in RemainingTime[j]) and\
                            (TaskTotal[str(taskList[0])][1] in RemainingTime[j]):

                        Counter += 1



                if S[0] < TaskTotal[str(taskList[0])][2] or Counter == 0:

                    # taskList.pop(0)  # 删除第一个元素
                    globalVariableLocalWorker3.taskListPop()
                    taskList = globalVariableLocalWorker3.get_value_taskList()
                    S[1] = taskList[0]



                else:

                    S[1] = taskList[0]

                    break

        # 判断此时的状态是否是之前的episode遍历过的
        #为什么需要判读：qtable中是为了对应状态的更新，这里是为了取出对应的timewindow
        diff = 0
        # 判断是否出现过同样的timewindow
        # print('RemainingTimeTotalBefore',RemainingTimeTotal)
        # print(Tasknum,A)

        for i in range(0, len(RemainingTimeTotal)):

            diff_TW = 0
            RemainingTime_i = RemainingTimeTotal[i].copy()
            CurrentStateRemaingingTime = RemainingTime.copy()
            CRT = len(CurrentStateRemaingingTime)
            RT = len(RemainingTime_i)

            if CRT != RT:

                diff_TW += 1


            else:
                # 由于窗口时间是被分成了几段interval存储，所以也要遍历
                for i_1 in range(0, CRT):

                    CurrentWindow = CurrentStateRemaingingTime[i_1]
                    ExisintWindow = RemainingTime_i[i_1]

                    if CurrentWindow.lower_bound != ExisintWindow.lower_bound:
                        diff_TW += 1

                        break

                    elif CurrentWindow.upper_bound != ExisintWindow.upper_bound:

                        diff_TW += 1

                        break

                    else:

                        pass
                # 判断若窗口全都一样，看看其它状态量是否相同
            if diff_TW == 0:

                S[2] = i #与RemainTimetotal中第i个时间窗口相同


            else:

                diff += 1

        if diff == len(RemainingTimeTotal):

            # new = pd.DataFrame({'Accept': 0,
            #                     'Reject': 0,
            #                     'Storage': S[0],
            #                     'IncomingTask': S[2]},
            #                    index=[0])
            #
            # q_table = q_table.append(new, ignore_index=True)
            # RemainingTimeTotal.append(RemainingTime)
            S[2]=len(RemainingTimeTotal)
            # globalVariableLocal.addNewState(S[0], S[1], S[2])
            RemainingTimeTotalModule.updateRemainTimeTotal(RemainingTime)


        else:

            pass


    else:

        R = float(0.01)

        # S[2] = taskList[0]
        # 更新下一个任务分配，如果下一个任务有冲突就跳到再下一个任务,一直验证到不冲突的任务再把任务给出去
        for i in range(0,len(taskList)):

            if taskList[0] == 0:

                S[1] = taskList[0]
                done = 1

                break

            else:

                Counter=0
                # rollAngleNew = S[3]
                # taskRollAngle = TaskTotal[str(taskList[0])][4]  # roll angle of incoming task
                # attitudeManeuverTimeSeconds = abs(taskRollAngle - rollAngleNew) / omega  # /s
                # attitudeManeuverTimeJulian = attitudeManeuverTimeSeconds / 86400.0
                rollAngleNew = S[3]
                taskRollAngleNew = TaskTotal[str(taskList[0])][4]  # roll angle of incoming task
                # attitudeManeuverTimeSeconds = abs(taskRollAngle - rollAngleNew ) / omega  # /s
                # attitudeManeuverTimeJulian = attitudeManeuverTimeSeconds / 86400.0
                deltaRollAngle = abs(taskRollAngleNew - rollAngleNew)  # 需要机动的角度
                if deltaRollAngle <= pow(maxOmega, 2) / a_omega:

                    attitudeManeuverTimeSeconds = 2 * pow(deltaRollAngle / a_omega, 0.5) + ms_b + ms_e

                else:

                    attitudeManeuverTimeSeconds = (a_omega * deltaRollAngle - pow(maxOmega, 2)) / (
                            a_omega * maxOmega) + ms_b + ms_e



                for j in range(0, len(RemainingTime)):

                    if ((TaskTotal[str(taskList[0])][0]-attitudeManeuverTimeSeconds) in RemainingTime[j]) and\
                            (TaskTotal[str(taskList[0])][1] in RemainingTime[j]):

                        Counter += 1



                if S[0] < TaskTotal[str(taskList[0])][2] or Counter == 0:

                    # taskList.pop(0)  # 删除第一个元素
                    #
                    # S[1] = taskList[0]

                    globalVariableLocalWorker3.taskListPop()
                    taskList = globalVariableLocalWorker3.get_value_taskList()
                    S[1] = taskList[0]




                else:

                    S[1] = taskList[0]

                    break

        # 判断此时的状态是否是之前的episode遍历过的
        diff = 0
        # 判断是否出现过同样的timewindow
        # print(RemainingTimeTotal)
        # print(Tasknum, A)
        for i in range(0, len(RemainingTimeTotal)):
            diff_TW = 0
            RemainTimeIndex = i
            RemainingTime_i = RemainingTimeTotal[RemainTimeIndex].copy()

            CurrentStateRemaingingTime = RemainingTime.copy()
            CRT = len(CurrentStateRemaingingTime)
            RT = len(RemainingTime_i)

            if CRT != RT:

                diff_TW += 1


            else:
                # 由于窗口时间是被分成了几段interval存储，所以也要遍历
                for i_1 in range(0, CRT):

                    CurrentWindow = CurrentStateRemaingingTime[i_1]
                    ExisintWindow = RemainingTime_i[i_1]

                    if CurrentWindow.lower_bound != ExisintWindow.lower_bound:
                        diff_TW += 1

                        break

                    elif CurrentWindow.upper_bound != ExisintWindow.upper_bound:

                        diff_TW += 1

                        break

                    else:

                        pass
                # 判断若窗口全都一样，看看其它状态量是否相同
            if diff_TW == 0:

                S[2] = i

            else:

                diff += 1

        if diff == len(RemainingTimeTotal):

            # new = pd.DataFrame({'Accept': 0,
            #                     'Reject': 0,
            #                     'Storage': S[0],
            #                     'IncomingTask': S[2]},
            #                    index=[0])
            #
            # q_table = q_table.append(new, ignore_index=True)
            # RemainingTimeTotal.append(RemainingTime)
            # S[3] = q_table.shape[0] - 1
            # S[1] = S[3]

            S[2]=len(RemainingTimeTotal)
            # globalVariableLocal.addNewState(S[0], S[1], S[2])
            RemainingTimeTotalModule.updateRemainTimeTotal(RemainingTime)

        else:

            pass

    return S,R,done

