class Para:
    RTN_FROM_FILE = True
    RTN_PATH = "/Users/ruiyang/Developer/occ/data/scn-chaos-morning.json"
    CMD_EXEC_MIN_TIME = 0.01
    CMD_EXEC_MAX_TIME = 1
    SHT_CMD_MIN_TIME = 1
    SHT_CMD_MAX_TIME = 5
    RTN_MIN_START_TIME = 0
    RTN_MAX_START_TIME = 10

    FST_RTN_FIXED = 0
    LST_RTN_FIXED = 1
    FST_LST_INTERVAL = 2
    start_time_paras = {
        "morning": [True, True, 1500]
    }

    OCC_STRATEGY = "cc-optimization"
