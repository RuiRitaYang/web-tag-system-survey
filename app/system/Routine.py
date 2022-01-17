from HyperParameters import Para
from Device import DevStateFactory
import random
import logging


class Command:
    def __init__(self, cmd_id="N/A", dev_id="default", dev_state="OFF", duration=-1,
                 stat_back=False, end_state="OFF",
                 begin_if=False, end_if=False):
        self.cmd_id = cmd_id
        self.dev_id = dev_id
        self.dev_state = dev_state.upper()
        self.begin_if = begin_if
        self.end_if = end_if
        if begin_if or end_if:
            self.state_change_after_cmd = False
            self.duration = 0
            return

        self.state_change_after_cmd = stat_back
        self.end_state = end_state
        if duration >= 0:
            self.duration = duration
        else:
            self.duration = random.uniform(Para.CMD_EXEC_MIN_TIME, Para.CMD_EXEC_MAX_TIME)

        # runtime state
        self.applicable = True

    def __str__(self):
        if self.begin_if:
            return "IF  {0:<12} -- {1:<5} {2:<3}" \
                .format(self.cmd_id[:12], self.dev_id[:5], self.dev_state[:3])
        elif self.end_if:
            return "ENDIF"
        else:
            return "CMD {0:<12} -- {1:<5} {2:<3} for {3:.2f}" \
                .format(self.cmd_id[:12], self.dev_id[:5], self.dev_state[:3], self.duration)


class ParallelCommands:
    def __init__(self, cmds, dur):
        self.commands = list(cmds)
        self.duration = dur
        # states for runtime execution
        self.start_time = 0
        self.execution_finished = False

    def __str__(self):
        return "--- Starts: {0} Dur: {1:.2f} ---\n {2} \n"\
            .format(self.start_time, self.duration, "\n ".join(str(x) for x in self.commands))

    def __lt__(self, other):
        if self.start_time == other.start_time:
            if self.duration == other.duration:
                if len(self.commands) == len(other.commands):
                    return True
                return len(self.commands) < len(other.commands)
            return self.duration < other.duration
        return self.start_time < other.start_time

    def appendCmd(self, cmd):
        self.commands.append(cmd)
        if cmd.duration > self.duration:
            self.duration = cmd.duration


class Routine:
    def __init__(self, rtn_id):
        self.rtn_id = rtn_id
        self.raw_cmds = [[]]  # Using list instead of set because of the "condition" block needs sequence
        self.cmd_sets = []  # A list of Parallel Commands, for easier execution
        self.if_depth = 0  # for routine validation
        self.devs_read = []
        self.devs_written = []

        # state for runtime execution
        self.start_time = 0
        self.execution_progress = 0  # record the index of next ParallelCommand that need to execute
        # skip_depth > 0 means the commands are in the if block that the condition is not satisfied;
        # skip _depth > 1 means the current cmd is in a nested if condition that a outer condition is not satisfied.
        self.skip_depth = 0
        self.dependency_group_id = -1
        self.commit_time = -1

        # states for co-commit runtime optimization
        self.with_condition = False
        self.final_states = {}
        self.read_from = []
        self.write_to = []

    def __str__(self):
        return "=================\n" \
               "RTN {0} starts at {3:.2f} commits at {2:.2f} with commands:\n{1}-----------\n"\
            .format(self.rtn_id, "".join(str(x) for x in self.cmd_sets),
                    self.commit_time, self.start_time)

    def appendCmd(self, cmd):
        if cmd.cmd_id is "guard":
            self.raw_cmds.append([])
        else:
            self.raw_cmds[-1].append(cmd)
            if cmd.begin_if is True:
                self.if_depth += 1
                self.with_condition = True
            elif cmd.end_if is True:
                cmd.cmd_id = ""
                self.if_depth -= 1
        return self

    '''
    Goal of finalize():
        All Commands in one Parallel Routine commands could be sent out together.
        The next ParallelCommands will be sent out right after the duration of the prev ParallelCommand in the list
        The finalized list is in cmd_sets.
    '''
    def finalize(self):
        self.validate()
        for cmd_set in self.raw_cmds:
            # dump_dict: used to deal with long running cmds (especially multiple LRC with different duration)
            #     key: start time; value: commands that shoot out at that time
            dump_dict = {0: ParallelCommands([], 0)}
            for cmd in cmd_set:
                # every cmd should be sent out at the beginning of each period
                dump_dict[0].appendCmd(cmd)
                if cmd.duration <= Para.SHT_CMD_MAX_TIME:  # One time execution, ``short running'' command
                    continue

                # "long running" command
                if cmd.state_change_after_cmd:
                    end_state_cmd = Command(cmd.cmd_id + "_back", cmd.dev_id, cmd.end_state,
                                            random.uniform(Para.CMD_EXEC_MIN_TIME, Para.CMD_EXEC_MAX_TIME))
                else:
                    end_state_cmd = Command(cmd.cmd_id + "_back", cmd.dev_id, cmd.dev_state, duration=0)

                if cmd.duration not in dump_dict:
                    dump_dict[cmd.duration] = ParallelCommands({end_state_cmd}, end_state_cmd.duration)
                else:
                    dump_dict[cmd.duration].appendCmd(end_state_cmd)

            # FIXME(@ry): check for duplicate touches on one device between guards
            # Sequentialize ParallelCommands for this cmd_set
            prev_start_t = 0
            for starting_time in sorted(dump_dict):
                self.cmd_sets.append(dump_dict[starting_time])
                if starting_time > prev_start_t:
                    self.cmd_sets[-2].duration = starting_time - prev_start_t
                    prev_start_t = starting_time
        self.devTouchInfoUpdate()

    def validate(self):
        if self.if_depth is not 0:
            logging.warning("Invalid Routine: if_depth {0}".format(self.if_depth))
            exit()

    def finished(self):
        return self.execution_progress >= len(self.cmd_sets)

    def devTouchInfoUpdate(self):
        for pcmds in self.cmd_sets:
            for cmd in pcmds.commands:
                if cmd.begin_if:
                    self.devs_read.append(cmd.dev_id)
                elif not cmd.end_if:
                    self.devs_written.append(cmd.dev_id)


class CommittedRoutines:
    def __init__(self):
        self.committed = []
        self.committed_states = DevStateFactory()

    def __str__(self):
        return "Committed Routines:\n{0}\n\nStates:\n{1}\n\nCommiting sequence {2}"\
            .format("\n".join(str(x) for x in self.committed),
                    self.committed_states,
                    ", ".join(x.rtn_id for x in self.committed))

    def commit(self, rtn, time=-1):
        # TODO(@ry) optimize
        rtn.commit_time = time
        self.committed.append(rtn)
        self.committed_states.applyRoutine(rtn)
        logging.info("States after committing {0} : \n{1}\n".format(rtn.rtn_id, self.committed_states))
        return

    def commitMultiple(self, rtns, time=-1):
        logging.info("committing rtns in sequence {0} \n with pre-commit states {1}".format(", ".join(x.rtn_id for x in rtns), self.committed_states))
        for rtn in rtns:
            self.commit(rtn, time)

    def apply(self, rtn):
        existing_states = DevStateFactory(self.committed_states.cur_stats)
        existing_states.applyRoutine(rtn)
        return existing_states

    def applyMultiple(self, rtns):
        logging.info("APPLYMULTIPLE rtns {0} atop \n{1}\n".format(", ".join(x.rtn_id for x in rtns), self.committed_states))
        existing_states = DevStateFactory(self.committed_states.cur_stats)
        for rtn in rtns:
            existing_states.applyRoutine(rtn)
        return existing_states

