import logging


class Device:
    def __init__(self, dev_id="default", dev_state="DEFAULT", pre_state=None, all_states=None):
        self.dev_id = dev_id
        self.cur_state = dev_state
        self.pre_state = dev_state if pre_state is None else pre_state
        self.states = all_states.copy() if all_states is not None else set()
        self.states.update([self.cur_state, self.pre_state])

    def __str__(self):
        return "DEV {0:<8} -- cur_state: {1:<5} -- pre_state: {2:<5}\n \t\t\t -- all states: {3}" \
            .format(self.dev_id[:8], self.cur_state, self.pre_state, self.states)

    def addState(self, stat):
        if stat not in self.states:
            self.states.add(stat)

    def setState(self, stat):
        self.addState(stat)
        self.pre_state = self.cur_state
        self.cur_state = stat


class DevStateFactory:
    def __init__(self, dev_stats=None):
        self.cur_stats = {}
        if dev_stats is None or not dev_stats:
            return
        # make a copy of DevStateFactory
        for dev_id in dev_stats:
            dev = dev_stats[dev_id]
            self.cur_stats[dev_id] = Device(dev.dev_id, dev.cur_state, dev.pre_state, dev.states)

    def __str__(self):
        return "\n".join(str(x) for x in self.cur_stats.values())

    def applyCommand(self, cmd):
        if cmd.dev_id not in self.cur_stats:
            self.cur_stats[cmd.dev_id] = Device(cmd.dev_id, cmd.dev_state)
        else:
            self.cur_stats[cmd.dev_id].setState(cmd.dev_state)

    def applyRoutine(self, rtn):
        rtn.skip_depth = 0
        for para_cmds in rtn.cmd_sets:
            self.applyParallelCmds(para_cmds, rtn)
        logging.info("States after APPLY {0} : \n{1}\n".format(rtn.rtn_id, str(self)))

    def applyParallelCmds(self, para_cmds, rtn):
        for cmd in para_cmds.commands:
            # logging.info("Executing: {0} at time {1}".format(cmd, para_cmds.start_time))
            # skip the commands that does not satisfy the condition
            if cmd.end_if is True and rtn.skip_depth > 0:
                rtn.skip_depth -= 1
            if rtn.skip_depth > 0:
                continue

            # if it's the start of condition block
            if cmd.begin_if is True:
                # if the dev in condition has not been touched yet, add the dev as DEFAULT by default
                if cmd.dev_id not in self.cur_stats:
                    logging.warning("Read from untouched device {0}".format(cmd.dev_id))
                    self.cur_stats[cmd.dev_id] = Device(cmd.dev_id)
                # condition is satisfied
                if self.cur_stats[cmd.dev_id].cur_state == cmd.dev_state:
                    continue
                # condition is not satisfied: skip all the commands until the end if
                logging.info("Condition not satisfied for cmd {0}".format(cmd))
                rtn.skip_depth += 1
                continue

            # Commands that need to be applied
            self.applyCommand(cmd)
        return

    def stateDiff(self, src_dev_states_fac):
        """
        :type source_states: DevStateFactory
        """
        # (this) is the target states
        diff_states = {}  # key: dev_id; value: target states
        source_states = src_dev_states_fac.cur_stats
        for dev_id in self.cur_stats:
            if dev_id not in source_states:
                logging.warning("Missing dev {0} states".format(dev_id))
                # diff_states[dev_id] = self.cur_stats[dev_id].cur_state
                continue
            if source_states[dev_id].cur_state != self.cur_stats[dev_id].cur_state:
                diff_states[dev_id] = self.cur_stats[dev_id].cur_state
        # TODO(@ry) currently is ignoring the states that source_states has but target (this) does not have

        return diff_states
